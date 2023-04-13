# -*- coding: utf-8 -*-
from nonebot import get_driver

config_dict = get_driver().config.dict()

search_proxy = None
if 'search_proxy' in config_dict:
    search_proxy = config_dict['saucenao_api_key']

saucenao_api_key = config_dict['saucenao_api_key']
