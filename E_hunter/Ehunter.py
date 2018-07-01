import requests
from requests.exceptions import RequestException
from config import *
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from multiprocessing import Pool
from pathos.multiprocessing import ProcessingPool
from hashlib import md5
import os
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'
}

#获取html
def get_one_page(url):
    try:
        response = requests.get(url,headers = headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求网页失败%s'%url)
        return None

#解析html
def parse_one_page(html):
    if html:
        BeautifulSoup(html,'lxml')
        detail_urls = re.findall(r'class="it5"><a href="(.*?)"',html,re.S)
        return detail_urls
    return None

#解析详情页的标题
def parse_title(html):
    title = re.findall(r'id="gn">(.*?)</h1>',html,re.S)[0]
    return title

#解析详情页的子层URL
def parse_detail_page(html):
    BeautifulSoup(html,'lxml')
    image_urls = re.findall(r'class="gdtm".*?<a href="(.*?)"',html,re.S)
    return image_urls

#解析详情页的兄弟层url
def parse_brother_page(html):
    BeautifulSoup(html,'lxml')
    brother_page_numbers = re.findall(r'firstChild.*?href.*?/.*?p=(.*?)" onclick',html,re.S)
    if brother_page_numbers:
        brother_final_page_number=brother_page_numbers[-2]
        print(brother_final_page_number)
        return int(brother_final_page_number)
    return 0

#解析详情页和兄弟页的下层url
def parse_one_gallery(gallery_url):
    html = get_one_page(gallery_url)
    title = parse_title(html)
    print(title)
    final_page =parse_brother_page(html)
    brother_urls =[]
    brother_urls.append(gallery_url)
    for i in range(1,final_page+1):
        brother_urls.append(gallery_url+'?p='+str(i))
    print(brother_urls)
    image_urls = []
    for brother_url in brother_urls:
        html =get_one_page(brother_url)
        one_page_image_urls = parse_detail_page(html)
        image_urls.extend(one_page_image_urls)
    print(image_urls)
    return title,image_urls

#解析图片地址(selenium模拟)
def parse_image_url_selenium(image_url,browser,count = 1):
    try:
        browser.get(image_url)
        html = browser.page_source
        real_url = re.findall(r'<img id="img" src="(.*?)"', html, re.S)[0]
        print(real_url)
        return real_url
    except:
        print('解析图片地址出错%s,重新解析，解析次数%d'%(image_url,count))
        count = count + 1
        if count <=5:
            parse_image_url_selenium(image_url, browser, count)
        else:
            print('解析图片地址%s失败，放弃解析，该图片未保存'%image_url)
            return None

def open_chrome_headless():
    option = webdriver.ChromeOptions()
    #禁止图片加载
    prefs = {
        'profile.default_content_setting_values': {
            'images': 2
        }
    }
    option.add_experimental_option('prefs', prefs)
    option.add_argument('headless')
    option.add_argument('window-size=1200x600')
    browser = webdriver.Chrome(chrome_options=option)
    return  browser

def parse_real_url(image_url,browser):
    real_url = parse_image_url_selenium(image_url,browser)
    while real_url == 'https://ehgt.org/g/509.gif':
        print('请更换IP')
        time.sleep(10)
        real_url = parse_image_url_selenium(image_url,browser)
    return real_url

#保存图片
def save_image(content,title,name,real_url):
    file_path = '{0}/{1}/{2}/{3}.{4}'.format(PATH,ARTIST,title,name,'jpg')
    image_md5 = md5(content).hexdigest()
    error_image_md5 = '88FE16AE482FADDB4CC23DF15722348C'.lower()
    if  image_md5 != error_image_md5:
        if not os.path.exists(file_path):
            with open(file_path,'wb') as f:
                f.write(content)
                f.close()
            print('%s/%s.jpg下载成功'%(title,name))
        else :
            print("%s/%s.jpg已存在"%(title,name))
    else :
        print("%s/%s.jpg下载出错"%(title,name))
        print("访问量超过上限，请更换代理IP")
        time.sleep(10)
        download_image(real_url,title,name)



#下载图片
def download_image(real_url,title,name):
    try:
        response = requests.get(real_url,headers = headers)
        if response.status_code == 200:
            save_image(response.content,title,name,real_url)
        return None
    except RequestException:
        print('下载图片%s失败'%real_url)
        return None

#建立文件夹
def make_a_dir(path):
    try:
        os.mkdir(path)
    except :
        pass


#主函数：用于下载一个画师的全部作品
def main():
    url='https://e-hentai.org/tag/artist%3A'+ARTIST
    browser = open_chrome_headless()
    html = get_one_page(url)
    detail_urls = parse_one_page(html)
    #print(detail_urls)
    for detail_url in detail_urls:
        title,image_urls= parse_one_gallery(detail_url)
        make_a_dir(PATH+'/'+ARTIST+'/'+title)
        count = 0
        for image_url in image_urls:
            real_url = parse_image_url_selenium(image_url,browser)
            name = str(count)
            download_image(real_url,title,name)
            count = count+1
        break
    print('下载结束')
    browser.close()

#附函数：use for download a gallery
def Download_a_gallery(gallery_url):
    browser = open_chrome_headless()
    title,image_urls= parse_one_gallery(gallery_url)
    make_a_dir(PATH+'/'+ARTIST)
    make_a_dir(PATH+'/'+ARTIST+'/'+title)
    name = 0
    for image_url in image_urls:
        real_url = parse_real_url(image_url,browser)
        download_image(real_url,title,name)
        name = name+1
    print('%s下载结束'%title)
    browser.close()

#快速下载
def Download_a_image_SP(image_url,title):
    browser = open_chrome_headless()
    real_url = parse_image_url_selenium(image_url, browser)
    browser.close()
    try:
        name = re.split('/', real_url)[-1][:-4]
    except:
        name = None
    if real_url and name:
        download_image(real_url, title, name)

def Download_a_gallery_SP(gallery_url):

    title,image_urls= parse_one_gallery(gallery_url)
    make_a_dir(PATH+'/'+ARTIST)
    make_a_dir(PATH+'/'+ARTIST+'/'+title)
    titles = []
    for i in range(len(image_urls)):
        titles.append(title)
    propool = ProcessingPool()
    propool.map(Download_a_image_SP,image_urls,titles)
    print('%s下载结束'%title)






#执行函数
if __name__ == '__main__':
    time_start =time.time()
    #创建保存目录
    make_a_dir(PATH)

    ##--------------------------------------------------------##
    # #功能一：保存一个画师全部作品
    # #使用方法：在config设置PATH和ARTIST参数即可
    # make_a_dir(PATH+'/'+ARTIST)
    # main()

    ##--------------------------------------------------------##
    # #功能二：下载单个gallery
    # #使用方法：将下方gallery_url替换为下载url
    # #替换ARTIST参数(建议存储为画师名称)
    # gallery_url = 'https://e-hentai.org/g/950404/d61f7f83cb/'
    # Download_a_gallery(gallery_url)

    ##--------------------------------------------------------##
    # #功能三：多进程下载
    # # 自定义urls
    gallery_urls = ['https://e-hentai.org/g/1144066/36d34e6283/',
                    'https://e-hentai.org/g/1118346/87b4194d0a/',
                    'https://e-hentai.org/g/1061586/551fcf3d28/',
                    'https://e-hentai.org/g/1200449/81436872f5/'
                    ]
    #解析ARTIST的urls
    # url = 'https://e-hentai.org/tag/artist%3Anohito'
    # browser = open_chrome_headless()
    # html = get_one_page(url)
    # gallery_urls2 = parse_one_page(html)
    # browser.close()

    pool = Pool()
    pool.map(Download_a_gallery,gallery_urls)

    ##-----------------------------------------------------------##
    ##单图集快速下载
    # Download_a_gallery_SP('https://e-hentai.org/g/481744/11007d0e36/')
    # time_end =time.time()
    # run_time=time_end-time_start
    # print('本次下载时间为%d分钟'%(run_time/60))









