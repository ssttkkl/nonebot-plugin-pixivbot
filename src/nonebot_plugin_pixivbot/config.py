from typing import Optional, List

from nonebot import get_driver
from pydantic import BaseSettings, validator
from pydantic.fields import ModelField

from nonebot_plugin_pixivbot.enums import *
from nonebot_plugin_pixivbot.global_context import context


@context.register_singleton(**get_driver().config.dict())
class Config(BaseSettings):
    blacklist: set[str] = set()

    pixiv_refresh_token: str
    pixiv_mongo_conn_url: str
    pixiv_mongo_database_name: str
    pixiv_proxy: Optional[str]
    pixiv_query_timeout: int = 60
    pixiv_simultaneous_query: int = 8

    pixiv_download_cache_expires_in = 3600 * 24 * 7
    pixiv_illust_detail_cache_expires_in = 3600 * 24 * 7
    pixiv_user_detail_cache_expires_in = 3600 * 24 * 7
    pixiv_illust_ranking_cache_expires_in = 3600 * 6
    pixiv_search_illust_cache_expires_in = 3600 * 24
    pixiv_search_user_cache_expires_in = 3600 * 24
    pixiv_user_illusts_cache_expires_in = 3600 * 24
    pixiv_user_bookmarks_cache_expires_in = 3600 * 24
    pixiv_related_illusts_cache_expires_in = 3600 * 24
    pixiv_other_cache_expires_in = 3600 * 6

    pixiv_block_tags: List[str] = []
    pixiv_block_action: BlockAction = BlockAction.no_image

    pixiv_download_quantity: DownloadQuantity = DownloadQuantity.original
    pixiv_download_custom_domain: Optional[str]

    pixiv_compression_enabled: bool = False
    pixiv_compression_max_size: Optional[int]
    pixiv_compression_quantity: Optional[float]

    @validator('pixiv_compression_max_size', 'pixiv_compression_quantity')
    def compression_validator(cls, v, values, field: ModelField):
        if values['pixiv_compression_enabled'] and v is None:
            raise ValueError(
                f'pixiv_compression_enabled is True but {field.name} got None.')
        return v

    # pixiv_illust_query_permission = {
    #     "group": [491959457],
    #     "friend": "all"
    # }
    #
    # @validator('pixiv_illust_query_permission')
    # def query_permission_validator(cls, v, field: ModelField):
    #     if v is not None and not isinstance(v, dict):
    #         raise ValueError(f'{field} expected a dict, but got a {type(v)}.')
    #     if "group" in v:
    #         if isinstance(v["group"], list):
    #             for i, x in enumerate(v["group"]):
    #                 if not isinstance(x, int):
    #                     raise ValueError(f'{field}["group"][{i}] expected a int, but got a {type(x)}.')
    #         elif v["group"] != "all":
    #             raise ValueError(f'{field}["group"] expected "all" or a list, but got a {type(v["group"])}.')
    #     if "friend" in v:
    #         if isinstance(v["friend"], list):
    #             for i, x in enumerate(v["group"]):
    #                 if not isinstance(x, int):
    #                     raise ValueError(f'{field}["friend"][{i}] expected a int, but got a {type(x)}.')
    #         elif v["friend"] != "all":
    #             raise ValueError(f'{field}["friend"] expected "all" or a list, but got a {type(v["friend"])}.')

    pixiv_query_to_me_only = False
    pixiv_command_to_me_only = False

    pixiv_query_cooldown = 0
    pixiv_no_query_cooldown_users: List[str] = []
    pixiv_max_item_per_query = 10

    pixiv_tag_translation_enabled = True

    pixiv_more_enabled = True
    pixiv_query_expires_in = 10 * 60

    pixiv_illust_query_enabled = True

    pixiv_ranking_query_enabled = True
    pixiv_ranking_default_mode: RankingMode = RankingMode.day
    pixiv_ranking_default_range = [1, 3]
    pixiv_ranking_fetch_item = 150
    pixiv_ranking_max_item_per_query = 10

    @validator('pixiv_ranking_default_range')
    def ranking_default_range_validator(cls, v, field: ModelField):
        if len(v) < 2 or v[0] > v[1]:
            raise ValueError(f'illegal {field.name} value: {v}')
        return v

    pixiv_random_illust_query_enabled = True
    pixiv_random_illust_method = RandomIllustMethod.bookmark_proportion
    pixiv_random_illust_min_bookmark = 0
    pixiv_random_illust_min_view = 0
    pixiv_random_illust_max_page = 20
    pixiv_random_illust_max_item = 500

    pixiv_random_recommended_illust_query_enabled = True
    pixiv_random_recommended_illust_method = RandomIllustMethod.uniform
    pixiv_random_recommended_illust_min_bookmark = 0
    pixiv_random_recommended_illust_min_view = 0
    pixiv_random_recommended_illust_max_page = 40
    pixiv_random_recommended_illust_max_item = 1000

    pixiv_random_related_illust_query_enabled = True
    pixiv_random_related_illust_method = RandomIllustMethod.bookmark_proportion
    pixiv_random_related_illust_min_bookmark = 0
    pixiv_random_related_illust_min_view = 0
    pixiv_random_related_illust_max_page = 4
    pixiv_random_related_illust_max_item = 100

    pixiv_random_user_illust_query_enabled = True
    pixiv_random_user_illust_method = RandomIllustMethod.timedelta_proportion
    pixiv_random_user_illust_min_bookmark = 0
    pixiv_random_user_illust_min_view = 0
    pixiv_random_user_illust_max_page = 2 ** 31
    pixiv_random_user_illust_max_item = 2 ** 31

    pixiv_random_bookmark_query_enabled = True
    pixiv_random_bookmark_user_id: Optional[int] = None
    pixiv_random_bookmark_method = RandomIllustMethod.uniform
    pixiv_random_bookmark_min_bookmark = 0
    pixiv_random_bookmark_min_view = 0
    pixiv_random_bookmark_max_page = 2 ** 31
    pixiv_random_bookmark_max_item = 2 ** 31

    class Config:
        extra = "ignore"


__all__ = ("Config",)
