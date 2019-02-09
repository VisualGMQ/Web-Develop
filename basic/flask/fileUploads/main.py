from flask import Flask,url_for,request,render_template
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER='./uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/',methods=['POST','GET'])
def mainpage():
    f = ""
    if request.method == 'POST':
        f = request.files.get('file','')
        filename = secure_filename(f.filename)
        f.save(os.path.dirname(__file__)+'/uploads/'+filename)
    return render_template('mainpage.html',info = f)