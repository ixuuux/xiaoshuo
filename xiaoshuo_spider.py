# -*- coding: utf-8 -*-
import re
import threading
import time
from lxml import etree
import requests

headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"
}


def get(url, timeout=5):  # 发起请求
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        time.sleep(0.5)
        if response.status_code == 200:
            return response.text
        time.sleep(0.5)
        return get(url, timeout=5)
    except TimeoutError:
        print("time out", url)
        time.sleep(0.5)
        return get(url, timeout=5)
    except Exception as e:
        print(e, url)
        time.sleep(0.5)
        return get(url, timeout=5)


def get_one_page():  # 获取榜单每一页，然后多线程发送请求
    start_url = "http://m.biquge.com.tw/top/allvisit_{}.html"
    for page in range(1, 10000):
        html = get(start_url.format(page))
        ele = etree.HTML(html)
        urls = ele.xpath('//div[@class="articlegeneral"]/p[2]')
        for url in urls:
            ur = "http://m.biquge.com.tw" + url.xpath('./a/@href')[0]
            num = re.findall('[0-9]', ur)
            if len(num) == 5:
                geshi = num[0]+num[1]+"_"+"".join(num)+"_{}"
                ur = "http://m.biquge.com.tw/{}/".format(geshi)  # 每本小说的章节列表，需翻页
                t1 = threading.Thread(target=td_get_doc, args=(ur, ))
                t1.start()
            else:
                geshi = num[0] + "_" + "".join(num) + "_{}"
                ur = "http://m.biquge.com.tw/{}/".format(geshi)
                t2 = threading.Thread(target=td_get_doc, args=(ur,))
                t2.start()
        if not urls:
            print("采集结束，共{}页".format(page-1))
            break


def td_get_doc(ur):  # 获取小说每章的正文
    for page in range(1, 10000):  # 翻页
        html = get(ur.format(page))
        ele = etree.HTML(html)
        urls = ele.xpath('//ul//li/a/@href')
        for url in urls:  # 请求每章
            html_doc = get("http://m.biquge.com.tw"+url)
            title = re.findall('h1.*?>《(.*)》.*?</h1>', html_doc, re.S)[0]
            elee = etree.HTML(html_doc)
            chaptertitle = elee.xpath('//h1[@id="chaptertitle"]/text()')[0]
            doc = elee.xpath('//div[@id="novelcontent"]/p//text()')
            with open("./xiaosuo/{}.txt".format(title), "a", encoding="utf-8") as f:
                f.write(chaptertitle)
                f.write("\n".join(doc))
                print("{}完成".format(title))


if __name__ == '__main__':
    get_one_page()
