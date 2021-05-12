# Captcha Recognition
## 前言
该项目分为2个部分：
1. 识别验证码
3. 将其改为BurpSuite的插件。
## 验证码
验证码的作用，可以认为是验证用户为人类使用，以防止攻击者爆破等行为。
常见的有图像验证，声音验证，国内常用的滑动验证码以及以谷歌为代表的识别验证码。

本文讨论与研究的为图像验证码。
## 利用 muggle-ocr 识别验证码
测试的验证码为URL如下：
1. 校内借阅系统的验证码: http://121.248.104.172:8080/kaptcha/image

### 设计思路

利用`muggle-ocr`来作为识别验证码的核心, 同时利用`http.server`包构建简单的web应用,客户端发送验证码`url`和`Cookie`的json格式数据,之后由服务器访问验证码地址和识别,最后返回json格式的结果.

这样的好处,可以面对多样化的环境,如方便的获取`https`协议的验证码,以及本地无法安装muggle-ocr的场景.

如发送一下格式的http包:

```http
POST / HTTP/1.1
Host: your_ip:port
Connection: close
Content-Length: 115

{"url":"http://121.248.104.172:8080/kaptcha/image","cookie":"jiagong=2FF2934F68AE4F216ABA5C7113A374DE","method":""}
```

返回结果如下:

![image-20210512195510064](http://img.xzaslxr.xyz/20210512195603.png)



此外,得益于web应用的设计,我们可以将应用布置到公网,再利用nps等内网穿透工具,该应用也就可以对内网的验证码服务进行识别,如下图:

![image-20210512195453481](http://img.xzaslxr.xyz/20210512195617.png)

### 应用测试

1. 校内借阅系统的验证码

![](http://img.xzaslxr.xyz/20210512193522.gif)

## BurpSuite 插件开发

BurpSuite设计上将URL和Cookie发送给web服务,并根据返回结果修改Captcha.

爆破模式选择![image-20210512200204827](http://img.xzaslxr.xyz/20210512200204.png)

第一个参数可为用户名或用户密码,第二个参数选择插件生成,如图

![image-20210512200316732](http://img.xzaslxr.xyz/20210512200316.png)

	### 应用测试

测试链接为:

1. 体质测试成绩查询: http://219.219.62.94:812/ValidPng.aspx

![image-20210512200745959](http://img.xzaslxr.xyz/20210512200745.png)

支持`https`和`http`两种协议.

## 参考链接

[NEW_xp_CAPTCHA/xp_CAPTCHA.py at main · smxiazi/NEW_xp_CAPTCHA (github.com)](https://github.com/smxiazi/NEW_xp_CAPTCHA/blob/main/xp_CAPTCHA.py)

[muggle-ocr - Python Package Health Analysis | Snyk](https://snyk.io/advisor/python/muggle-ocr)

## 环境搭建
```python
python3 -m pip install -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com muggle-ocr
```

* `main.py` 为 识别服务

```python
python3 main.py
```

默认服务地址为`0.0.0.0:9090`,也可以修改

![image-20210512202905891](/Users/fe1w0/Library/Application Support/typora-user-images/image-20210512202905891.png)

* `own_CAPTCHA.py` 为插件

使用前,需要将host 改为 服务地址,如`host  = ('127.0.0.1',9090)`

![image-20210512202359596](http://img.xzaslxr.xyz/20210512202505.png)

## 不足与改进

BurpSuite 插件存在一个问题,当验证码识别失败时,BurpSuite无法自动地根据请求返回页面来判断是否重新发包测试,但我们可以改用脚步来爆破,可以自主地根据返回页面来重新发包.

## 项目代码

[fe1w0/own_captcha (github.com)](https://github.com/fe1w0/own_captcha)

