import requests
from urllib.parse import urlencode
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import re
import json
import os
from hashlib import md5
from config import *
from multiprocessing import Pool
#请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'
}
#获取html文件
def get_one_page(offset,keyword):
    #字典对象
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': '20',
        'cur_ta': 1
    }
    #urlencode()将字典对象转化为URL的请求参数
    url='https://www.toutiao.com/search_content/?'+urlencode(data)
    try:
        response = requests.get(url,headers = headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求网页失败')
        return None

#解析html文本
#返回数组,数组内容为 图集的url
def parse_page_index(html):
    #将Html文本(字符串格式)转换为json格式
    data = json.loads(html)
    #data为字典结构，且为多层嵌套字典结构，其中所需解析的URL在第二层
    #dirt.keys() 返回所有的键名

    if data and 'data' in data.keys():
        #遍历第一层字典结构
        for item in data.get('data'):
            #返回第二层字典结构中键为'article_url'的值
            yield item.get('article_url')

#继续获取详情页的信息
#url参数为上步解析所得
def get_page_detail(url):
    try:
        response = requests.get(url,headers = headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求详情页失败')
        return None

#解析详情页
def parse_page_detail(html):
    soup = BeautifulSoup(html,'lxml')
    title = soup.select('title')[0].get_text()
    image_pattern = re.compile('gallery: JSON.parse.*?"(.*?)"\),',re.S)
    result0 = re.findall(image_pattern,html)
    result = re.sub(r'\\',"",str(result0))[2:-2]
    if result:
        data = json.loads(result)
        if data :
            sub_images = data.get('sub_images')
            images = [item.get('url') for item in sub_images]
            return {
                'title': title,
                'images': images
            }

#下载图片
def download_image(path,url):
    try:
        response = requests.get(url,headers = headers)
        if response.status_code == 200:
            with open(path, 'wb') as f:
                f.write(response.content)
                f.close()
                return True
        return False
    except RequestException:
        print('请求图片失败')
        return False

#下载图片集
def download_images(images,title):
    i = 0
    for image_url in images:
        path = title + '/' + str(i) + '.jpg'
        download_image(path, image_url)
        print(i, ".jpg", "下载成功")
        i = i + 1


#创建文件夹
def make_a_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)

#另外一种图片创建方式
def save_image(content):
    file_path = '{0}/{1}.{2}'.format(os.getcwd(),md5(content).hexdigest(),'jpg')
    if not os.path.exists(file_path):
        with open(file_path,'wb') as f:
            f.write(content)
            f.close()

def main(offset):
    #获取Html数据
    make_a_dir(KEYWORD)
    html = get_one_page(offset,KEYWORD)
    #解析html
    for url in parse_page_index(html):
        if url:
            html = get_page_detail(url)
            if html:
                result = parse_page_detail(html)
                print(result)
                if result:
                    title = result.get('title')
                    path = KEYWORD+'/'+title
                    make_a_dir(path)
                    images = result.get('images')
                    download_images(images,path)

    print('下载完成')


if __name__ == '__main__':
    groups = [ x*20 for x in range(OFFSET_START,OFFSET_END+1)]
    #开启多进程
    pool =Pool()
    #pool(目标元素，参数的集合)
    pool.map(main,groups)
