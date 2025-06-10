import os
import re

import pymysql
from collections import defaultdict
import unit


def list_all_file_paths(directory, file_type):
    directory1 = []
    if file_type == 'png':
        for root, _, files in os.walk(directory):
            directory_small = []
            for file_name in files:
                file_path = os.path.join(root, file_name)
                # print(file_path)
                file_path_list = file_path.split("\\")
                if len(file_path_list) < 10:
                    continue
                elif file_path_list[8] != 'screenshot' and file_path_list[8] != 'result' and file_path_list[8] != 'backend':
                    continue
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


def convert_and_rename_images(directory1, increment_by1, start_index, end_index):
    # 获取指定目录中的所有图片文件，此处可更换为
    image_extensions = ['.jpg', '.jpeg', '.webp', '.png', '.gif', '.txt']
    files = [f for f in os.listdir(directory1) if os.path.splitext(f)[1].lower() in image_extensions]

    # 按名称排序文件
    if increment_by1 > 0:
        files.sort(reverse=True, key=lambda x: int(x.split('_')[-1].split('.')[0]))
    else:
        files.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))

    for i, filename in enumerate(files):
        # for filename in os.listdir(directory1):
        if re.match(r".*_(\d+)\.png", filename):
            number_temp = filename.split('_')[-1]
            number = int(number_temp.split('.')[0])
            if start_index <= number <= end_index:
                new_number = number + increment_by1
                new_filename = f"result_{new_number}.{filename.split('.')[1]}"
                os.rename(os.path.join(directory1, filename), os.path.join(directory1, new_filename))
        elif re.match(r".*_(\d+)\.txt", filename):
            number_temp = filename.split('_')[-1]
            number = int(number_temp.split('.')[0])
            if start_index <= number <= end_index:
                new_number = number + increment_by1
                new_filename = f"html_{new_number}.{filename.split('.')[1]}"
                os.rename(os.path.join(directory1, filename), os.path.join(directory1, new_filename))


def record_results(prefix1, index, test_str):
    prefix = prefix1
    prefix = prefix.split("\\")
    platform_type = prefix[2]
    if prefix[4] == '3. Malicious_Phishtank':
        url_Type = 'Malicious'
        region1 = 'Phishtank'
    elif prefix[4] == '2. Benign':
        url_Type = 'Benign'
        region1 = 'Tranco'
    elif prefix[4] == '1. Malicious_China':
        url_Type = 'Malicious'
        region1 = 'China'
    else:
        raise Exception(f"PATH:{prefix1} wrong!")
    target_app = prefix[7]
    # number_temp = prefix[-1].split('_')[-1].split('.')[0]
    number = index
    record_test_results(target_app, platform_type, url_Type, region1, number, test_str)


def get_app_index(app, platform_type):
    mydb = pymysql.connect(
        host=unit.database_host,
        user="root",
        passwd="XXXXXXXX",
        database="webclients_test_db"
    )

    # mydb.config['prepared'] = True

    mycursor = mydb.cursor()

    app_index = -1
    sql = "SELECT * FROM web_clients WHERE name = \'%s\' and platform = \'%s\'" % (app, platform_type)

    try:
        # 执行SQL语句
        mycursor.execute(sql)
        # 获取所有记录列表
        results = mycursor.fetchall()
        app_index = results[0][0]
    except Exception as e:
        app_index = -1
        print("\tError: unable to fecth data")
        print(e)

    mydb.close()

    return app_index


def get_url_index(url_type_, region_, index_in_set_):
    mydb = pymysql.connect(
        host=unit.database_host,
        user="root",
        passwd="XXXXXXXXX",
        database="webclients_test_db"
    )

    # mydb.config['prepared'] = True

    mycursor = mydb.cursor()

    url_index = -1
    if region_ != 'Tranco':
        sql = "SELECT id FROM urls WHERE type = \'%s\' and region = \'%s\' and index_in_set = %d" % (
            url_type_, region_, index_in_set_)
    else:
        sql = "SELECT id FROM urls WHERE type = \'%s\' and index_in_set = %d" % (
            url_type_, index_in_set_)

    try:
        # print(mycursor.mogrify(sql))
        # 执行SQL语句
        mycursor.execute(sql)
        # 获取所有记录列表
        results = mycursor.fetchall()
        url_index = results[0][0]
    except Exception as e:
        url_index = -1
        print("\tError: unable to fecth data")
        print(e)

    mydb.close()

    return url_index


def record_test_results(app1, platform1, url_type1, region1, index_in_set1, test_str):
    mydb = pymysql.connect(
        host=unit.database_host,
        user="root",
        passwd="XXXXXXXXXX",
        database="webclients_test_db"
    )

    # mydb.config['prepared'] = True

    mycursor = mydb.cursor()

    sql = ""
    app_id = get_app_index(app1, platform1)
    url_id = get_url_index(url_type1, region1, index_in_set1)
    if url_id == -1:
        raise f"\tURL：{platform1}, {url_type1}, {region1}, {index_in_set1} 不存在"
    tested_str = test_str
    sql = "INSERT INTO test_records (app_index, url_index, vpn_chose, validity, tested, validity_America) VALUES (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\')  AS new_values ON DUPLICATE KEY UPDATE vpn_chose= new_values.vpn_chose, tested = new_values.tested, validity = new_values.validity, validity_America = new_values.validity_America" % (
        app_id, url_id, "America", tested_str, tested_str, 'Yes')

    try:
        # 执行sql语句
        mycursor.execute(sql)
        # 执行sql语句
        mydb.commit()
        print(f"\tDatabase: APP:{app_id} : URL:{url_id} : RESULT:{tested_str} \t\t$测试记录$\t\t插入/更新成功。")
    except:
        # 发生错误时回滚
        mydb.rollback()
        print(f"\tDatabase: APP:{app_id} : URL:{url_id} : RESULT:{tested_str} \t\t$测试记录$\t\t插入/更新失败。")

    mydb.close()
    #
    # return url_index


def group_and_extract_integers(file_list):
    prefix_dict = defaultdict(list)

    for file_path in file_list:
        # 获取文件路径的前缀
        prefix = os.path.dirname(file_path)
        # 使用正则表达式提取文件名中的整数部分
        match = re.search(r'.*_(\d+)\.png', file_path)
        if match:
            integer_value = int(match.group(1))
            prefix_dict[prefix].append(integer_value)

    # 返回按前缀分组且提取整数后的字典
    return dict(prefix_dict)


if __name__ == '__main__':
    # 使用示例，地址更换为需要重命名的文件地址
    # directory_path = r'H:\Target1\iOS\Browser\1. Malicious_China\result\301-400\quark\sceenshot'
    # convert_and_rename_images(directory_path, 1, 301, 400)

    # 使用时指定你的目录路径
    directory_path = r'H:\Target1'
    directorys = list_all_file_paths(directory_path)
    grouped_integers = group_and_extract_integers(directorys)
    total_number = 0
    numbers_dict = {}

    # 输出结果
    for prefix, integers in grouped_integers.items():
        print(f"Prefix: {prefix}, Integers: {integers}")
        index_range = prefix.split('\\')[6]
        int_start = int(index_range.split('-')[0])
        int_end = int(index_range.split('-')[1])
        app = prefix.split('\\')[7]
        app = app + '_' + prefix.split('\\')[2]
        print(app)
        numbers_dict.setdefault(app, [0, 0, 0])
        list1 = numbers_dict[app]
        app_totalnum = 0
        if len(prefix.split('\\')) == 10:
            if prefix.split('\\')[9] == 'frontend':
                continue
        if integers[0] >= int_start and integers[-1] <= int_end:
            # print(f"Prefix: {prefix}, index wrong!")
            # continue
            for i in range(int_start, int_end + 1):
                total_number += 1
                app_totalnum += 1
                if i in integers:
                    record_results(prefix, i, 'Yes')
                else:
                    record_results(prefix, i, 'No')
            if prefix.split('\\')[4] == '3. Malicious_Phishtank':
                list1[2] += app_totalnum
            elif prefix.split('\\')[4] == '2. Benign':
                list1[1] += app_totalnum
            elif prefix.split('\\')[4] == '1. Malicious_China':
                list1[0] += app_totalnum
            numbers_dict[app] = list1
        else:
            print(f"Prefix: {prefix}, index wrong!")

    print(total_number)
    print(numbers_dict)

