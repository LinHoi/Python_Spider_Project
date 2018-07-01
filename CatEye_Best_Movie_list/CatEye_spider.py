import requests
from requests.exceptions import RequestException
import re
import json
from multiprocessing import Pool

def get_one_page(url,headers):
    try:
        response = requests.get(url,headers = headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None

def main(offset):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'
    }
    url = 'http://maoyan.com/board/4?'+str(offset)
    html = get_one_page(url,headers)
    print(html)
    for item in parse_one_page(html):
        print(item)
        write_to_file(item)

def parse_one_page(html):
    pattern = re.compile('<dd>.*?index.*?>(.*?)</i>.*?data-src="(.*?)".*?name"><a'
                         +'.*?>(.*?)</a>.*?star">(.*?)</p>.*?releasetime">(.*?)</p>'
                         +'.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>',re.S)
    items =re.findall(pattern,html)
    for item in items:
        yield{
            'index': item[0],
            'image': item[1],
            'name': item[2],
            'staff': item[3].strip()[3:],
            'releastime': item[4][5:],
            'score': item[5]+item[6]
        }

def write_to_file(content):
    with open('result.txt','a',encoding='utf-8') as f:
        f.write(json.dumps(content,ensure_ascii=False)+'\n')
        f.close()


if __name__ == '__main__':
    '''
    for i in range(10):
        main(i*10)
    '''
    pool = Pool()
    pool.map(main,[i*10 for i in range(10)])
