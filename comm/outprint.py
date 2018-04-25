#!/usr/bin/python
#coding:utf-8

import os

def create_view(result):
	html_content = '''
		<html>
			<head>
				<title>result</title>
				<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
				<style>
					.pre{
						width: 1000px;
					}
				</style>
			    <link href="http://libs.baidu.com/bootstrap/3.0.3/css/bootstrap.min.css" rel="stylesheet">
			    <script src="http://libs.baidu.com/jquery/2.0.0/jquery.min.js"></script>
			    <script src="http://libs.baidu.com/bootstrap/3.0.3/js/bootstrap.min.js"></script>
				<script>
				    function display(id){  
				        var traget=document.getElementById(id);  
				        if(traget.style.display=="none"){  
				            traget.style.display="";  
				        }else{  
				            traget.style.display="none";  
				      	}  
				   	}
				</script>
			</head>
			<body>

			<div class="navbar navbar-inverse" role="navigation">
			  <div class="navbar-header">
			     <a href="#" class="navbar-brand" disabled>linux信息收集</a>
			  </div>
			  <ul class="nav navbar-nav">
			    <li><a href="?system" >系统信息</a></li>
			    <li><a href="?user" >用户信息</a></li>
			    <li><a href="?service" >服务信息</a></li>
			    <li><a href="?file" >安全扫描</a></li>
			    <li><a href="?network" >主机存活信息</a></li>
			  </ul>
			</div>

			
	'''

	#systeminfo
	tr_content = tr_content_create(result['system'])
	html_content = html_content + table_content('system',tr_content)

	#userinfo
	tr_content = tr_content_create(result['user'])
	html_content = html_content + table_content('user',tr_content)

	#service
	tr_content = tr_content_create(result['service'])
	html_content = html_content + table_content('service',tr_content)

	#file
	tr_content =tr_content_create(result['file'])
	html_content = html_content + table_content('file',tr_content)

	# #network
	# tr_content =tr_content_create(result['network'])
	# html_content = html_content + table_content('network',tr_content)

	html_content = html_content + '''
		<script>
		var act = window.location.search.substr(1);
		switch(act){
			case 'system': display('system');break;
			case 'user': display('user');break;
			case 'service' : display('service');break;
			case 'file' : display('file');break;
			case 'network' : display('network');break;
			default : display('system');
		}
		$(function () { $('#myModal').modal({
	      keyboard: true,
	      show: false
		})});
		</script>
		</body>
		</html>
	'''
	return html_content

def table_content(id,tr):
	content = '''
		<div id="{id}" style="display: none">

		<table class="table table-hover">
		  <thead>
		    <tr>
		      <th>描述</th>
		      <th>结果</th>
		    </tr>
		  </thead>
		  <tbody>
		  	{tr}
		  </tbody>
		</table>
		</div>
	'''.format(id=id, tr=tr)
	return content

# class: view是可以下拉的、danger等其它是对信息的重要性标注
def simple_content(content, describe, classname="success"):
	try:
		tempcontent = ""
		content = [str(t).replace('\n','&nbsp;&nbsp;&nbsp;').replace('\t','&nbsp;&nbsp;&nbsp;') for t in content]
		#数组内容中文会被编码
		for i in content:
			tempcontent = tempcontent + i + ","
		tempcontent = tempcontent[:-1]
	except Exception,e:
		print e
		pass
	info = '''
		<tr class="{classname}">
	      <td>{describe}</td>
	      <td>
	      	{info}
	      </td>
	    </tr>
	'''.format(info=tempcontent, describe=describe, classname=classname)
	return info

def detailed_content(content, describe, idkey, classname="view danger"):
	try:
	#先判断content是不是list还是dic等
		tempcontent = ""
		content = [str(t).replace('\n','<br>').replace('\t','&#009;') for t in content]
		for i in content:
			tempcontent = tempcontent + i + ","
		tempcontent = tempcontent[:-1]
	except Exception,e:
		print e
		pass
	info = '''
    <tr class="{classname}">
      <td>{describe}</td>
      <td>

		<button class="btn btn-primary" data-toggle="modal" data-target="#{idkey}">
		   查看详情
		</button>
		<div class="modal fade" id="{idkey}" tabindex="-1" role="dialog" 
		   aria-labelledby="myModalLabel" aria-hidden="true">
		   <div class="modal-dialog" style="width:1000px;">
		      <div class="modal-content">
		         <div class="modal-header">
		            <button type="button" class="close" data-dismiss="modal" 
		               aria-hidden="true">
		            </button>
		            <h4 class="modal-title" id="myModalLabel">
		               {describe}
		            </h4>
		         </div>
		         <div class="modal-body">
		         		{info}
		         </div>
		         <div class="modal-footer">
		            <button type="button" class="btn btn-default" 
		               data-dismiss="modal">关闭
		            </button>
		         </div>
		      </div>
		   </div>
		</div>

      </td>
    </tr>
	'''.format(info=tempcontent, describe=describe, idkey=idkey, classname=classname)
	return info

def list_str_length(list_):
	length = 0
	for item in list_:
		length = length + len(item)
	return length

def tr_content_create(result):
	tr_content = ""
	for key in sorted(result):
		
		#对soft\server特殊处理
		if key == 'e_program' or key == 'scan' or key == 'weakpassscan':
			soft_content = []
			print result[key]
			for soft in result[key][1]:
				print soft
				if soft[-1] == '1':
					if key == 'scan':
						c = '<font color="red">' + soft[:-1] + '  exist</font>&nbsp;&nbsp;&nbsp;<a href="./files/{filename}">查看</a>\n'.format(filename=os.path.basename(soft[:-1]))
					else:
						c = '<font color="red">' + soft[:-1] + '  exist</font>\n'
					soft_content.append(c)
				else:
					soft_content.append('<font>' + soft[:-1] + '  not exist</font>\n')
			tr_content = tr_content + detailed_content(soft_content, result[key][0][1], key)
			continue

		try:

			#对结果返回为空处理，也针对对[""]和[]情况处理
			if len(result[key][1]) == 1 and not result[key][1][0].strip():
				tr_content = tr_content + simple_content(result[key][1], result[key][0][1], "")
				continue
			#根据内容长度、是否有转行来判断显示
			length = list_str_length(result[key][1])
			if length > 100 or '\n' in result[key][1] or '\t' in result[key][1]:
				tr_content = tr_content + detailed_content(result[key][1], result[key][0][1], key)
			else:
				tr_content = tr_content + simple_content(result[key][1], result[key][0][1])
		except Exception,e:
			print e
			pass
	return tr_content