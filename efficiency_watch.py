import datetime
from py2neo import Graph

graph = Graph(password='test')
def eff():
    tmp = graph.run('''MATCH (n) RETURN count(n)''').evaluate()
    return tmp

with open('log.txt','a') as f:
    f.write('%s %s' % (str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), eff()))