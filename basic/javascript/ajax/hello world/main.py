from flask import Flask,url_for,request,render_template

app = Flask(__name__)

@app.route('/')
def mainpage():
    return render_template('mainpage.html')