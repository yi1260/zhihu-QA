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
  return (re.match(r"[0-9]+ ", line) is not None) or \
         (re.match(r"[0-9]+\.", line) is not None) or \
         (re.match(r"[0-9]+\\\.", line) is not None) or \
         (re.match(r"\*\*[0-9]+", line) is not None) or \
         (re.match(r"^\*\*.*\*\*$", line) is not None)

def title_preprocess(title):
  '''
  筛选网址
  去除非文字部分
  去除标号
  :param title:
  :return: title, urls
  '''
  pass



def get_answer(inputfile):
  with open(inputfile, 'r', encoding='utf-8') as f:
    content = f.read()
    for i, v in enumerate(content.split('#### 孙雅坤小朋友 ####')):
      print("@@@@@@@@@@@@@@ Answer {} @@@@@@@@@@@@@@@".format(i))
      describe_line = []
      last_title = ''
      for j, vv in enumerate(v.strip().split('\n')):
        # if is_title(vv):
        #   print(vv.strip())
        # todo: 筛选title中的网址
        # todo: 筛选title的长度
        if is_title(vv) and last_title == '':
          vvv = re.search(r"(.*)([a-zA-z]+://[^\s)]*)", vv.strip())
          urls = re.findall(r"[a-zA-z]+://[^\s)]*", vv.strip())
          if vvv and len(urls) != 0:
            print("@@@@@ Item title: {} @@@@@".format(vvv.group(1)))
            print(urls)
          else:
            reg = re.compile(r'[\W0-9]')
            title = reg.sub(' ', vv).strip()
            print("@@@@@ Item title: {} @@@@@".format(title.strip()))
          last_title = vv
        elif is_title(vv) and last_title != '':
          # print('\n'.join(describe_line))
          describe_line.clear()

          vvv = re.search(r"(.*?)([a-zA-z]+://[^\s)]*)", vv.strip())
          urls = re.findall(r"[a-zA-z]+://[^\s)]*", vv.strip())
          if vvv and len(urls) != 0:
            title = vvv.group(1)
            reg = re.compile(r'[\W0-9]')
            title = reg.sub(' ', title).strip()
            print("@@@@@ Item title: {} @@@@@".format(title))
            print(urls)
          else:
            reg = re.compile(r'[\W0-9]')
            title = reg.sub(' ', vv).strip()
            print("@@@@@ Item title: {} @@@@@".format(title.strip()))
        elif last_title != '':
          describe_line.append(vv)


if __name__ == "__main__":
  inputf = '有哪些出租屋实用神器？--内容.md'
  get_answer(inputf)
  # vv = "**3.门后挂钩**![](https://pic2.zhimg.com/50/6d4d66bbf28e8cc1b0958b600004e385_hd.jpg)![](data:image/svg+xml;utf8,<svg%20xmlns='http://www.w3.org/2000/svg'%20width='430'%20height='430'></svg>)"
  # vvv = re.findall(r"[a-zA-z]+://[^\s\)]*", vv.strip())
  # if vvv:
  #   print(vvv)
