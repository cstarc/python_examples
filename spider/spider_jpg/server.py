#!/usr/bin/python
# -*- coding:utf-8 -*-
# all the imports
#import sys 
##from imp import reload
#print sys.getdefaultencoding()
#reload(sys) 
#sys.setdefaultencoding('utf8') 
#print sys.getdefaultencoding()

import sqlite3
import os
import time
import sys
sys.path.append('../../')
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash,send_from_directory
from contextlib import closing  
from werkzeug import secure_filename
from spider_ht  import spider_image
from multiprocessing.pool import ThreadPool as Pool
from multiprocessing import Process

from common import FileDir



# configuration
#DATABASE = 'D:/tmp/w.db'
DATABASE = 'tmp/account.db'
#DEBUG = True
SECRET_KEY = 'development key'

ADMINACCOUNT='admin'
ADMINPASSWORD='31415926'

UPLOAD_FOLDER = 'static/uploads/'
#ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','mp4','avi'])
app = Flask(__name__)
app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['IMAGES'] = 'static/images/'

DAY=60*60*24
global photos_name_array


#路由 
@app.route('/')
def show():
    return redirect(url_for('login'))
    
#管理员登入    
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if session.get('remember'):
        #return redirect(url_for('photos',index_id=0))
        return redirect(url_for('home'))
    if request.method == 'POST':
        if request.form['username'] != ADMINACCOUNT:
            error = 'Invalid username'
        elif request.form['password'] != ADMINPASSWORD:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            if request.form.get('remember'):
                session['remember'] = True
            #return redirect(url_for('photos',index_id=0))
            return redirect(url_for('home'))
    return render_template('login.html', error=error)  

# home 查看照片集
@app.route('/home')
def home():
    global photos_name_array
    photos_name_array=FileDir.get_subdir(app.config['IMAGES'])  #获取照片集name
    #print photos_name_array
    session['photos_num'] = len(photos_name_array)
    photo_names=get_sample_of_photos()         
    #print photo_names
    return render_template('home.html',photos_name_array=photos_name_array,photo_names=photo_names)

# 获取照片集中第一张照片name
def get_sample_of_photos():
    global photos_name_array
    photo_names=[]
    #print photos_name_array
    #从每个图片集下取第一张照片name，若不存在再在图片集数组中删除此图片集
    for photos_name in photos_name_array:
        names=FileDir.get_subfile(app.config['IMAGES']+photos_name , ['.jpg',])
        if names:
            photo_names.append(names[0])
        else:
            photos_name_array.remove(photos_name)
    return photo_names

# 查看照片集内照片
@app.route('/index/<int:index_id>')
def photos(index_id=0):
    global photos_name_array
    session['cur_photo_index'] = index_id
    photos_name=photos_name_array[index_id]
    #names=os.listdir(app.config['IMAGES']+photos_name)   #获取照片集中所有照片name
    names=FileDir.get_subfile(app.config['IMAGES']+photos_name , ['.jpg',])
    return render_template('photos.html',photos_name=photos_name,image_names=names)


# 下一照片集
@app.route('/photos_next')
def next_photos():
    next_index_id=session.get('cur_photo_index')+1
    #print next_index_id
    if next_index_id+1 > session.get('photos_num'):
        next_index_id=0
    return redirect(url_for('photos',index_id = next_index_id))


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('remember', None)
    return redirect(url_for('login'))

           
def spider_images():
    spider=spider_image('http://www.mmjpg.com',1,8,app.config['IMAGES'])
    while 1:
        #print('start rm dir')
        FileDir.rm_dir(app.config['IMAGES'],['save',])
        #print('end rm dir')
        spider.run()
        time.sleep(DAY)
        
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    p = Process(target=spider_images)
    print('Child process will start.')
    p.start() 
    app.run('0.0.0.0',port)   
    #pool = Pool()
    #pool.apply_async(spider_images)
    #pool.apply_async(flask_web_run,args=('0.0.0.0',port))
    #pool.close()
    #pool.join()    
    #app.run(debug=True)

    