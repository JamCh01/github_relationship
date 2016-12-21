import requests
from bs4 import BeautifulSoup
res = []


class github_spider(object):

    def __init__(self):
        self.base_url = 'https://github.com/'

    def __get_page(self, url):
        r = requests.get(url=url)
        res = (r.text.encode(r.encoding).decode('utf8'))
        soup = BeautifulSoup(res, 'html.parser')
        return soup

    def user_info(self, username):
        try:
            node = self.__get_page(url='%s%s' % (self.base_url, username))
            email = node.find('li', {'aria-label': 'Email'}).text.strip()
        except Exception as e:
            email = ''
        return {'username': username, 'email': email}

    def user_followers(self, username, action, page=1):
        try:
            # 遍历用户列表
            node = self.__get_page(
                url='%s%s/?page=%s&tab=%s' %
                (self.base_url, username, page, action))
            all_user_node = node.find(
                'div', {'class': 'js-repo-filter position-relative'})
            users_node = all_user_node.find_all(
                'div', {
                    'class': 'd-table col-12 width-full py-4 border-bottom border-gray-light'})
            if users_node == []:
                return res
            for i in users_node:
                user = i.find('span', {'class': 'link-gray pl-1'}).text
                res.append(user)
            print(page, res)
            try:
                # 页码数目加一
                self.user_followers(
                    username=username, action=action, page=page + 1)
            except Exception as e:
                pass
        except Exception as e:
            pass
        return res



new = github_spider()
new.user_followers(username='Evi1m0', action='followers')