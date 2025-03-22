"""
这个文件用于自定义一些项目中会用到的工具函數和类
"""
import json
import os
import smtplib
import time

import jwt
import redis
import pymysql
from flask import current_app,abort
from dbutils import pooled_db


# 用于读取配置文件
configPath = os.path.join(os.path.dirname(__file__),"config.json")
def configReader(configKey=None,file=configPath) -> str:
    "这个方法用来获取config.json文件中的配置"
    with open(file) as file:
        if configKey is None:
            return json.load(file)
        else:
            return json.load(file)[configKey]
        


# 配置redis连接池
redis_env = configReader("redis")
redis_pool = redis.ConnectionPool(
    host=redis_env["ServerHost"],
    password=redis_env["password"],
    decode_responses=True,
    max_connections=4
    )
# 工厂设计模式开发一个redis连接工厂函数
def redis_pool_conn(redis_pool=redis_pool) -> redis.Redis:
    return redis.Redis(connection_pool=redis_pool)


# 配置mysql连接池 - 连接没有指定数据库实例
mysql_env = configReader("mysql")
mysql_pool = pooled_db.PooledDB(
    creator = pymysql,
    maxconnections = 4,
    mincached = 2,
    maxcached = 2,
    maxshared = 4,
    blocking = True,
    ping = 1,
    host = mysql_env["ServerHost"],
    user = mysql_env["MysqlUser"],
    password = mysql_env["MysqlPassword"],
    database = mysql_env["Datebase"]
)
class MysqlPool:
    def __init__(self, mysql_pool=mysql_pool):
        self.pool = mysql_pool
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = self.pool.connection()
        self.cursor = self.conn.cursor()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.conn.close()
# 单例设计模式开发一个连接对象
mysql_pool_conn = MysqlPool()



# 发送邮件的工具函数
stmp_env = configReader("stmpServer")
def send_email(to_addrs :str| list[str], content :str) -> None:
    "这个方法用来发送邮件"
    with smtplib.SMTP_SSL(stmp_env["serverHost"]) as smtp:
        smtp.login(stmp_env["serverUser"],stmp_env["userPassword"])
        smtp.sendmail(stmp_env["serverUser"],to_addrs,content)



# 用于生成JWT字符串对象的工厂函数
def jwt_factory(*user_info: tuple, algorithm :str = "HS256", lifetime :int = 3600) -> str:
    "这个函数用来生成一个JWT"
    payload = {
        "user_name": user_info[0],
        "user_email": user_info[1],
        "exp": lifetime + time.time() 
    }
    return jwt.encode(payload,current_app.secret_key,algorithm=algorithm)

# 用于验证JWT实收有效的函数
def jwt_verify(token :str, algorithm :str = "HS256",key :str= None) -> str:
    "这个函数用来验证JWT"
    if not key:
        key = current_app.secret_key
    try:
        payload = jwt.decode(token,key,algorithms=algorithm)
    except jwt.ExpiredSignatureError:
        abort(401,{"result":"error","description":"Your token has expired."})
    except jwt.InvalidTokenError:
        abort(401,{"resutl":"error","description":"Your token is invalid."})
    return payload