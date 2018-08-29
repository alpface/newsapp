# -*- coding: utf-8 -*-

from pyquery import PyQuery as pq
from urllib.parse import urlparse #这个是python3.x的用法，python2.x的请自己修改
import requests
from utils import get_random_user_agent

headers = {
    'User-Agent': get_random_user_agent
}

class myResponse:
    def __init__(self,url,method='GET',headers = headers, encode = None, **kwargs):
        try:
            self.host = urlparse(url).scheme+'://'+urlparse(url).netloc
            self.rep = requests.request(url=url, method=method,headers = headers, verify=False, **kwargs)
            self.method = method
            self.headers = self.rep.request.headers
            self.ok = self.rep.ok
            self.url = self.rep.url
            self.rep.encoding = encode
            self.text = self.rep.text
            content = self.rep.content
         #   print(content)
            self.doc = pq(content)
            try:
                self.json = self.rep.json()
            except:
                self.json = {}
            self.cookies = self.rep.cookies    
        except Exception as e:
            print('链接' + url + '获取错误：' + str(e))

        
