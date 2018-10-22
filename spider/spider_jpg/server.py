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

from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash,send_from_directory
from contextlib import closing  
from werkzeug import secure_filename
from spider_ht  import spider_image
from multiprocessing.pool import ThreadPool as Pool
from multiprocessing import Process


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
#def allowed_file(filename):
  #  return '.' in filename and \
   #        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
   
   
##上传文件
#@app.route('/upload', methods=['GET', 'POST'])
#def upload_file():
#    if request.method == 'POST':
#        file = request.files['file']
#        if file:
#            filename = secure_filename(file.filename)
#            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#            g.db.execute('insert into video (name) values (?)',[filename])  #[]
#            g.db.commit()
#            return "succeed"
#    return redirect(url_for('login'))

##查看文件   
#@app.route('/uploads/<filename>')
#def uploaded_file(filename):
#    return render_template('video.html', filename=url_for('static', filename='uploads/'+filename))
#


##用户注册  
#@app.route('/usersign', methods=['GET', 'POST'])  
#def usersign():
#    error = None
#    if request.method == 'POST':
#        #判断是否已注册
#        cur = g.db.execute('select username from account') 
#        for row in cur.fetchall():
#            if request.form['username']==row[0]:
#                return  "已注册"
#        g.db.execute('insert into account (username, password) values (?, ?)',
#                 [request.form['username'], request.form['password']])
#        g.db.commit()
#        #session['logged_in'] = True
#        #flash('You were logged in')
#        return "注册成功"
#    return "注册失败"
#    
##用户登陆处理   
#@app.route('/userlogin', methods=['GET', 'POST'])
#def userlogin():
#    error = None
#    if request.method == 'POST':
#        if checkUsername(request.form['username']) == False:
#            error = 'Invalid username'
#        elif checkPassword(request.form['username'],request.form['password']) == False:
#            error = 'Invalid password'
#        else:
#            #session['logged_in'] = True
#            #flash('You were logged in')
#            if hasBind(request.form['username'])=="尚未绑定情侣":
#                return "尚未绑定情侣"
#            if hasBind(request.form['username'])==False:
#                return "情侣尚未成功绑定"               
#            return "登入成功"
#    return error
#    

##连接数据库                         
#def connect_db():
#    return sqlite3.connect(app.config['DATABASE'])        
#@app.before_request
#def before_request():
#    g.db = connect_db()
#
#@app.teardown_request
#def teardown_request(exception):
#    db = getattr(g, 'db', None)
#    if db is not None:
#        db.close()
#    g.db.close()
#
#
##检查用户名 
#def checkUsername(username):
#    cur = g.db.execute('select username from account')
#    for row in cur.fetchall():
#        if username==row[0] :
#             return True
#    return False
##检查密码
#def checkPassword(username,password):
#    cur = g.db.execute('select username, password from account')
#    for row in cur.fetchall():
#        if username==row[0] :
#            if password==row[1]:
#                return True
#            else:
#                return False            
#    return False  

    
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
    photos_name_array=dir_name(app.config['IMAGES'])  #获取照片集name
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
    for photos_name in photos_name_array:
        photo_name=os.listdir(app.config['IMAGES']+photos_name)[0]
        photo_names.append(photo_name)
    return photo_names

# 查看照片集内照片
@app.route('/index/<int:index_id>')
def photos(index_id=0):
    global photos_name_array
    session['cur_photo_index'] = index_id
    photos_name=photos_name_array[index_id]
    names=os.listdir(app.config['IMAGES']+photos_name)   #获取照片集中所有照片name
    return render_template('photos.html',photos_name=photos_name,image_names=names)


# 下一照片集
@app.route('/photos_next')
def next_photos():
    next_index_id=session.get('cur_photo_index')+1
    #print next_index_id
    if next_index_id+1 > session.get('photos_num'):
        next_index_id=0
    return redirect(url_for('photos',index_id = next_index_id))

    
# 获取文件名
def file_name(file_dir,file_postfix):  
  files_name=[]  
  for root, dirs, files in os.walk(file_dir): 
    for file in files: 
      if os.path.splitext(file)[1] == file_postfix: 
        files_name.append(file) #os.path.join(root, file)
  return files_name  

# 获取文件名
#def clean_images(file_dir):  
#  files_name=[]
#  try:  
#      for root, dirs, files in os.walk(file_dir): 
#          for file in files: 
#              del_file = os.path.join(root, file)
#              os.remove(del_file)
#          for dir in dirs:
#            if dir =='save':
#                continue
#            del_dir = os.path.join(root, dir)    
#            os.rmdir(del_dir)
#  except Exception e:
#    traceback.print_exc()          

# 获取文件名
def dir_name(file_dir):  
  files_name=[]  
  for root, dirs, files in os.walk(file_dir): 
      return dirs
    

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('remember', None)
    return redirect(url_for('login'))

           
def spider_images():
    spider=spider_image('http://www.mmjpg.com',1,8,'static/images/')
    while 1:
        spider.run()
        time.sleep(DAY)

def flask_web_run(host,port):
    app.run(host, port)
        
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

    