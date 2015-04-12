#encoding:utf-8
"""
功能:
1.模拟登陆登出北邮网络自助服务中心http://gwself.bupt.edu.cn;
2.获取个人信息,余额,本月使用流量,本月使用时长,费用;
3.获取指定时间内相信上网信息;
4.获取已登录设备ip地址,并可以对其进行下线操作;

说明:
1.recognise.py是验证码图片识别函数,利用ORC进行识别,须事先安装好tesseract, 并使用python三方库pytesseract;
2.网络请求使用库requests, html解析使用库lxml
"""

import hashlib
import requests
import re
import random
from datetime import datetime
from lxml import etree
from recognise import recognise

HOST = "http://gwself.bupt.edu.cn"

login_url = HOST + "/nav_login"
logout_url = HOST + '/LogoutAction.action'
code_img_url = HOST + "/RandomCodeAction.action?randomNum=%s" % random.random()
post_url = HOST + "/LoginAction.action"
profile_url = HOST + "/nav_getUserInfo"
online_info_url = HOST + "/nav_offLine"
net_info_url = HOST + '/UserLoginLogAction.action'


class BuptGwSelf:

    def __init__(self, session=None):
        self.session = session if session else requests.session()
        self.session.headers.update({
            'user-agent': 'Mozilla/5.0',
            'host': 'gwself.bupt.edu.cn',
            'origin': 'http://gwself.bupt.edu.cn',
        })
        self.is_login = True if session else False
        self.online_devices = []

    def login(self, username, password):
        """
        模拟账号登陆,获取登陆cookie,得到属性session供之后的方法调用;
        返回(code, msg) code=0正确, code=1发生错误
        """
        try:
            #get random check code
            r = self.session.get(login_url)
            checkcode = re.findall('var checkcode="(\d+)"', r.text)[0].encode('utf-8')

            #get img code number
            code_img_data = self.session.get(code_img_url, stream=True).raw.read()
            code = recognise(code_img_data).strip()

            data = {
                'account':username,
                'password':hashlib.md5(password).hexdigest(),
                'code':code,
                'checkcode':checkcode,
                'Submit': '登 陆'
            }
            r = self.session.post(post_url, data=data)
            error_divs = etree.HTML(r.text).xpath('//div[@id="fielderror2"]')
            if not error_divs:
                self.is_login = True
                return (0, 'success')
            error_msg = etree.tostring(error_divs[0], method='text', encoding='utf-8')
            error_msg = re.findall(r"&nbsp;([\s\S]*)</div>", error_msg)[0]
            return (1, error_msg)
        except:
            return False

    def logout(self):
        assert self.is_login
        self.session.get(logout_url)
        self.is_login = False

    def myprofile(self):
        """
        获取个人信息
        返回字典,键值为balance(余额), time(使用时长), flow(使用流量), cost(花费)
        """
        assert self.is_login
        html_text = self.session.get(profile_url).content
        trs = etree.HTML(html_text).xpath('//div[@class="tabcontent"]/table/tr')
        balance = trs[0].xpath('//font/text()')[0].strip().encode('utf-8')
        time = trs[1].xpath('td[2]/text()')[0].strip().encode('utf-8')
        flow = trs[2].xpath('td[2]/text()')[0].strip().encode('utf-8')
        cost = trs[3].xpath('td[2]/text()')[0].strip().encode('utf-8')
        return {'balance':balance, 'time':time, 'flow':flow, 'cost':cost}

    def get_online_info(self):
        """
        获取账号在线设备信息,
        返回list, 每个item格式(ipv4, ipv6, mac, 请求下线的链接)
        """
        assert self.is_login
        r = self.session.get(online_info_url)
        trs = etree.HTML(r.content).xpath('//tbody/tr')
        online_ips = []
        for tr in trs:
            ipv4 = tr[0].text.strip()
            ipv6 = tr[1].text.strip()
            mac = tr[2].text.strip()
            code = tr[3].text.strip()
            toofline_url = HOST + "/tooffline?t=%s&fldsessionid=%s" % (random.random(), code)
            online_ips.append((ipv4, ipv6, mac, toofline_url))
        self.online_devices = online_ips
        return online_ips

    def to_offline(self, ipaddr):
        """
        将ip地址为ipaddr的终端下线
        """
        devices = filter(lambda x:x[0]==ipaddr, self.online_devices)
        if (not devices) or len(devices)>1:
            return False
        toofline_url = devices[0][-1]
        if self.session.get(toofline_url).status_code == '200':
            return True

    def get_log(self, begin_date, end_date):
        """
        获取账号登陆情况,直接从http://gwself.bupt.edu.cn/UserLoginLogAction.action爬取,
        args: 格式如'2015-01-01'
        返回list, list中每一项格式是
        (上线时间	,下线时间	,使用时长(分钟),使用流量(MB),计费金额(元),上行流量(MB)	,下行流量(MB)	,登录所在IP)
        """
        assert self.is_login
        data = {
            'startDate':self._get_str_datetime(begin_date),
            'endDate':self._get_str_datetime(end_date),
            'type':4
        }
        r = self.session.post(net_info_url, data)
        trs = etree.HTML(r.content).xpath('//tbody/tr')
        logs = []
        for tr in trs[::-1]:
            (login_time, logout_time, last_time, flow, cost, uflow, dflow, ip) = [tr[i].text.strip() for i in range(8)]
            logs.append((login_time, logout_time, last_time, flow, cost, uflow, dflow, ip))
        return logs

    def _get_str_datetime(self, date):
        """
        获取字符串形式datetime, '2015-01-01'
        """
        if isinstance(date, datetime):
            return date.strftime('%Y-%m-%d')
        return date


if __name__ == '__main__':
    from pprint import pprint as pp
    username = ''   #自己用户名
    password = ''   #自己密码
    bgs = BuptGwSelf()
    print 'login...'
    bgs.login(username, password)
    print 'my profile:'
    pp(bgs.myprofile())
    print 'online devices:'
    pp(bgs.get_online_info())
    print 'logs:'
    pp(bgs.get_log('2015-04-01', '2015-04-19'))
    bgs.logout()
