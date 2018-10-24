


import sys
sys.path.append('../../')
from common import FileDir

import os
import requests
from requests.exceptions import RequestException
from pyquery import PyQuery as pq
from hashlib import md5
from multiprocessing.pool import ThreadPool as Pool
import argparse

class spider_image:
    def __init__(self,url,max_page,max_pic,path):
        self.m_url=url
        self.m_max_page=max_page
        self.m_max_pic=max_pic
        self.image_path=path
        self.exist_pics=FileDir.get_subdir(self.image_path)
        print(self.exist_pics)

    def run(self):
        pool = Pool()
        groups = ([item for item in self.get_all_pic_url()]) 
        pool.map(self.parse_and_save_image, groups)
        pool.close()
        pool.join()
    
    # 获取图集的url，通过yield 返回 便于并发处理
    def get_all_pic_url(self):
        next_url=self.m_url
        page_num=1
        pic_num=0
        while (next_url):
            # parse page
            html=self.get_one_page(next_url)
            doc=pq(html)
            lis=doc('.main .pic li').items()
            if lis:
                for item in lis:
                    if item.find('img').attr.alt in self.exist_pics:   # 相同照片集name，不再爬取
                        continue
                    
                    yield {#yield 不能放在另一函数
                        'image_url': item.children('a').attr.href,
                        'title': item.find('img').attr.alt
                    }
                    ++pic_num
                    if pic_num >= self.m_max_pic:
                        break

            if page_num == self.m_max_page:
                break

            # get next url 
            new_postfix=self.get_next_images_page(html)
            if new_postfix!=None:
                next_url=self.m_url+new_postfix
            else:
                next_url=None
                break
            ++page_num

    def get_one_page(self,url):
        try:
            response = requests.get(url)
            response.encoding='utf-8'
            if response.status_code == 200:
                return response.text.encode('utf-8')
            return None
        except RequestException:
            return None

#    def get_one_image(self,url):
#        try:
#            # proxies={
#            #     "http": "http://127.0.0.1:1080", 
#            # }
#            response = requests.get(url)
#            response.encoding='utf-8'
#            print(response.text)
#            if response.status_code == 200:
#                return response.text
#            return None
#        except RequestException:
#            return None

    # #解析获取图集的url
    # def get_pic_url(self,html):
    #     doc=pq(html)
    #     lis=doc('.main .pic li').items()
    #     if lis:
    #         for item in lis:
    #             yield {
    #                 'image_url': item.children('a').attr.href,
    #                 'title': item.find('img').attr.alt
    #             }
                
    def get_next_images_page(self,html):
        doc=pq(html)
        text='下一页'
        page_url=doc('.main .page .ch').items()
        for page in page_url:  
            if page.text()==text:
                return page.attr('href')
            else:
                continue
        return None

    #获取图片集图片
    def get_image_from_pic(self,url):
        next_url=url
        while (next_url):
            doc=pq(self.get_one_page(next_url))
            image=doc('.content a img ')
            new_postfix=self.get_next_image(next_url)
            if new_postfix!=None:
                next_url=self.m_url+new_postfix
            else:
                next_url=None
                continue

            yield {
                'image': image.attr.src,
                }

    def get_next_image(self,url):
        doc=pq(self.get_one_page(url))
        text='下一张'
        a=doc('.page .ch.next')
        if a.text()==text:
            return a.attr('href')
        else:
            return None


    def save_image(self,item,dir_name):
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
            #print(dir_name)
        try:
            #print(str(item.get('image')))
            # 加headers的Referer，不加为防盗图
            headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/201001',
                    'Referer': self.m_url}
            response = requests.get(item.get('image'),headers=headers)
            if response.status_code == 200:
                file_path = '{0}/{1}.{2}'.format(dir_name, md5(response.content).hexdigest(), 'jpg')
                #print('file_path:'+file_path)
                if not os.path.exists(file_path):
                    with open(file_path, 'wb')as f:
                        f.write(response.content)
                else:
                    print('Already Downloaded', file_path)
        except requests.ConnectionError:
            print('Failed to save image')

    def parse_and_save_image(self,item):
        dir_name=self.image_path+item.get('title')
        
        #print(self.image_path)
        #print(item.get('title'))       
        #dir_name.encode('utf-8')
        #print(dir_name)

        for image in self.get_image_from_pic(item.get('image_url')):
            self.save_image(image,dir_name)   

def main(args):
    spider=spider_image('http://www.mmjpg.com',args.page_num,args.image_path)
    spider.run()      

if __name__ =='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n','--page_num',help='获取的最大page数',default='1')
    parser.add_argument('-p','--image_path',help='image dir path',default='./')
    args = parser.parse_args()        
    main(args)
