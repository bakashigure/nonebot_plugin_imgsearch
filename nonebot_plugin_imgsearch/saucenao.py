# -*- coding:utf-8 -*-
import json
import re
from collections import OrderedDict

import httpx
from loguru import logger
from .response import *

Response = BaseResponse


class SauceNao:
    """ # SauceNAO search moudle #"""

    __instance = None

    def __init__(self, saucenao_api: str, proxy: None) -> None:
        self.log = ""  # 每次搜索后更新本次日志
        self.short_remaing = 0  # 每次搜索后更新30s剩余次数
        self.long_remaing = 0  # 每次搜索后更新24h剩余次数
        self.proxy = proxy  # 魔法
        self.raw = ""  # 每次搜索的原始数据
        self.saucenao_api_key = saucenao_api

    def __new__(cls, *a, **k):
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    async def search(self, url: str) -> "Response":
        """ # SauceNAO search moudle #
        在SauceNAO中搜索这张图, 采用api模式而非网页解析, 所以你需要先去SauceNAO注册一个APIKEY

        :Args:
        * ``file_path:str`` target picture
        * ``APIKEY: str`` saucenao APIKEY (apply from https://saucenao.com/account/register)
        * ``proxy: str`` proxy (default: None , edit in .env file)

        :Returns:
        ``Response: Response``

        当搜索结果相似度小于75%时:
        >>> Response.status = ACTION_WARNING
        >>> Response.message:dict #此api在30s | 24h 内的剩余搜索次数
        >>> Response.message:str #相似度信息

        当搜索结果相似度大于75%时:
        >>> Response.status = ACTION_SUCCESS
        >>> Response.message:str #此api剩余搜索次数
        >>> Response.content:dict #返回搜索结果字典

        其他情况:
        >>> Response.status = ACTION_FAILED
        >>> Response.message:str #错误信息
        """
        bitmask_all = '999'  # 搜索saucenao全部index
        default_minsim = '75!'  # 最小匹配相似度
        #ImageFile.LOAD_TRUNCATED_IMAGES = True  # qq有时候拿到的是烂图, 不完整的
        client = httpx.AsyncClient(proxies=None)
        
        
        for i in range(3):
            try:
                img = (await client.get(url)).content
                await client.aclose()
                break
            except httpx.ReadTimeout:
                logger.warning(f"SauceNAO: 请求超时, 尝试次数 {i}")
        else:
            return Response(ACTION_FAILED,message="图片下载失败, 请检查网络是否通畅.")
            
        '''
        image = Image.open(file_path)
        image = image.convert('RGB')
        
        thumbSize = (250, 250)
        image.thumbnail(thumbSize, resample=Image.ANTIALIAS)
        imageData = io.BytesIO()
        image.save(imageData, format='PNG')
        '''

        url_all = 'http://saucenao.com/search.php?output_type=2&numres=1&minsim=' + default_minsim + '&db=' + bitmask_all + '&api_key=' + self.saucenao_api_key
        files = {'file': ('img.jpeg', img,'image/jpeg')}
        #imageData.close()
        r = None
        try:
            async with httpx.AsyncClient(proxies=self.proxy) as client:
                r = await client.post(url=url_all, files=files,follow_redirects=True)
        except httpx.ProxyError:
            return Response(ACTION_FAILED, message="代理错误, 请检查代理")
        except httpx.ReadTimeout:
            return Response(ACTION_FAILED, message="请求超时, 请检查网络, 或者是SauceNAO暂时无法访问")

        if r.status_code != 200:
            if r.status_code == 403:
                return Response(ACTION_FAILED, message="SAUCENAO_APIKEY 设置错误")
            else:
                return Response(ACTION_FAILED, message="其他错误, Error Code: " + str(r.status_code))
        else:
            results = json.JSONDecoder(
                object_pairs_hook=OrderedDict).decode(r.text)
            if int(results['header']['user_id']) > 0:
                _remain_searches = 'Remaining Searches 30s|24h: ' + \
                    str(results['header']['short_remaining']) + \
                    '|' + str(results['header']['long_remaining'])
                # print(_remain_searches)
                self.short_remaing = results['header']['short_remaining']
                self.long_remaing = results['header']['long_remaining']
                if int(results['header']['status']) == 0:
                    ...
                else:
                    if int(results['header']['status']) > 0:
                        return Response(ACTION_FAILED, message="SauceNAO服务器部分索引出现问题, 请稍后再试")
                    else:
                        return Response(ACTION_FAILED, message="图片无法读取或其他请求错误")
            else:
                return Response(ACTION_FAILED, message="图片无法读取或API错误")

            found_json = {'index': "", 'rate': "", 'data': {}}
            if int(results['header']['results_returned']) > 0:
                artwork_url = ""
                # print(results)
                self.raw = results
                rate = results['results'][0]['header']['similarity']+'%'
                # one or more results were returned
                if float(results['results'][0]['header']['similarity']) > float(results['header']['minimum_similarity']):
                    #print('hit! ' + str(results['results'][0]['header']['similarity']))

                    illust_id = 0
                    member_id = -1
                    index_id = results['results'][0]['header']['index_id']
                    page_string = ''
                    page_match = re.search(
                        '(_p[\d]+)\.', results['results'][0]['header']['thumbnail'])
                    if page_match:
                        page_string = page_match.group(1)

                    _data = results['results'][0]['data']
                    """
                    这里包含了绝大部分经常出现的搜索结果索引index, 
                    部分index由copilot自动补全,
                    如果是没包含到的index, 会返回给bot Unhandeled Index, 本次搜索结果的原始数据在self.raw中
                    """
                    if index_id == 5 or index_id == 6:
                        # 5->pixiv 6->pixiv historical
                        found_json['index'] = "pixiv"
                        member_name = _data['member_name']
                        illust_id = _data['pixiv_id']
                        title = _data['title']
                        artwork_url = f"https://pixiv.net/artworks/{illust_id}"
                        found_json['data'] = {
                            "title": title, "illust": illust_id, "author": member_name, "artwork": artwork_url}
                    elif index_id == 8:
                        # 8->nico nico seiga
                        found_json['index'] = 'seiga'
                        member_id = _data['member_id']
                        illust_id = _data['seiga_id']
                        found_json['data'] = {
                            "author": member_id, "illust": illust_id}
                    elif index_id == 9:
                        # 9 -> danbooru
                        # index name, danbooru_id, gelbooru_id, creator, material, characters, sources
                        found_json['index'] = "danbooru"
                        creator = _data['creator']
                        characters = _data['characters']
                        source = _data['source']
                        found_json['data'] = {
                            "creator": creator, "characters": characters, "source": source}
                    elif index_id == 10:
                        # 10->drawr
                        found_json['index'] = 'drawr'
                        member_id = _data['member_id']
                        illust_id = _data['drawr_id']
                        found_json['data'] = {
                            "member_id": member_id, "illust_id": illust_id}
                    elif index_id == 11:
                        # 11->nijie
                        found_json['index'] = 'nijie'
                        member_id = _data['member_id']
                        illust_id = _data['nijie_id']
                        found_json['data'] = {
                            "member_id": member_id, "illust_id": illust_id}
                    elif index_id == 12:
                        # 12 -> Yande.re
                        # ext_urls, yandere_id, creator, material, characters, source
                        found_json['index'] = "yandere"
                        creator = _data['creator']
                        if type(creator) == list:
                            creator = (lambda x: ", ".join(x))(creator)
                        characters = _data['characters']
                        source = _data['source']
                        found_json['data'] = {
                            "creator": creator, "characters": characters, "source": source}

                    elif index_id == 13:
                        # 13 -> konachan
                        # ext_urls, konachan_id, creator, material, characters, source
                        found_json['index'] = "konachan"
                        creator = _data['creator']
                        if type(creator) == list:
                            creator = (lambda x: ", ".join(x))(creator)
                        characters = _data['characters']
                        source = _data['source']
                        found_json['data'] = {
                            "creator": creator, "characters": characters, "source": source}
                    elif index_id == 18:
                        # 18-> H-Misc nhentai
                        found_json['index'] = "H-Misc"
                        source = _data['source']
                        creator = _data['creator']
                        if type(creator) == list:
                            creator = (lambda x: ", ".join(x))(creator)
                        found_json['data'] = {
                            "source": source, "creator": creator}
                        if (x := _data['jp_name']):
                            found_json['data']['jp_name'] = x
                        if (x := _data['eng_name']):
                            found_json['data']['eng_name'] = x
                    elif index_id == 31:
                        # 31 -> bcy.net
                        found_json['index'] = "bcy"
                        url = _data['ext_urls'][0]
                        title = _data['title']
                        member_name = _data['member_name']
                        found_json['data'] = {
                            'title': title, 'url': url, 'member_name': member_name}
                    elif index_id == 34:
                        # 34->da
                        found_json['index'] = 'da'
                        illust_id = _data['da_id']
                        found_json['data'] = {"illust_id": illust_id}
                    elif index_id == 38:
                        # 38 -> H-Misc (E-Hentai)
                        found_json['index'] = "H-Misc"
                        source = _data['source']
                        creator = _data['creator']
                        if type(creator) == list:
                            creator = (lambda x: ", ".join(x))(creator)
                        jp_name = _data['jp_name']
                        found_json['data'] = {
                            "source": source, "creator": creator, "jp_name": jp_name}
                    elif index_id == 39:
                        # 39 -> Artstation
                        found_json['index'] = "artstation"
                        url = _data['ext_urls'][0]
                        title = _data['title']
                        author_name = _data['author_name']
                        found_json['data'] = {
                            'title': title, 'url': url, 'author_name': author_name}
                    elif index_id == 41:
                        # 41->twitter
                        found_json['index'] = "twitter"
                        url = ",".join(_data['ext_urls'])
                        date = _data['created_at']
                        creator = _data['twitter_user_handle']
                        found_json['data'] = {"url": url,
                                              "date": date, "creator": creator}

                    else:
                        return Response(ACTION_FAILED, message=f"Unhandled Index {index_id}, check log for more infomation.")
                    #found_json['index'] = index
                    found_json['rate'] = rate
                    return Response(ACTION_SUCCESS, content=found_json)

                else:
                    return Response(ACTION_WARNING, message=f"rate: {rate}\nnot found... ;_;")

            else:
                # could potentially be negative
                if int(results['header']['long_remaining']) < 1:
                    return Response(ACTION_FAILED, message="Out of searches today. ")

                if int(results['header']['short_remaining']) < 1:
                    return Response(ACTION_FAILED, message="Out of searches in 30s. ")
