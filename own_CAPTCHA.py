#!/usr/bin/env python
#coding:utf-8
from burp import IBurpExtender
from burp import IIntruderPayloadGeneratorFactory
from burp import IIntruderPayloadGenerator
import base64
import json
import re
import urllib2
import ssl

host = ('1.116.20.49', 9090)

class BurpExtender(IBurpExtender, IIntruderPayloadGeneratorFactory):
    def registerExtenderCallbacks(self, callbacks):
        #注册payload生成器
        callbacks.registerIntruderPayloadGeneratorFactory(self)
        #插件里面显示的名字
        callbacks.setExtensionName("own_CAPTCHA")
        print 'own_CAPTCHA  中文名:验证码识别\n用法：\n在head头部添加url_captcha:验证码的URL\n\n如：\n\nPOST /login HTTP/1.1\nHost: www.baidu.com\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0\nAccept: text/plain, */*; q=0.01\nAccept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2\nContent-Type: application/x-www-form-urlencoded; charset=UTF-8\nX-Requested-With: XMLHttpRequest\nurl_captcha:http://www.baidu.com/get-validate-code\nContent-Length: 84\nConnection: close\nCookie: JSESSIONID=24D59677C5EDF0ED7AFAB8566DC366F0\n\nusername=admin&password=admin&vcode=8888\n\n'

    def getGeneratorName(self):
        return "own_CAPTCHA"

    def createNewInstance(self, attack):
        return own_CAPTCHA(attack)

class own_CAPTCHA(IIntruderPayloadGenerator):
    def __init__(self, attack):
        tem = "".join(chr(abs(x)) for x in attack.getRequestTemplate()) #request内容
        user_cookie = re.findall("Cookie: (.+?)\r\n", tem)[0] #获取cookie
        url_captcha = re.findall("url_captcha:(.+?)\r\n", tem)[0]
        print 'url_captcha: ' + url_captcha + '\n'
        print 'user_cookie:' + user_cookie+'\n'
        self.url_captcha = url_captcha
        self.user_cookie = user_cookie
        self.max = 1 #payload最大使用次数
        self.num = 0 #标记payload的使用次数
        self.attack = attack

    def hasMorePayloads(self):
        #如果payload使用到了最大次数reset就清0
        if self.num == self.max:
            return False  # 当达到最大次数的时候就调用reset
        else:
            return True

    def getNextPayload(self, payload):  # 这个函数请看下文解释
        post_data = {"url":self.url_captcha,"cookie":self.user_cookie,"method":''}
        post_data = json.dumps(post_data)
        print('post_data: ' + post_data + '\n')            
        request = urllib2.Request('http://%s:%s/'%host, post_data)
        response = urllib2.urlopen(request).read()
        code = json.loads(response)['code']
        print('code: '+ code)
        return code

    def reset(self):
        self.num = 0  # 清零
        return