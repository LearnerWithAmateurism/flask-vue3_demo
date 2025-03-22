import random
import hashlib


from flask import (
    Blueprint,
    request,
    session,
    make_response
    )
# from flask import url_for

# from projTool import configReader
from projTool import redis_pool_conn, mysql_pool_conn, send_email, jwt_factory

userManagement = Blueprint("userManagement",__name__,url_prefix="/user")

# 用户登陆接口
@userManagement.get("/login")
def user_login():
    "获取用户名和密码，校验是否允许登陆，如果允许登陆，则设置cookies，用于之后的登陆状态维护"
    # 将配置读取到字典，节省每次读取配置的开销
    # mysqlConfigDict = configReader()["mysql"]
    # 获取用户输入的用户名和密码，并进行校验
    userName = request.get_json()["userName"]
    userPasswordInput = request.get_json()["userPassword"]
    # 通过用户输入的用户名对数据库进行查询，获取用户密码并进行比对
    userPasswordQuerySql = f"select userPassword from user where userName = '{userName}'"
    with mysql_pool_conn as conn:
        if conn.cursor.execute(userPasswordQuerySql) != 1:
            if len(conn.cursor.fetchall()) > 1:
                return {"result":"fail","description":"This user is abnorma! Please report it to the administrator!"},200
            return {"result":"fail","description":"User not found!"},200
        userPassword = conn.cursor.fetchone()
        if hashlib.md5(userPasswordInput.encode()).hexdigest() == userPassword[0]:
            # 密码正确，生成token，发送给客户端cookies中
            conn.cursor.execute(f"select userName,userEmail from user where userName = {userName}")
            user_info = conn.cursor.fetchone()
            response = make_response({"result":"success","description":"User login success!"},200)
            response.set_cookie("user_token",jwt_factory(*user_info),max_age=3600,httponly=True)
            return response
        else:
            # 如果不一致则说明用户密码输入错误
            return {"result":"fail","description":"User password is wrong!"},200
        
    # with pymysql.connect(host=mysqlConfigDict["ServerHost"],user=mysqlConfigDict["MysqlUser"],password=mysqlConfigDict["MysqlPassword"],database=mysqlConfigDict["Datebase"]) as connection:
    #     with connection.cursor() as cursor:
    #         if cursor.execute(userPasswordQuerySql) == 0:
    #             # 如果查不到这个用户，则说明用户名输入错误
    #             return "user is not exist!"
    #         userPassword = cursor.fetchone()
    #         if hashlib.md5(userPasswordInput.encode()).hexdigest() == userPassword[0]:
    #             # 判断用户输入的密码是否与数据库一致，一致则登陆成功
    #             print(len(userPassword))
    #             return "user login success"
    #         else:
    #             # 如果不一致则说明用户密码输入错误
    #             return "password is wrong!"


# 验证码发送接口
@userManagement.post("/verifyCodeSend")
def send_vericode_email():
    "用来给用户输入的邮箱发送验证码"
    # 将配置读取到字典，节省每次读取配置的开销
    # configDict = configReader()
    # 生成随机6位数字验证码
    # 获取用户输入的邮箱地址
    emailAddress = request.get_json()["userEmail"]
    # 获得redis连接，并判断这个邮箱一分钟内是否发送过验证码，如果发送过则拒绝发送
    redis_conn = redis_pool_conn()
    if redis_conn.ttl(emailAddress) >= 240:
        return {"result":"fail","description":"This vertification code in this email was sent in 1 minute! Please wait a moment and try again!"},200
    randomCode = random.randint(000000,999999)
    randomCode = f"{randomCode:>06}"    # 确保生成的随机数为六位数字
    randomCodeMd5 = hashlib.md5(randomCode.encode()).hexdigest()
    # 向用户的邮箱发送6位验证码
        # 验证码邮件的内容
    verifyCodeMailBody = f"From:FlaskProjSystem@126.com\nTo:{emailAddress}\nSubject:VerifyCode from FlaskProjSystem\n\nWelcome!\nYou are registing the FlaskProject system or changing you password,\n\tand your verify Code is {randomCode}"
    # 生成smtp实例并发送邮件验证码
    send_email(to_addrs=emailAddress,content=verifyCodeMailBody)
    # with smtplib.SMTP_SSL(configDict["stmpServer"]["serverHost"]) as smtpService:
    #     smtpService.login(configDict["stmpServer"]["serverUser"],configDict["stmpServer"]["userPassword"])
    #     smtpService.sendmail(configDict["stmpServer"]["serverUser"],emailAddress,verifyCodeMailBody)
    # redis存储验证码与验证码写入时间，设置5分钟过期
    redis_conn.setex(emailAddress,300,f"{randomCodeMd5}")
    # with redis.Redis(host=configDict["redis"]["ServerHost"],password=configDict["redis"]["password"],decode_responses=True) as verifyCodeRedis:
    #     verifyCodeRedis.setex(emailAddress,300,randomCodeMd5)
    return {"result":"success","description":f"email sending success, randomCode:{randomCode}, randomCodeMd5:{randomCodeMd5}"},200


# 用户注册接口
@userManagement.post("/register")
def user_register():
    "根据用户输入的邮箱和验证码，判断用户和邮箱是否已存在，邮箱是否有效，从而选择是否创建用户；如果创建用户，则自动处于登录状态"
    # 将配置读取到字典，节省每次读取配置的开销
    # configDict = configReader()
    # 获取用户输入的验证码、邮箱、用户名和密码
    userRegistReqBody = request.get_json()
    userEmail = userRegistReqBody["userEmail"]
    userName = userRegistReqBody["userName"]
    verification_code_md5 = hashlib.md5(userRegistReqBody["userVerifyCode"].encode()).hexdigest()
    password_md5 = hashlib.md5(userRegistReqBody["userPassword"].encode()).hexdigest()
    # 查询redis验证码记录，比较邮箱和验证码是否符合，且验证码是否过期
    if redis_pool_conn().get(userEmail) != verification_code_md5:
        return {"result":"fail","description":"Verification code could not be verified! Please check your email address and verification code, if they are correct, please try again!"},200
    with mysql_pool_conn as conn:
        # 判断输入的用户和邮箱是否已经存在的sql查询语句
        ifUserExistsql = f"select count(*) from user where userName = '{userName}'"
        ifEmailExistsql = f"select count(*) from user where userEmail = '{userEmail}'"
        if conn.cursor.execute(ifUserExistsql) > 0:
            # 判断数据库中用户是否已经存在
            return {"result":"fail","description":"This user exists already!"},200
        elif conn.cursor.execute(ifEmailExistsql) > 0:
            # 判断数据库中邮箱是否已经存在
            return {"result":"fail","description":"This email exists already!"},200
        userCreateSql = f"insert into user(userName,userEmail,userPassword) values ('{userName}','{userEmail}','{password_md5}')"
        conn.cursor.execute(userCreateSql)
        conn.conn.commit()
        resp = make_response({"result":"success","description":"User created successfully!"},200)
        resp.set_cookie("user_token",jwt_factory(userName,userEmail),max_age=3600,httponly=True)
    return resp

    # with pymysql.connect(host=configDict["mysql"]["ServerHost"],user=configDict["mysql"]["MysqlUser"],password=configDict["mysql"]["MysqlPassword"],database=configDict["mysql"]["Datebase"]) as userRegisterMysql:
    #     with userRegisterMysql.cursor() as userRegisterMysqlCursor:
    #         if userRegisterMysqlCursor.execute(ifUserExistsql) > 0:
    #             print(ifUserExistsql)
    #             print(userRegisterMysqlCursor.execute(ifUserExistsql))
    #             # 判断数据库中用户是否已经存在
    #             return "user already exists"
    #         elif userRegisterMysqlCursor.execute(ifEmailExistsql) > 0:
    #             # 判断数据库中邮箱是否已经存在
    #             return "email already exists"
            # 查询redis验证码记录，比较邮箱和验证码是否符合，且验证码是否过期
            # with redis.Redis(host=configDict["redis"]["ServerHost"],password=configDict["redis"]["password"],decode_responses=True) as userRegisterRedis:
            #     # 获取用户输入的验证码
            #     verifyCodeInputMd5 = hashlib.md5(userRegistReqBody["userVerifyCode"].encode()).hexdigest()
            #     if userRegisterRedis.get(userEmail) == verifyCodeInputMd5:
            #         # 获取用户输入的密码
            #         userPassword = hashlib.md5(userRegistReqBody["userPassword"].encode()).hexdigest()
            #         # 如果验证码正确，则新建用户并写入数据库，之后进入功能页主页面
            #         userCreateSql = f"insert into user(userName,userEmail,userPassword) values ('{userName}','{userEmail}','{userPassword}')"
            #         userRegisterMysqlCursor.execute(userCreateSql)
            #         userRegisterMysql.commit()
            #         return "user created success!"
            #     else:
            #         # 其他情况则不创建用户，并提示该邮箱不存在验证码，请重新生成并输入验证码
            #         return "verifyCode is not correct or expired"


# 更改用户密码接口
@userManagement.put("/changePassword")
def change_password():
    "通过注册邮箱以及接收的验证码更改用户的历史密码,更改成功后退出登录"
    # 获取用户输入的邮箱
    user_email_input = request.get_json()["userEmail"]
    vericode_inpu_md5 = hashlib.md5(request.get_json()["userVerifyCode"].encode()).hexdigest()
    password_inpu_md5 = hashlib.md5(request.get_json()["userNewPassword"].encode()).hexdigest()
    if redis_pool_conn().get(user_email_input) != vericode_inpu_md5:
        return {"result":"fail","description":"Your verification code is not correct or expired, please try again!"}
    with mysql_pool_conn as conn:
        # 判断输入的邮箱是否已经存在的sql查询语句
        if_email_exist = f"select count(1) from user where userEmail = '{user_email_input}'"
        if conn.cursor.execute(if_email_exist) != 1:
            return {"result":"fail","description":"Please check your email and try again, if this problem persists, please contact the administrator!"},200
        # 更改数据库中用户的密码
        password_create_sql = f"update user set userPassword = '{password_inpu_md5}' where userEmail = '{user_email_input}'"
        conn.cursor.execute(password_create_sql)
        conn.commit()
        # 用户登录状态退出
        resp = make_response({"result":"success","description":"Your password has been changed successfully!"},200)
        resp.delete_cookie("user_token",httponly=True)
        return resp


# 用户退出登录状态
@userManagement.delete("/logout")
def user_logout():
    "用户退出登录状态"
    resp = make_response({"result":"success","description":"Logout sucess!"},200)
    resp.delete_cookie("user_token",httponly=True)
    return resp
    




@userManagement.route("/")
def test():
    session["123"] = "123"
    return "sessioon accept!"

@userManagement.post("/formDataTest")
def formDataTest():
    print(f"this is formDataTest")
    print(request.form)
    return "formData test access success!"