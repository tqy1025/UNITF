import pymysql

import unit


def get_app_index(app_, platform_):
    mydb = pymysql.connect(
        host=unit.database_host,
        user="root",
        passwd="XXXXXXXXXX",
        database="webclients_test_db"
    )

    # mydb.config['prepared'] = True

    mycursor = mydb.cursor()

    app_index = -1
    sql = "SELECT * FROM web_clients WHERE name = \'%s\' and platform = \'%s\'" % (app_, platform_)

    try:
        # 执行SQL语句
        mycursor.execute(sql)
        # 获取所有记录列表
        results = mycursor.fetchall()
        app_index = results[0][0]
    except Exception as e:
        app_index = -1
        print("Error: unable to fecth data")
        print(e)

    mydb.close()

    return app_index


def get_url_index(type_, region_, index_in_set_):
    mydb = pymysql.connect(
        host=unit.database_host,
        user="root",
        passwd="XXXXXXXXXXX",
        database="webclients_test_db"
    )

    # mydb.config['prepared'] = True

    mycursor = mydb.cursor()

    url_index = -1
    if type_ == 'Malicious':
        sql = "SELECT id FROM urls_new WHERE type = \'%s\' and region = \'%s\' and index_in_set = %d" % (type_, region_,
                                                                                                     index_in_set_)
    else:
        sql = "SELECT id FROM urls_new WHERE type = \'%s\' and index_in_set = %d" % (type_, index_in_set_)

    try:
        print(mycursor.mogrify(sql))
        # 执行SQL语句
        mycursor.execute(sql)
        # 获取所有记录列表
        results = mycursor.fetchall()
        url_index = results[0][0]
    except Exception as e:
        url_index = -1
        print("Error: unable to fecth data")
        print(e)

    mydb.close()

    return url_index


def get_keywords(app_, platform):
    keywords_list = []
    mydb = pymysql.connect(
        host=unit.database_host,
        user="root",
        passwd="XXXXXXX",
        database="webclients_test_db"
    )

    mycursor = mydb.cursor()

    # app_index = -1
    sql = "SELECT t.key_words FROM webclients_test_db.web_clients t WHERE t.name = \'%s\' and t.platform = \'%s\'" % (
        app_, platform)

    try:
        # 执行SQL语句
        mycursor.execute(sql)
        # 获取所有记录列表
        results = mycursor.fetchall()
        if results[0][0] is not None:
            key_words = results[0][0]
            keywords_list = key_words.split(unit.split_words)
        else:
            print("\tNote: keywords 为空")
    except Exception as e:
        print("\tError: unable to fecth data")
        print(e)

    mydb.close()

    return keywords_list


def update_keywords(app_, keyword_str1, platform):
    app_index = get_app_index(app_, platform)
    keywords_list = []
    mydb = pymysql.connect(
        host=unit.database_host,
        user="root",
        passwd="XXXXXXXXX",
        database="webclients_test_db"
    )

    mycursor = mydb.cursor()

    # app_index = -1
    sql = "UPDATE webclients_test_db.web_clients t SET t.key_words = \'%s\' WHERE t.name = \'%s\' and t.platform = " \
          "\'%s\'" % (keyword_str1, app_, platform)

    try:
        # 执行sql语句
        mycursor.execute(sql)
        # 执行sql语句
        mydb.commit()
        print(f"\tDatabase: APP:{app_index} : \t$关键词$\t插入/更新成功。")
    except:
        # 发生错误时回滚
        mydb.rollback()
        print(f"\tDatabase: APP:{app_index} :  \t$关键词$\t插入/更新失败。")

    mydb.close()

    return


def get_allow_keywords():
    keywords_list = []
    mydb = pymysql.connect(
        host=unit.database_host,
        user="root",
        passwd="XXXXXXXXX",
        database="webclients_test_db"
    )

    mycursor = mydb.cursor()

    # app_index = -1
    sql = "SELECT t.network_keywords FROM webclients_test_db.allowlist t"

    try:
        # 执行SQL语句
        mycursor.execute(sql)
        # 获取所有记录列表
        results = mycursor.fetchall()
        if len(results) > 0:
            key_words = results[0][0]
            keywords_list = key_words.split(unit.split_words)
        else:
            print("\tNote: keywords 为空")
    except Exception as e:
        print("\tError: unable to fecth data")
        print(e)

    mydb.close()

    return keywords_list


def update_allow_keywords(keyword_str1):
    keywords_list = []
    mydb = pymysql.connect(
        host=unit.database_host,
        user="root",
        passwd="XXXXXXXXX",
        database="webclients_test_db"
    )

    mycursor = mydb.cursor()

    # app_index = -1
    sql = "UPDATE webclients_test_db.allowlist t SET t.network_keywords = \'%s\'" % keyword_str1

    try:
        # 执行sql语句
        mycursor.execute(sql)
        # 执行sql语句
        mydb.commit()
        print(f"\tDatabase: \t$Allowlist$\t:\t关键词$\t插入/更新成功。")
    except:
        # 发生错误时回滚
        mydb.rollback()
        print(f"\tDatabase: \t$Allowlist$\t:\t关键词$\t插入/更新失败。")

    mydb.close()

    return


def update_intercepted(app_, platform_, type_, region_, index_in_set_, wherther_intercepted,vpn_global):
    # app_index = get_app_index(app_, platform_)
    # keywords_list = []
    mydb = pymysql.connect(
        host=unit.database_host,
        user="root",
        passwd="XXXXXXXXXX",
        database="webclients_test_db"
    )

    mycursor = mydb.cursor()

    app_index = get_app_index(app_, platform_)
    url_index = get_url_index(type_, region_, int(index_in_set_))

    # app_index = -1
    if wherther_intercepted == '否':
        wherther_intercepted = 'No'
    elif wherther_intercepted == '是':
        wherther_intercepted = 'Yes'

    if vpn_global == 'DIRECT':
        sql = "UPDATE webclients_test_db.test_records_newest t SET t.intercepted_China = \'%s\' WHERE t.app_index = \'%s\' and t.url_index = " \
              "\'%s\'" % (wherther_intercepted, app_index, url_index)
    elif vpn_global == '美国':
        sql = "UPDATE webclients_test_db.test_records_newest t SET t.intercepted_America = \'%s\' WHERE t.app_index = \'%s\' and t.url_index = " \
              "\'%s\'" % (wherther_intercepted, app_index, url_index)

    try:
        # 执行sql语句
        mycursor.execute(sql)
        # 执行sql语句
        mydb.commit()
        print(f"\tDatabase: APP:{app_index} : URL:{url_index} \t$是否拦截$\t插入/更新成功。")
    except:
        # 发生错误时回滚
        mydb.rollback()
        print(f"\tDatabase: APP:{app_index} : URL:{url_index} \t$是否拦截$\t插入/更新失败。")

    mydb.close()

    return


def update_hijacked(app_, platform_, type_, region_, index_in_set_, wherther_hijacked, vpn_global):
    # app_index = get_app_index(app_, platform_)
    # keywords_list = []
    mydb = pymysql.connect(
        host=unit.database_host,
        user="root",
        passwd="XXXXXXXXXXXX",
        database="webclients_test_db"
    )

    mycursor = mydb.cursor()

    app_index = get_app_index(app_, platform_)
    url_index = get_url_index(type_, region_, int(index_in_set_))

    # app_index = -1
    if wherther_hijacked == '否':
        wherther_hijacked = 'No'
    elif wherther_hijacked == '是':
        wherther_hijacked = 'Yes'

    if vpn_global == 'DIRECT':
        sql = "UPDATE webclients_test_db.test_records_newest t SET t.haijacked_China = \'%s\' WHERE t.app_index = \'%s\' and t.url_index = " \
              "\'%s\'" % (wherther_hijacked, app_index, url_index)
    elif vpn_global == '美国':
        sql = "UPDATE webclients_test_db.test_records_newest t SET t.haijacked_America = \'%s\' WHERE t.app_index = \'%s\' and t.url_index = " \
              "\'%s\'" % (wherther_hijacked, app_index, url_index)

    try:
        # 执行sql语句
        mycursor.execute(sql)
        # 执行sql语句
        mydb.commit()
        print(f"\tDatabase: APP:{app_index} : URL:{url_index} \t$是否拦截$\t插入/更新成功。")
    except:
        # 发生错误时回滚
        mydb.rollback()
        print(f"\tDatabase: APP:{app_index} : URL:{url_index} \t$是否拦截$\t插入/更新失败。")

    mydb.close()

    return

def update_intercepted_type(app_, platform_, type_, region_, index_in_set_, form, vpn_global):
    # app_index = get_app_index(app_)
    # keywords_list = []
    mydb = pymysql.connect(
        host=unit.database_host,
        user="root",
        passwd="XXXXXXXXXXX",
        database="webclients_test_db"
    )

    mycursor = mydb.cursor()

    app_index = get_app_index(app_, platform_)
    url_index = get_url_index(type_, region_, int(index_in_set_))

    # app_index = -1
    if '网络' in form:
        intercepted_type = 'Network Intercepted'
    elif '浏览器' in form:
        intercepted_type = 'WebCs Intercepted'
    else:
        intercepted_type = form
    if vpn_global == 'DIRECT':
        sql = "UPDATE webclients_test_db.test_records_newest t SET t.intercepted_form_China = \'%s\' WHERE t.app_index = \'%s\' and " \
              "t.url_index = \'%s\'" % (intercepted_type, app_index, url_index)
    elif vpn_global == '美国':
        sql = "UPDATE webclients_test_db.test_records_newest t SET t.intercepted_form_America = \'%s\' WHERE t.app_index = \'%s\' and " \
              "t.url_index = \'%s\'" % (intercepted_type, app_index, url_index)

    try:
        # 执行sql语句
        mycursor.execute(sql)
        # 执行sql语句
        mydb.commit()
        print(f"\tDatabase: APP:{app_index} : URL:{url_index} \t$拦截主体$\t插入/更新成功。")
    except:
        # 发生错误时回滚
        mydb.rollback()
        print(f"\tDatabase: APP:{app_index} : URL:{url_index} \t$拦截主体$\t插入/更新失败。")

    mydb.close()

    return


def update_intercepted_reason(app_, platform_, type_, region_, index_in_set_, reason_, vpn_global):
    # app_index = get_app_index(app_)
    # keywords_list = []
    mydb = pymysql.connect(
        host=unit.database_host,
        user="root",
        passwd="XXXXXXXXXXX",
        database="webclients_test_db"
    )

    mycursor = mydb.cursor()

    app_index = get_app_index(app_, platform_)
    url_index = get_url_index(type_, region_, int(index_in_set_))

    # app_index = -1
    # if '网络' in form:
    #     intercepted_type = 'Network Intercepted'
    # elif '浏览器' in form:
    #     intercepted_type = 'WebCs Intercepted'
    if vpn_global == 'DIRECT':
        sql = "UPDATE webclients_test_db.test_records_newest t SET t.intercepted_reason_China = \'%s\' WHERE t.app_index = \'%s\' and " \
              "t.url_index = \'%s\'" % (reason_, app_index, url_index)
    elif vpn_global == '美国':
        sql = "UPDATE webclients_test_db.test_records_newest t SET t.intercepted_reason_America = \'%s\' WHERE t.app_index = \'%s\' and " \
              "t.url_index = \'%s\'" % (reason_, app_index, url_index)

    try:
        # 执行sql语句
        mycursor.execute(sql)
        # 执行sql语句
        mydb.commit()
        print(f"\tDatabase: APP:{app_index} : URL:{url_index} \t$拦截分析$\t插入/更新成功。")
    except:
        # 发生错误时回滚
        mydb.rollback()
        print(f"\tDatabase: APP:{app_index} : URL:{url_index} \t$拦截分析$\t插入/更新失败。")

    mydb.close()

    return


if __name__ == '__main__':
    allow_list = get_allow_keywords()

    # words = get_keywords('uc')
    # print(words)
    keyword_str = []
    # d = [y for y in keyword_str if y not in words]
    d = [y for y in keyword_str if y not in allow_list]
    keyword_str2 = unit.split_words.join(allow_list+d)
    print(keyword_str2)
    if len(d) != 0:
        # update_keywords('uc', keyword_str2)
        update_allow_keywords(keyword_str2)

    # words = get_keywords('uc')
    allow_list = get_allow_keywords()
    print(allow_list)
