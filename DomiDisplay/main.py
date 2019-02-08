from flask import Flask,url_for,render_template,session,request,redirect,flash
import sqlite3
import os
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)
app.config['DATABASE'] = ''

#用于在数据库查询当中配合where句
def _tDB(string):
    if string == None:
        return '"null"'
    else:
        return '"'+string+'"'


'''
数据库查找函数
如果db为None，那么函数会通过你给出的参数来进行一次性查询（在内部打开和关闭数据库）。
如果db为已经生成的数据库链接，那么查询之后不会关闭数据库。
* condition参数给出查找条件，条件中不需要加上WHERE
* fetch参数决定cursor获得多少数据：
    1：执行.fetchone()获取一条数据
    >1：执行.fetchmany()获取多条数据
    <1：执行.fetchall()获取所有数据
'''
def searchDB(db,table,condition="",fetch=-1,cols='*',OrderBy=None,isDesc=False):
    global flag
    flag = False
    if type(db) == str:
        db = sqlite3.connect(app.config['DATABASE'] + db)
        flag = True
    elif db == None:
        return None

    cursor = db.cursor()
    string = 'SELECT %s FROM %s'% (cols,table)
    if not condition=="":
        string += ' WHERE %s' % condition
    if not OrderBy == None:
        string += " ORDER BY %s" % OrderBy
    if isDesc == True:
        string += " DESC"
    cursor.execute(string)

    global info
    if fetch<1:
        info = cursor.fetchall()
    elif fetch==1:
        info = cursor.fetchone()
    else:
        info = cursor.fetchmany(fetch)
    if flag == True:
        db.close()
    return info

def doLogin(username, password):
    '''
    db = sqlite3.connect(app.config['DATABASE']+"users.db")
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE name=%s' % "'"+username+"'")
    info = cursor.fetchone()
    db.close()
    '''
    info = searchDB('users.db','users',"name=%s" % _tDB(username),fetch=1)
    if info == None:
        return False
    else:
        if info[2] == password:
            return True
        else:
            return False

def changeScore(dom,score):
    '''
    cursor = db.cursor()
    cursor.execute('SELECT score FROM domits WHERE name=%s' % '"'+dom+'"')
    info = cursor.fetchall()
    '''
    db = sqlite3.connect(app.config['DATABASE'] + 'domis.db')
    cursor = db.cursor()
    info = searchDB(db,'domits',"name=%s" % _tDB(dom))
    if not info:
        db.close()
        return False
    else:
        cursor.execute('UPDATE domits SET score=%d WHERE name=%s' % (score,'"'+dom+'"'))
        db.commit()
        db.close()
        return True

@app.route('/',methods=['POST','GET'])
def homepage():
    db = sqlite3.connect(app.config['DATABASE']+"domis.db")
    #cursor = db.cursor()
    sortway=1
    global info
    if request.method == 'POST':
        #依据文本框查找寝室
        if 'searchdom' in request.form:
            searchinfo = searchDB(db,'domits',"name=%s" % _tDB(request.form.get('searchdom', 'null')),1)
            info = [(request.form.get('searchdom','null'),searchinfo[0] if searchinfo!=None else 'NAN')]    #三目表达式
         #按照下拉列表排序寝室
        if 'sortway' in request.form:
            if request.form['sortway'] == 'byscore':
                info = searchDB(db, 'domits', OrderBy='score', isDesc=True, cols='name,score')
                sortway = 1
            else:
                info = searchDB(db, 'domits', OrderBy='name', isDesc=True, cols='name,score')
                sortway = 2
    else:
        #显示全部寝室
        #info = cursor.execute("SELECT name,score FROM domits ORDER BY score DESC").fetchall()
        info = searchDB(db,'domits',OrderBy='score',isDesc=True,cols='name,score')
    db.close()
    return render_template('homepage.html',infoes=info,sortway=sortway)

@app.route('/display/<dominame>')
def displayDom(dominame):
    return render_template('display.html',img = dominame,root_path=app.root_path)

@app.route('/modify/',methods=['GET','POST'])
def modify():
    if not ("logined" in session) or session['logined']==False:
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            global score
            score = request.form['score']
            if score.isdigit():
                score = int(score)
            else:
                flash('not number')
                return render_template('modify.html')
            if changeScore(request.form['dom'],score)==True:
                flash('changed success')
            else:
                flash('changed failed')
        #get doms info
        db = sqlite3.connect(app.config['DATABASE'] + "domis.db")
        cursor = db.cursor()
        cursor.execute("SELECT name,score FROM domits ORDER BY name DESC")
        info = cursor.fetchall()
        return render_template('modify.html',doms=info)

@app.route('/login/',methods=['POST','GET'])
def login():
    if request.method == 'POST':
        if doLogin(request.form.get('username','null'), request.form.get('password','null')) == True:
            session['logined']=True
            return redirect(url_for('modify'))
        else:
            flash('login failed')

    return render_template('login.html')

@app.route('/logout/',methods=['POST'])
def logout():
    if 'logined' in session:
        session.pop('logined')
    return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

