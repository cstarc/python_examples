import os
import requests
from requests.exceptions import RequestException
from pyquery import PyQuery as pq
from hashlib import md5
from multiprocessing.pool import Pool

def get_one_page(url):
    try:
        response = requests.get(url)
        response.encoding='utf-8'
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None

def get_one_image(url):
    try:
        # proxies={
        #     "http": "http://127.0.0.1:1080", 
        # }
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None

def get_all_pic_url(url):
    next_url=url
    while (next_url):
        html=get_one_page(next_url)
        new_postfix=get_next_images_page(html)

        if new_postfix!=None:
            next_url='http://www.mmjpg.com'+new_postfix
        else:
            next_url=None
            continue

        doc=pq(html)
        lis=doc('.main .pic li').items()
        if lis:
            for item in lis:
                yield {
                    'image_url': item.children('a').attr.href,
                    'title': item.find('img').attr.alt
                }
#获取首页图集的url
def get_pic_url(html):
    doc=pq(html)
    lis=doc('.main .pic li').items()
    if lis:
        for item in lis:
            yield {
                'image_url': item.children('a').attr.href,
                'title': item.find('img').attr.alt
            }
            
def get_next_images_page(html):
    doc=pq(html)
    text='下一页'
    page_url=doc('.main .page .ch').items()
    for page in page_url:  
        if page.text()==text:
            return page.attr('href')
        else:
            continue
    return None

def get_next_image(url):
    doc=pq(get_one_page(url))
    text='下一张'
    a=doc('.page .ch.next')
    if a.text()==text:
        return a.attr('href')
    else:
        return None

#获取图片集图片
def get_image_from_pic(url):
    next_url=url
    while (next_url):
        doc=pq(get_one_page(next_url))
        image=doc('.content a img ')
        new_postfix=get_next_image(next_url)
        if new_postfix!=None:
            next_url='http://www.mmjpg.com'+new_postfix
        else:
            next_url=None
            continue

        yield {
            'image': image.attr.src,
            }        


def save_image(item,dir_name):
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
        print(dir_name)
    try:
        print(str(item.get('image')))
        # 加headers的Referer，不加为防盗图
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/201001',
                'Referer': 'http://www.mmjpg.com'}
        response = requests.get(item.get('image'),headers=headers)
        if response.status_code == 200:
            file_path = '{0}/{1}.{2}'.format(dir_name, md5(response.content).hexdigest(), 'jpg')
            print('file_path:'+file_path)
            if not os.path.exists(file_path):
                with open(file_path, 'wb')as f:
                    f.write(response.content)
            else:
                print('Already Downloaded', file_path)
    except requests.ConnectionError:
        print('Failed to save image')

def get_save_image(item):
    dir_name=item.get('title')
    for image in get_image_from_pic(item.get('image_url')):
        save_image(image,dir_name)   

def main():
    url = 'http://www.mmjpg.com/'

    pool = Pool()
    groups = ([item for item in get_all_pic_url(url)]) 
    pool.map(get_save_image, groups)
    pool.close()
    pool.join()        

if __name__ =='__main__':    
    main()