#!/usr/bin/python
#coding:utf-8

import requests
import argparse
import re, sys, os, os.path
import base64
from time import sleep

def login(usr, pwd):
	data = {'DDDDD' : usr, 'upass' : pwd, '0MKKey': ''}
	r = requests.post('http://gw.bupt.edu.cn/', data)
	result = re.findall(r"You have successfully logged into our system" ,r.text)
	if result:
		print "Login successfully!"
	else:
		msg = re.findall(r"Msg=(\d{1,2})", r.text)[0]
		msg = int(msg)
		if msg == 1:
			pass;
		elif msg == 2:
			xip = re.findall(r"xip='(\d+.\d+.\d+.\d+)", r.text)[0]
			y_or_n = raw_input("now this account is used at ip: %s, do u want to disconnect it and try again?(y/n):" % xip)
			if y_or_n in ['y', 'Y', 'yes', 'YES', 'Yes']:
				data = {'DDDDD' : usr, 'upass' : pwd, 'passplace' : '', 'AMKKey' : ''}
				requests.post('http://gw.bupt.edu.cn/a11.htm', data)


def logout(usr, pwd):
	r = requests.get('http://gw.bupt.edu.cn/F.html')
	msg = re.findall(r"Msg=(\d{1,2})", r.text)[0]
	msg = int(msg)
	#print account info
	if msg == 14:
		print "Logout successfully!"
		print "***Used time: " + re.findall(r"time='(\d+)", r.text)[0] + "Min"

		flow = re.findall(r"flow='(\d+)", r.text)[0]; flow=int(flow)
		flow0=flow%1024;flow1=flow-flow0;flow0=flow0*1000;flow0=flow0-flow0%1024;
		flow3='.'
		if flow0/1024<10:
			flow3='.00'
		elif flow0/1024<100:
			flow3='.0'
		print "***Used internet traffic: %s%s%s MBytes" % (flow1/1024,flow3,flow0/1024)

		fee = re.findall(r"fee='(\d+)", r.text)[0]; fee = int(fee);
		fee1=fee-fee%100
		print "***Balance: "+"RMB"+str(fee1/10000)
	elif msg == 1:
		print "Logout error!"


def main(username, password):
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--quit', action="store_false", help="logout")
    args = parser.parse_args()
    try:
        if args.quit:
            login(username, real_password)
        else:
            logout(username, real_password)
    except:
        print("there is some errors, please check the code!")
        sys.exit(1)


if __name__ == '__main__':
    username = ''
    base64_pwd = '' #"username-password" base64 encode
    real_password = base64.b64decode(base64_pwd).split("-")[-1]
    main(username, real_password)
