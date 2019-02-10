from flask import Flask,url_for,render_template,session,request,redirect,flash,app
from werkzeug.utils import secure_filename
import sqlite3
import os
import pandas
from database.initDomits import refactoryDomits
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)
app.config['DATABASE'] = './database/'

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

#检查用户名和密码是否正确
def doLogin(username, password):
    info = searchDB('users.db','users',"name=%s" % _tDB(username),fetch=1)
    if info == None:
        return False
    else:
        if info[2] == password:
            return True
        else:
            return False

#修改宿舍得分
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

#上传的文件是不是.xlsx,.xls的文件
def isFileIlligel(filename):
    if '.xlsx' in filename or '.xls' in filename:
        return True
    return False

def isImgIlligel(imgname):
    if '.jpeg' in imgname or '.jpg' in imgname or '.png' in imgname or '.bmp' in imgname or '.gif' in imgname:
        return True
    return False

#上传Excel文件
def upLoadExcel():
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
        flash('save success')
        session['excel'] = os.getcwd() + "/files/" + filename

#上传寝室图片
def uploadImage():
    #global  imgname,imgfile
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
        imgpath = './static/images/'+docname
        if not os.path.exists(imgpath):
            os.makedirs(imgpath)
        imgfile.save(imgpath+'/'+imgname)
        flash('image success')
    return redirect(url_for('modify'))



#根据上传的Excel文件修改domis数据库
def modifyDomits(filename):
    df = pandas.read_excel(filename)
    for i in range(len(df)):
        changeScore(df.iloc[i]['宿舍'],df.iloc[i]['分数'])

@app.route('/',methods=['POST','GET'])
def homepage():
    db = sqlite3.connect(app.config['DATABASE']+"domis.db")
    sortway=1
    global info
    if request.method == 'POST':
        #依据文本框输入查找寝室
        if 'searchdom' in request.form:
            searchinfo = searchDB(db,'domits',condition = ("name=%s" % _tDB(request.form.get('searchdom', 'null').upper())),cols='score',fetch = 1)
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
        info = searchDB(db,'domits',OrderBy='score',isDesc=True,cols='name,score')
    db.close()
    return render_template('homepage.html',infoes=info,sortway=sortway)

@app.route('/display/<dominame>')
def displayDom(dominame):
    root_path = './static/images/'+dominame
    global images
    images = []
    for root, dirs, files in os.walk(root_path):
        images += files
    return render_template('display.html',dominame = dominame,root_path=root_path,images=images)

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

@app.route('/modify/logout/', methods=['POST'])
def logout():
    if 'logined' in session:
        if 'logined' in session:
            session.pop('logined')
        if 'excel' in session:
            session.pop('excel')
    return redirect(url_for('login'))

@app.route('/modify/uploadexcel/', methods=['POST'])
def uploadexcel():
    upLoadExcel()
    refactoryDomits(session['excel'],app.config['DATABASE'])
    return redirect(url_for('modify'))

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

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__=='__main__':
    app.run(debug = True)