# import time
import os
# import json
import secrets


from flask import Flask
from flask import request
# from flask import abort
from flask import session
from pymysql import connect

from projTool import mysql_pool_conn
from BluePrints.userManagement import userManagement
from BluePrints.api4Test import api4Test


flaskInstance = Flask(__name__)
# # 配置环境参数
# flaskInstance.config.from_file("config.json", load=json.load)
# 注册蓝图
flaskInstance.register_blueprint(userManagement)
flaskInstance.register_blueprint(api4Test)
# 设置秘钥
flaskInstance.secret_key = secrets.token_hex()


# 定义一个钩子函数，在每次请求执行前执行
@flaskInstance.before_request
def record_visit_ip():
    ## 将配置中mysql参数获取并存储
    # mysqlConfigDict = configReader()["mysql"]
    # 将访问flask服务器的客户端ip信息写入数据库，并返回该IP访问次数
    visitIp = request.remote_addr
    visitRecordAddSql = f"insert into visitRecord(ip,visitTime) values ('{visitIp}',now());"
    ## visitRecordCount = f"select count(*) from visitRecord where ip ='{visitIp}';"
    with mysql_pool_conn as conn:
        conn.cursor.execute(visitRecordAddSql)
        conn.conn.commit()
    # with connect(
    #     host=mysqlConfigDict["ServerHost"],
    #     user=mysqlConfigDict["MysqlUser"],
    #     password=mysqlConfigDict["MysqlPassword"],
    #     database=mysqlConfigDict["Datebase"]
    #     ) as connection:
    #     with connection.cursor() as cursor:
    #         cursor.execute(visitRecordAddSql)
    #         connection.commit()
    #         # cursor.execute(visitRecordCount)
    #         # clientVisitTimens = cursor.fetchone()[0]
    #         # print(clientVisitTimens)

@flaskInstance.route("/")
def helloFlask():
    # session["test"] = "test"
    print(session)
    session.clear()
    # redis_connc = redis.Redis(connection_pool=flaskInstance.config["redis_pool"])
    return f"Hello Flask!",200

# @flaskInstance.route("/test/")
# def test_func():
#     abort(400,description="test")




if __name__ == '__main__':
    print(os.getcwd())
    print(flaskInstance.root_path)
    flaskInstance.run(host="185.239.86.98",port=50001,debug=True,ssl_context=None)
# flaskInstance.run(debuger=True)
# flaskInstance.run(port=4999)