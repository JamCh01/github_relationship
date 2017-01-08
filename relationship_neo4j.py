import common_spider
import gc
from py2neo import Graph, Node, Relationship
import gevent
from gevent import monkey
monkey.patch_socket()
graph = Graph(password='test')
graph.delete_all()
username = 'HolaJam'
level = 0
main_node = Node('user', name=username, level=level, referer='')
graph.create(main_node)

res = {}

# common_spider.info(username=username)
# common_spider.starred(username=username)
# common_spider.repos(username=username)


def user_info(username):
    gevent.joinall([
        gevent.spawn(common_spider.followers, username),
        gevent.spawn(common_spider.following, username),
    ])
    each = set(res['followers']) & set(res['following'])  # 互相关注为关注者和粉丝的交集
    res['followers'] = list(set(res['followers']) -
                            each)  # 根据关注和粉丝与互相关注的差集去掉重复数据
    res['following'] = list(set(res['following']) - each)
    res['each'] = list(each)
    return res


def find_node(level):
    # 获得同等级所有用户节点，遍历之
    user_list = graph.find(
        label='user',
        property_key='level',
        property_value=level)
    return user_list


def find_rel(main, target):
    run = '''Match(main:user {name:"%s"}) Match(target:user {name:"%s"}) return (main)-[*]->(target)''' % (
        main, target)
    print(run)
    a = graph.run(run).data()
    return a


def draw(res, referer, level):
    draw_tx = graph.begin(autocommit=False)
    # 在neo4j中绘制节点和关系
    # main_node为name: referer
    main_node = graph.find_one(
        'user',
        property_key='name',
        property_value=referer)
    for key in res.keys():
        for i in res[key]:
            # 暂存节点，label:user name:表示referer的关系用户，包括follower，following，each
            tmp = graph.find_one('user', property_key='name', property_value=i)
            if tmp is None:
                tmp = Node('user', name=i, referer=referer, level=level)
                draw_tx.create(tmp)
            if find_rel(main=referer, target=i) != []:
                continue

            # 因为关注是用户行为，不能以偏概全作为一种关系，所以详细的将each分为四种关系，在逻辑层面上更加合理
            rel_type = {
                # 主节点和tmp节点关系为follower
                'main2tmp_follower': Relationship(main_node, 'follower', tmp),
                # 主节点和tmp节点关系为following
                'main2tmp_following': Relationship(main_node, 'following', tmp),
                # tmp节点和主节点关系为follower
                'tmp2main_follower': Relationship(tmp, 'follower', main_node),
                # tmp节点和主节点关系为following
                'tmp2main_following': Relationship(tmp, 'following', main_node)
            }

            # 分别判断关系类型，绘制关系
            if key == 'each':
                for rel_key in rel_type.keys():
                    draw_tx.create(rel_type[rel_key])
            elif key == 'followers':
                draw_tx.create(rel_type['main2tmp_follower'])
            elif key == 'following':
                draw_tx.create(rel_type['main2tmp_following'])
    draw_tx.commit()
    draw_tx.finished()


while level != 5:
    for i in find_node(level=level):
        print(i['name'])
        res = user_info(username=i['name'])
        draw(res=res, referer=i['name'], level=level + 1)
    level += 1
    gc.collect()
