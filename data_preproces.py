# coding: utf-8
"""
目标: 将每个回答分割成结构化形式
结构:
    1. introduction: 该回答的说明, 前言
    2. title: 物品:含有物品名称或者关键词的语句 ---- 需要提取关键词
    3. describe: 用户对于该商品的推荐理由
    4. link: 淘宝或其他渠道的购买链接
    5. image: 图片后期需要去知乎上爬下来存储到本地
去除:
    1.跟知乎相关的一些词语: 知友, 前面的回答, 知乎...
    2.末尾的求赞之类的语句
"""
import re


class Item:
  def __init__(self, title, describe, link, images):
    self.title = title
    self.describe = describe
    self.link = link
    self.images = images

  def get_item(self):
    pass


class Answer:
  def __init__(self, intro, items):
    self.intro = intro
    self.items = items


def is_title(line):
  return (re.match(r"[0-9]*\.", line) is not None) or \
         (re.match(r"[0-9]*\\\.", line) is not None) or \
         (re.match(r"\*\*[0-9]*", line) is not None) or \
         (line.startswith('**') and line.endswith('**'))


def get_answer(input):
  with open(input, 'r', encoding='utf-8') as f:
    content = f.read()
    for i, v in enumerate(content.split('#### 孙雅坤小朋友 ####')):
      for j, vv in enumerate(v.strip().split('\n')):
        if is_title(vv):
          print("{}: {}".format(vv.strip(), len(vv.strip())))


if __name__ == "__main__":
  inputf = '有哪些出租屋实用神器？--内容.md'
  get_answer(inputf)
