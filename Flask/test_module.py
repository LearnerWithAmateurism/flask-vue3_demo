# # 假设现在有一个计算加法的函数
# def add_caculation(a,b): #原有的函数C
# 	return a+b
	
# # 声明一个装饰器，用来在该函数执行时打印一下计算开始的提示
# def decorator(functionName): #定义的函数A
# 	def newFunction(*args,**kwargs): #定义的函数B
# 		print("the caculation is about to start!")
# 		result = functionName(*args,**kwargs) #在函数B中引用原有的函数C
# 		return result #将函数C的结果作为函数B的返回
# 	return newFunction #将定义的函数B作为函数A的返回

# @decorator
# def add_caculation_2(a,b):
# 	return a+b

# print(add_caculation_2(1,2))

# def repeat(n):
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             for _ in range(n):
#                 result = func(*args, **kwargs)
#             return result
#         return wrapper
#     return decorator

# @repeat(3)
# def greet(name):
#     print(f"Hello, {name}!")

# greet("Alice")
# -----------------------------------------------------------------------

# str = "你好"
# bStr = str.encode()
# print(bStr)
# bStr.decode()

# -----------------------------------------------------------------------
# import hashlib
# md5_hash_object = hashlib.new("md5")
# md5_hash_object.update(b"123456")
# print(md5_hash_object.digest_size)
# print(md5_hash_object.digest())
# print(md5_hash_object.hexdigest())
# print(hashlib.algorithms_available)

# 0xe10n0xdc9I0xbaY0xab0xbeV0xe0W0xf20x0f0x88

# -----------------------------------------------------------------------

# import random
# var = random.choices([1,2,3,4,5,6,7,8,9,0],k=6)
# print(var)

# for i in range(9):
#     print(i)
# print(random.choices(range(9),k=6))
# randomNumber = random.randint(000000,999999)
# print(f"{randomNumber:>06}")
# --------------------------------------------------------------------------

# from pymysql import connect

# connection = connect(host="185.239.86.98",user="flask_proj",password="m4nW9Db3mn",database="flask_Prac")
# print("connect success")
# connection.close()

# --------------------------------------------------------------------------

# import smtplib
# from email import message
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart

# msg = MIMEMultipart()
# msg['From'] = "ie_vs@126.com"
# msg['To'] = "bzm519xr@qabq.com"
# msg['Subject'] = 'Test Email'
# msg['Content-Type'] = 'multipart/alternative; boundary=\"----=_Part_21782_186307006.1730624577940\"'
# msg['X-Priority'] = '3'
# msg['X-Coremail-Locale'] = 'zh_CN'
# msg['X-Mailer'] = 'Coremail Webmail Server Version XT5.0.14 build 20240801(9da12a7b) Copyright (c) 2002-2024 www.mailtech.cn 126com'

# body = 'Hello'
# msg.attach(MIMEText(body, 'plain'))

# messageInstance = message.EmailMessage()
# print(messageInstance.as_string())

# message2send = f"""
# From:jie_vs@126.com
# To:bzm519xr@qabq.com
# Subject:Hello\n\n

# hello,this is the body part
# """

# message2send = f"From: jie_vs@126.com\n" \
#       f"To: bzm519xr@qabq.com\n" \
#       f"Subject: Hello\n" \
#       f"\n" \
#       f"hello,this is the body part"

# print(message2send)
# smtplibInstance = smtplib.SMTP_SSL("smtp.126.com")
# with smtplibInstance:
#     smtplibInstance.login("jie_vs@126.com","ZUZKQTRQZAXZOIIL")
#     smtplibInstance.sendmail("jie_vs@126.com","bzm519xr@qabq.com",msg=message2send)

# -----------------------------------------------------------------------------

# import redis
# redisInstance = redis.Redis(host="185.239.86.98",decode_responses=True,password="m4nW9Db3mn")
# with redisInstance:
#     print(redisInstance.ping())
#     print(hash("324553"))

# --------------------------------------------------------------------------

# from projTool import configReader
# print(configReader("redis"))
# import json
# import pathlib
# print(pathlib.Path(__file__).parent.absolute())
# with open("config.json","r") as file :
#     print(json.load(file))

# --------------------------------------------------------------------------

import asyncio
import time

async def main():
    print("hello,it's a async test program")
    await asyncio.sleep(1)
    print("hello again")

async def mainloop():
    timestart = time.time()
    tasks = [asyncio.create_task(main()) for i in range(10)]
    # [await i for i in tasks]
    await asyncio.gather(*tasks)
    print(tasks)
    print(*tasks)
    # for i in range(10):
    #     await asyncio.create_task(main())
    print(f"time spent here is {time.time() - timestart} seconds")

coroutine = main()
print(coroutine)

asyncio.run(mainloop())

