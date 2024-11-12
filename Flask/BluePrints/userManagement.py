import random
import hashlib
import smtplib

import redis
from flask import Blueprint
from flask import request

from projTool import configReader

userManagement = Blueprint("userManagement",__name__,url_prefix="/user")

# 用户登陆注册页
@userManagement.get("/userLogin")
def user_login():
    return "user login"



# 触发邮件发送接口
@userManagement.post("/verifyCodeSend")
def sendEmail():
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
    # 获取用户输入的验证码和邮箱
    userVerifyCode = request.get_json()["userVerifyCode"]
    userEmail = request.get_json()["userEmail"]
    # 对用户输入的验证码进行md5加密
    userVerifyCodeMd5 = hashlib.md5(userVerifyCode.encode()).hexdigest()
    # 查询redis验证码记录，比较邮箱和验证码是否符合，且验证码是否过期