import random
import hashlib
import smtplib

import redis
import pymysql
from flask import Blueprint
from flask import request
from flask import session
# from flask import url_for

from projTool import configReader

userManagement = Blueprint("userManagement",__name__,url_prefix="/user")

# 用户登陆
@userManagement.get("/userLogin")
def user_login():
    "获取用户名和密码，校验是否允许登陆，如果允许登陆，则设置cookies，用于之后的登陆状态维护"
    # 将配置读取到字典，节省每次读取配置的开销
    mysqlConfigDict = configReader()["mysql"]
    # 获取用户输入的用户名和密码，并进行校验
    userName = request.get_json()["userName"]
    userPasswordInput = request.get_json()["userPassword"]
    # 通过用户输入的用户名对数据库进行查询，获取用户密码并进行比对
    userPasswordQuerySql = f"select userPassword from user where userName = '{userName}'"
    with pymysql.connect(host=mysqlConfigDict["ServerHost"],user=mysqlConfigDict["MysqlUser"],password=mysqlConfigDict["MysqlPassword"],database=mysqlConfigDict["Datebase"]) as connection:
        with connection.cursor() as cursor:
            if cursor.execute(userPasswordQuerySql) == 0:
                # 如果查不到这个用户，则说明用户名输入错误
                return "user is not exist!"
            userPassword = cursor.fetchone()
            if hashlib.md5(userPasswordInput.encode()).hexdigest() == userPassword[0]:
                # 判断用户输入的密码是否与数据库一致，一致则登陆成功
                print(len(userPassword))
                return "user login success"
            else:
                # 如果不一致则说明用户密码输入错误
                return "password is wrong!"



# 触发邮件发送接口
@userManagement.post("/verifyCodeSend")
def sendEmail():
    "用来给用户输入的邮箱发送验证码"
    # 将配置读取到字典，节省每次读取配置的开销
    configDict = configReader()
    # 生成随机6位数字验证码
    randomCode = random.randint(000000,999999)
    randomCode = f"{randomCode:>06}"    # 确保生成的随机数为六位数字
    # print(randomCode)
    randomCodeMd5 = hashlib.md5(randomCode.encode()).hexdigest()
    # 获取用户输入的邮箱地址
    emailAddress = request.get_json()["emailAddress"]
    # 向用户的邮箱发送6位验证码
        # 验证码邮件的内容
    verifyCodeMailBody = f"From:FlaskProjSystem@126.com\nTo:{emailAddress}\nSubject:VerifyCode from FlaskProjSystem\n\nWelcome!\nYou are registing the FlaskProject system or changing you password,\n\tand your verify Code is {randomCode}"
    # 生成smtp实例并发送邮件验证码
    with smtplib.SMTP_SSL(configDict["stmpServer"]["serverHost"]) as smtpService:
        smtpService.login(configDict["stmpServer"]["serverUser"],configDict["stmpServer"]["userPassword"])
        smtpService.sendmail(configDict["stmpServer"]["serverUser"],emailAddress,verifyCodeMailBody)
    # 将验证码写入redis，设置5分钟过期
    with redis.Redis(host=configDict["redis"]["ServerHost"],password=configDict["redis"]["password"],decode_responses=True) as verifyCodeRedis:
        verifyCodeRedis.setex(emailAddress,300,randomCodeMd5)
    return f"email sending success, randomCode:{randomCode}, randomCodeMd5:{randomCodeMd5}"



@userManagement.post("/register")
def user_register():
    "根据用户输入的邮箱和验证码，判断用户和邮箱是否已存在，邮箱是否有效，从而选择是否创建用户"
    # 将配置读取到字典，节省每次读取配置的开销
    configDict = configReader()
    # 获取用户输入的验证码、邮箱、用户名和密码
    userRegistReqBody = request.get_json()
    userEmail = userRegistReqBody["userEmail"]
    userName = userRegistReqBody["userName"]
    # 优先判断该用户是否已经存在，如果已经存在，则提示用户已经存在，并拒绝创建
    ifUserExistsql = f"select count(*) from user where userName = '{userName}'"
    ifEmailExistsql = f"select count(*) from user where userEmail = '{userEmail}'"
    with pymysql.connect(host=configDict["mysql"]["ServerHost"],user=configDict["mysql"]["MysqlUser"],password=configDict["mysql"]["MysqlPassword"],database=configDict["mysql"]["Datebase"]) as userRegisterMysql:
        with userRegisterMysql.cursor() as userRegisterMysqlCursor:
            if userRegisterMysqlCursor.execute(ifUserExistsql) > 0:
                print(ifUserExistsql)
                print(userRegisterMysqlCursor.execute(ifUserExistsql))
                # 判断数据库中用户是否已经存在
                return "user already exists"
            elif userRegisterMysqlCursor.execute(ifEmailExistsql) > 0:
                # 判断数据库中邮箱是否已经存在
                return "email already exists"
            # 查询redis验证码记录，比较邮箱和验证码是否符合，且验证码是否过期
            with redis.Redis(host=configDict["redis"]["ServerHost"],password=configDict["redis"]["password"],decode_responses=True) as userRegisterRedis:
                # 获取用户输入的验证码
                verifyCodeInputMd5 = hashlib.md5(userRegistReqBody["userVerifyCode"].encode()).hexdigest()
                if userRegisterRedis.get(userEmail) == verifyCodeInputMd5:
                    # 获取用户输入的密码
                    userPassword = hashlib.md5(userRegistReqBody["userPassword"].encode()).hexdigest()
                    # 如果验证码正确，则新建用户并写入数据库，之后进入功能页主页面
                    userCreateSql = f"insert into user(userName,userEmail,userPassword) values ('{userName}','{userEmail}','{userPassword}')"
                    userRegisterMysqlCursor.execute(userCreateSql)
                    userRegisterMysql.commit()
                    return "user created success!"
                else:
                    # 其他情况则不创建用户，并提示该邮箱不存在验证码，请重新生成并输入验证码
                    return "verifyCode is not correct or expired"
                    
@userManagement.route("/")
def test():
    session["123"] = "123"
    return "sessioon accept!"

@userManagement.post("/formDataTest")
def formDataTest():
    print(f"this is formDataTest")
    print(request.form)
    return "formData test access success!"