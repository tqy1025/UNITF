# import eventlet  # 导入eventlet这个模块/
#
# eventlet.monkey_patch()  # 必须加这条代码
import os
import re
import call_LLM
import keywords
import txt_rename
import unit
from collections import defaultdict
import imgkit
import time
from bs4 import BeautifulSoup


import imghdr

options = {
    "enable-local-file-access": None
}


# folder_path = r'G:\OfficialTest\iOSBrowser\Malware\uc'
# type = 'Malware'
# counter = 1
# region = 'China'


def clean_text(text):
    # 去除格式为 xx:xx 的时间字符串
    text = re.sub(r'\b\d{1,2}:\d{2}\b', '', text)
    # 去除多余的空格和换行符
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    # 保留中文、字母、数字和空格，去掉其他特殊字符
    text = re.sub(r'[^\w\s\u4e00-\u9fa5]', '', text)  # \u4e00-\u9fa5 是中文字符范围
    return text


def group_and_extract(file_list):
    prefix_dict = defaultdict(list)

    for file_path in file_list:
        # 获取文件路径的前缀
        prefix = os.path.dirname(file_path)
        # 使用正则表达式提取文件名中的整数部分
        match = re.search(r'.*_(\d+)\.[png|txt]', file_path)
        if match:
            integer_value = int(match.group(1))
            png_name = file_path.split('\\')[-1]
            prefix_dict[prefix].append([integer_value, png_name])

    # 返回按前缀分组且提取整数后的字典
    return dict(prefix_dict)


def record_four_inf(target_app, platform_type, url_Type, region1, counter, intercepted, text1, form, keyword, reason,
                    allow_list, block_list, vpn_global):
    # 存是否拦截
    keywords.update_intercepted(target_app, platform_type, url_Type, region1, counter, intercepted, vpn_global)
    if intercepted == '是':
        # 更新拦截类型：网络 or WebCs
        keywords.update_intercepted_type(target_app, platform_type, url_Type, region1, counter, form, vpn_global)
        if '网络' in form:
            # 更新网络关键字列表
            if keyword not in allow_list and keyword in text1:
                allow_list.append(keyword)
                allow_keyword_str = unit.split_words.join(allow_list)
                keywords.update_allow_keywords(allow_keyword_str)
        elif '浏览器' in form:
            # 更新APP关键字列表
            if keyword not in block_list and keyword in text1:
                block_list.append(keyword)
                block_keyword_str = unit.split_words.join(block_list)
                keywords.update_keywords(target_app, block_keyword_str, platform_type)
            # 记录拦截原因
            keywords.update_intercepted_reason(target_app, platform_type, url_Type, region1, counter,
                                               reason, vpn_global)


def html2img(path, out_file):
    # 从文本文件中读取 HTML 内容
    # value = 0
    with open(path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    output_file = out_file
    config = imgkit.config(wkhtmltoimage=r'D:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe')
    try:
        imgkit.from_string(html_content, output_file, config=config, options=options)
        value = 1
    except Exception as e:
        value = 0
    print(f"\tvalue:{value}")
    return value

def html2text(path):
    # 从文本文件中读取 HTML 内容
    # value = 0
    with open(path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    paragraph = soup.get_text()
    paragraph = paragraph.replace("\n", "")
    paragraph = re.sub(r'\s+', ' ', paragraph)
    print(paragraph)

    return paragraph


def html_analysis(directory_path1):
    Haijacked = 0
    directory_path = directory_path1
    directorys = txt_rename.list_all_file_paths(directory_path, 'txt')
    grouped_integers = group_and_extract(directorys)

    for prefix, integers in grouped_integers.items():
        print(f"Prefix: {prefix}, Integers: {integers}")
        prefix1 = prefix.split('\\')
        target_app = prefix1[7]
        platform_type = prefix1[2]
        index_range = prefix1[6]
        int_start = int(index_range.split('-')[0])
        int_end = int(index_range.split('-')[1])
        if prefix1[1].split('_')[1] == 'direct':
            vpn_global = 'DIRECT'
        else:
            vpn_global = '美国'
        if prefix1[4] == '3. Malicious_Phishtank':
            url_Type = 'Malicious'
            region1 = 'Phishtank'
        elif prefix1[4] == '2. Benign':
            url_Type = 'Benign'
            region1 = 'Tranco'
        elif prefix1[4] == '1. Malicious_China':
            url_Type = 'Malicious'
            region1 = 'China'
        else:
            raise Exception('prefix wrong!')
        if len(prefix1) == 10:
            if prefix1[9] == 'frontend':
                continue
        if integers[0][0] >= int_start and integers[-1][0] <= int_end:
            for index in range(len(integers)):
                html_path = os.path.join(prefix, integers[index][1])
                print(f"Processing: {html_path}")
                # print(html_path)
                # output_file = f"file/output.png"
                counter = integers[index][0]
                try:
                    text = html2text(html_path)

                    allow_list = keywords.get_allow_keywords()

                    keyword_hit = 0

                    for allow_word in allow_list:
                        if allow_word in text:
                            intercepted = '是'
                            # form = '网络拦截'
                            # keyword = allow_word
                            # reason = allow_word
                            keywords.update_hijacked(target_app, platform_type, url_Type, region1, counter, intercepted, vpn_global)
                            keyword_hit = 1
                            break

                    block_list = keywords.get_keywords(target_app, platform_type)
                    if len(block_list) != 0:
                        for block_word in block_list:
                            if block_word in text:
                                intercepted = '是'
                                # form = '浏览器拦截'
                                # keyword = block_word
                                # reason = block_word
                                keywords.update_hijacked(target_app, platform_type, url_Type, region1, counter,
                                                         intercepted, vpn_global)
                                keyword_hit = 1
                                break

                    if keyword_hit != 1:
                        # keywords.update_hijacked(target_app, platform_type, url_Type, region1, counter, '否')
                        # gpt_analysis = call_LLM.analyze_blocking_reason_wenxinyiyan(allow_list, block_list, text)
                        # gpt_analysis = call_LLM.analyze_text_for_interception(text)
                        gpt_analysis = call_LLM.analyze_text_for_interception_ollama(text)

                        print("\t", gpt_analysis)

                        # call_LLM.extract_keywords_and_reason(gpt_analysis)
                        intercepted, form, keyword, reason = call_LLM.extract_fields(gpt_analysis)
                        keywords.update_hijacked(target_app, platform_type, url_Type, region1, counter, intercepted, vpn_global)

                except Exception as msg:
                    # Haijacked = 0
                    keywords.update_hijacked(target_app, platform_type, url_Type, region1, counter, '否', vpn_global)


def png_analysis(directory_path1):
    directory_path = directory_path1
    directorys = txt_rename.list_all_file_paths(directory_path, 'png')
    grouped_integers = group_and_extract(directorys)

    for prefix, integers in grouped_integers.items():
        print(f"Prefix: {prefix}, Integers: {integers}")
        prefix1 = prefix.split('\\')
        target_app = prefix1[7]
        platform_type = prefix1[2]
        index_range = prefix1[6]
        int_start = int(index_range.split('-')[0])
        int_end = int(index_range.split('-')[1])
        if prefix1[1].split('_')[1] == 'direct':
            vpn_global = 'DIRECT'
        else:
            vpn_global = '美国'
        if prefix1[4] == '3. Malicious_Phishtank':
            url_Type = 'Malicious'
            region1 = 'Phishtank'
        elif prefix1[4] == '2. Benign':
            url_Type = 'Benign'
            region1 = 'Tranco'
        elif prefix1[4] == '1. Malicious_China':
            url_Type = 'Malicious'
            region1 = 'China'
        else:
            raise Exception('prefix wrong!')
        if len(prefix1) == 10:
            if prefix1[9] == 'frontend':
                continue
        if integers[0][0] >= int_start and integers[-1][0] <= int_end:
            for index in range(len(integers)):
                image_path = os.path.join(prefix, integers[index][1])
                print(f"\t正在分析图片: {image_path}")
                counter = integers[index][0]

                # OCR 识别
                text_ch = call_LLM.ocr_image(image_path, 'chi_sim')
                # text_ch = re.sub(r'\s+', ' ', text_ch)
                text_ch = clean_text(text_ch)
                text_ch = re.sub(r'[a-zA-Z]', '', text_ch)
                print("\t", text_ch)
                text_en = call_LLM.ocr_image(image_path, '')
                text_en = clean_text(text_en)
                print("\t", text_en)
                text = f"中文：{text_ch}, English：{text_en}"

                allow_list = keywords.get_allow_keywords()

                keyword_hit = 0

                for allow_word in allow_list:
                    if allow_word in text:
                        intercepted = '是'
                        form = '网络拦截'
                        print("\t网络keyword拦截")
                        keyword = allow_word
                        reason = allow_word
                        record_four_inf(target_app, platform_type, url_Type, region1, counter, intercepted, text, form,
                                        keyword, reason, allow_list, '', vpn_global)
                        keyword_hit = 1
                        break

                block_list = keywords.get_keywords(target_app, platform_type)
                if len(block_list) != 0:
                    for block_word in block_list:
                        if block_word in text:
                            intercepted = '是'
                            form = '浏览器拦截'
                            print("\t浏览器keyword拦截")
                            keyword = block_word
                            reason = block_word
                            record_four_inf(target_app, platform_type, url_Type, region1, counter, intercepted, text,
                                            form, keyword, reason, allow_list, block_list,vpn_global)
                            keyword_hit = 1
                            break

                if keyword_hit != 1:
                    # gpt_analysis = call_LLM.analyze_blocking_reason_wenxinyiyan(allow_list, block_list, text)
                    # gpt_analysis = call_LLM.analyze_text_for_interception(text)
                    gpt_analysis = call_LLM.analyze_text_for_interception_ollama(text)

                    print("\t", gpt_analysis)

                    # call_LLM.extract_keywords_and_reason(gpt_analysis)
                    intercepted, form, keyword, reason = call_LLM.extract_fields(gpt_analysis)
                    record_four_inf(target_app, platform_type, url_Type, region1, counter, intercepted, text, form,
                                    keyword, reason, allow_list, block_list, vpn_global)


if __name__ == '__main__':
    png_analysis(r'G:\Target_us_phishtank_1-700')