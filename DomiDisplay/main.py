## @package main
#  @author VisualGMQ
#  @brief 程序的主文件，代码在此运行
from flask import Flask,url_for,render_template,session,request,redirect,flash
from werkzeug.utils import secure_filename
import sqlite3
import pandas as pd
import os
import shutil
import pandas
from database.initDomits import refactoryDomits
from datetime import timedelta

## @var app
# @brief 网站的app，里面保存着配置和功能(详见flask)
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)
app.config['DATABASE'] = './database/'
app.config['DOMITSIMAGES'] = './static/images/domits/'

## @fn _tDB(string)
#  @brief 在字符串最外面加上双引号
#  @param string 要加上双引号的字符串
#  @return 加上双引号的string
#  @see searchDB()
#
#  这个函数用来给字符串最外面加上双引号，用于配合数据库查找函数来进行字符串拼接。
def _tDB(string):
    if string == None:
        return '"null"'
    else:
        return '"'+string+'"'

## @fn searchDB(db,table,condition="",fetch=-1,cols='*',OrderBy=None,isDesc=False)
#  @brief 数据库查找函数
#  @param condition 给出查找条件，条件中不需要加上WHERE，会自动将这个参数和WHERE语句拼接
#  @param fetch 决定cursor获得多少数据：
#    * 1：执行.fetchone()获取一条数据
#    * >1：执行.fetchmany()获取多条数据
#    * <1：执行.fetchall()获取所有数据
#       默认为-1
#  @param table 要查找的表名
#  @param cols 要匹配的列名，默认为全部匹配
#  @param OrderBy 是否按序查找，默认不按序查找。可以传入按序的列名（只能按照一列）
#  @param isDesc 在按序查找的情况下是否降序查找，默认为False
#  @return 返回查询结果，使用元组返回
#
#  如果db为None，那么函数会通过你给出的参数来进行一次性查询（在内部打开和关闭数据库）。
#  如果db为已经生成的数据库链接，那么查询之后不会关闭数据库。
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

## @fn doLogin(username,password) 
#  @brief 检查用户名和密码是否正确
#  @param username 用户输入的用户名
#  @param password 用户密码
#  @return 成功返回True，失败返回False
#
#这个函数会将用户输入的用户名和密码与database/user.db数据库匹配。
def doLogin(username, password):
    info = searchDB('users.db','users',"name=%s" % _tDB(username),fetch=1)
    if info == None:
        return False
    else:
        if info[2] == password:
            return True
        else:
            return False

## @fn changeScore(dom,score) 
#  @brief 修改宿舍得分
#  @param dom 宿舍的名称
#  @param score 要修改的分数
#  @return 修改成功返回True，否则返回False
#
#这个函数会查找database/domis.db数据库，并且修改里面的score字段
def changeScore(dom,score):
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

## @fn isFileIlligel(filename) 
#  @brief 文件是不是.xlsx,.xls的文件
#  @param filename 文件的名称
#  @return 如果满足格式返回True，否则返回False
#  @see isImgIlligel()
#
#这个函数会检查你给出的文件名称里面有没有.xlsx或者.xlsx来确定这个文件是不是excel文件。
def isFileIlligel(filename):
    if '.xlsx' in filename or '.xls' in filename:
        return True
    return False

## @fn isImgIlligel(imgname)
#  @brief 文件是不是图片
#  @param imgname 文件的名称
#  @return 如果是图片返回True
#  @see isFileIlligel()
#
#这个函数会查找imgname里面是否有.jpg .jpeg .png .bmp .gif文件，从而判断是否是图片。
def isImgIlligel(imgname):
    if '.jpeg' in imgname or '.jpg' in imgname or '.png' in imgname or '.bmp' in imgname or '.gif' in imgname:
        return True
    return False

## @fn uploadExcel() 
#  @brief 上传Excel文件
#  @see uploadImage() isFileIlligel()
#
#上传用户选择的excel文件
def uploadExcel():
    global file
    if request.method == 'POST':
        if 'excelfile' not in request.files:
            flash('no file')
            return redirect(url_for('modify'))
        file = request.files['excelfile']
        filename = secure_filename(file.filename)
        if not isFileIlligel(filename):
            flash('file format error')
            return redirect(url_for('modify'))
        file.save(os.getcwd() + "/files/" + filename)
        df = pd.read_excel(os.getcwd() + "/files/" + filename)
        if '宿舍' not in df or '分数' not in df:
            flash('excel not format')
            return redirect(url_for('modify'))
        flash('save success')
        session['excel'] = os.getcwd() + "/files/" + filename

## @fn uploadImage() 
#  @brief 上传图片
#  @see uploadExcel() isImgIlligel()
#
#上传用户选择的图片
def uploadImage():
    if request.method == 'POST':
        if 'docimg' not in request.files:
            flash('no image')
            return redirect(url_for('modify'))
        imgfile = request.files['docimg']
        imgname = secure_filename(imgfile.filename)
        if not isImgIlligel(imgname):
            flash('image failed')
            return redirect(url_for('modify'))
        if 'docname' not in request.form:
            flash('no doc')
            return redirect(url_for('modify'))
        docname = request.form['docname'].upper()
        imgpath = app.config['DOMITSIMAGES'] + docname
        if not os.path.exists(imgpath):
            os.makedirs(imgpath)
        imgfile.save(imgpath+'/'+imgname)
        flash('image success')
    return redirect(url_for('modify'))



## @fn modifyDomits() 
#  @brief 根据上传的Excel文件修改domis数据库
#  
#这个函数根据你最近一次上传的文件来修改databaswe/domis.db，这个函数在上传文件的同时自动调用
def modifyDomits(filename):
    df = pandas.read_excel(filename)
    for i in range(len(df)):
        changeScore(df.iloc[i]['宿舍'],df.iloc[i]['分数'])

## @defgroup 路由函数
#  @brief flask要求的，可以生产网络页面的函数
#  @{

## @fn homepage()
#  @brief 主页，url:'/'
#
#用于显示主页
@app.route('/',methods=['POST','GET'])
def homepage():
    db = sqlite3.connect(app.config['DATABASE']+"domis.db")
    sortway=1
    isTextSearch = False
    info = []
    rank = None
    rank = None
    if request.method == 'POST':
        #依据文本框输入查找寝室
        if 'searchdom' in request.form:
            searchinfo = searchDB(db,'domits',condition = ("name=%s" % _tDB(request.form.get('searchdom', 'null').upper())),cols='score',fetch = 1)
            info = [(request.form.get('searchdom','null'),searchinfo[0] if searchinfo!=None else 'NAN')]    #三目表达式
            orderinfo = searchDB(db,'domits',cols = 'name',OrderBy = 'score', isDesc=True)
            for k,i in enumerate(orderinfo):
                if i[0]==request.form['searchdom']:
                    rank = k
            isTextSearch = True
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
        info = searchDB(db,'domits',OrderBy='score',isDesc=True,cols='name,score')
    db.close()
    return render_template('homepage.html',infoes=info,sortway=sortway,isTextSearch = isTextSearch,rank=rank)

## @fn displayDom(dominame)
#  @brief 展示宿舍页面，url:'/display/<dominame>'
#  @param dominame 要展示的宿舍
#
#展示前三名宿舍图片的页面
@app.route('/display/<dominame>')
def displayDom(dominame):
    root_path = app.config['DOMITSIMAGES']+dominame
    images = []
    for root, dirs, files in os.walk(root_path):
        images += files
    root_path = root_path.replace('./static/', "")
    return render_template('display.html',dominame = dominame,root_path=root_path,images=images)

## @fn modify()
#  @brief 后台修改页面,url:'/modify/'
#
#后台修改页面，方便修改，进入前必须登录
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

## @fn login()
#  @brief 登录界面,url:'/login/'
#
#管理者要想进入后台，比如进入这个页面进行登录
@app.route('/login/',methods=['POST','GET'])
def login():
    if request.method == 'POST':
        if doLogin(request.form.get('username','null'), request.form.get('password','null')) == True:
            session['logined']=True
            return redirect(url_for('modify'))
        else:
            flash('login failed')

    return render_template('login.html')

## @fn logout()
#  @brief 登出
#
#只POST，用于实现登出功能
@app.route('/modify/logout/', methods=['POST'])
def logout():
    if 'logined' in session:
        if 'logined' in session:
            session.pop('logined')
        if 'excel' in session:
            session.pop('excel')
    return redirect(url_for('login'))

## @fn uploadexcel()
#  @brief 上传excel文件
#
# 管理者在文件功能部分点击“上传”的时候触发,只POST
@app.route('/modify/uploadexcel/', methods=['POST'])
def uploadexcel():
    uploadExcel()
    if 'excel' in session:
        refactoryDomits(session['excel'],app.config['DATABASE'])
    return redirect(url_for('modify'))

## @fn uploadimg()
#  @brief 上传图像
#
#  管理者在图像功能部分点击“上传”的时候触发,只POST
@app.route('/modify/uploadimg/', methods=['POST'])
def uploadimg():
    uploadImage()
    return redirect(url_for('modify'))

'''
@app.route('/modify/refactoryDomits/', methods=['POST'])
def domrefact():
    if request.method == 'POST':
        if 'excel' in session:
            print(os.path.dirname(__file__) + '/files/' + session['excel'])
            refactoryDomits(os.path.dirname(__file__)+'/files/'+session['excel'])
        else:
            flash('excel file not found')
    return redirect(url_for('modify'))
'''

## @fn clearimages()
#  @brief 清除以前的全部图像
#
#  在管理者点击“清除图像”按钮的时候触发，只POST
@app.route('/modify/clearimages/',methods=['POST'])
def clearimages():
    if request.method == 'POST':
        for ele in os.listdir(app.config['DOMITSIMAGES']):
            if os.path.isdir(app.config['DOMITSIMAGES']+ele):
                shutil.rmtree(app.config['DOMITSIMAGES']+ele)
        flash('images delete')
    return redirect(url_for('modify'))


## @fn page_not_found(error)
#  @brief 404错误返回的页面
#  @param 系统错误参数
#
#当发生404时会返回的页面
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

##@}

if __name__=='__main__':
    app.run(debug = True)
