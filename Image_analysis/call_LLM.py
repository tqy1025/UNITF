import os
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

# 初始化关键词列表为空
blocked_phrases = []

# 指定图片所在的文件夹路径
# folder_path = r'G:\OfficialTest\iOSBrowser\Malware\uc'


API_KEY = "XXXX"
SECRET_KEY = "XXXXX"

api_key_ = "XXXXX"


api_key_llama = "XXXXXXX"


def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))


# Step 1: 获取并按文件名排序图片文件列表
def get_sorted_image_files(folder_path1):
    files = [f for f in os.listdir(folder_path1) if f.endswith(('.png', '.jpg', '.jpeg'))]
    files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
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



def analyze_text_for_interception_ollama(input_text_):
    host = "127.0.0.1"
    port = "11434"
    url = f"http://{host}:{port}/api/chat"
    model = "deepseek-r1:8b"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,  # 模型选择
        "options": {
            "temperature": 0.  # 为0表示不让模型自由发挥，输出结果相对较固定，>0的话，输出的结果会比较放飞自我
        },
        "stream": False,  # 流式输出
        "messages": [
            {
                "role": "user",
                "content": "你是一个通过文本检测网页是否已经被浏览器拦截的分析助手，我会提供给你浏览器对某一网址的访问结果中包括的文本，网页的文本出现与拦截相关的字符或词语：如：’禁止‘，’拦截‘，视为被拦截。注意1" \
                           "：不需要根据文本性质判断该网页是否会被拦截，举例如：假设文本里面包含成人内容，视为是否拦截必须为‘否’，原因是:如果其已经被拦截了，就不会包括成人内容。注意2"
                           "：区分浏览器拦截和网络拦截并记录，比如，具有以下或者类似关键字的，(404, " \
                           "网络错误, 无法访问)，不视为浏览器拦截，是网络拦截。具有以下或者类似关键字的【钓鱼, 拦截, 外链】视为浏览器拦截。注意3：登陆页面、自动关闭提示、最新地址、非正常字符不视为拦截。注意4：精明扼要说明拦截原因," \
                           "拦截形式（网络拦截或者浏览器拦截）以及从原文中截取出与最代表本次拦截相关的一个关键词（不应为单个英文单词或中文汉字，保留中文或者英文原文，着重，原文！），该关键字必须来源于提供的原文。注意5" \
                           "：结果以表格形式给出，表头为（是否拦截，拦截形式，拦截关键词，拦截原因），[是否拦截必须为‘是’或者‘否’，是否拦截为‘否’的时候，后面置为空]。网页文本如下：" + input_text_
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


def html2img(page_source_path):
    # 加载HTML文件
    doc = aw.Document(page_source_path)

    # 设置图像保存选项
    imageOptions = aw.saving.ImageSaveOptions(aw.SaveFormat.JPEG)
    imageOptions.jpeg_quality = 100
    imageOptions.horizontal_resolution = 72

    # 保存为图片
    for page in range(doc.page_count):
        extractedPage = doc.extract_pages(page, 1)
    extractedPage.save(f"Page_{page + 1}.jpg", imageOptions)


