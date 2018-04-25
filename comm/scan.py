#!/usr/bin/python
#coding:utf-8

import os
import sys
import platform

import function

class scan(object):
	
	# 命令收集、python自带收集、信息处理
	# xxInfo = {
	#  "info" : "[[commad,readme],[result]]"
	# }
	def __init__(self):
		self.commandDir = sys.path[0] + "/config/commandInfo/"
		self.configDir = sys.path[0] + "/config/"
		self.systemInfo = {
			"info" : "",
			"localIp" : "",
		}
		self.userInfo = {
		}
		self.serviceInfo = {
		}
		self.fileInfo = {
		}
		self.getNetworkInfo = {
			"internalIp" : [],
			"survivalIp" : ""
		}

	def getSystemInformation(self):
		print "getSystemInformation..."

		# uname返回的是system, node, release, version, machine, processor的列表
		self.systemInfo['a_info'] = [['python_get','系统名称'],[platform.platform()]]
		try:
			self.systemInfo['b_localIp'] = [['local_ip','本地ip'],function.get_all_ip(platform.system())]
		except:
			pass
		self.systemInfo = self.dealCmdInfo(self.systemInfo, self.commandDir + 'systemInfo.txt')

		return self.systemInfo

	def getUserInformation(self):
		print "getUserInfo..."

		self.userInfo = self.dealCmdInfo(self.userInfo, self.commandDir + 'userInfo.txt')
		#commandInfo = function.open_command_file('./config/commandInfo/userInfo.txt')
		return self.userInfo

	def getServiceInformation(self):
		print "getServiceInfo..."

		self.serviceInfo = self.dealCmdInfo(self.serviceInfo, self.commandDir + 'serviceInfo.txt') 

		#可执行的命令获取-字典式扫描,在软件名后面加上flag以表示是否存在，其中1表示安装，0表示未安装
		content = function.open_file(self.configDir + '/command.txt')
		self.serviceInfo['e_program'] = [['program','常用程序扫描'],[]]
		for line in content:
			command = "which {program} 2>/dev/null".format(program=line)
			result = os.popen(command).read()
			if result.strip():
				self.serviceInfo['e_program'][1].append(line + '1')
			else:
				self.serviceInfo['e_program'][1].append(line + '0')

		#可执行的命令获取-软件安装获取
		if self.serviceInfo['d_soft']:
			content = function.open_file(self.configDir + '/service.txt')
			for line in content:
				self.softDeal(line)
		self.serviceInfo['e_program'][1] = function.list_no_repeat(self.serviceInfo['e_program'][1])

		return self.serviceInfo

	def getFileInformation(self,resultPath):
		print "getFileInformation..."

		self.fileInfo = self.dealCmdInfo(self.fileInfo, self.commandDir + 'fileInfo.txt')

		#敏感服务配置文件扫描-字典式扫描
		content = function.open_file(self.configDir + '/file.txt')
		self.fileInfo['scan'] = [['filescan','敏感配置文件扫描'],[]]
		for line in content:
			command = "ls {filename} 2>/dev/null".format(filename=line)
			result = os.popen(command).read()
			if result.strip():
				self.fileInfo['scan'][1].append(line+'1')
			else:
				self.fileInfo['scan'][1].append(line+'0')

		#敏感服务配置文件扫描-find命令中寻找,在软件名后面加上flag以表示是否存在，其中1表示安装，0表示未安装
		content = function.open_file(self.configDir + '/conffile.txt')
		if self.fileInfo['conf']:
			for line in content:
				for fileline in self.fileInfo['conf']:
					if line in fileline:
						self.fileInfo['scan'][1].append(line+'1')
					else:
						self.fileInfo['scan'][1].append(line+'0')
		#去重复
		self.fileInfo['scan'][1] = function.list_no_repeat(self.fileInfo['scan'][1])

		#敏感文件下载
		for f in self.fileInfo['scan'][1]:
			if f[-1] == '1':
				try:
					command = 'cp {filename} {resultPath}/files/'.format(filename=f[:-1], resultPath=resultPath)
					os.popen(command)
				except Exception,e:
					print e
					pass

		#匿名服务检测
		self.fileInfo['weakpassscan'] = [['weakpassscan','匿名登录'],[]]
		ftpcommand = 'chmod 777 {ftpfile}/ftp.sh; bash {ftpfile}/ftp.sh 2>/dev/null'.format(ftpfile=self.configDir)
		commands = {
			'redis' : 'redis-cli -h 127.0.0.1 info 2>/dev/null',
			'rsync' : 'rsync 127.0.0.1:: 2>/dev/null',
			'ftp' : ftpcommand
		}

		for server in commands:
			result = os.popen(commands[server]).read()
			if result.strip():
				if 'failed' not in result or 'incorrect' not in result or 'refused' not in result:
					self.fileInfo['weakpassscan'][1].append(server+'1')
				else:
					self.fileInfo['weakpassscan'][1].append(server+'0')
			else:
				self.fileInfo['weakpassscan'][1].append(server+'0')

		return self.fileInfo

	#获取本地内网ip，进行内网主机存活扫描
	def getNetworkInfomation(self):
		print "getNetworkInfomation..."
		if not self.systemInfo['localIp']:
			print '请先获取本地ip或者电脑正处于断网状态'
			return 0

		for ip in self.systemInfo['localIp']:
			if function.is_internal_ip(ip):
				self.getNetworkInfo['internalIp'].append(ip)

		if not self.getNetworkInfo['internalIp']:
			print '没有内网地址'
			return 1

		iplist = function.create_subnet(self.getNetworkInfo['internalIp'])

		self.getNetworkInfo['survivalIp'] = function.ping_scan(iplist)

		return self.getNetworkInfo

	#处理命令结果，放入非命令收集的后面
	def dealCmdInfo(self,Info,commandFile,diffCommand={}):
		commandInfo = function.open_command_file(commandFile)
		#系统差异性的命令
		if not diffCommand:
			commandInfo = dict(commandInfo, **diffCommand)
		for key in commandInfo:
			commandResult = os.popen(commandInfo[key][0][0]).read()
			commandInfo[key][1].append(commandResult)
		result = dict(Info, **commandInfo)
		return result

	#对软件处理
	def softDeal(self,line):
		#去服务和命令重复
		if not self.serviceInfo['e_program'][1].count(line+'1') or self.serviceInfo['e_program'][1].count(line+'0'):
			for soft in self.serviceInfo['d_soft'][1]:
				if line in soft:
					self.serviceInfo['e_program'][1].append(line + '1')
					break
				else:
					self.serviceInfo['e_program'][1].append(line + '0')
					break
