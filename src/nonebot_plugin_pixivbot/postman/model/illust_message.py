from io import BytesIO
from typing import Optional

from pydantic import BaseModel

from nonebot_plugin_pixivbot.config import Config
from nonebot_plugin_pixivbot.config.block_action import BlockAction
from nonebot_plugin_pixivbot.data import PixivRepo
from nonebot_plugin_pixivbot.global_context import context
from nonebot_plugin_pixivbot.model import Illust

conf = context.require(Config)
repo = context.require(PixivRepo)


class IllustMessageModel(BaseModel):
    title: str = ""
    author: str = ""
    create_time: str = ""
    link: str = ""
    image: bytes = bytes(0)

    header: Optional[str] = None
    number: Optional[int] = None

    block_action: Optional[BlockAction] = None
    block_message: str = ""

    @staticmethod
    def from_illust(illust: Illust, *,
                    header: Optional[str] = None,
                    number: Optional[int] = None) -> Optional["IllustMessageModel"]:
        model = IllustMessageModel(header=header, number=number)

        if illust.has_tags(conf.pixiv_block_tags):
            model.block_action = conf.pixiv_block_action
            if conf.pixiv_block_action == BlockAction.no_image:
                model.block_message = "该画像因含有不可描述的tag而被自主规制"
            elif conf.pixiv_block_action == BlockAction.completely_block:
                model.block_message = "该画像因含有不可描述的tag而被自主规制"
                return model
            elif conf.pixiv_block_action == BlockAction.no_reply:
                return None
        else:
            with BytesIO() as bio:
                bio.write(await repo.image(illust))
                model.image = bio.getvalue()

        model.title = illust.title
        model.author = f"{illust.user.name} ({illust.user.id})"
        model.create_time = illust.create_date.strftime('%Y-%m-%d %H:%M:%S')
        model.link = f"https://www.pixiv.net/artworks/{illust.id}"

        return model
