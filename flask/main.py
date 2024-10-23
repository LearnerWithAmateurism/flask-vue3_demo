from flask import Flask

flaskInstance = Flask(__name__)

@flaskInstance.route("/")
def helloFlask():
    return "Hello Flask!"

flaskInstance.run(host="185.239.86.98",port=50001,debug=True)
# flaskInstance.run(debuger=True)
# flaskInstance.run(port=4999)