import time

from flask import Flask
from flask import request
from flask import url_for
from pymysql import connect

from projTool import configReader
from BluePrints.userManagement import userManagement

flaskInstance = Flask(__name__)
flaskInstance.register_blueprint(userManagement)

# 定义一个钩子函数，在每次请求执行前执行
@flaskInstance.before_request
def record_visit_ip():
    # 将配置中mysql参数获取并存储
    mysqlConfigDict = configReader()["mysql"]
    # 将访问flask服务器的客户端ip信息写入数据库，并返回该IP访问次数
    visitIp = request.remote_addr
    visitRecordAddSql = f"insert into visitRecord(ip,visitTime) values ('{visitIp}',now());"
    visitRecordCount = f"select count(*) from visitRecord where ip ='{visitIp}';"
    with connect(host=mysqlConfigDict["ServerHost"],user=mysqlConfigDict["MysqlUser"],password=mysqlConfigDict["MysqlPassword"],database=mysqlConfigDict["Datebase"]) as connection:
        with connection.cursor() as cursor:
            cursor.execute(visitRecordAddSql)
            connection.commit()
            cursor.execute(visitRecordCount)
            clientVisitTimens = cursor.fetchone()[0]
            print(clientVisitTimens)

@flaskInstance.route("/")
def helloFlask():
    return f"Hello Flask!"

flaskInstance.run(host="185.239.86.98",port=50001,debug=True)
# flaskInstance.run(debuger=True)
# flaskInstance.run(port=4999)