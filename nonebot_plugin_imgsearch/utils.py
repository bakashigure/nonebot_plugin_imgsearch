from typing import Literal, Optional, Union
import json
from PIL import Image
from io import BytesIO


def get_message_image(data:Union[str,dict]) -> "list":
    """
    返回一个包含消息中所有图片文件路径的list,

    Args : 
          * ``data: str`` : 消息内容, 来自event.json()  
          * ``type: Literal['file','url']``: 当``type``为``'file'``时, 返回的是文件路径, 当``type``为``'url'``时, 返回的是url  

    Return :
          * ``img_list: list`` : 包含图片绝对路径或url的list
    """
    if isinstance(data,str):
        data = json.loads(data)
    return  [message['data']['url'] for message in data['message'] if message['type'] == 'image']


def compress_image(bytes_image: bytes) -> "bytes":
    """
    压缩图片, 搞小一点，excited!

    Args :
          * ``bytes_image: bytes``: 图片的bytes数据

    Return :
          * ``image: bytes``: 压缩后的图片
    """

    image = Image.open(BytesIO(bytes_image))
    image.thumbnail((250,250),resample=Image.ANTIALIAS)
    image_data = BytesIO()
    image.save(image_data, format='JPEG')
    return image_data.getvalue()

