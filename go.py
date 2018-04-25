#!/usr/bin/python
#coding:utf-8

'''
文件下载
检测无密码

	linux下的信息收集
	1、系统信息收集
	2、用户信息收集
	3、程序服务收集
	4、敏感文件
	5、可使用程序
	6、交互通信ip
	7、提权帮助

'''

import os
import sys
import time
from comm.scan import * 
from comm.outprint import create_view

begin = scan()

def main():
	nowtime = str(time.time())
	rootPath = sys.path[0]
	resultPath = rootPath + '/result/' + nowtime

	#创建获取放入结果目录
	try:
		os.makedirs(resultPath + '/files/')
	except Exception,e:
		print e
		pass

	systeminfo = begin.getSystemInformation()
	userinfo = begin.getUserInformation()
	serviceinfo = begin.getServiceInformation()
	fileinfo = begin.getFileInformation(resultPath)
	# networkinfo = begin.getNetworkInfomation()

	result = {
		'system' : systeminfo,
		'user' : userinfo,
		'service' : serviceinfo,
		'file' : fileinfo,
		# 'network' : networkinfo
	}
	print result

	html_content = create_view(result)

	# 结果页面生成
	filepath = resultPath + "/result.html"

	try:
		file_object = open(filepath, 'w')
		file_object.writelines(html_content)
		file_object.close()
	except Exception, e:
		return "error"
	finally:
		print '-' * 50
		print "* Report is generated : {filepath}".format(filepath=filepath)
		print '-' * 50

	return 0

if __name__ == '__main__':
	main()
