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

def repeat(n):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(n):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def greet(name):
    print(f"Hello, {name}!")

greet("Alice")