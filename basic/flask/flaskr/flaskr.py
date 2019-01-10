import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

app = Flask('welcome')

@app.route('/')
def welcome():
    db = sqlite3.connect('domi.db')
    cursor = db.cursor()
    domicol = cursor.execute('SELECT DISTINCT * FROM domitory ORDER BY vote')
    domidata = domicol.fetchall()
    return render_template('show_welcome.html', data=domidata)

@app.route('/another')
def another():
    data = 'you jumped here!!'
    return render_template('another.html', data=data)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run()
