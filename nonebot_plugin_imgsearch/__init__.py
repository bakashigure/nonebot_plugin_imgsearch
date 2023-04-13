from nonebot import on_command
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.log import logger
from nonebot.typing import T_State

from .ascii2d import Ascii2D
from .saucenao import SauceNao
from .utils import get_message_image
from .config import search_proxy, saucenao_api_key

logger.warning(f"PROXY: {search_proxy}")
logger.warning(f"S_API: {saucenao_api_key}")
Search = on_command('search')


def have_image(images: list) -> bool:
    return len(images) > 0

saucenao = SauceNao(saucenao_api_key, search_proxy)
ascii2d = Ascii2D(search_proxy)

@Search.handle()
async def search(bot: Bot, event: Event, state: T_State):
    images = get_message_image(event.json())
    if have_image(images):
        for image in images:
            logger.info(f"imgsearch: search -> \"{image}\"")

            logger.info(f"SauceNAO: searching...")
            res_sauce = await saucenao.search(image)
            if res_sauce.status_code//100 == 2:
                logger.info(f"SauceNAO: hit on {res_sauce.content['rate']}")
                res_text = f"[ {res_sauce.content['index']} / {res_sauce.content['rate']} ]\n" + \
                    "\n".join(f"{k}: {v}"for k,
                              v in res_sauce.content['data'].items())
                message = MessageSegment.reply(
                    event.message_id)+MessageSegment.text(res_text)
                await bot.send(event, message)
            elif res_sauce.status_code//100 == 3:
                logger.info("SauceNAO: not found")
                logger.info(f"Ascii2D: searching...")
                res_ascii = await ascii2d.search(image)
                if res_ascii.status_code//100 == 2:
                    message = MessageSegment.reply(event.message_id)+MessageSegment.text(
                        "\n".join(f"{k}: {v}"for k, v in res_ascii.content.items()))
                    await bot.send(event, message)

                elif res_ascii.status_code//100 == 3:
                    message_1 = MessageSegment.reply(event.message_id)+MessageSegment.text("\n".join(f"{k}: {v}"for k, v in res_ascii.content[0].items())) +\
                        MessageSegment.image(res_ascii.content[1])
                    message_2 = MessageSegment.reply(event.message_id)+MessageSegment.text("\n".join(f"{k}: {v}"for k, v in res_ascii.content[2].items())) +\
                        MessageSegment.image(res_ascii.content[3])
                    logger.info(f"Ascii2D: sending possible results...")
                    await bot.send(event, message_1)
                    await bot.send(event, message_2)
                elif res_ascii.status_code//100 == 4:
                    logger.info(f"Ascii2D: {res_ascii.message}")

            elif res_sauce.status_code//100 == 4:
                logger.error(f"SauceNAO: {res_sauce.message}")
