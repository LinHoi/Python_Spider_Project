import requests
import re
import os
import time
path="D:\python"
#网页地址
url="http://book.suixw.com/modules/article/reader.php?aid=436"
#http请求
response = requests.get(url)
#编码方式
response.encoding = 'gbk'
#网页源码
html = response.text
#获取小说名并建立文件夹
novel = re.findall(r'<div id="title">(.*?)</div>',html,re.S)[0]
novelpath=path+"\%s"%novel
if os.path.exists(novelpath)==False:
    os.mkdir(novelpath)
print(novel)
#print(html)
#获取章节信息
dl = re.findall(r'<table(.*?)</table>',html,re.S)[0]
#获取卷名
#用与匹配正则表达式的是字符串，不能是数组，故上述dl是指数组第一个元素，末尾加【0】
parts=re.findall(r'class="vcss"(.*?)<td colspan="4"',dl,re.S)
#print(parts)
#part包含各个卷的信息（卷名，卷内容
for part in parts:
    #提取卷标题
    name = re.findall(r'>(.*?)<!-',part,re.S)[0]
    name2=re.findall(r'\r\n\t\r\n    (.*?)\r\n    \r\n\t',name,re.S)[0]
    #name2原本格式为['第九卷 Alicization Beginning']，需要去掉前后的[',']
    filename=name2[:]
    print("正在下载：%s"%filename)
    #建立卷文件夹
    filepath=novelpath+"\%s"%filename
    if os.path.exists(filepath) == False:
        os.mkdir(filepath)
    
    #提取小说文本
    texts = re.findall(r'<td class="ccss">(.*?)</td>',part,re.S)
    for text0 in texts:
        text = re.findall(r'<a href="(.*?)">',text0,re.S)
        #提取文本链接（需要去除空链接）
        if text:
            #加上下标居然可以去掉[',']
            textpath=text[0]
            response = requests.get(textpath)
            response.encoding = 'gbk'
            texthtml = response.text
            #提取文本
            title = re.findall(r'id="title">(.*?)</div',texthtml,re.S)[0]
            textemp=re.findall(r'id="content">(.*?)</div',texthtml,re.S)[0]
            

            #过滤文本
            finaltext0=textemp.replace("&nbsp;","")
            finaltext=finaltext0.replace("<br />","")
            #print(finaltext)

            #写入文件
            fpath=filepath+"\%s"%title+".txt"
            fname = open(fpath,"w")
            fname.write(finaltext)

            time.sleep(8)

    print("%s下载完毕"%filename)


            
print("文件已经下载完毕")
            
            
            


#创建章节文件夹


