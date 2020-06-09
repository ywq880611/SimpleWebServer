import sys, os
from http.server import BaseHTTPRequestHandler, HTTPServer

class ServerException(Exception):
    '''服务器内部错误'''
    pass


class RequestHandler(BaseHTTPRequestHandler):
    Page = '''\
            <html>
            <body>
            <table>
            <tr>  <td>Header</td>         <td>Value</td>          </tr>
            <tr>  <td>Date and time</td>  <td>{date_time}</td>    </tr>
            <tr>  <td>Client host</td>    <td>{client_host}</td>  </tr>
            <tr>  <td>Client port</td>    <td>{client_port}</td> </tr>
            <tr>  <td>Command</td>        <td>{command}</td>      </tr>
            <tr>  <td>Path</td>           <td>{path}</td>         </tr>
            </table>
            </body>
            </html>'''

    Error_Page = """\
                <html>
                <body>
                <h1>Error accessing {path}</h1>
                <p>{msg}</p>
                </body>
                </html>
                """
    
    #path = "123"

    def create_page(self):
        values = {
            'date_time'   : self.date_time_string(),
            'client_host' : self.client_address[0],
            'client_port' : self.client_address[1],
            'command'     : self.command,
            'path'        : self.path
        }
        page = self.Page.format(**values)
        return page

    def do_GET(self):
        try:
            # 文件完整路径
            full_path = os.getcwd() + self.path
            # 如果该路径不存在...
            if not os.path.exists(full_path):
                #抛出异常：文件未找到
                raise ServerException("'{0}' not found".format(self.path))
            # 如果该路径是一个文件
            elif os.path.isfile(full_path):
                #调用 handle_file 处理该文件
                self.handle_file(full_path)
            # 如果该路径不是一个文件
            else:
                #抛出异常：该路径为不知名对象
                raise ServerException("Unknown object '{0}'".format(self.path))
        # 处理异常
        except Exception as msg:
            self.handle_error(msg)

    def handle_file(self, full_path):
        try:
            with open(full_path, 'rb') as reader:
                content = reader.read()
            self.send_content(content)
        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(self.path, msg)
            self.handle_error(msg)

    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path, msg=msg)
        self.send_content(content.encode('utf-8'), 404)



    def send_content(self, page, status = 200):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(page)

if __name__=='__main__':
    serverAddress = ('', 8080)
    server = HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()
