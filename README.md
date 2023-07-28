# nonebot_plugin_rhythm_minigame
nonebot2 插件 - 音游小游戏

idea by @书狼

Edited from https://github.com/Mai-icy/nonebot-plugin-bread-shop

## 功能：
### 打歌

歌曲分为三个等级 Basic/Adv/Exp，使用时指定等级或难度，如果不指定等级，难度将会分别在1-5/6-10/11-15级别中随机

**示例命令：打歌 Basic；打歌 Adv；打歌 13**

难度会随机小数点后两位，指定难度无法指定小数点后难度

根据不同情况会有以下结果（Ra. min 指打的歌需要的最小 rating）：

- 越级：``Rating /15 < Ra. min``，有10% 可能性超常发挥（越级成功）按下埋计算，90% 可能性在 0-97% 中随机（越级失败）
- 正常打：``Rating / 15 - Ra. min ∈ [0, 难度 * 105.5)``，20%可能超常发挥算 100.5%，80% 可能性在 [97, 100) % 中随机
- 下埋：``Rating / 15 - Ra. min ∈ [难度 * 105.5, 难度 * 112]``，必 100.5%

Ra. min 计算方法：``难度 * 等级AAA（84）``

获得 Rating 计算方法：``难度 * 等级分数``，总 Rating 按照 b10 计算

一天一个人最多只能打10首歌
## 段位模式

- 固定段位：一段-十段-皆传，根据段位随机四首歌总成绩大于395%过关，一天一次，好友对战后不可使用
- 好友对战：使用固定段位计算，赢者段位上升一级
### NET

#### 本群 Rating 排行榜
#### 好友对战 

同时受付两个人的对战申请，主催选一首歌，两个人按照打歌随机结算出结果并比较，赢者固定段位上升一级
#### 生成b10+段位 列表

#### 自定义称号（计划外）
## 附录：定数表
