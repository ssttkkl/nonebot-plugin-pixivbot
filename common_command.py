# import nonebot

from nonebot import Bot, on_regex, on_notice
from nonebot.adapters.cqhttp import GroupMessageEvent, Event, PokeNotifyEvent
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.typing import T_State

from .config import conf
from .distributor import distributor
from .utils import decode_integer


def _get_user_or_group_id(event: Event):
    if isinstance(event, GroupMessageEvent):
        return {"group_id": event.group_id}
    else:
        return {"user_id": event.get_user_id()}


def _parse_ranking_mode(mode):
    if mode == "日":
        mode = "day"
    elif mode == "周":
        mode = "week"
    elif mode == "月":
        mode = "month"
    elif mode == "男性":
        mode = "day_male"
    elif mode == "女性":
        mode = "day_female"
    elif mode == "原创":
        mode = "week_original"
    elif mode == "新人":
        mode = "week_rookie"
    elif mode == "漫画":
        mode = "day_manga"
    return mode


async def handle_random_recommended_illust_query(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    await distributor.distribute_random_recommended_illust(bot=bot, **_get_user_or_group_id(event))


async def handle_random_user_illust_query(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    word = state["_matched_groups"][0]
    await distributor.distribute_random_user_illust(word, bot=bot, **_get_user_or_group_id(event))


async def handle_ranking_nth_query(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    mode = state["_matched_groups"][0]
    num = state["_matched_groups"][1]

    mode = _parse_ranking_mode(mode)

    try:
        num = decode_integer(num)
    except ValueError:
        await matcher.send(f"{num}不是合法的数字")

    await distributor.distribute_ranking(mode, num, bot=bot, **_get_user_or_group_id(event))


async def handle_illust_query(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    raw_illust_id = state["_matched_groups"][0]
    try:
        illust_id = int(raw_illust_id)
    except ValueError:
        await matcher.send(raw_illust_id + "不是合法的插画ID")
        return

    await distributor.distribute_illust(illust_id, bot=bot, **_get_user_or_group_id(event))


async def handle_random_bookmark_query(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    await distributor.distribute_random_bookmark(bot=bot, **_get_user_or_group_id(event))


async def handle_random_illust_query(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    word = state["_matched_groups"][0]
    await distributor.distribute_random_illust(word, bot=bot, **_get_user_or_group_id(event))


async def handle_ranking_query(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    if "_matched_groups" in state:
        mode = state["_matched_groups"][0]
        mode = _parse_ranking_mode(mode)

        start = state["_matched_groups"][2]
        end = state["_matched_groups"][3]
        if start is not None and end is not None:
            range = (int(start), int(end))
        else:
            range = None
    else:
        mode, range = None, None

    await distributor.distribute_ranking(mode, range, bot=bot, **_get_user_or_group_id(event))


if conf.pixiv_random_recommended_illust_query_enabled:
    on_regex("来张图", priority=3, block=True).append_handler(handle_random_recommended_illust_query)

if conf.pixiv_random_user_illust_query_enabled:
    on_regex("来张(.+)老师的图", priority=4, block=True).append_handler(handle_random_user_illust_query)

if conf.pixiv_ranking_query_enabled:
    on_regex(r"看看(日|周|月|男性|女性|原创|新人)?榜\s*([1-9][0-9]*|[零一两二三四五六七八九十百千万亿]+)",
             priority=4, block=True).append_handler(handle_ranking_nth_query)
    on_regex(r"看看(日|周|月|男性|女性|原创|新人|漫画)?榜\s*(([1-9][0-9]*)[-~]([1-9][0-9]*))?",
             priority=5).append_handler(handle_ranking_query)

if conf.pixiv_illust_query_enabled:
    on_regex(r"看看图\s*([1-9][0-9]*)", priority=5).append_handler(handle_illust_query)

if conf.pixiv_random_bookmark_query_enabled:
    on_regex("来张私家车", priority=5).append_handler(handle_random_bookmark_query)

if conf.pixiv_random_illust_query_enabled:
    on_regex("来张(.+)图", priority=5).append_handler(handle_random_illust_query)

if conf.pixiv_poke_action:
    if conf.__getattribute__(f'pixiv_{conf.pixiv_poke_action}_query_enabled'):
        async def _group_poke(bot: Bot, event: Event, state: T_State) -> bool:
            return isinstance(event, PokeNotifyEvent) and event.is_tome()


        group_poke = on_notice(_group_poke, priority=10, block=True)
        group_poke.append_handler(locals()[f'handle_{conf.pixiv_poke_action}_query'])
    else:
        logger.warning(f"Bot will not respond to poke since {conf.pixiv_poke_action} is disabled.")