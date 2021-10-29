from nonebot import on_command, CommandSession
from nonebot.adapters import Bot,Event
from nonebot.adapters.cqhttp import MessageSegment
from nonebot.log import logger

@on_command('search')
async def search(bot:Bot, session: CommandSession):
    ...
