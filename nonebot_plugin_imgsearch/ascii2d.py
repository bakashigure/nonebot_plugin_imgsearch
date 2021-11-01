# -*- coding:utf-8 -*-
# Modified from https://github.com/kitUIN/PicImageSearch/blob/main/PicImageSearch/ascii2d.py
# Created by bakashigure
from typing import Coroutine
from bs4 import BeautifulSoup
from requests_toolbelt import MultipartEncoder
import httpx
from response import *
from typing import Coroutine
import asyncio



class SingleRes():
    def __init__(self, title=None, title_url=None, author=None, author_url=None,thumb_url=None):
        self.title = title
        self.title_url = title_url
        self.author = author
        self.author_url = author_url
        self.thumbnail_url = thumb_url
        self.thumbnail = None


class Ascii2D:
    """

    """

    def __init__(self, **requests_kwargs):
        self.requests_kwargs = requests_kwargs

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

    async def search(self, url):

        client = httpx.AsyncClient(proxies="http://127.0.0.1:7890")
        # color_res = await client.post("https://ascii2d.net/search/multi", files=files)
        color_response = await client.get("https://ascii2d.net/search/url/"+url)
        print(color_response.url)
        bovw_url = color_response.url.__str__().replace("/color/", "/bovw/")
        bovw_response = await client.get(bovw_url)
        await client.aclose()
        color_results = self.parse_html(color_response)
        bovw_results = self.parse_html(bovw_response)
        #res = requests.post(ASCII2DURL, headers=headers, data=m, verify=False, **self.requests_kwargs)

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
                {'index': "ascii2d颜色检索",  'title': color_results[1].title, 'title_url': color_results[1].title_url,
                "author":color_results[1].author,"author_url":color_results[1].author_url}, color_results[1].thumbnail_url,
                
                {'index': "ascii2d特征检索",  'title': bovw_results[1].title, 'url': bovw_results[1].title_url,
                "author":bovw_results[1].author,"author_url":bovw_results[1].author_url}, bovw_results[1].thumbnail_url])



def sync(coroutine: Coroutine):
    """
    同步执行异步函数，使用可参考 [同步执行异步代码](https://www.moyu.moe/bilibili-api/#/sync-executor)

    Args:
        coroutine (Coroutine): 异步函数

    Returns:
        该异步函数的返回值
    """
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coroutine)

"""
asc = Ascii2D()
res = sync(asc.search("https://gchat.qpic.cn/gchatpic_new/1142580641/830606346-3201629122-9F46B66B93B5CF7712D7FD28D90CEB0B/0?term=3"))
print(res.content)
"""
