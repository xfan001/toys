功能:
1.模拟登陆登出北邮网络自助服务中心http://gwself.bupt.edu.cn;
2.获取个人信息,余额,本月使用流量,本月使用时长,费用;
3.获取指定时间内相信上网信息;
4.获取已登录设备ip地址,并可以对其进行下线操作;

说明:
1.recognise.py是验证码图片识别函数,利用ORC进行识别,须事先安装好tesseract, 并使用python三方库pytesseract;
2.网络请求使用库requests, html解析使用库lxml

