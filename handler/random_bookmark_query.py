# import nonebot

from nonebot import on_regex
from nonebot.adapters import Bot, Event
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.typing import T_State

from ..config import conf
from ..data_source import data_source
from ..errors import QueryError, NoReplyError
from ..msg_maker import make_illust_msg
from ..utils import random_illust

if conf.pixiv_random_bookmark_query_enabled:
    random_bookmark_query = on_regex("来张私家车", priority=5)


    @random_bookmark_query.handle()
    async def handle_random_bookmark_query(bot: Bot, event: Event, state: T_State, matcher: Matcher):
        try:
            illusts = await data_source.user_bookmarks(conf.pixiv_random_bookmark_user_id,
                                                       conf.pixiv_random_bookmark_max_item,
                                                       conf.pixiv_random_bookmark_max_page,
                                                       conf.pixiv_block_tags,
                                                       conf.pixiv_random_bookmark_min_bookmark,
                                                       conf.pixiv_random_bookmark_min_view)

            if len(illusts) > 0:
                illust = random_illust(illusts, conf.pixiv_random_bookmark_method)
                logger.debug(f"{len(illusts)} bookmarks found, select {illust.title} ({illust.id}).")
                msg = await make_illust_msg(illust)
                await matcher.send(msg)
            else:
                await matcher.send("别看了，没有的。")
        except NoReplyError:
            pass
        except QueryError as e:
            await matcher.send(e.reason)
            logger.warning(e)
        except TimeoutError as e:
            await matcher.send("下载超时")
            logger.warning(e)
        except Exception as e:
            logger.exception(e)
