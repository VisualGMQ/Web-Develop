from flask import Flask,url_for,render_template,session,request,redirect,flash
import sqlite3
import os
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)
app.config['DATABASE'] = ''

def doLogin(username, password):
    db = sqlite3.connect(app.config['DATABASE']+"users.db")
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE name=%s' % "'"+username+"'")
    info = cursor.fetchone()
    db.close()
    if info == None:
        return False
    else:
        if info[2] == password:
            return True
        else:
            return False

def changeScore(dom,score):
    db = sqlite3.connect(app.config['DATABASE'] + 'domis.db')
    cursor = db.cursor()
    cursor.execute('SELECT score FROM domits WHERE name=%s' % '"'+dom+'"')
    info = cursor.fetchall()
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
    cursor = db.cursor()
    info = cursor.execute("SELECT name,score FROM domits ORDER BY score DESC").fetchall()
    return render_template('homepage.html',doms=info)

@app.route('/login/',methods=['POST','GET'])
def login():
    if request.method == 'POST':
        if doLogin(request.form.get('username','null'), request.form.get('password','null')) == True:
            session['logined']=True
            return redirect(url_for('modify'))
        else:
            session['logined']=False
            flash('login failed')

    return render_template('login.html')

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

@app.route('/logout/',methods=['POST'])
def logout():
    if 'logined' in session and session['logined']==True:
        session['logined']=False
    return redirect(url_for('homepage'))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

