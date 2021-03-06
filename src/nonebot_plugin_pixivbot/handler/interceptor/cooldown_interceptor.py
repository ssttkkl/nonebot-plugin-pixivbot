from datetime import datetime
from math import ceil
from typing import TypeVar, Generic

from nonebot import logger

from nonebot_plugin_pixivbot.config import Config
from nonebot_plugin_pixivbot.global_context import context
from nonebot_plugin_pixivbot.model import UserIdentifier
from nonebot_plugin_pixivbot.protocol_dep.post_dest import PostDestination
from .permission_interceptor import PermissionInterceptor

UID = TypeVar("UID")
GID = TypeVar("GID")


@context.register_singleton()
class CooldownInterceptor(PermissionInterceptor):
    def __init__(self):
        super().__init__()
        self.conf = context.require(Config)
        self.last_query_time = dict[UserIdentifier[UID], datetime]()

    def has_permission(self, post_dest: PostDestination[UID, GID]) -> bool:
        if self.conf.pixiv_query_cooldown == 0:
            return True

        if not post_dest.user_id:
            logger.debug("cooldown intercept was skipped for group post")
            return True

        identifier = UserIdentifier(post_dest.adapter, post_dest.user_id)

        if str(post_dest.user_id) in self.conf.pixiv_no_query_cooldown_users \
                or str(identifier) in self.conf.pixiv_no_query_cooldown_users:
            return True

        now = datetime.now()
        if identifier not in self.last_query_time:
            self.last_query_time[identifier] = now
            return True
        else:
            logger.debug(f"last query time ({identifier}): {self.last_query_time[identifier]}")
            delta = now - self.last_query_time[identifier]
            cooldown = self.conf.pixiv_query_cooldown - delta.total_seconds()
            if cooldown > 0:
                logger.debug(f"cooldown ({identifier}): {cooldown}s")
                return False
            else:
                self.last_query_time[identifier] = now
                return True

    def get_permission_denied_msg(self, post_dest: PostDestination[UID, GID]) -> str:
        identifier = UserIdentifier(post_dest.adapter, post_dest.user_id)
        now = datetime.now()
        delta = now - self.last_query_time[identifier]
        cooldown = ceil(self.conf.pixiv_query_cooldown - delta.total_seconds())
        return f"??????CD??????{cooldown}s??????"


__all__ = ("CooldownInterceptor",)
