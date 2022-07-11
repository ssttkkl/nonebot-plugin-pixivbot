from typing import Generic, TypeVar, Sequence, Any

from nonebot_plugin_pixivbot.global_context import context as context
from nonebot_plugin_pixivbot.handler.common.common_handler import CommonHandler
from nonebot_plugin_pixivbot.postman import PostDestination, post_illusts
from nonebot_plugin_pixivbot.service.pixiv_account_binder import PixivAccountBinder
from nonebot_plugin_pixivbot.utils.errors import BadRequestError

UID = TypeVar("UID")
GID = TypeVar("GID")


@context.root.register_singleton()
class RandomBookmarkHandler(CommonHandler[UID, GID], Generic[UID, GID]):
    binder = context.require(PixivAccountBinder)

    @classmethod
    def type(cls) -> str:
        return "random_bookmark"

    @classmethod
    def enabled(cls) -> bool:
        return cls.conf.pixiv_random_bookmark_query_enabled

    def parse_args(self, args: Sequence[Any], post_dest: PostDestination[UID, GID]) -> dict:
        pixiv_user_id = 0
        sender_user_id = post_dest.user_id

        if len(args) > 0:
            try:
                pixiv_user_id = int(args[0])
            except ValueError:
                raise BadRequestError(f"{args[0]}不是合法的ID")

        return {"pixiv_user_id": pixiv_user_id, "sender_user_id": sender_user_id}

    async def actual_handle(self, *, sender_user_id: UID,
                            pixiv_user_id: int = 0,
                            count: int = 1,
                            post_dest: PostDestination[UID, GID],
                            silently: bool = False):
        if not pixiv_user_id and sender_user_id:
            pixiv_user_id = await self.binder.get_binding(sender_user_id)

        if not pixiv_user_id:
            pixiv_user_id = self.conf.pixiv_random_bookmark_user_id

        if not pixiv_user_id:
            raise BadRequestError("无效的Pixiv账号，或未绑定Pixiv账号")

        illusts = await self.service.random_bookmark(pixiv_user_id, count=count)

        # 记录请求
        self.record_req(post_dest.user_id, pixiv_user_id, post_dest=post_dest, count=count)
        # 记录结果
        if len(illusts) == 1:
            self.record_resp_illust(illusts[0].id, post_dest=post_dest)

        await post_illusts(illusts,
                           header=f"这是您点的私家车",
                           post_dest=post_dest)