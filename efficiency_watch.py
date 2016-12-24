import time
import sys
import datetime
from py2neo import Graph
import pymysql as mariadb


def neo4j():
    graph = Graph(password='test')
    tmp = graph.run('''MATCH (n) RETURN count(n)''').evaluate()
    with open('eff.txt', 'a') as f:
        f.write('%s %s' % (str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), tmp))
def maria():
    conn = mariadb.connect(
        host='localhost',
        port=3306,
        user='root',
        passwd='test',
        db='github',
        charset='UTF8')
    with conn as cursor:
        SQL = '''SELECT COUNT(*) FROM relationship'''
        cursor.execute(SQL)
    tmp = cursor.fetchone()
    cursor.close()
    with open('eff.txt', 'a') as f:
        f.write('%s %s' % (str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), tmp))


if sys.argv[1] == 'neo4j':
    neo4j()
elif sys.argv[0] == 'maria':
    maria()