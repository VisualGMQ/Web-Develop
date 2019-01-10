from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return 'this is a home page!'

@app.route('/welcome')
def welcome():
    return 'hello custom!'

@app.route('/person/<person_name>')
def showperson(person_name):
    return "you are "+person_name

if __name__ == '__main__':
    app.debug=True
    app.run()
