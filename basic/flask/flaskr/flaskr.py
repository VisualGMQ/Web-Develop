import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

app = Flask('welcome')

@app.route('/')
def welcome():
    db = sqlite3.connect('domi.db')
    cursor = db.cursor()
    domicol = cursor.execute('SELECT DISTINCT * FROM domitory ORDER BY vote DESC')
    domidata = domicol.fetchall()
    db.close()
    return render_template('show_welcome.html', data=domidata)

@app.route('/another/')
def another():
    data = 'you jumped here!!'
    return render_template('another.html', data=data)

@app.route('/modify/')
def modify():
    db = sqlite3.connect('domi.db')
    cursor = db.cursor()
    data = cursor.execute('SELECT * FROM domitory ORDER BY name').fetchall()
    db.close()
    return render_template('modify.html',data=data)

@app.route('/login/')
def login():
    db = sqlite3.connect('admins.db')
    cursor = db.cursor()
    userdata = cursor.execute('SELECT * FROM admins').fetchall()
    return render_template('login.html',data=userdata)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.run(debug=True)
    app.run()
