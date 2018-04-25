#!/usr/bin/python
#coding:utf-8

import re
import uuid
import subprocess
import socket
import fcntl
import struct

#获取本机所有ip
def get_all_ip(platform):
	ipstr = '([0-9]{1,3}\.){3}[0-9]{1,3}'
	try:
		ipconfig_process = subprocess.Popen("ifconfig", stdout=subprocess.PIPE)
		output = ipconfig_process.stdout.read()
		ip_pattern = re.compile('(inet %s)' % ipstr)
		if platform == "Linux":
			ip_pattern = re.compile('(inet addr:%s)' % ipstr)
		pattern = re.compile(ipstr)
		iplist = []
		for ipaddr in re.finditer(ip_pattern, str(output)):
			ip = pattern.search(ipaddr.group())
			if ip.group() != "127.0.0.1":
				iplist.append(ip.group())
	except Exception,e:
		print e
		pass
	return iplist

#获取ip或者ip:port
def ip_filter(content):
	ipList = []
	ipstr = '((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))(:\d*|)'
	result = re.findall(ipstr,content)
	for ip in result:
		ipList.append(ip[0])
	return list_no_repeat(ipList)

def ip_into_int(ip):
    # 先把 192.168.1.13 变成16进制的 c0.a8.01.0d ，再去了“.”后转成10进制的 3232235789 即可。
    # (((((192 * 256) + 168) * 256) + 1) * 256) + 13
    return reduce(lambda x,y:(x<<8)+y,map(int,ip.split('.')))

#判断ip是否为内网ip
def is_internal_ip(ip):
	ip = ip_into_int(ip)
	net_a = ip_into_int('10.255.255.255') >> 24
	net_b = ip_into_int('172.31.255.255') >> 20
	net_c = ip_into_int('192.168.255.255') >> 16
	return ip >> 24 == net_a or ip >>20 == net_b or ip >> 16 == net_c

#打开文件，返回每一行为一个列表，不可打开大文件
def open_file(filename,method='r'):
	lineContent = []
	f = open(filename,method)
	for line in f:
		lineContent.append(line.strip())
	f.close()
	return lineContent

#dict{
#	'info_key' : '[[command,readme],[result]]'
#}
def open_command_file(filename,method='r'):
	content= {}
	f = open(filename,method)
	for line in f:
		if line[0] == '#':
			key = ''
			key = line[2:].strip()
		elif line[0] == '+':
			readme = ''
			readme = line[2:].strip()
		elif line[0] == '>':
			command = ''
			command = line[2:].strip()
			content[key] = [[command,readme],[]]
	f.close()
	return content

#利用set去重复，返回列表无序
def list_no_repeat(list_content):
	norepeat = list(set(list_content))
	return norepeat

#ping扫描
def ping_scan(subnet):
	survivalIp = []
	for ip in subnet:
		p=subprocess.Popen(['ping','-c 2',ip],stdout=subprocess.PIPE)
		m = re.search('(\d)\sreceived', p.stdout.read())
		try:
			if m.group(1)!='0':
				survivalIp.append(ip)
		except:
			pass
	return survivalIp

#c段ip处理
def create_subnet(iplist):
	subnet = []
	for ip in iplist:
		c_ip = ip[:ip.rfind('.')]
		for i in range(254):
			i = i + 1
			subip = c_ip + '.' + str(i)
			subnet.append(subip)
	return subnet

