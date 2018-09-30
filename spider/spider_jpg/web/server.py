# all the imports
import sqlite3
import os
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash,send_from_directory
from contextlib import closing  
from werkzeug import secure_filename

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


#def allowed_file(filename):
  #  return '.' in filename and \
   #        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
   
   
#上传文件
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            g.db.execute('insert into video (name) values (?)',[filename])  #[]
            g.db.commit()
            return "succeed"
    return redirect(url_for('login'))

#查看文件   
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return render_template('video.html', filename=url_for('static', filename='uploads/'+filename))


#用户注册  
@app.route('/usersign', methods=['GET', 'POST'])  
def usersign():
    error = None
    if request.method == 'POST':
        #判断是否已注册
        cur = g.db.execute('select username from account') 
        for row in cur.fetchall():
            if request.form['username']==row[0]:
                return  "已注册"
        g.db.execute('insert into account (username, password) values (?, ?)',
                 [request.form['username'], request.form['password']])
        g.db.commit()
        #session['logged_in'] = True
        #flash('You were logged in')
        return "注册成功"
    return "注册失败"
    
#用户登陆处理   
@app.route('/userlogin', methods=['GET', 'POST'])
def userlogin():
    error = None
    if request.method == 'POST':
        if checkUsername(request.form['username']) == False:
            error = 'Invalid username'
        elif checkPassword(request.form['username'],request.form['password']) == False:
            error = 'Invalid password'
        else:
            #session['logged_in'] = True
            #flash('You were logged in')
            if hasBind(request.form['username'])=="尚未绑定情侣":
                return "尚未绑定情侣"
            if hasBind(request.form['username'])==False:
                return "情侣尚未成功绑定"               
            return "登入成功"
    return error
    
# 情侣绑定 
@app.route('/bind', methods=['GET', 'POST'])
def bind():
    error = None
    cur = g.db.execute('select username from account')
    if request.method == 'POST':
        for row in cur.fetchall():
            if request.form['anotherName'] == row[0]:
                g.db.execute("update account set anotherName=? where username=? ",
                [request.form['anotherName'],request.form['ownName']])
                g.db.commit()
                #己方已绑定，判断对方情况
                return isBind(request.form['anotherName'],request.form['ownName'])
        error= "对方尚未注册"  
    return error
#判断是否绑定    
def isBind(username,anotherName):
    cur = g.db.execute('select anotherName from account where username=?',[username])
    for row in cur.fetchall():
        if row[0]==anotherName:
            return "已绑定"
        elif row[0]==None:
            return "对方尚未绑定"     
        return "对方已绑定其他人"   
 
 #判断是否有绑定对象
def hasBind(username):
    cur = g.db.execute('select anotherName from account where username=?',[username])
    for row in cur.fetchall():
        if row[0]==None:
            return "尚未绑定情侣"
        if isBind(row[0],username)=="已绑定":
            return True
        return False    


#更新礼物
@app.route('/gift', methods=['GET', 'POST'])
def gift():
    cur = g.db.execute('select anotherName from account where username=?',[request.form['username']])
    for row in cur.fetchall():
        g.db.execute("update account set curGift=? , curVideo=? where username=? ",
                [request.form['giftImage'],request.form['video'],row[0]])
        g.db.commit()               
        return "True"
    return "False"  
#获得图片地址
@app.route('/getGift', methods=['GET', 'POST'])
def getGift():
    cur = g.db.execute('select curGift from account where username=?',[request.form['username']])
    for row in cur.fetchall():
        if row[0]==None:
            return "无图片"
        return row[0]
        
#获得视频地址
@app.route('/getVideo', methods=['GET', 'POST'])
def getVideo():
    cur = g.db.execute('select curVideo from account where username=?',[request.form['username']])
    for row in cur.fetchall():
        if row[0]==None:
            return "无视频"
        return row[0]

        
#连接数据库                         
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])        
@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
    g.db.close()


#检查用户名 
def checkUsername(username):
    cur = g.db.execute('select username from account')
    for row in cur.fetchall():
        if username==row[0] :
             return True
    return False
#检查密码
def checkPassword(username,password):
    cur = g.db.execute('select username, password from account')
    for row in cur.fetchall():
        if username==row[0] :
            if password==row[1]:
                return True
            else:
                return False            
    return False  

    
#路由 
@app.route('/')
def show():
    return redirect(url_for('login'))
    
#管理员登入    
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if session.get('remember'):
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        if request.form['username'] != ADMINACCOUNT:
            error = 'Invalid username'
        elif request.form['password'] != ADMINPASSWORD:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            if request.form.get('remember'):
                session['remember'] = True
            return redirect(url_for('dashboard'))
    return render_template('login.html', error=error)  
    
@app.route('/index')
def dashboard():
    if session.get('logged_in'):
        cur = g.db.execute('select username,anotherName ,curGift,curVideo from account')
        dict={}
        name=[]
        anotherName=[]       
        inf=[]
        for row in cur.fetchall():
            information=[]
            information.append(row[0])
            information.append(row[1])
            information.append(row[2])
            information.append(row[3])
            inf.append(information)
        cur = g.db.execute('select name from video')
        fname=[]
        for row in cur.fetchall():
            fname.append(row[0])
        return render_template('dashboard.html',information=inf,filename=fname)
        
    return redirect(url_for('login')) 
    
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('remember', None)
    return redirect(url_for('login'))

           

        
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=port)
    