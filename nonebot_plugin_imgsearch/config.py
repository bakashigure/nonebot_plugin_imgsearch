# -*- coding: utf-8 -*-
from nonebot import get_driver

config_dict = get_driver().config.dict()

search_proxy = config_dict.get('search_proxy')
saucenao_api_key = config_dict.get('saucenao_api_key')
