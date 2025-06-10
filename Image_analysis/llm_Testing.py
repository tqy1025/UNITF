import os
import time

import pytesseract
import re
from PIL import Image
import openai
from openai import OpenAI
import ollama
import csv
import requests
import json
from PIL import Image, ImageEnhance, ImageFilter

import unit
import aspose.words as aw

API_KEY = "XXXXXX"
SECRET_KEY = "XXXXXXX"

api_key_ = "XXXXXXXX"

api_key_llama = "XXXXXXXXX"

deepseek_version = "deepseek-r1:14b"


# Step 1: 获取并按文件名排序图片文件列表
def get_sorted_image_files(folder_path1):
    files = [f for f in os.listdir(folder_path1) if f.endswith(('.png', '.jpg', '.jpeg'))]
    # files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
    return files


# Step 2: OCR 识别图片中的文字
def ocr_image(image_path, language_):
    try:
        image = Image.open(image_path)

        # 指定Tesseract的路径（根据实际情况修改）
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

        # 加载并预处理图像
        # image = Image.open('path/to/your/image.jpg')
        image = image.convert('L')  # 转换为灰度图
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2)  # 提高对比度
        # image = image.filter(ImageFilter.MedianFilter())  # 应用中值滤波去噪
        image = image.point(lambda x: 0 if x < 140 else 255)  # 二值化

        if language_ != '':
            text = pytesseract.image_to_string(image, lang=language_)
        else:
            text = pytesseract.image_to_string(image)
    except Exception as msg:
        text = ''
    return text


def clean_text(text1):
    # 去除格式为 xx:xx 的时间字符串
    text1 = re.sub(r'\b\d{1,2}:\d{2}\b', '', text1)
    # 去除多余的空格和换行符
    text1 = re.sub(r'\s+', ' ', text1)
    text1 = text1.strip()
    # 保留中文、字母、数字和空格，去掉其他特殊字符
    text1 = re.sub(r'[^\w\s\u4e00-\u9fa5]', '', text1)  # \u4e00-\u9fa5 是中文字符范围
    return text1


def analyze_text_for_interception_ollama(input_text_):
    host = "127.0.0.1"
    port = "11434"
    url = f"http://{host}:{port}/api/chat"
    model = deepseek_version
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,  # 模型选择
        "options": {
            "temperature": 0.5  # 为0表示不让模型自由发挥，输出结果相对较固定，>0的话，输出的结果会比较放飞自我
        },
        "stream": False,  # 流式输出
        "messages": [
            {
                "role": "user",
                "content": "1. 将 Web Client 页面显示的文字按照“是否直接表达了被干预的意思”分类为Intervened或Allowed。" \
                           "2. 你不需要判断提供的文字是否应该被干预，只需要判断文字是否直接表示它们本次已经被干预；" \
                           "3. 如果是Intervened，请根据文字指出：拦截原因(Intervened_Reason)，拦截关键词("
                           "Intervened_Keywords)。拦截原因是对被干预的原因的总结，拦截关键词是原文中用于作出判断的关键词。" \
                           "4. 使用示例JSON格式回答，一个包含三个key的JSON对象。" \
 \
                           "示例1：" \
                           "\"Everything starts with Identity Identity can create great user experiences "
                           "increase customer signups improve employee productivity and get apps to market faster "
                           "Talk to us\"" \
 \
                           "JSON响应：" \
                           "{" \
                           "\"IntervenedOrAllowed\": \"Allowed\"," \
                           "\"Intervened_Reason\": \"null\"," \
                           "\"Intervened_Keywords\": \"null\"," \
                           "}" \
 \
                           "示例2：" \
                           "\"您要访问的是诈骗网站 currentlyatt.mmm.page上的攻击者可能会诱骗您做一些危险的事情，例如安装软件或泄露您的个人信息（如密码、电话号码或信用卡信息)。了解详情 "
                           "向Google发送您访问的部分网页的网址、有限的系统信息 以及部分网页内容，帮助我们为所有人改善网络安全环 境。隐私权政策\"" \
 \
                           "JSON响应：" \
 \
                           "{" \
                           "\"IntervenedOrAllowed\": \"Intervened\"," \
                           "\"Intervened_Reason\": \"Security\"," \
                           "\"Intervened_Keywords\": \"诈骗网站\"," \
                           "}" \
 \
                           "示例3：" \
                           "\"非官方网页，如需继续访问，请保护好个人信息。\"" \
 \
                           "JSON响应：" \
 \
                           "{" \
                           "\"IntervenedOrAllowed\": \"Intervened\"," \
                           "\"Intervened_Reason\": \"External\"," \
                           "\"Intervened_Keywords\": \"非官方网页\"," \
                           "}" \
 \
                           "现在，请分析：" + input_text_
            }]  # 对话列表
    }
    try:
        response = requests.post(url, json=data, headers=headers, timeout=600)
    except Exception as e:
        input_text = re.sub(r'[a-zA-Z]', '', input_text_)
        data["messages"][0]["content"] = "你是一个通过文本检测网页是否已经被浏览器拦截的分析助手，我会提供给你浏览器对某一网址的访问结果中包括的文本，网页的文本出现与拦截相关的字符或词语：如：’禁止‘，’拦截‘，视为被拦截。注意1：不需要根据文本性质判断该网页是否会被拦截，举例如：假设文本里面包含成人内容，视为是否拦截必须为‘否’，原因是:如果其已经被拦截了，就不会包括成人内容。注意2：区分浏览器拦截和网络拦截并记录，比如，具有以下或者类似关键字的，(404, 网络错误, 无法访问)，不视为浏览器拦截，是网络拦截。具有以下或者类似关键字的【钓鱼, 拦截, 外链】视为浏览器拦截。注意3：登陆页面、自动关闭提示、最新地址、非正常字符不视为拦截。注意4：精明扼要说明拦截原因, 拦截形式（网络拦截或者浏览器拦截）以及从原文中截取出与最代表本次拦截相关的一个关键词（不应为单个英文单词或中文汉字，保留中文或者英文原文，着重，原文！），该关键字必须来源于提供的原文。注意5：结果以表格形式给出，表头为（是否拦截，拦截形式，拦截关键词，拦截原因），[是否拦截必须为‘是’或者‘否’，是否拦截为‘否’的时候，后面置为空]。网页文本如下：" + input_text
        response = requests.post(url, json=data, headers=headers, timeout=600)
    res = response.json()

    return res['message']['content']


def extract_fields(text):

    pattern = (
        r'\|.*?\|.*?\|.*?\|.*?\|\n'
        r'\|[-\| ]+\|\n'
        r'\|(\s*.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|'
    )

    # 查找所有符合模式的行
    match = re.search(pattern, text, re.DOTALL)
    # match = re.search(pattern, text, re.MULTILINE)

    if match:
        intercepted = match.group(1).strip()
        form = match.group(2).strip()
        keyword = match.group(3).strip()
        reason = match.group(4).strip()
        return intercepted, form, keyword, reason
    else:
        return None, None, None, None


def save_to_csv(csv_path, filename1, intercepted1, form1, keyword1, reason1):
    """将独立变量值写入CSV文件"""
    # 组织数据结构
    row_data = {
        "file_name": str(filename1),
        "intercepted": str(intercepted1),
        "form": str(form1),
        "keyword": str(keyword1),
        "reason": str(reason1)
    }

    # 定义CSV表头顺序
    fieldnames = ["file_name", "intercepted", "form", "keyword", "reason"]

    # 自动处理文件存在性检测和编码
    file_exists = os.path.isfile(csv_path)

    with open(csv_path, 'a' if file_exists else 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(row_data)


def save_to_csv_json(csv_path, data):
    """将独立变量值写入CSV文件"""

    # 定义CSV表头顺序
    fieldnames = ["filename", "IntervenedOrAllowed", "Intervened_Keywords", "Intervened_Reason", "time"]

    # 自动处理文件存在性检测和编码
    file_exists = os.path.isfile(csv_path)

    with open(csv_path, 'a' if file_exists else 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(data)


def extract_json_string(input_str):
    # 匹配 ```json 和 ``` 之间的内容（包含换行符）
    pattern = r'```json\s*(.*?)\s*```'
    match = re.search(pattern, input_str, re.DOTALL)
    return match.group(1).strip() if match else None


def aggregate_results(result_):
    # 统计Allowed和Intervened的数量
    count_allowed = 0
    count_intervened = 0
    for item in result_:
        if item["IntervenedOrAllowed"] == "Allowed":
            count_allowed += 1
        else:
            count_intervened += 1

    # 判断多数派
    if count_allowed >= 2:
        return {
            "IntervenedOrAllowed": "Allowed",
            "Intervened_Keywords": None,
            "Intervened_Reason": None
        }
    else:
        # 收集所有Intervened项的Keywords和Reason
        keywords = []
        reasons = []
        for item in result_:
            if item["IntervenedOrAllowed"] == "Intervened":
                if item["Intervened_Keywords"] not in keywords:
                    keywords.append(item["Intervened_Keywords"])
                if item["Intervened_Reason"] not in reasons:
                    reasons.append(item["Intervened_Reason"])
        return {
            "IntervenedOrAllowed": "Intervened",
            "Intervened_Keywords": keywords,
            "Intervened_Reason": reasons
        }


if __name__ == '__main__':
    page_path = "I:\\Target_LLM_Testing\\Allowed10"
    image_files = get_sorted_image_files(page_path)

    for filenames in image_files:
        text_path = page_path + "_text\\" + filenames + '.txt'

        with open(text_path, 'r', encoding='utf-8') as file:
            text = file.read()  # 将整个文件内容读取为一个字符串

        print(text)  # 输出文件内容

        result_ = []
        time_ = 0
        digit = 0
        while digit < 3:
            print(f"=======================第{digit + 1}次测试===========================")
            T1 = time.time()
            result = analyze_text_for_interception_ollama(text)
            T2 = time.time()
            print(result)
            time_ += (T2 - T1) * 1000

            result1 = extract_json_string(result)
            result1 = result1.replace('\n', '')

            try:
                data = json.loads(result1)
            except Exception as msg:
                continue

            if ("IntervenedOrAllowed" not in data) or ("Intervened_Reason" not in data) \
                    or ("Intervened_Keywords" not in data):
                continue
            result_.append(data)
            digit += 1


        data1 = aggregate_results(result_)

        data1['filename'] = filenames
        data1['time'] = time_

        save_to_csv_json(page_path + "_" + deepseek_version.split(':')[1] + ".csv", data1)

