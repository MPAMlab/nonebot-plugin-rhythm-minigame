#!/usr/bin/python
# -*- coding:utf-8 -*-
import random
from functools import wraps
from datetime import datetime

from .rhythm_handle import Action
from .rhythm_operate import PlayEvent, DanEvent, FightEvent, _Event
from .config import MIN, MAX, rhythm_config
#from .__init__ import play_lev

play_events = []
dan_events = []
fight_events = []


# 特殊事件修饰器
def probability(value, action: Action, *, priority: int = 5, group_id_list: list = None):
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            if random.random() < value:
                return func(*args, **kwargs)
            else:
                return None
        setattr(inner, "priority", priority)
        setattr(inner, "group_id_list", group_id_list)
        events_lists = (play_events, dan_events, fight_events)
        if action == Action.ALL:
            for events in events_lists:
                events.append(inner)
        else:
            event_list = events_lists[action.value]
            event_list.append(inner)
        return inner
    return wrapper

# region 打歌特殊事件
# 越级
@probability(0.9, Action.PLAY, priority=5)
def play_event_not_qualified(event: PlayEvent):
    random_rating = random.randint(40, 94)
    final_rating = random_rating * 0.8 
    ref_min_rating = play_lev * 84
    if event.user_data.OVERALL_RATING / 15 < ref_min_rating:
        return

    append_text = f"越级失败！{event.group_id}，得分：{random_rating}，获得Rating：{final_rating}"
    event.rhythm_db.cd_update_stamp(event.user_id, Action.PLAY)
    return append_text

# 越级成功

@probability(0.1, Action.PLAY, priority=5)
def play_event_not_qualified_lucky(event: PlayEvent):
    final_rating = 100.5 * 0.8 * play_lev
    ref_min_rating = play_lev * 84

    if event.user_data.OVERALL_RATING / 15 < ref_min_rating:
        return

    append_text = f"越级成功！{event.other_name}，得分：{random_rating}，获得Rating：{final_rating}"
    event.rhythm_db.cd_update_stamp(event.user_id, Action.PLAY)
    return append_text

"""
# 普通打

@probability(0.8, Action.PLAY, priority=5)
def play_event_normal(event: PlayEvent):
    random_rating = random.uniform(97.0, 100.4)
    final_rating = random_rating * 0.8 * play_lev
    ref_min_rating = play_lev * 84

    if 0 < event.user_data.rating / 15 - ref_min_rating < play_lev * 105.5:
        return

    append_text = f"打歌成功！{event.other_name}，得分：{random_rating}，获得Rating：{final_rating}"
    event.rhythm_db.cd_update_stamp(event.user_id, Action.PLAY)
    return append_text
"""

# 超常发挥

@probability(0.2, Action.PLAY, priority=5)
def play_event_normal_superb(event: PlayEvent):

    final_rating = 100.5 * 0.8 * play_lev
    ref_min_rating = play_lev * 84

    if 105.5 < event.user_data.rating / 15 - ref_min_rating < play_lev * 112:
        return

    append_text = f"超常发挥！{event.other_name}，得分：{random_rating}，获得Rating：{final_rating}"
    event.rhythm_db.cd_update_stamp(event.user_id, Action.PLAY)
    return append_text

# 下埋

@probability(0.1, Action.PLAY, priority=5)
def play_event_overdone(event: PlayEvent):

    final_rating = 100.5 * 0.8 * play_lev
    ref_min_rating = play_lev * 84
    if event.user_data.rating / 15 - ref_min_rating > play_lev * 112:
        return

    append_text = f"下埋完成！{event.other_name}，得分：{random_rating}，获得Rating：{final_rating}"
    event.rhythm_db.cd_update_stamp(event.user_id, Action.PLAY)
    return append_text

# endregion

# region 单曲特殊事件

# 断网

@probability(0.025, Action.PLAY, priority=5)
def play_event_lost_connection(event: PlayEvent):
    append_text = f"当前使用的账号没有正常登出，请过15分钟后再试"
    event.rhythm_db.cd_ban_action(event.user_id, Action.PLAY, 1000)
    return append_text

# 拼机（未完成）

@probability(0.2, Action.PLAY, priority=5)
def play_event_dual(event: PlayEvent):
    append_text = f"拼机成功！"
    event.rhythm_db.cd_refresh(event.user_id, Action.PLAY)
    return append_text

# 手套破了（未完成）

@probability(0.1, Action.PLAY, priority=5)
def play_event_glove_broken(event: PlayEvent):
    append_text = f"手套破了！"
    event.rhythm_db.cd_refresh(event.user_id, Action.PLAY)
    return append_text

# endregion