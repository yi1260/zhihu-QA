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
  def __init__(self, title, describe, link_map, image_map):
    self.title = title
    self.describe = describe  # multi lines
    self.links = link_map
    self.images = image_map  # map: key:image num value: image link

  def get_title(self):
    return self.title

  def get_describe(self):
    return self.describe

  def get_link_map(self):
    return self.links

  def get_image_map(self):
    return self.images


class Answer:
  def __init__(self, intro, upvote, items):
    self.intro = intro
    self.upvote = upvote
    self.items = items

  def get_items(self):
    return self.items

  def get_upvote(self):
    return self.upvote

  def get_intro(self):
    return self.intro

# todo: 利用学习的方式, 筛选出不是商品title的
def title_preprocess(title):
  """
  1. 去除非文字部分, 空格切分后选取第一部分
  2. 将title中的link*以及image*提取出来, 作为describe的第一行
  :param title:
  :return: new_title
  """
  new_title = title

  # 用于提取处理过的url
  re_link = re.compile(r'link[0-9]+')
  re_image = re.compile(r'image[0-9]+')
  links = ['[]({})'.format(i) for i in re_link.findall(new_title)]
  images = ['![]({})'.format(i) for i in re_image.findall(new_title)]

  # print('links: {}'.format(links))
  # print('images: {}'.format(images))

  reg = re.compile(r'[\W0-9]+|[（）《》——__；，。“”<>！]+')  # 用于去除非文字部分
  new_title = reg.sub(' ', new_title).strip()
  parts = new_title.split(' ')
  if len(parts[0]) <= 2 and len(parts) >= 2:
    return parts[0] + parts[1], links, images
  else:
    return parts[0], links, images


def url_draw(line, image_map, link_map):
  """
  提取行文字中的url, 并区分是jpg还是link
  :param line:
  :return: jpg_url_list, link_url_list
  """
  reg_data = re.compile(r'!\[]\(data:.*?\)')  # 去除有干扰的url
  line = reg_data.sub('', line)

  urls = re.findall(r"https*://[^\s)]*", line.strip())  # 提取url

  images = []
  links = []
  for url in urls:
    if url.endswith('.jpg') or url.endswith('.png') or url.endswith('.gif') or url.endswith('.bmp'):
      images.append(url)
    else:
      links.append(url)

  for i, v in enumerate(images):
    key = 'image{}'.format(len(image_map))
    image_map[key] = v
    line = line.replace(v, key)

  for i, v in enumerate(links):
    key = 'link{}'.format(len(link_map))
    link_map[key] = v
    line = line.replace(v, key)

  return line, image_map, link_map


def title_draw(line):
  reg_list = [re.compile(r'(^[#@!$%^&]*\**\(*（*[0-9]+\)*）*)(．|、|\s|\\*\.)+(.*)'),
              re.compile(r'(^[#@!$%^&]*\**（[0-9]+）)(．|、|\s|\\*\.)*(.*)'),
              re.compile(r'(^[#@!$%^&]*\**\(*（*[a-oA-O]+\)*）*)(．|、|\s|\\*\.)+(.*)'),
              re.compile(r'(^[#@!$%^&]*\**（[a-oA-O]+）)(．|、|\s|\\*\.)*(.*)'),
              re.compile(r'(^[#@!$%^&]*\**\(*（*[一二三四五六七八九十]+\)*）*)(．|、|\s|\.)+(.*)'),
              re.compile(r'(^[#@!$%^&]*\**（[一二三四五六七八九十]+）)(．|、|\s|\.)*(.*)'),
              re.compile(r'(^[#@!$%^&]*\**[①②③④⑤⑥⑦⑧⑨⑩]+)(．|、|\s|\.)*(.*)')
              # re.compile(r'(^\*)(\*)(.*)(\*\*)')
              ]

  result = None
  for r in reg_list:
    result = re.match(r, line)
    if result:
      result = result.group(3)
      break

  return result


def is_line(line):
  """
  筛选规则:
  1. 筛掉只有符号的句子
  2. 筛掉含有日期的句子
  3. 筛掉还有点赞/点个赞的句子
  :return:
  """

  # 判断是否有日期
  is_date = re.search(r'[0-9]{4}[._\-年][0-9]{1,2}[._\-月][0-9]{1,2}[日]*', line)
  # 去除line中的标点, 数字
  reg = re.compile(r'[\W0-9]|[】【（）《》——__；，。“”<>！]')
  new_line = reg.sub('', line)

  return new_line.strip() != '' and \
         re.search(r'点赞|点个赞', new_line) is None and \
         is_date is None


def is_item(title, describe, image_map):
  """
  item初选规则:
  1. 筛掉title为空白的item
  2. 筛掉不含图片的item
  3. 筛掉describe为空的item
  4. 筛掉describe行数大于10的item
  5. 筛掉title长度小于等于1的item
  :param title:
  :param describe:
  :param image_map:
  :return:
  """
  # print(len(describe.split('\n')))
  return (title.strip() != '') and \
         (len(image_map) != 0) and \
         (describe.strip() != '') and \
         (len(describe.strip().split('\n')) <= 10) and \
         (len(title.strip()) > 1)


def is_describe(line):
  """
  筛选规则:
  1. 筛掉汉字少于2个的句子
  :return:
  """
  # 去除line中的标点, 数字
  reg = re.compile(r'[\W0-9]|[】【（）《》——__；，。“”<>！]')
  new_line = reg.sub('', line)

  return len(new_line) > 2


def get_answer(inputfile):
  with open(inputfile, 'r', encoding='utf-8') as f:
    content = f.read()
    total_item_count = 0
    answer_list = []
    for i, v in enumerate(content.split('#### 孙雅坤小朋友 ####')):
      # print("@@@@@@@@@@@@@@ Answer {} @@@@@@@@@@@@@@@".format(i))
      upvote = 0

      line_list = []
      item_list = []
      link_map = {}
      image_map = {}
      last_title = ''
      for j, line in enumerate(v.strip().split('\n')):
        print(line)
        if j == 0:
          print(line)
          upvote = int(v.strip())
          continue

        if not is_line(line):
          continue

        title = title_draw(line)
        if title and last_title == '':
          # 保存intro
          intro = ('\n'.join(line_list))


          title, image_map, link_map = url_draw(title, image_map, link_map)
          title, title_links, title_images = title_preprocess(title)
          for ll in title_links + title_images:
            line_list.append(ll)
          # print("@@@@@ The first title of this Answer: {} @@@@@".format(title.strip()))

          last_title = title
        elif title and last_title != '':
          # 保存上一个的
          item_describes = ('\n'.join(line_list))
          # print(dict(image_map, **link_map))
          # print(item_describes)
          if is_item(last_title, item_describes, image_map.copy()):
            item = Item(title=last_title, link_map=link_map.copy(), image_map=image_map.copy(), describe=item_describes)
            item_list.append(item)

          # 清理上一个的
          line_list.clear()
          image_map.clear()
          link_map.clear()

          # 开始下一个的
          title, image_map, link_map = url_draw(title, image_map, link_map)
          title, title_links, title_images = title_preprocess(title)
          for ll in title_links + title_images:
            line_list.append(ll)
          # print("@@@@@ Item title: {} @@@@@".format(title.strip()))

          last_title = title
        elif last_title != '':
          line, image_map, link_map = url_draw(line, image_map, link_map)
          if is_describe(line):
            line_list.append(line.strip())

      # 保存最后一个的
      item_describes = ('\n'.join(line_list))
      if is_item(last_title, item_describes, image_map.copy()):
        item = Item(title=last_title, link_map=link_map, image_map=image_map, describe=item_describes)
        item_list.append(item)
      # print('first describe: \n{}'.format(item_list[0].get_describe()))

      # test
      total_item_count += len(item_list)
      # for item in item_list:
      #   ds = item.get_describe()
      #   print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ Item title: {} @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@".format(item.get_title()))
        # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ Item describe: @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n{}".format(ds))
        # print("@@@@@ Item map: @@@@@")
        # for k, v in dict(item.get_image_map(), **(item.get_link_map())).items():
        #   print('{}: {}'.format(k, v))
        # if re.search(k, ds) is None:
        #   print(ds)
        #   print('!!!!!!!!!!!!!!!!!!!!!! {} !!!!!!!!!!!!!!!!!!!!!!'.format(k))

      answer_list.append(Answer(intro=None, items=item_list, upvote=upvote))

    for i, an in enumerate(answer_list):
      print("@@@@@@@@@@@@@@ Answer NO{} @@@@@@@@@@@@@@@".format(i))
      print("@@@@@@@@@@@@@@ Answer upvote: {} @@@@@@@@@@@@@@@".format(an.get_upvote()))
      for item in an.get_items():
        ds = item.get_describe()
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ Item title: {} @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@".format(item.get_title()))
        # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ Item describe: @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n{}".format(ds))

    print('&&&&&&&&&&&&&&&&&& total item count: {} &&&&&&&&&&&&&&&&&&&'.format(total_item_count))


if __name__ == "__main__":

  # # 测试title是不是筛选正确
  # tt = ['**（五）家纺类',
  #       'Microsoft Sculpt Ergonomic Mouse',
  #       '**一、装饰部分**',
  #       '**1、地毯**',
  #       '**喏，就是这种地毯。**',
  #       '**点我赞我瘦10斤!!! 快来种下一片草原!**',
  #       '2、[首页-陌希生活-',
  #       '**2、床品**',
  #       '**⑴**[抱枕/靠枕-MOREOVER-淘宝网__](https://link.zhihu.com/?target=https%3A//moreover.jiyoujia.com/category-1239620223.htm%3Fspm%3Da1z10.5-c.w4010-13956535389.13.555c1c99oRDQ0l%26search%3Dy%26catName%3D%25B1%25A7%25D5%25ED%252F%25BF%25BF%25D5%25ED%23bd) (性冷淡风)']
  #
  # for i in tt:
  #   res = is_title(i)
  #   print(res)

  # vv = 'A泡沫板'
  # re1 = re.compile(r'(^[a-zA-Z])(、|\s|\.)+(.*)')
  # re2 = re.compile(r'(^一.*|二.*|三.*|四.*|五.*|六.*|七.*|八.*|九.*|十.*)(、|\s|\.)+(.*)')
  # re_list = [re1, re2]
  # res = None
  # for i in re_list:
  #   res = re.match(i, vv)
  #   if res:
  #     break
  # if res:
  #   print(res.group(3))

  # vv = '2\. 晾衣绳（没有晾衣杆的可以买一个），约5元，关键词：晾衣绳 防滑'
  # res = re.match(r'(^[0-9]+)(、|\s|\\*\.)+(.*)', vv)
  # if res:
  #   print(res.group(3))

  # image_map = {}
  # link_map = {}
  # vv = '**[原木多功能底座__](https://link.zhihu.com/?target=http%3A//knewone.com/things/yuan-mu-duo-gong-neng-di-zuo)**'
  # title = is_title(vv)
  # print(title)
  # if title:
  #   title, image_map, link_map = url_draw(title, image_map, link_map)
  #   title, _, _ = title_preprocess(vv)
  #   print(title)


  # vv = '**春秋****天竺棉四件套**** 关键词：无印 ****天竺棉****裸睡****全棉四件套**'
  # title, _, _ = title_preprocess(vv)
  # print(title)

  inputf = '有哪些出租屋实用神器？--内容.md'
  get_answer(inputf)

  # line = '【清洁】'
  # describe_line_filter(line)

  # line = "**3.门后挂钩**[怎么花最少的钱提升出租屋的格调？ - 生活](https://www.zhihu.com/question/27391031)![](https://pic2.zhimg.com/50/2ac45903159a16c87cc7f80d542e75b1_hd.jpg)![](data:image/svg+xml;utf8,<svg%20xmlns='http://www.w3.org/2000/svg'%20width='2688'%20height='1520'></svg>)![](https://pic4.zhimg.com/50/38607572688a6686a6abc56311841d7f_hd.jpg)![](data:image/svg+xml;utf8,<svg%20xmlns='http://www.w3.org/2000/svg'%20width='2688'%20height='1520'></svg>)![](https://pic2.zhimg.com/50/21b54490e7676004dea5923ed65ce1c1_hd.jpg)![](data:image/svg+xml;utf8,<svg%20xmlns='http://www.w3.org/2000/svg'%20width='2688'%20height='1520'></svg>)"
  #
  #
  #
  # reg_data = re.compile(r'!\[]\(data:.*?\)')
  # line = reg_data.sub('', line)
  # print(line)
  #
  # urls = re.findall(r"https*://[^\s)]*", line.strip())
  # print(urls)
  #
  # images = []
  # links = []
  # for url in urls:
  #   if url.endswith('.jpg') or url.endswith('.png') or url.endswith('.gif') or url.endswith('.bmp'):
  #     images.append(url)
  #   else:
  #     links.append(url)
  #
  # image_map = {}
  # link_map = {}
  # for i, v in enumerate(images):
  #   key = 'image{}'.format(len(image_map))
  #   image_map[key] = v
  #   line = line.replace(v, key)
  #
  # for i, v in enumerate(links):
  #   key = 'link{}'.format(len(link_map))
  #   link_map[key] = v
  #   line = line.replace(v, key)
  #
  # print(image_map)
  # print(link_map)
  #
  # # reg_image = re.compile(r'\[]\(.*\)')
  # # vv = reg_image.sub('', vv)
  # print(line)
  # # if vvv:
  # #   print(vvv)
  #   # print(vvv.group(1))
  #   # print(vvv.group(2))
  #   # print(vvv.group(3))
  #   # print(vvv.group(4))
