# nonebot-plugin-rhythm-minigame
nonebot2 插件 - 音游小游戏

idea by @书狼

Origin from https://github.com/Mai-icy/nonebot-plugin-bread-shop

## 功能：
### 打歌

使用时指定等级，等级范围1-15

**示例命令：打歌 Basic；打歌 Adv；打歌 13**

难度会随机小数点后两位，指定难度无法指定小数点后难度

根据不同情况会有以下结果（Ra. min 指打的歌需要的最小 rating）：

- 越级：``Rating /15 < Ra. min``，90% 越级失败，有 10% 可能性超常发挥（越级成功）按100.5计算
- 正常打：``Rating / 15 - Ra. min ∈ [0, 难度 * 105.5)``，20%可能超常发挥算 100.5%，80% 可能性在 [97, 100.5) % 中随机
- 下埋：``Rating / 15 - Ra. min ∈ [难度 * 105.5, 难度 * 112]``，必 100.5%

Ra. min 计算方法：``难度 * 等级AAA（84）``

获得 Rating 计算方法：``难度 * 等级分数``，总 Rating 按照 b10 计算，每周减少 b5

一天一个人最多只能打10首歌

### 特殊事件

- 断网：打歌cd被迫+15分钟
- 拼机：随机事件，可以多打一首歌，不算每日上限
- 手套破了：打歌分数 -5%
### 段位模式 （TO-DO）

- 固定段位：一段-十段-皆传，根据段位随机四首歌总成绩大于395%过关，一天一次，好友对战后不可使用，达到皆传后不再掉段，段位每周重置
- 好友对战：使用固定段位计算，赢者段位上升一级
### NET 

#### 本群 Rating 排行榜
#### 好友对战 （TO-DO）

同时受付两个人的对战申请，主催选一首歌，两个人按照打歌随机结算出结果并比较，赢者固定段位上升一级
#### 生成b10+段位 列表

用法示例：``b10 @nonefffds`` ``b10``
#### 群内排行榜

显示群内 rating 前 5 名排行

用法示例：排行榜

#### 自定义称号（计划外）
## 附录：定数表
| border(%, float) | score(rating) | expression                  | range of border |
|------------------|---------------|-----------------------------|-----------------|
| 100.5            | 112           | score=108+(border-100)*8    | 100-100.5       |
| 100              | 108           |                             |                 |
| 99.5             | 105.5         | score=105.5+(border-99.5)*5 | 99.5-100        |
| 99               | 104           | score=104+(border-99)*3     | 99-99.5         |
| 98               | 101.5         | score=101.5+(border-98)*5   | 98-99           |
| 97               | 100           | score=100+(border-97)*3     | 97-98           |
| 94               | 84            | score=84+(border-94)*5.3333 | 94-97           |
| 90               | 68            | score=68+(border-90)*4      | 90-94           |
| 80               | 64            | score=64+(border-80)*0.4    | 80-90           |
| 75               | 60            | score=border*0.8            | 0-75            |
| 70               | 56            |                             |                 |
| 60               | 48            |                             |                 |
| 50               | 40            |                             |                 |
| 40               | 32            |                             |                 |
| 30               | 24            |                             |                 |
| 20               | 16            |                             |                 |
| 10               | 8             |                             |                 |
| 0                | 0             | score=border*0.8            | 0-75            |