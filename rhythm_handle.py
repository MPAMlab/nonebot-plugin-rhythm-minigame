#!/usr/bin/python
# -*- coding:utf-8 -*-
import sqlite3
import time

from collections import namedtuple
from enum import Enum
from functools import wraps
from inspect import signature
from pathlib import Path
from typing import List
from .config import LEVEL

DATABASE = Path() / "data" / "rhythm"


class Action(Enum):
    ALL = -1
    PLAY = 0
    FIGHT = 1
    DAN = 2


rhythmData = namedtuple("rhythmData", ["no", "user_id", "rhythm_rating", "rhythm_eaten", "level"])
LogData = namedtuple("LogData", ["user_id", "buy_times", "eat_times", "rob_times", "give_times", "bet_times"])


def type_assert(*ty_args, **ty_kwargs):
    """sql类型检查"""
    def decorate(func):
        sig = signature(func)
        bound_types = sig.bind_partial(*ty_args, **ty_kwargs).arguments

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound_values = sig.bind(*args, **kwargs)
            for name, value in bound_values.arguments.items():
                if name in bound_types:
                    if bound_types[name] == "user_id":
                        if isinstance(value, str):
                            if not value.isdigit():
                                raise TypeError("user_id must consist of numeric characters.")
                        else:
                            raise TypeError('Argument {} must be {}'.format(name, str))
                    elif not isinstance(value, bound_types[name]):
                        raise TypeError('Argument {} must be {}'.format(name, bound_types[name]))
            return func(*args, **kwargs)
        return wrapper
    return decorate


class rhythmDataManage:
    _instance = {}
    _has_init = {}
    CD_COLUMN = ("PLAY_CD", "DAN_CD", "FIGHT_CD")
    DATA_COLUMN = ("OVERALL_RATING", "BEST_ONE", "BEST_TWO", "BEST_THREE", "BEST_FOUR", "BEST_FIVE", "BEST_SIX", "BEST_SEVEN", "BEST_EIGHT", "BEST_NINE", "BEST_TEN")


    def __new__(cls, group_id):
        if group_id is None:
            return None
        if cls._instance.get(group_id) is None:
            cls._instance[group_id] = super(rhythmDataManage, cls).__new__(cls)
        return cls._instance[group_id]

    def __init__(self, group_id):
        if not rhythmDataManage._has_init.get(group_id):
            rhythmDataManage._has_init[group_id] = True
            self.database_path = DATABASE / group_id
            if not self.database_path.exists():
                self.database_path.mkdir(parents=True)
                self.database_path /= "rhythm.db"
                self.conn = sqlite3.connect(self.database_path)
                self._create_file()
            else:
                self.database_path /= "rhythm.db"
                self.conn = sqlite3.connect(self.database_path)
            print(f"群组{group_id}数据库连接！")

    def close(self):
        self.conn.close()
        print("数据库关闭！")

    def _create_file(self) -> None:
        """创建数据库文件"""
        c = self.conn.cursor()
        c.execute('''CREATE TABLE RHYTHM_DATA 
                  (NO INTEGER PRIMARY KEY UNIQUE, 
                  USERID TEXT , 
                  OVERALL_RATING INTEGER , 
                  BEST_ONE INTEGER , 
                  BEST_TWO INTEGER , 
                  BEST_THREE INTEGER , 
                  BEST_FOUR INTEGER , 
                  BEST_FIVE INTEGER , 
                  BEST_SIX INTEGER , 
                  BEST_SEVEN INTEGER , 
                  BEST_EIGHT INTEGER , 
                  BEST_NINE INTEGER , 
                  BEST_TEN INTEGER
                );''') 
        c.execute('''CREATE TABLE PLAY_CD 
                  (USERID TEXT , 
                  PLAY_CD INTEGER , 
                  DAN_CD INTEGER , 
                  FIGHT_CD INTEGER
                );''') 
        self.conn.commit()



    def _get_id(self) -> int:
        """获取下一个id"""
        cur = self.conn.cursor()
        cur.execute('select * from RHYTHM_DATA')
        result = cur.fetchall()
        return len(result) + 1

    @classmethod
    def close_dbs(cls):
        for group_id in cls._instance.keys():
            rhythmDataManage(group_id).close()

    @type_assert(object, "user_id")
    def _create_user(self, user_id: str) -> None:
        """在数据库中创建用户并初始化"""
        new_id = self._get_id()
        c = self.conn.cursor()
        sql = f"INSERT INTO RHYTHM_DATA (NO, USERID, OVERALL_RATING, BEST_ONE, BEST_TWO, BEST_THREE, BEST_FOUR, BEST_FIVE, BEST_SIX, BEST_SEVEN, BEST_EIGHT, BEST_NINE, BEST_TEN) VALUES (?,?,0,0,0,0,0,0,0,0,0,0,0)"
        c.execute(sql, (new_id, user_id))
        sql = f"INSERT INTO PLAY_CD (USERID,PLAY_CD,DAN_CD,FIGHT_CD) VALUES (?,0,0,0)"
        c.execute(sql, (user_id,))
        self.conn.commit()

    @type_assert(object, "user_id", Action)
    def cd_refresh(self, user_id: str, action: Action) -> None:
        """刷新用户操作cd"""
        if action == Action.ALL:
            cur = self.conn.cursor()
            for key in self.CD_COLUMN:
                sql = f"update PLAY_CD set {key}=? where USERID=?"
                cur.execute(sql, (1, user_id))
            self.conn.commit()
            return
        op_key = self.CD_COLUMN[action.value]
        sql = f"update PLAY_CD set {op_key}=? where USERID=?"
        cur = self.conn.cursor()
        cur.execute(sql, (1, user_id))
        self.conn.commit()

    @type_assert(object, "user_id", Action)
    def cd_get_stamp(self, user_id: str, action: Action) -> int:
        """获取用户上次操作时间戳"""
        cur = self.conn.cursor()
        sql = f"select * from PLAY_CD where USERID=?"
        cur.execute(sql, (user_id,))
        result = cur.fetchone()
        if not result:
            self._create_user(user_id)
            result = (user_id, 0, 0, 0, 0, 0)
        self.conn.commit()
        return result[action.value + 1]

    @type_assert(object, "user_id", Action, int)
    def cd_reduce_action(self, user_id: str, action: Action, reduce_time) -> None:
        """单次剪短cd，单位为秒"""
        op_key = self.CD_COLUMN[action.value]
        sql = f"update PLAY_CD set {op_key}=? where USERID=?"
        cur = self.conn.cursor()
        cur.execute(sql, (int(time.time()) - reduce_time, user_id))
        self.conn.commit()

    @type_assert(object, "user_id", Action, int)
    def cd_ban_action(self, user_id: str, action: Action, ban_time) -> None:
        """禁止用户一段时间操作，单次延长cd，单位为秒"""
        op_key = self.CD_COLUMN[action.value]
        sql = f"update PLAY_CD set {op_key}=? where USERID=?"
        cur = self.conn.cursor()
        cur.execute(sql, (int(time.time()) + ban_time, user_id))
        self.conn.commit()

    @type_assert(object, "user_id", Action)
    def cd_update_stamp(self, user_id: str, action: Action) -> None:
        """重置用户操作CD(重新开始记录冷却)"""
        op_key = self.CD_COLUMN[action.value]
        sql = f"update PLAY_CD set {op_key}=? where USERID=?"
        stamp = int(time.time())
        cur = self.conn.cursor()
        cur.execute(sql, (stamp, user_id))
        self.conn.commit()

    @type_assert(object, "user_id", int, Action)
    def add_rhythm(self, user_id: str, add_num: int, action: Action = Action.BUY) -> int:
        """添加用户面包数量，可以添加已经吃了的面包数量，返回增加后的数量"""
        if action == Action.EAT:
            col_name = self.DATA_COLUMN[1]
        else:
            col_name = self.DATA_COLUMN[0]
        cur = self.conn.cursor()
        sql = f"select * from RHYTHM_DATA where USERID=?"
        cur.execute(sql, (user_id,))
        data = cur.fetchone()
        if not data:
            self._create_user(user_id)
            data = (0, user_id, 0, 0)
        if col_name == self.DATA_COLUMN[1]:
            ori_num = data[3]
        else:
            ori_num = data[2]
        new_num = ori_num + add_num
        sql = f"update RHYTHM_DATA set {col_name}=? where USERID=?"
        cur.execute(sql, (new_num, user_id))
        self.conn.commit()
        return new_num

    @type_assert(object, "user_id", int, Action)
    def add_rating(self, user_id: str, new_rating: int, action: Action = Action.PLAY) -> int:
        cur = self.conn.cursor()
        sql = f"select * from RHYTHM_DATA where USERID=?"
        cur.execute(sql, (user_id,))
        rating = cur.fetchone()
        if not data:
            self._create_user(user_id)
            rating = (0, user_id, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        for rating in rating:
            if new_rating < rating[0]:
                # Insert the new number into the database
                rating.append(new_rating)
                rating.sort(reverse=True)
                rating.pop()
                overall_rating = sum(rating)
                cur.execute("UPDATE RHYTHM_DATA SET BEST_ONE=?, BEST_TWO=?, BEST_THREE=?, BEST_FOUR=?, BEST_FIVE=?, BEST_SIX=?, BEST_SEVEN=?, BEST_EIGHT=?, BEST_NINE=?, BEST_TEN=?", rating)
                conn.commit()
                conn.close()
                return overall_rating  # Return True if the new number is smaller
        
        """
        sql = f"update RHYTHM_DATA set {col_name}=? where USERID=?"
        cur.execute(sql, (new_num, user_id))

        cur.execute("SELECT number FROM RHYTHM_DATA")


        # Check if the new number is smaller than any number in the database
        for rating in ratings:
            if new_rating < rating[0]:
                # Insert the new number into the database
                ratings.append(new_rating)
                ratings.sort(reverse=True)
                ratings.pop()
                overall_rating = sum(ratings)
                cur.execute("INSERT INTO RHYTHM_DATA(number) VALUES (?)", (new_rating,))
                conn.commit()
                conn.close()
                return overall_rating  # Return True if the new number is smaller

    
        # Insert a new number
        sql_insert = f"INSERT INTO RHYTHM_DATA (BEST_ONE, BEST_TWO, BEST_THREE, BEST_FOUR, BEST_FIVE, BEST_SIX, BEST_SEVEN, BEST_EIGHT, BEST_NINE, BEST_TEN) VALUES (?,?,?,?,?,?,?,?,?,?)"
        cur.execute(sql_insert, (new_rating,))

        # Check if the new number is greater than the smallest number
        sql_select = "SELECT * FROM RHYTHM_DATA"
        cur.execute(sql_select)
        data = cur.fetchone()

        # Get the smallest number
        smallest_number = min(data)

        # If the new number is greater than the smallest number, replace it and sort the array
        if new_number > smallest_number:
            data = sorted(data)
            data[0] = new_number

        # Update the table with the modified array
        sql_update = f"UPDATE RHYTHM_DATA SET BEST_ONE=?, BEST_TWO=?, BEST_THREE=?, ..., BEST_TEN=?"
        cur.execute(sql_update, tuple(data))

        # Commit the changes and close the connection
        conn.commit()
        conn.close()
"""

    @type_assert(object, "user_id", int, Action)
    def reduce_rhythm(self, user_id: str, red_num: int, action: Action = Action.BUY) -> int:
        """减少用户面包数量，可以减少已经吃的数量，返回减少后的数量"""
        if action == Action.EAT:
            col_name = self.DATA_COLUMN[1]
        else:
            col_name = self.DATA_COLUMN[0]
        cur = self.conn.cursor()
        sql = "select * from RHYTHM_DATA where USERID=?"
        cur.execute(sql, (user_id,))
        data = cur.fetchone()
        if not data:
            self._create_user(user_id)
            data = (0, user_id, 0, 0)
        if col_name == "rhythm_EATEN":
            ori_num = data[3]
        else:
            ori_num = data[2]
        new_num = ori_num - red_num
        sql = f"update RHYTHM_DATA set {col_name}=? where USERID=?"
        cur.execute(sql, (new_num, user_id))
        self.conn.commit()
        return new_num

    @type_assert(object, "user_id")
    def update_no(self, user_id: str) -> int:
        """更新用户排名并返回"""
        cur = self.conn.cursor()
        sql = "select * from RHYTHM_DATA where USERID=?"
        cur.execute(sql, (user_id,))
        data = cur.fetchone()
        now_no = data[0]
        user_num = (data[3] // LEVEL, data[2])
        while now_no != 1:
            cur.execute("select * from RHYTHM_DATA where NO=?", (now_no - 1,))
            data = cur.fetchone()
            up_num = (data[3] // LEVEL, data[2])
            if user_num > up_num:
                cur.execute(f"update RHYTHM_DATA set NO={0} where NO={now_no}")
                cur.execute(f"update RHYTHM_DATA set NO={now_no} where NO={now_no - 1}")
                cur.execute(f"update RHYTHM_DATA set NO={now_no - 1} where NO={0}")
            else:
                break
            now_no -= 1
        while now_no != self._get_id() - 1:
            cur.execute("select * from RHYTHM_DATA where NO=?", (now_no + 1,))
            data = cur.fetchone()
            down_num = (data[3] // LEVEL, data[2])
            if user_num < down_num:
                cur.execute("update RHYTHM_DATA set NO=? where NO=?", (0, now_no))
                cur.execute("update RHYTHM_DATA set NO=? where NO=?", (now_no, now_no + 1))
                cur.execute("update RHYTHM_DATA set NO=? where NO=?", (now_no + 1, 0))
            else:
                break
            now_no += 1
        self.conn.commit()
        return now_no

    @type_assert(object, "user_id")
    def get_RHYTHM_DATA(self, user_id: str) -> rhythmData:
        """获取用户面包数据并返回"""
        cur = self.conn.cursor()
        cur.execute("select * from RHYTHM_DATA where USERID=?", (user_id,))
        data = cur.fetchone()
        if not data:
            self._create_user(user_id)
            data = (0, user_id, 0, 0)
        self.conn.commit()
        return rhythmData(*data, level=data[3] // LEVEL)

    def get_all_data(self) -> List[rhythmData]:
        """获取一个数据库内的所有用户数据"""
        cur = self.conn.cursor()
        cur.execute(f"select * from RHYTHM_DATA")
        data = cur.fetchall()
        self.conn.commit()
        return [rhythmData(*item, level=item[3] // LEVEL) for item in data]

if __name__ == "__main__":
    DATABASE = Path() / ".." / ".." / ".." / "data" / "rhythm"
