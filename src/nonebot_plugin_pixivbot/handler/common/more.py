from typing import TypeVar

from nonebot_plugin_pixivbot.global_context import context
from nonebot_plugin_pixivbot.model import PostIdentifier
from nonebot_plugin_pixivbot.postman import PostDestination
from nonebot_plugin_pixivbot.utils.errors import BadRequestError
from .common import CommonHandler

UID = TypeVar("UID")
GID = TypeVar("GID")


@context.root.register_singleton()
class MoreHandler(CommonHandler):
    @classmethod
    def type(cls) -> str:
        return "more"

    def enabled(self) -> bool:
        return self.conf.pixiv_more_enabled

    async def actual_handle(self, *, count: int = 1,
                            post_dest: PostDestination[UID, GID],
                            silently: bool = False):
        req = self.recorder.get_req(PostIdentifier.from_post_dest(post_dest))
        if not req:
            raise BadRequestError("你还没有发送过请求")

        await req(count=count, post_dest=post_dest)