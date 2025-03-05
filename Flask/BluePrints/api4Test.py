import random
import datetime

from flask import Blueprint
from flask import request
from flask import jsonify

api4Test = Blueprint("api4Test",__name__, url_prefix="/api4Test")

@api4Test.get("/randomNum")
def get_randomNum():
    "获取一个随机[0,100]的整数"
    print(request.args)
    if len(request.args) == 0:
        return f"{random.randint(0,100)}"
    else:
        maxBorder = int(request.args["max"])
        if maxBorder < 0:
            return "Error! maxBoder is less than 0",400
        return f"{random.randint(0,maxBorder)}"

@api4Test.get("/order/getOrderId")
def orderId_generator():
    return f"Order{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:17]}"