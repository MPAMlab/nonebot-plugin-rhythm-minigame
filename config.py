#!/usr/bin/python
# -*- coding:utf-8 -*-
from enum import Enum
from nonebot import get_driver
from pydantic import BaseSettings, Extra


class Config(BaseSettings, extra=Extra.ignore):

    global_rhythm: bool = True  # 面包默认开关
    black_rhythm_groups: list = []  # 黑名单
    white_rhythm_groups: list = []  # 白名单

    global_database: bool = False  # 数据库是否全局，若设置了group_database，以其为优先，全局数据库文件夹名为"global"
    group_database: dict = {}  # 合并一些群的数据库 分组id将作为文件夹名 例：{"分组id":["群号1", "群号2", "群号3"]}
    # 注意：此处的分组id将生效于 special_thing_group 的设置 示例{"分组id": "炸鸡"}，原来的设置将失效
    # 特殊事件同理设置的群聊id同理请改为组id

    """操作冷却（单位：秒）"""
    cd_play: int = 900
    cd_fight: int = 5000
    cd_dan: int = 82800

    """操作随机值上限"""
    max_play: float = 15.000
    max_fight: float = 15.000
 

    """操作随机值下限"""
    min_play: float = 1.000
    min_fight: float = 1.000

    """设置是否操作值都由随机值决定"""
    is_random_play: bool = True
    is_random_fight: bool = True

    """设置是否启用有效@"""
    is_at_valid: bool = False


global_config = get_driver().config
rhythm_config = Config(**global_config.dict())  # 载入配置

class CD(Enum):
    """操作冷却（单位：秒）"""
    PLAY = rhythm_config.cd_play
    FIGHT = rhythm_config.cd_fight



class MAX(Enum):
    """操作随机值上限"""
    PLAY = rhythm_config.max_play
    FIGHT = rhythm_config.max_fight



class MIN(Enum):
    """操作随机值下限"""
    PLAY = rhythm_config.min_play
    FIGHT = rhythm_config.min_fight



def random_config():
    """设置操作数量是否由用户指定或随机"""
    from .rhythm_operate import PlayEvent, DanEvent, FightEvent
    events = [PlayEvent, DanEvent, FightEvent]
    global_settings = [rhythm_config.is_random_play, rhythm_config.is_random_fight, rhythm_config.is_random_dan]

    for event_, setting in zip(events, global_settings):
        if not setting:
            event_.set_random_global(False)
"""
    for event_, setting in zip(events, special_settings):
        if setting:
            for group_id in setting.keys():
                event_(group_id).set_random(setting[group_id])
"""