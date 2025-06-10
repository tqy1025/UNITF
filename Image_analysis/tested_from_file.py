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


def into_database(app_, platform_, app_type, url_type, region1, counter, vpn_global):
    mydb = pymysql.connect(
        host=unit.database_host,
        user="root",
        passwd="XXXXXXXXXX",
        database="webclients_test_db"
    )

    # mydb.config['prepared'] = True
    app_index = keywords.get_app_index(app_, platform_)
    # url_index = keywords.get_url_index(type_, region_, int(index_in_set_))

    my_cursor = mydb.cursor()
    if vpn_global == '美国':
        sql = "INSERT INTO webclients_test_db.tested_records_from_file_US (app_index, app_name, app_platform, app_type, url_type, url_region, IndexInSet) values (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\',%d)" % (
            app_index, app_, platform_, app_type, url_type, region1, int(counter))

    else:
        sql = "INSERT INTO webclients_test_db.tested_records_from_file_CN (app_index, app_name, app_platform, app_type, url_type, url_region, IndexInSet) values (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\',%d)" % (
            app_index, app_, platform_, app_type, url_type, region1, int(counter))

    try:
        # 执行sql语句
        my_cursor.execute(sql)
        # 执行sql语句
        mydb.commit()
        print(f"\tDatabase: APP:{app_index} URL:{url_type}:{counter} 记录插入/更新成功。")
    except:
        # 发生错误时回滚
        mydb.rollback()
        print(f"\tDatabase: APP:{app_index} URL:{url_type}:{counter} 记录插入/更新失败。")

    mydb.close()

    return


def png_records_get(directory_path1):
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
        if len(prefix1) == 10:
            if prefix1[9] == 'frontend':
                continue
        if integers[0][0] >= int_start and integers[-1][0] <= int_end:
            for index in range(len(integers)):
                image_path = os.path.join(prefix, integers[index][1])
                print(f"\t正在记录图片: {image_path}")
                counter = integers[index][0]
                into_database(target_app, platform_type, app_type, url_Type, region1, counter, vpn_global)


if __name__ == '__main__':
    png_records_get(r'I:\Target_direct_chinamalware_1-500')
    # G:\Target_us_benign_1-1000\Android\APP\2. Benign\US_result