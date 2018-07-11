# -*- coding: utf-8 -*-
# @Time             :  2018/7/11 17:32
# @Author           :  lenovo;
# @project_name     :  work_space
# @File             :  toutiao_jiepai.py
# @Software         :  PyCharm
# @belong to file   :  今日头条街拍图片

import os
import requests


from hashlib import md5
#进程
from multiprocessing.pool import Pool


GROUP_START=1
GROUP_END=5

#获取街拍列表
def get_page(offset):

    #参数
    params={
        'offset':offset,
        'format':'json',
        'keyword':'街拍',
        'autoload':'true',
        'count':'20',
        'cur_tab':'1',
        'from':'search_tab'

    }
    url='https://www.toutiao.com/search_content/?'

    try:
        response=requests.get(url,params=params)
        if response.status_code==200:
            return response.json()
    except requests.ConnectionError:
        return None

#获取图片列表
def get_img(json):
    data=json.get('data')
    if data:
        for item in data:
            img_list=item.get('image_list')
            title=item.get('title')

            for img in img_list:
                yield {
                    'image':img.get('url'),
                    'title':title,
                }

#下载图片
def save_image(item):
    #判断当前路径下是否已经存在文件夹，不存在创建文件夹
    if not os.path.exists(item.get('title')):
        os.mkdir(item.get('title'))

    #保存图片
    try:
        local_img_url=item.get('image')

        #得到的URL列表路径里含有list ，图片具体地址是list换为large
        new_image_url = local_img_url.replace('list', 'large')

        #将图片链接补全
        response = requests.get('http:' + new_image_url)

        #请求正常，得到响应
        if response.status_code == 200:
            #format()函数拼接   0 是文件夹名title   1 是  将文本生成16进制的md5加密   2是图片文件后缀。
            file_path = '{0}/{1}.{2}'.format(item.get('title'), md5(response.content).hexdigest(), 'jpg')
            #文件不存在
            if not os.path.exists(file_path):
                with open(file_path, 'wb')as f:
                    f.write(response.content)
            #文件名已存在
            else:
                print('Already Downloaded', file_path)
    except requests.ConnectionError:
        print('Failed to save image')


#爬虫主要过程
def main(offset):
    #请求得到街拍列表数据
    json=get_page(offset)
    #得到每个图片属性
    for item in get_img(json):
        print(item)
        #保存图片
        save_image(item)


if __name__ == '__main__':

    pool=Pool()
    groups = ([x * 25 for x in range(GROUP_START, GROUP_END + 1)])
    # groups:要处理的数据列表，main：处理testFL列表中数据的函数
    pool.map(main, groups)
    # 关闭进程池，不再接受新的进程
    pool.close()
    # 主进程阻塞等待子进程的退出
    pool.join()
