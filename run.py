import requests
from bs4 import BeautifulSoup
followers = []

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
            email = node.find('li',{'aria-label':'Email'}).text.strip()
        except Exception as e:
            email = ''
        return {'username':username,'email':email}

    def user_followers(self, username, page=1):
        try:
            # 遍历用户列表
            node = self.__get_page(url='%s%s/?page=%s&tab=followers' % (self.base_url, username, page))
            all_user_node = node.find('div',{'class':'js-repo-filter position-relative'})
            users_node = all_user_node.find_all('div',{'class':'d-table col-12 width-full py-4 border-bottom border-gray-light'})
            for i in users_node:
                follower = i.find('span',{'class':'link-gray pl-1'}).text
                followers.append(follower)
            print(page, followers)
            try:
                # 页码数目加一
                self.user_followers(username=username, page=page+1)
            except Exception as e:
                pass
        except Exception as e:
            pass
        return followers



new = github_spider()
new.user_followers(username='gvanrossum')