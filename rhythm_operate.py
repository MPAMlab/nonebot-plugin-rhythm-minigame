#!/usr/bin/python
# -*- coding:utf-8 -*-
import time
import random
from .rhythm_handle import rhythmDataManage, Action, rhythmData
from .config import MAX, MIN, CD, rhythm_config
from enum import Enum
#from .__init__ import play_lev 

def cd_wait_time(group_id, user_id, operate: Action) -> int:
    """获取需要等待的CD秒数，小于0则被ban，大于0则还在冷却，等于0则可操作"""
    cd_stamp = rhythmDataManage(group_id).cd_get_stamp(user_id, operate)
    now_stamp = int(time.time())
    sep_time = now_stamp - cd_stamp
    cd = getattr(CD, operate.name)
    if sep_time < 0:
        return sep_time
    return cd.value - sep_time if sep_time < cd.value else 0


class _Event:
    event_type = Action.ALL
    _instance = {}
    _has_init = {}
    _public_events = []
    _is_random = {}
    _is_random_global = True

    def __new__(cls, group_id: str):
        """事件关于群单例，每个群只能有一个事件实例"""
        if group_id is None:
            return None
        if cls._instance.get(group_id) is None:
            cls._instance[group_id] = super(_Event, cls).__new__(cls)
        return cls._instance[group_id]

    def __init__(self, group_id: str):
        if not self._has_init.get(group_id):
            self._has_init[group_id] = True
            self.group_id = group_id
            self.rhythm_db = rhythmDataManage(group_id)
            self.user_id = None
            self.user_data = rhythmData(0, "0", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            self._private_events = []
            #self.thing = rhythm_config.special_thing_group.get(group_id, rhythm_config.rhythm_thing)
            #if isinstance(self.thing, list):
            #    self.thing = self.thing[0]

    @classmethod
    def add_event(cls, func):
        """添加单个特殊事件"""
        if not func.group_id_list:
            cls._public_events.append(func)
        else:
            for group_id in func.group_id_list:
                cls(group_id)._private_events.append(func)

    @classmethod
    def add_events(cls, func_list):
        """添加多个特殊事件"""
        for func in func_list:
            cls.add_event(func)

    @classmethod
    def set_random_global(cls, flag):
        """全局是否随机"""
        cls._is_random_global = flag

    def set_random(self, flag):
        """设置是否随机操作数量，若为False，可以通过指令指定数量"""
        self._is_random[self.group_id] = flag

    def is_random(self):
        """获取 self.group_id 群组是否随机"""
        if self._is_random.get(self.group_id) is not None:
            return self._is_random.get(self.group_id)
        else:
            return self._is_random_global

    def _special_event(self):
        """按照优先级排布，同优先级随机排布"""
        events = self._private_events + self._public_events
        events.sort(key=lambda x: (x.priority, random.random()))
        for event_func in events:
            return_data = event_func(self)
            if return_data:
                return return_data

    def set_user_id(self, user_id: str):
        """设置用户id以及获取用户数据以待判断"""
        self.user_id = user_id
        self.user_data = self.rhythm_db.get_RHYTHM_DATA(self.user_id)

    def execute(self, num=None):
        """事件执行"""
        pre_error = self._pre_event(num)
        if pre_error:
            return pre_error

        return_data = self._special_event()
        #self.rhythm_db.add_user_log(self.user_id, self.event_type)
        if return_data:
            return return_data

        return self.normal_event()

    def normal_event(self):
        """正常事件流程 （虚函数）"""

    def _pre_event(self, num=None):
        """预处理事件，提前生成随机值或其它值。 num 为非随机情况下得指定数量值
        self.thing = rhythm_config.special_thing_group.get(self.group_id, rhythm_config.rhythm_thing)
        if isinstance(self.thing, list):
            self.thing = self.thing[0]
"""
        # 获取操作最大值或者最小值
        max_num = getattr(MAX, self.event_type.name).value
        min_num = getattr(MIN, self.event_type.name).value

        if not self.is_random() and num is not None:
            if min_num <= num <= max_num:
                self.action_num = num
                return
            else:
                return "数量和限制不符！"
        #self.action_num = random.uniform(min_num, min(max_num, self.user_data.))


class _Event2(_Event):
    """双用户事件"""

    def __init__(self, group_id: str):
        super().__init__(group_id)
        self.other_id = None
        self.other_name = None
        self.other_data = rhythmData(0, "0", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

    def set_other_id(self, other_id: str, other_name: str):
        """设置第二个用户id 通常为”被操作“的用户"""
        self.other_id = other_id
        self.other_name = other_name
        self.other_data = self.rhythm_db.get_RHYTHM_DATA(other_id)

# 可能要添加新 class：PlayEventNormal, PlayEventUp, PlayEventDown，分别添加判断，按照条件判断是否触发特殊事件（以下分别为：普通、越级、下埋）
"""
class PlayEventNormal(_Event):
    
    event_type = Action.PLAYNORMAL
    _instance = {}
    _has_init = {}
    _public_events = []
    _is_random = {}
    _is_random_global = True
    def normal_event(self, group_id: str, play_lev: str):
        super().__init__(group_id)
        play_level = float(play_lev)
        random_rating = random.uniform(97.0, 100.4)
        final_rating = random_rating * 0.8 * play_level
        ref_min_rating = play_level * 84
        now_rating = self.rhythm_db.add_rating(self.user_id, self.action_num)
        if 0 < self.user_data[2] / 15 - ref_min_rating and self.user_data[2] / 15 - ref_min_rating < play_level * 105.5:
            
    # if event.user_data.self.user_data[2] / 15 < ref_min_rating:
    #
    # if event.user_data.self.user_data[2] / 15 - ref_min_rating > play_lev * 112:
    #
"""
# 计算分段得分
def get_final_rating(random_rating: float) -> int:
    rating_ranges = {
        (100, 100.5): lambda x: int(108 + (x - 100) * 8),
        (99.5, 100): lambda x: int(105.5 + (x - 99.5) * 5),
        (99, 99.5): lambda x: int(104 + (x - 99) * 3),
        (98, 99): lambda x: int(101.5 + (x - 98) * 5),
        (97, 98): lambda x: int(100 + (x - 97) * 3),
        (94, 97): lambda x: int(84 + (x - 94) * (5 + (1 / 3))),
        (90, 94): lambda x: int(68 + (x - 90) * 4),
        (80, 90): lambda x: int(64 + (x - 80) * 0.4),
        (0, 80): lambda x: int(x * 0.8)
    }

    for (lower, upper), formula in rating_ranges.items():
        if lower < random_rating < upper:
            return formula(random_rating)

    return 0  # Default value if no range is matched

class PlayEvent(_Event):
    """
    打歌事件
    """
    event_type = Action.PLAY
    _instance = {}
    _has_init = {}
    _public_events = []
    _is_random = {}
    _is_random_global = True

    def normal_event(self, group_id: str, play_lev: str):
        
        super().__init__(group_id)
        play_level = float(play_lev)
        ref_min_rating = play_level * 84
        if 0 < self.user_data[2] / 15 - ref_min_rating and self.user_data[2] / 15 - ref_min_rating < play_level * 105.5:
            random_rating = random.uniform(97.0000, 100.4000)
            final_rating = get_final_rating(random_rating)
            rating = final_rating * play_level
            now_rating = self.rhythm_db.add_rating(str(self.user_id), int(self.action_num))
            append_text = f"打歌成功！{self.user_id}，得分：{random_rating}，获得Rating：{rating}，现在总rating：{now_rating}"
            return append_text
        elif self.user_data[2] / 15 < ref_min_rating:
            random_rating = random.randint(40, 94)
            final_rating = get_final_rating(random_rating)
            rating = final_rating * play_level
            now_rating = self.rhythm_db.add_rating(str(self.user_id), int(self.action_num))
            append_text = f"越级失败！{self.user_id}，得分：{random_rating}，获得Rating：{final_rating}，现在总rating：{now_rating}"
            return append_text
        elif self.user_data[2] / 15 - ref_min_rating > play_lev * 112:
            final_rating = 100.5 * 0.8 * play_level
            now_rating = self.rhythm_db.add_rating(str(self.user_id), int(self.action_num))
            append_text = f"下埋nb！{self.user_id}，得分：100.5000%，获得Rating：{final_rating},现在总rating：{now_rating}"
            return append_text

        self.rhythm_db.cd_update_stamp(str(self.user_id), Action.PLAY)
        return

    def _pre_event(self, num=None):
        self.action_num = random.uniform(MIN.PLAY.value, MAX.PLAY.value)
        return super(PlayEvent, self)._pre_event(num) 


class DanEvent(_Event):
    """
    段位事件（未完成）
    """
    event_type = Action.DAN
    _instance = {}
    _has_init = {}
    _public_events = []
    _is_random = {}
    _is_random_global = True
"""
    def normal_event(self):
        now_rhythm = self.rhythm_db.reduce_rhythm(self.user_id, self.action_num)
        eaten_rhythm = self.rhythm_db.add_rhythm(self.user_id, self.action_num, Action.EAT)
        append_text = f"成功吃掉了{self.action_num}个{self.thing}w！现在你还剩{now_rhythm}个{self.thing}w！您目前的等级为Lv.{eaten_rhythm // LEVEL}"
        self.rhythm_db.cd_update_stamp(self.user_id, Action.EAT)
        self.rhythm_db.update_no(self.user_id)
        return append_text

    def _pre_event(self, num=None):
        if self.user_data.rhythm_num < MIN.EAT.value or (num and self.user_data.rhythm_num < num):
            append_text = f"你的{self.thing}还不够吃w，来买一些{self.thing}吧！"
            return append_text

        self.action_num = random.randint(MIN.EAT.value, min(MAX.EAT.value, self.user_data.rhythm_num))
        return super(EatEvent, self)._pre_event(num)
"""

class FightEvent(_Event2):
    """
    友人对战事件（未完成）
    """
    event_type = Action.FIGHT
    _instance = {}
    _has_init = {}
    _public_events = []
    _is_random = {}
    _is_random_global = True
"""
    def normal_event(self):
        new_rhythm_num = self.rhythm_db.add_rhythm(self.user_id, self.action_num)
        self.rhythm_db.reduce_rhythm(self.other_id, self.action_num)
        new_rhythm_no = self.rhythm_db.update_no(self.user_id)
        self.rhythm_db.update_no(self.other_id)

        append_text = f"成功抢了{self.other_name}{self.action_num}个{self.thing}，你现在拥有{new_rhythm_num}个{self.thing}！" \
                      f"您的{self.thing}排名为:{new_rhythm_no}"
        self.rhythm_db.cd_update_stamp(self.user_id, Action.ROB)
        return append_text

    def _pre_event(self, num=None):
        if not self.other_data or self.other_data.rhythm_num < MIN.ROB.value\
                or (num and self.other_data.rhythm_num < num):
            append_text = f"{self.other_name}没有那么多{self.thing}可抢呜"
            return append_text

        self.action_num = random.randint(MIN.ROB.value, min(MAX.ROB.value, self.other_data.rhythm_num))
        pre_res = super(RobEvent, self)._pre_event(num)
        if pre_res:  # 有返回值代表事件提前结束
            return pre_res

        if self.user_id == self.other_id:
            reduce_num = min(self.action_num, self.user_data.rhythm_num)
            append_text = f"这么想抢自己哇，那我帮你抢！抢了你{reduce_num}个{self.thing}嘿嘿！"
            self.rhythm_db.reduce_rhythm(self.user_id, reduce_num)
            self.rhythm_db.update_no(self.other_id)
            self.rhythm_db.cd_update_stamp(self.user_id, Action.ROB)
            return append_text
"""
