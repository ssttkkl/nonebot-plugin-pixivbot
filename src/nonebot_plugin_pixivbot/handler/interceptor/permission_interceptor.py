from abc import ABC, abstractmethod
from inspect import isawaitable
from typing import TypeVar, Callable, Generic, Union, Awaitable

from lazy import lazy
from nonebot import get_bot, logger

from nonebot_plugin_pixivbot.config import Config
from nonebot_plugin_pixivbot.global_context import context
from nonebot_plugin_pixivbot.handler.interceptor.interceptor import Interceptor
from nonebot_plugin_pixivbot.postman import PostDestination, Postman
from nonebot_plugin_pixivbot.utils.nonebot import get_adapter_name

UID = TypeVar("UID")
GID = TypeVar("GID")


class PermissionInterceptor(Interceptor[UID, GID], ABC, Generic[UID, GID]):
    permission_denied_reply = None

    @lazy
    def postman(self):
        return context.require(Postman)

    @abstractmethod
    def has_permission(self, post_dest: PostDestination[UID, GID]) -> Union[bool, Awaitable[bool]]:
        raise NotImplementedError()

    async def intercept(self, wrapped_func: Callable, *,
                        post_dest: PostDestination[UID, GID],
                        silently: bool,
                        **kwargs):
        p = self.has_permission(post_dest)
        if isawaitable(p):
            p = await p

        if p:
            await wrapped_func(post_dest=post_dest, silently=silently, **kwargs)
        else:
            if not silently and self.permission_denied_reply:
                await self.postman.send_plain_text(self.permission_denied_reply, post_dest=post_dest)


class AnyPermissionInterceptor(PermissionInterceptor[UID, GID], Generic[UID, GID]):
    def __init__(self, *interceptors: PermissionInterceptor):
        self.interceptors = list(interceptors)

    def append(self, interceptor: PermissionInterceptor):
        self.interceptors.append(interceptor)

    async def has_permission(self, post_dest: PostDestination[UID, GID]) -> bool:
        for inter in self.interceptors:
            p = inter.has_permission(post_dest)
            if isawaitable(p):
                p = await p

            if p:
                return True

        return False


class AllPermissionInterceptor(PermissionInterceptor[UID, GID], Generic[UID, GID]):
    def __init__(self, *interceptors: PermissionInterceptor):
        self.interceptors = list(interceptors)

    def append(self, interceptor: PermissionInterceptor):
        self.interceptors.append(interceptor)

    async def has_permission(self, post_dest: PostDestination[UID, GID]) -> bool:
        for inter in self.interceptors:
            p = inter.has_permission(post_dest)
            if isawaitable(p):
                p = await p

            if not p:
                return False

        return True


@context.register_singleton()
class SuperuserInterceptor(PermissionInterceptor[UID, GID], Generic[UID, GID]):
    def __init__(self):
        bot = get_bot()
        self.superusers = bot.config.superusers.copy()

    def has_permission(self, post_dest: PostDestination[UID, GID]) -> bool:
        return str(post_dest.user_id) in self.superusers \
               or f"{get_adapter_name()}:{post_dest.user_id}" in self.superusers


@context.register_singleton()
class GroupAdminInterceptor(PermissionInterceptor[UID, GID], Generic[UID, GID]):
    def has_permission(self, post_dest: PostDestination[UID, GID]) -> bool:
        logger.warning("base GroupAdminInterceptor was used, please implement it for your specific adaptor.")
        return not post_dest.group_id


@context.register_singleton()
class BlacklistInterceptor(PermissionInterceptor[UID, GID], Generic[UID, GID]):
    def __init__(self):
        self.blacklist = context.require(Config).blacklist

    def has_permission(self, post_dest: PostDestination[UID, GID]) -> bool:
        return str(post_dest.user_id) not in self.blacklist \
               and f"{get_adapter_name()}:{post_dest.user_id}" not in self.blacklist