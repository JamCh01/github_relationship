from py2neo import Node, Graph, Relationship

graph = Graph(password='test')
tmp = graph.run('''MATCH (n) RETURN count(n)''').data()