# -*- coding:utf-8 -*-
import httpx
from bs4 import BeautifulSoup
from .response import *

class SingleRes():
    def __init__(self, title=None, title_url=None, author=None, author_url=None,thumb_url=None):
        self.title = title
        self.title_url = title_url
        self.author = author
        self.author_url = author_url
        self.thumbnail_url = thumb_url
        self.thumbnail = None


class Ascii2D:
    """ Ascii2D search module
    """
    __instance = None

    def __init__(self,proxy=None):
        self.proxy = proxy

    def __new__(cls, *a, **k):
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def parse_html(self, data: httpx.Response) -> "list":
        soup = BeautifulSoup(data.text, 'html.parser')
        results = []
        # 找到class="wrap"的div里面的所有<img>标签
        for img in soup.find_all('div', attrs={'class': 'row item-box'}):
            img_url = "https://ascii2d.net" + str(img.img['src'])
            the_list = img.find_all('a')
            title = str(the_list[0].get_text())
            if title == "色合検索":
                results.append(SingleRes())
                continue
            title_url = str(the_list[0]["href"])
            author = str(the_list[1].get_text())
            author_url = str(the_list[1]["href"])
            results.append(SingleRes(title, title_url, author, author_url,img_url))
            #photo_file = session.get(img_url)
            text = f"titile:[{title}]({title_url})\nauther:[{author}]({author_url})"
        return results

    async def search(self, url) -> "BaseResponse":
        try:
            client = httpx.AsyncClient(proxies=self.proxy,follow_redirects=True)
            # color_res = await client.post("https://ascii2d.net/search/multi", files=files)
            color_response = await client.get("https://ascii2d.net/search/url/"+url,follow_redirects=True)
            #print(color_response.url)
            bovw_url = color_response.url.__str__().replace("/color/", "/bovw/")
            bovw_response = await client.get(bovw_url)
            color_results = self.parse_html(color_response)
            bovw_results = self.parse_html(bovw_response)
            color_results[1].thumbnail = (await client.get(color_results[1].thumbnail_url)).content
            bovw_results[1].thumbnail = (await client.get(bovw_results[1].thumbnail_url)).content
        #res = requests.post(ASCII2DURL, headers=headers, data=m, verify=False, **self.requests_kwargs)
            await client.aclose()
        except httpx.ReadTimeout:
            return BaseResponse(ACTION_FAILED,message="链接超时, 请检查网络是否通畅")
        except httpx.ProxyError:
            return BaseResponse(ACTION_FAILED,message="连接代理服务器出现错误, 请检查代理设置")

        if color_results[0].title:
            single = color_results[0]
            # 处理逻辑： 先看第一个返回结果是否带上title，如果有说明这张图已经被搜索过了，有直接结果
            # 如果第一个结果的title为空，那么直接返回第二个结果，带上缩略图让用户自行比对是否一致
            return BaseResponse(ACTION_SUCCESS, "get direct result from ascii2d color", {'index': "ascii2d颜色检索", 'title': single.title, 'url': single.title_url})
        elif bovw_results[0].title:
            single = bovw_results[0]
            return BaseResponse(ACTION_SUCCESS, "get direct result from ascii2d bovw", {'index': "ascii2d特征检索", 'title': single.title, 'url': single.title_url})
        else:

            return BaseResponse(ACTION_WARNING, "get possible results from ascii2d", [
                {'[ ascii2d': " 颜色检索 ]",  'title': color_results[1].title, 'title_url': color_results[1].title_url,
                "author":color_results[1].author,"author_url":color_results[1].author_url}, color_results[1].thumbnail,
                
                {'[ ascii2d': " 特征检索 ]",  'title': bovw_results[1].title, 'url': bovw_results[1].title_url,
                "author":bovw_results[1].author,"author_url":bovw_results[1].author_url}, bovw_results[1].thumbnail])
