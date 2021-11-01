import asyncio
from nonebot import on_command
from nonebot.adapters import Bot,Event
from nonebot.adapters.cqhttp import MessageSegment
from nonebot.log import logger
from nonebot.typing import T_State

from .utils import get_message_image

async def check(images:list) -> bool:
    return len(images) == 0


_search = on_command('search')
@_search.handle()
async def search(bot:Bot, event:Event,state:T_State):
    images = get_message_image(event.json())
    if len(images) == 0:
        try:
            await asyncio.wait_for(check(images),timeout=5)
        except asyncio.TimeoutError:
            logger.warning('没有图')
            return
    #for image in images:
