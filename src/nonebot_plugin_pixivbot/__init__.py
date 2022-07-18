"""
nonebot-plugin-pixivbot

@Author         : ssttkkl
@License        : MIT
@GitHub         : https://github.com/ssttkkl/nonebot-plugin-pixivbot
"""

# ================= provide beans =================
from .global_context import context
from .providers import provide

provide(context)

# ================= register query =================
from .query import *

__all__ = ("context",)
