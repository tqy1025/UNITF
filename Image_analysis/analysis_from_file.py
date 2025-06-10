# import eventlet  # 导入eventlet这个模块/
#
# eventlet.monkey_patch()  # 必须加这条代码
import os
import re

import pymysql

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


def into_database(app_, platform_, app_type, url_type, region1, counter, vpn_global, reason, key):
    mydb = pymysql.connect(
        host=unit.database_host,
        user="root",
        passwd="XXXXXXX",
        database="XXXXXXXXX"
    )

    # mydb.config['prepared'] = True
    app_index = keywords.get_app_index(app_, platform_)
    # url_index = keywords.get_url_index(type_, region_, int(index_in_set_))

    my_cursor = mydb.cursor()
    if vpn_global == '美国':
        # sql = "UPDATE webclients_test_db.web_clients t SET t.key_words = \'%s\' WHERE t.name = \'%s\' and t.platform = " \
        #       "\'%s\'" % (keyword_str1, app_, platform)
        sql = "UPDATE webclients_test_db.tested_records_from_file_US d SET d.reason = \'%s\', d.key_words = \'%s\' " \
              " WHERE d.app_index = \'%s\' and d.url_type = \'%s\' and d.url_region = \'%s\' and d.IndexInSet = %d" % (
                  reason, key, app_index,
                  url_type, region1, int(counter))

        # sql = "INSERT INTO webclients_test_db.tested_records_from_file_US (app_index, app_name, app_platform, app_type, url_type, IndexInSet) values (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\', %d)" % (
        #     app_index, app_, platform_, app_type, url_type, int(counter))

    else:
        sql = "UPDATE webclients_test_db.tested_records_from_file_CN d SET d.reason = \'%s\', d.key_words = \'%s\' " \
              " WHERE d.app_index = \'%s\' and d.url_type = \'%s\' and d.url_region = \'%s\' and d.IndexInSet = %d" % (
                  reason, key, app_index,
                  url_type, region1, int(counter))
        # sql = "INSERT INTO webclients_test_db.tested_records_from_file_CN (app_index, app_name, app_platform, app_type, url_type, IndexInSet) values (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\', %d)" % (
        #     app_index, app_, platform_, app_type, url_type, int(counter))

    try:
        # 执行sql语句
        my_cursor.execute(sql)
        # 执行sql语句
        mydb.commit()
        print(f"\tDatabase: APP:{app_index} URL:{url_type}:{counter} 记录原因插入/更新成功。")
    except:
        # 发生错误时回滚
        mydb.rollback()
        print(f"\tDatabase: APP:{app_index} URL:{url_type}:{counter} 记录原因插入/更新失败。")

    mydb.close()

    return


def list_all_file_paths_here(directory, file_type):
    directory1 = []
    if file_type == 'png':
        for root, _, files in os.walk(directory):
            directory_small = []
            for file_name in files:
                file_path = os.path.join(root, file_name)
                # print(file_path)
                file_path_list = file_path.split("\\")
                if len(file_path_list) < 11:
                    continue
                # elif file_path_list[8] != 'screenshot' and file_path_list[8] != 'result' and file_path_list[8] != 'backend':
                #     continue
                else:
                    directory_small.append(file_path)
            try:
                directory_small.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))
            except Exception as msg:
                print(file_path)
            directory1 = directory1 + directory_small
    elif file_type == 'txt':
        for root, _, files in os.walk(directory):
            directory_small = []
            for file_name in files:
                file_path = os.path.join(root, file_name)
                # print(file_path)
                file_path_list = file_path.split("\\")
                if len(file_path_list) < 10:
                    continue
                elif file_path_list[8] != 'page_source':
                    continue
                elif file_path_list[9] == '.DS_Store':
                    continue
                else:
                    directory_small.append(file_path)
            directory_small.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))
            directory1 = directory1 + directory_small
    # directory1.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))
    return directory1


def png_records_get(directory_path1):
    directory_path = directory_path1
    directorys = list_all_file_paths_here(directory_path, 'png')
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
        if prefix1[3] == 'APP':
            app_type = 'WebView'
        else:
            app_type = 'Browser'
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
        reason = prefix1[8]
        key = prefix1[9]
        if integers[0][0] >= int_start and integers[-1][0] <= int_end:
            for index in range(len(integers)):
                image_path = os.path.join(prefix, integers[index][1])
                print(f"\t正在记录图片: {image_path}")
                counter = integers[index][0]
                into_database(target_app, platform_type, app_type, url_Type, region1, counter, vpn_global, reason, key)


if __name__ == '__main__':
    png_records_get(r'I:\Target_direct_chinamalware_1-500_analysis')
    # G:\Target_us_benign_1-1000\Android\APP\2. Benign\US_result
