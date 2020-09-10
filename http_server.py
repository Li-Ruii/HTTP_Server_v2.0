"""
    http_server 2.0
    * IO并发处理
    * 基本的request解析
    * 使用类封装
"""
from socket import *
from select import select

# 将具体的http_server功能封装


class HTTP_Server:
    def __init__(self, addr, dir):
        # 添加属性
        self.server_address = addr
        self.static_dir = dir
        self.rlist = []
        self.wlist = []
        self.xlist = []
        self.create_socket()
        self.bind()

    def create_socket(self):
        self.sockfd = socket()
        self.sockfd.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    def bind(self):
        self.sockfd.bind(self.server_address)
        self.ip = self.server_address[0]
        self.port = self.server_address[1]

    # 启动服务
    def serve_forever(self):
        self.sockfd.listen(5)
        print('Listening to the PORT: %d' % self.port)
        self.rlist.append(self.sockfd)
        while True:
            rs, ws, xs = select(self.rlist, self.wlist, self.xlist)  # 循环监听
            for r in rs:
                if r is self.sockfd:
                    c, addr = r.accept()
                    print('Connected from:', addr)
                    self.rlist.append(c)
                else:
                    # 处理浏览器请求
                    self.handle(r)

    # 处理客户端请求
    def handle(self, connfd):
        # 接收http请求
        request = connfd.recv(4096)
        # 防止浏览器断开
        if not request:
            connfd.close()
            self.rlist.remove(connfd)
            return
        # 请求解析
        request_line = request.splitlines()[0]
        info = request_line.decode().split(' ')[1]
        print(connfd.getpeername(), ':', info)
        # info 分为访问网页和其他
        if info == '/' or info[-5:] == '.html':
            self.get_html(connfd, info)
        else:
            self.get_data(connfd, info)
        self.rlist.remove(connfd)
        connfd.close()

    # 处理网页
    def get_html(self, connfd, info):
        if info == '/':
            # 网页文件
            filename = self.static_dir + '/index.html'
        else:
            filename = self.static_dir + info
        try:
            fd = open(filename, 'r')
        except Exception:
            # 没有网页
            responseHeaders = 'HTTP/1.1 404 Not Found\r\n'
            responseHeaders += '\r\n'
            responseBody = '<h1>Sorry, Not Found the page</h1>'
        else:
            responseHeaders = 'HTTP/1.1 200 OK\r\n'
            responseHeaders += '\r\n'
            responseBody = fd.read()
        finally:
            response = responseHeaders + responseBody
            connfd.send(response.encode())

    def get_data(self, connfd, info):
        responseHeaders = 'HTTP/1.1 200 OK\r\n'
        responseHeaders += '\r\n'
        responseBody = '<h1>Waiting HTTPServer 3.0</h1>'
        response = responseHeaders + responseBody
        connfd.send(response.encode())
    pass


# 如何使用HTTPServer类
# 服务器的地址和网页内容不能由设计者决定
if __name__ == '__main__':
    server_addr = ('0.0.0.0', 8888)  # 服务器地址
    static_dir = './static'  # 网页存放位置

    httpd = HTTP_Server(server_addr, static_dir)  # 生成实例对象
    httpd.serve_forever()  # 启动服务
