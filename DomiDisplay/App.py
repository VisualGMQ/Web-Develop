## @package App
#  @brief 封装着app变量的文件
#
#将app变量独立出来，方便其他文件的调用和松耦合

from flask import Flask
import os
from datetime import timedelta

## @var app
# @brief 网站的app，里面保存着配置和功能(详见flask)
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)
app.config['DATABASE'] = './database/'
app.config['DOMITSIMAGES'] = './static/images/domits/'