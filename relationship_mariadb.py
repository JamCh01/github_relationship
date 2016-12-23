import pymysql as mariadb
from common_spider import user_info

user_name = 'HolaJam'
level = 0



    # 连接MariaDB
conn = mariadb.connect(
        host='localhost',
        port=3306,
        user='root',
        passwd='test',
        db='github',
        charset='UTF8')


def mariadb_insert(user_name, level, referer, type):
    with conn as cursor:
        SQL = '''INSERT INTO relationship (user_name, level, referer, type) VALUES (%s,%s,%s,%s)'''
        cursor.execute(SQL, (user_name, level, referer, type))
    cursor.close()

def mariadb_select_forward(user_name, referer):
    with conn as cursor:
        SQL = '''SELECT * FROM relationship WHERE user_name=%s AND referer=%s'''
        cursor.execute(SQL, (user_name, referer))
    user = cursor.fetchone()
    cursor.close()
    return user


def mariadb_select_reverse(user_name, referer):
    with conn as cursor:
        SQL = '''SELECT * FROM relationship WHERE user_name=%s AND referer=%s'''
        cursor.execute(SQL, (referer, user_name))
    user = cursor.fetchone()
    cursor.close()
    return user


def find_all_level(level):
    with conn as cursor:
        SQL = '''SELECT * FROM relationship WHERE level=%s'''
        cursor.execute(SQL, level)
    levels = cursor.fetchall()
    cursor.close()
    return levels

res = user_info(username=user_name)


def draw(res, referer, level):
    for key in res.keys():
        for i in res[key]:
            # 校验是否存在本关系
            # 不存在时候插入
            if mariadb_select_forward(
                user_name=i,
                referer=referer,
            ) is None and mariadb_select_reverse(
                    user_name=i,
                    referer=referer) is None:
                # 判断关系是否为each
                if key == 'each':
                    mariadb_insert(
                        user_name=i,
                        level=level + 1,
                        referer=referer,
                        type='followers')
                    mariadb_insert(
                        user_name=i,
                        level=level + 1,
                        referer=referer,
                        type='following')
                    mariadb_insert(
                        user_name=referer,
                        level=level + 1,
                        referer=i,
                        type='followers')
                    mariadb_insert(
                        user_name=referer,
                        level=level + 1,
                        referer=i,
                        type='following')
                else:
                    mariadb_insert(
                        user_name=i,
                        level=level + 1,
                        referer=referer,
                        type=key)

mariadb_insert(user_name=user_name, level=level, referer=' ', type='self')
while level != 6:
    for i in find_all_level(level=level):
        print(i)
        draw(res=user_info(username=i[1]), referer=i[1], level=level)
    level += 1
