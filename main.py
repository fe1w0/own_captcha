import os
import muggle_ocr
import time
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from http import HTTPStatus
import json

def write_file(file_name, content):
    with open(file_name, 'wb') as file:
        file.write(content)
        file.close()


def download_captcha(url, cookie):
    """
    下载验证码，并保存在captcha文件下,文件名为时间戳.png
    :param url: 验证码链接
    :param cookie: 用户Cookie
    :return file_name: 验证码本地存储相对地址
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0',
        'Cookie': cookie,
    }
    res = requests.get(
        url=url,
        headers=headers,
        verify=False  # 取消SSL验证
    )
    file_name = 'captcha/' + str(int(time.time()*1000)) + '.png'
    write_file(file_name=file_name, content=res.content)
    return file_name


def get_captcha(url, cookie):
    """
    直接将图片放入上下文
    :rtype: str
    :param url: 验证码链接
    :param cookie : 用户Cookie
    :return image_captcha: 验证码图片
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0',
        'Cookie': cookie,
    }
    res = requests.get(
        url=url,
        headers=headers,
        verify=False  # 取消SSL验证
    )
    image_captcha = res.content  # 获得验证码图片
    return image_captcha


def recognize(image_bytes='', file_name=''):
    """
    识别验证码
    :param image_bytes:
    :param file_name:
    :return:captcha_code 识别的验证码
    """
    local_sdk = muggle_ocr.SDK(model_type=muggle_ocr.ModelType.Captcha)  # muggle_ocr SDK 设置为验证码模式
    if file_name != '':
        with open(file_name, 'rb') as file:
            image_bytes = file.read()
            file.close()
        # os.unlink(file_name)  # 删除验证码
    print("file_name: " + file_name + "\n")
    captcha_code = local_sdk.predict(image_bytes=image_bytes)
    return captcha_code


def captcha_recognize(url, cookie, method=''):
    """
    根据 method 来决定验证码是否存储
    :param url:
    :param cookie:
    :param method:
    :return:
    """
    if method == 'download':
        file_name = download_captcha(url=url, cookie=cookie)
        captcha_code = recognize(file_name=file_name)
        return captcha_code
    # method != 'download' 的 情况
    image_captcha = get_captcha(url=url, cookie=cookie)
    captcha_code = recognize(image_bytes=image_captcha)
    print("captcha_code: "+captcha_code+"\n")
    return captcha_code


class _RequestHandler(BaseHTTPRequestHandler):
    # Borrowing from https://gist.github.com/nitaku/10d0662536f37a087e1b
    def _set_headers(self):
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write(json.dumps({'hello': 'world'}).encode('utf-8'))

    def do_POST(self):
        length = int(self.headers.get('content-length'))
        message = json.loads(self.rfile.read(length))
        captcha_code = captcha_recognize(message['url'], message['cookie'], message['method'])
        self._set_headers()
        self.wfile.write(json.dumps({'code': captcha_code}).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST')
        self.send_header('Access-Control-Allow-Headers', 'content-type')
        self.end_headers()


def run_server():
    server_address = ('0.0.0.0', 9090)
    httpd = HTTPServer(server_address, _RequestHandler)
    print('serving at http://%s:%d' % server_address)
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()
