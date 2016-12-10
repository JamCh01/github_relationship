import requests
import demjson
from bs4 import BeautifulSoup
headers = {

}
'''
一个辣鸡爬虫
'''


class github_spider(object):

    def __init__(self):
        pass

    def __page_source(self, username, action):
        '''
        :param action: your repo star folloing follower and so on
        :return:
        '''
        _url = 'https://github.com/%s?tab=%s' % (username, action)
        r = requests.get(url=_url)
        res = (r.text.encode(r.encoding).decode('utf8'))
        return res

    def __page_soup(self, username, action):
        return BeautifulSoup(
            self.__page_source(
                username=username,
                action=action),
            'html.parser')

    def __get_data(self, soup, **kwargs):
        '''
        私有方法，获得单一标签
        :param soup: bs4对象
        :param kwargs: 对应标签参数，tag标签名，key-value标签特有属性
        :return: 标签
        '''
        tag = kwargs['tag']
        key = kwargs['key']
        value = kwargs['value']
        node = soup.find(tag, {key: value})
        return node

    def __get_all_data(self, soup, **kwargs):
        '''
        私有方法，获得一类标签
        :param soup: bs4对象
        :param kwargs: 对应标签参数，tag标签名，key-value标签特有属性
        :return: 标签
        '''
        tag = kwargs['tag']
        key = kwargs['key']
        value = kwargs['value']
        node = soup.find_all(tag, {key: value})
        return node

    def __foreach_data(self, data):
        '''
        私有方法，遍历标签获得字符串
        :param data: 标签
        :return: 字符串存储列表
        '''
        tmp = []
        for i in data:
            tmp.append(i.text.strip())
        return tmp

    def user_info(self, username):
        try:
            node = self.__get_data(
                soup=self.__page_soup(
                    username=username,
                    action=''),
                tag='li',
                key='aria-label',
                value='Email')
            email = node.text.strip()
        except Exception as e:
            email = ''
        res = {
            'username': username,
            'email': email
        }
        return res

    def user_followers(self, username):
        node = self.__get_data(soup=self.__page_soup(username=username,
                                                     action='followers'),
                               tag='div',
                               key='class',
                               value='js-repo-filter position-relative')
        try:
            followers_node = self.__get_all_data(soup=node,
                                                 tag='span',
                                                 key='class',
                                                 value='link-gray pl-1')
            followers = self.__foreach_data(data=followers_node)
        except Exception as e:
            followers = []
        return followers

    def user_following(self, username):
        node = self.__get_data(soup=self.__page_soup(username=username,
                                                     action='following'),
                               tag='div',
                               key='class',
                               value='js-repo-filter position-relative')
        try:
            following_node = self.__get_all_data(soup=node,
                                                 tag='span',
                                                 key='class',
                                                 value='link-gray pl-1')

            following = self.__foreach_data(data=following_node)
        except Exception as e:
            following = []
        return following

    def user_starred(self, username):
        '''
        不要问我这里为什么偷懒，就是懒
        :param username: 用户名
        :return: starred列表
        '''

        try:
            starred_node = self.__get_all_data(
                soup=self.__page_soup(
                    username=username,
                    action='stars'),
                tag='div',
                key='class',
                value='d-inline-block mb-1')
            starred = self.__foreach_data(data=starred_node)
        except Exception as e:
            starred = []
        return starred

    def user_repos(self, username):
        soup = self.__page_soup(username=username, action='repositories')
        node = soup.find('div', {'class': 'js-repo-list'})
        repos = node.find_all('li')
        user_repos = []
        for repo in repos:
            name = repo.find('a', {'itemprop': 'name codeRepository'})['href']
            repo_name = name.split('/')[-1]
            try:
                description = repo.find(
                    'p', {'itemprop': 'description'}).text.strip()
            except Exception as e:
                # 没有description异常
                description = ''
            if 'fork' in repo['class']:
                fork = 'True'
            else:
                fork = 'False'
            url = 'https://github.com/%s' % name
            res = {
                'name': repo_name,
                'fork': fork,
                'url': url,
                'description': description
            }
            user_repos.append(res)
            pass
        return user_repos
