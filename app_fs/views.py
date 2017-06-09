# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,HttpResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
import json

import models
from models import FCBOperation, FileOperation 

# Create your views here.

@cache_page(60 * 15) # 900s
def home(request):
	return render(request, 'home.html')

@csrf_exempt
def ajax_treeMenu(request):
	if request.method == 'POST':
		res = {'code': '0', 'data': ''}
		flag = request.POST.get('flag')
		if flag == '1':
			fo = FileOperation()
			allFile = fo.getTreeMenu()
			res['data'] = allFile
			res['code'] = '1'
	return HttpResponse(json.dumps(res), content_type = 'application/json')

@csrf_exempt
def ajax_readFile(request):
	if request.method == 'POST':
		res = {'code': '0', 'data': ''}
		path = request.POST.get('path')
		fo = FileOperation()
		content = fo.readFile(path)
		res['data'] = content
		res['code'] = '1'
	return HttpResponse(json.dumps(res), content_type = 'application/json')

@csrf_exempt
def ajax_rename(request):
	if request.method == 'POST':
		res = {'code': '0'}
		path = request.POST.get('path')
		name = request.POST.get('name')
		fo = FileOperation()
		fo.renameFile(path, name)
		res['code'] = '1'
	return HttpResponse(json.dumps(res), content_type = 'application/json')

@csrf_exempt
def ajax_createFile(request):
	if request.method == 'POST':
		res = {'code': '0'}
		path = request.POST.get('path')
		name = request.POST.get('name')
		date = str(request.POST.get('date'))
		kind = request.POST.get('kind')
		contents = request.POST.get('contents')
		fo = FileOperation()
		fo.createFile(path, name, date, kind, contents)
		res['code'] = '1'
	return HttpResponse(json.dumps(res), content_type = 'application/json')

@csrf_exempt
def ajax_deleteFile(request):
	if request.method == 'POST':
		res = {'code': '0'}
		path = request.POST.get('path')

		fo = FileOperation()
		fo.deleteFolder(path)
		res['code'] = '1'
	return HttpResponse(json.dumps(res), content_type = 'application/json')

@csrf_exempt
def ajax_reviseFile(request):
	if request.method == 'POST':
		res = {'code': '0'}
		path = request.POST.get('path')
		#
		contents = request.POST.get('contents').strip()
		fo = FileOperation()
		fo.reviseFile(path, contents)
		res['code'] = '1'
	return HttpResponse(json.dumps(res), content_type = 'application/json')

@csrf_exempt
def ajax_readFCB(request):
	if request.method == 'POST':
		res = {'code': '0','data': {'path': '', 'name': '', 'size': '', 'date': '', 'kind': '', 'startIndexBlock': ''}}
		path = request.POST.get('path')

		fo = FCBOperation()
		fcb = fo.readFCB(path)
		res['code'] = '1'
		res['data']['path'] = fcb['path']
		res['data']['name'] = fcb['name']
		res['data']['size'] = fcb['size']
		res['data']['date'] = fcb['date']
		res['data']['kind'] = fcb['kind']
		res['data']['startIndexBlock'] = fcb['startIndexBlock']
	return HttpResponse(json.dumps(res), content_type = 'application/json')

@csrf_exempt
def ajax_about(request):
	if request.method == 'POST':
		res = {'code': '0','content': ''}
		flag = request.POST.get('flag')

		fo = FileOperation()
		content = fo.getHeadInfo()

		res['code'] = '1'
		res['content'] = content

	return HttpResponse(json.dumps(res), content_type = 'application/json')

@csrf_exempt
def ajax_readUserInfo(request):
	if request.method == 'POST':
		res = {'code': '0', 'msg': ''}
		name = str(request.POST.get('username'))
		pwd = str(request.POST.get('password'))

		fo = FileOperation()
		userInfoList = fo.getUserInfo()

		# userInfoList = [{'name':'Root','pwd':'root'},{'name':'Adminstrator','pwd':'admin'},{'name':'ych','pwd':'123456'}]

		for userInfo in userInfoList:
			if name == str(userInfo['name']):
				if pwd == str(userInfo['pwd']):
					res['code'] = '1'
					break
				else:
					res['msg'] = 'Wrong Password'
			else:
				res['msg'] = 'User doesn\'t exsit'
	return HttpResponse(json.dumps(res), content_type = 'application/json')