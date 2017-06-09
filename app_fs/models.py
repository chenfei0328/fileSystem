# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


import numpy as np
import re
import copy

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

root = 'D:/fs/fileSystem/app_fs/root.txt'

# 位示图
class BitMapFunction(object):	
	
	def __init__(self):		
		self.n = 64
		self.BitMap = np.ones([self.n,self.n], dtype = np.int8)

	# 从源文件中读取位示图
	def getBitMap(self):
		with open(root, 'r') as f:
			content = f.readlines()
			for i in range(self.n):
				j = 0
				for value in content[i+2].strip():
					self.BitMap[i,j] = value
					j += 1	

	# 更新位示图并载入源文件
	def updateBitMap(self):
		with open(root, 'r') as f:
			content = f.readlines()
			for i in range(self.n):
				content[i+2] = str(self.BitMap[i])

		with open(root, 'w') as f:
			for i in range(len(content)):
				line = content[i]
				if i >= 2 and i <= 65:
					line = re.sub('\D', '', line) + '\n'
				f.write(line)

	# 从位示图中分配新文件所需的盘块数
	def getBlockByBitMap(self, blockAmount):	# 参数为新文件内容所需盘块
		self.getBitMap()
		blockList = []
		k = 0
		for i in range(self.n):
			for j in range(self.n):
				if self.BitMap[i,j] == 0:
					b = self.n * i + (j + 1)
					k += 1
					blockList.append(b)
					self.BitMap[i,j] = 1
				if len(blockList) == blockAmount:
					self.updateBitMap()
					return blockList
		
		# 如果块数不够，则回收这些盘块并返回0
		if k < blockAmount:
			self.recoverBlockByBitMap(blockList)
			return 0

	# 删除文件后回收盘块
	def recoverBlockByBitMap(self, blockList):
		self.getBitMap()
		for b in blockList:
			i = b / self.n 
			j = b % self.n - 1
			self.BitMap[i,j] = 0
		self.updateBitMap()

# 文件控制块
class FCBOperation(object):
	# 此类中的block都是指文件中的行数
	def __init__(self):
		self.FCB = {
			# path = ''
			# name = '',
			# size = 0,
			# date = '',
			# kind = 0,	# 0表示文件夹，1表示文件
			# startIndexBlock = 0,	# 文件的索引块
		}

	def readFCB(self, path):
		block = path.count('/') + 65
		with open(root, 'r') as f:
			content = f.readlines()[block].split()
			for item in content:
				if path == item.split(':')[0]:
					item = item.split(':')
					self.FCB['path'] = item[0]
					self.FCB['name'] = item[1]
					self.FCB['size'] = item[2]
					self.FCB['date'] = item[3]
					self.FCB['kind'] = item[4]
					self.FCB['startIndexBlock'] = item[5]
					return self.FCB



	def writeFCB(self, fcb):
		block = fcb['path'].count('/') + 65
		s = fcb['path'] + ':' + fcb['name'] + ':' + fcb['size'] + ':' + fcb['date'] + ':' + fcb['kind'] + ':' + fcb['startIndexBlock']
		with open(root, 'r') as f:
			content = f.readlines()
			content[block] = s + ' ' + content[block]
		with open(root, 'w') as f:
			for line in content:
				f.write(line)

	def deleteFCB(self, path):
		block = path.count('/') + 65
		with open(root, 'r') as f:
			content = f.readlines()
			s = content[block].split()
			for item in s:
				if path == item.split(':')[0]:
					s.remove(item)
					break
		s = ' '.join(s) + '\n'
		content[block] = s
		with open(root, 'w') as f:
			for line in content:
				f.write(line)


# # 索引块 64*64=4096 盘块号大小为4B，理论最多512B/4B=128个，但设定一个盘块最多放64个盘块号

# 二级索引操作
class IndexBlockFunction(BitMapFunction):

	def __init__(self):
		super(IndexBlockFunction, self).__init__()

	# 根据指定索引块从源文件中读取盘块列表
	def readIndexBlock(self, blockNumber):	# 参数为第一级索引盘块号
		blockList = []
		with open(root, 'r') as f:
			content = f.readlines()
			for index in content[blockNumber - 1].split():
				data = content[int(index) - 1].split()
				for block in data:
					blockList.append(int(block))
		# 返回索引中所有数据块的块号列表
		return blockList

	# 根据盘块列表在源文件中构建二级索引块
	def createIndexBlock(self, blockList):
		indexBlockList = []
		secondIndexBlockAmount = len(blockList) / 64
		if len(blockList) % 64 != 0:
			secondIndexBlockAmount += 1
		blockAmount = secondIndexBlockAmount + 1
		# 获得索引块列表

		indexBlockList = self.getBlockByBitMap(blockAmount)

		blockList = map(str, blockList)
		indexBlockList = map(str, indexBlockList)

		with open(root, 'r') as f:
			content = f.readlines()
			firstIndexBlock = indexBlockList[0]
			del indexBlockList[0]
			
			s =  ' '.join(indexBlockList)
			content[int(firstIndexBlock) - 1] = s + '\n'
			
			for i in range(secondIndexBlockAmount):
				if (i+1) < secondIndexBlockAmount:
					s = ' '.join(blockList[(64*i):(64*i+63)])					
				else:
					s = ' '.join(blockList[(64*i):])
				content[int(indexBlockList[i])-1] = s +'\n' 

		with open(root, 'w') as f:
			f.writelines(content)

		indexBlockList.insert(0, firstIndexBlock)	

		return indexBlockList

# 文件操作
class FileOperation(IndexBlockFunction, FCBOperation):
	
	def __init__(self):
		# super(FileOperation, self).__init__()
		IndexBlockFunction.__init__(self)
		FCBOperation.__init__(self)

	# 读取文件
	def readFile(self, path):
		self.FCB = self.readFCB(path)
		if self.FCB['kind'] == 0:
			return
		else:
			blockNumber = int(self.FCB['startIndexBlock'])
			blockList = self.readIndexBlock(blockNumber)
			fileData = ''
			with open(root, 'r') as f:
				content = f.readlines()
				for block in blockList:
					fileData += content[block - 1].strip()
			return fileData

	# 新建文件
	def createFile(self, path, name, date, kind, contents):
		if kind == '1':
			data = ['']
			s = 0 
			i = 0
			allBytes = 0

			for word in contents:
				# 中文占两个字节
				if word >= u'\u4e00' and word <= u'\u9fa5' :
					byte = 2
				else:
					byte = 1

				allBytes += byte

				if (s + byte) > 512:
					s = 0
					i += 1
					data.append(word)
				else:
					s += byte
					data[i] += word

			allBytes = (str(allBytes) + 'B') if allBytes < 1024 else (str(allBytes / 1024) + 'KB')
			
			# 分配数据块
			blockAmount = len(data)
			blockList = self.getBlockByBitMap(blockAmount)
			
			# 分配索引块
			indexBlockList = self.createIndexBlock(blockList)
			startIndexBlock = indexBlockList[0]
			
			with open(root, 'r') as f:
				content = f.readlines()
				
			for i,block in zip(range(len(data)),blockList):
				content[block - 1] = data[i] + '\n'
			
			with open(root, 'w') as f:
				f.writelines(content)
				# for line in content:
				# 	f.write(line)			
		else:
			allBytes = '0'	
			startIndexBlock = '0'
		
		# 写入FCB
		fcb = {}
		fcb['path'] = path
		fcb['name'] = name
		fcb['size'] = allBytes
		fcb['date'] = date
		fcb['kind'] = kind
		fcb['startIndexBlock'] = startIndexBlock
		
		self.writeFCB(fcb)

	# 删除文件
	def deleteFolder(self, path):
		fcb = self.readFCB(path)
		
		# 删除文件
		if fcb['kind'] == '1':
			self.deleteFCB(path)
			self.deleteFile(fcb)
		# 删除文件夹
		else:
			self.deleteFCB(path)
			line = path.count('/') + 66
			if line < 70:
				num = len(path)
				childpath = []

				with open(root, 'r') as f:
					content = f.readlines()[line].split()
					for item in content:
						if path == item.split(':')[0][0:num]:
							childpath.append(item.split(':')[0])
						
				for p in childpath:
					self.deleteFolder(p)

	def deleteFile(self, fcb):
		blockNumber = int(fcb['startIndexBlock']) 
		blockList = self.readIndexBlock(blockNumber)
		indexBlockList = [blockNumber]
		
		with open(root, 'r') as f:
			content = f.readlines()

		for indexBlock in content[blockNumber - 1].split():
			indexBlockList.append(int(indexBlock))
		
		# 数据块清空	
		for block in blockList:
			content[block - 1] = '' + '\n'

		# 索引块清空
		for indexBlock in indexBlockList:
			content[indexBlock - 1] = '' + '\n'

		with open(root, 'w') as f:
			for line in content:
				f.write(line)

		# 回收盘块
		self.recoverBlockByBitMap(blockList)
		self.recoverBlockByBitMap(indexBlockList)
		

	# 修改文件
	def reviseFile(self, path, contents):
		
		fcb = self.readFCB(path)

		self.deleteFolder(path)
		
		path = fcb['path']
		name = fcb['name']
		date = fcb['date']
		kind = fcb['kind']
		self.createFile(path, name, date, kind, contents)

	# 重命名文件
	def renameFile(self, path, newName):
		fcb = self.readFCB(path)

		item = fcb['path'].split('/')
		item[-1] = newName
		fcb['path'] = '/'.join(item)
		fcb['name'] = newName

		self.deleteFCB(path)
		self.writeFCB(fcb)

	# 获得所有文件信息
	def getTreeMenu(self):
		allFile = []

		with open(root, 'r') as f:
			content = f.readlines()

		for line in range(66,70):
			newContent = content[line].split()
			for item in newContent:
				newContent[newContent.index(item)] = item.split(':')[4] + item.split(':')[0]
			allFile.append(newContent)

		return allFile

	def getHeadInfo(self):
		with open(root, 'r') as f:
			content = f.readlines()[0].strip()
			return content

	def getUserInfo(self):	
		userInfoList = []

		with open(root, 'r') as f:
			content = f.readlines()[1].split()		 
			
		for user in content:
			userInfo = {}		
			userInfo['name'] = user.split(':')[0]
			userInfo['pwd'] = user.split(':')[1]

			userInfoList.append(userInfo)

		return userInfoList


# if __name__ == '__main__':

	# # for BitMapFunction test
	
	# bp = BitMapFunction()
	
	# bp.getBlockByBitMap(4)
	# blockList = [71,72,73,74]
	# bp.recoverBlockByBitMap(blockList)



	# # for FileOperation test
	# # 分布执行这些函数并查看root.txt变化
	
	# fo = FCBOperation()
	
	# path = 'root/A/AA/aaa.txt'
	# FCB = fo.readFCB(path)
	# fo.writeFCB(FCB)
	# fo.deleteFCB(path)



	# # for IndexBlockFunction test
	
	# ib = IndexBlockFunction()
	
	# blockList = ib.readIndexBlock(75)
	# print blockList
	# blockList = range(71,75,1)
	# ib.createIndexBlock(blockList)



	# for FileOperation test
	
	# fo = FileOperation()
	
	# 查找文件	
	# path = 'root/B/BB/bbb.txt'
	# fileData = fo.readFile(path)
	# print fileData

	# 创建文件
	# path = 'root/B/BB/bbb.txt'
	# name = 'bbb.txt'
	# date = '2016/5/27'
	# kind = '1'
	# contents = u"s2f程序员杂志一2d3程序员杂志二2d3程序员杂志三2d3程序员杂志四2d3s2f程序员杂志一2d3程序员杂志二2d3程序员杂志三2d3程序员杂志四2d3s2f程序员杂志一2d3程序员杂志二2d3程序员杂志三2d3程序员杂志四2d3s2f程序员杂志一2d3程序员杂志二2d3程序员杂志三2d3程序员杂志四2d3s2f程序员杂志一2d3程序员杂志二2d3程序员杂志三2d3程序员杂志四2d3s2f程序员杂志一2d3程序员杂志二2d3程序员杂志三2d3程序员杂志四2d3s2f程序员杂志一2d3程序员杂志二2d3程序员杂志三2d3程序员杂志四2d3s2f程序员杂志一2d3程序员杂志二2d3程序员杂志三2d3程序员杂志四2d3s2f程序员杂志一2d3程序员杂志二2d3程序员杂志三2d3程序员杂志四2d3s2f程序员杂志一2d3程序员杂志二2d3程序员杂志三2d3程序员杂志四2d3s2f程序员杂志一2d3程序员杂志二2d3程序员杂志三2d3程序员杂志四2d3s2f程序员杂志一2d3程序员杂志二2d3程序员杂志三2d3程序员杂志四2d3s2f程序员杂志一2d3程序员杂志二2d3程序员杂志三2d3程序员杂志四2d3s2f程序员杂志一2d3程序员杂志二2d3程序员杂志三2d3程序员杂志四2d3s2f程序员杂志一2d3程序员杂志二2d3程序员杂志三2d3程序员杂志四2d3s2f程序员杂志一2d3程序员杂志二2d3程序员杂志三2d3程序员杂志四2d3s2f程序员杂志一2d3程序员杂志二2d3程序员杂志三2d3程序员杂志四2d3s2f程序员杂志一2d3程序员杂志二2d3程序员杂志三2d3程序员杂志四2d3s2f程序员杂志一2d3程序员杂志二2d3程序员杂志三2d3程序员杂志四2d3s2f程序员杂志一2d3程序员杂志二2d3程序员杂志三2d3程序员杂志四2d3"  
	# fo.createFile(path, name, date, kind, contents)
	# path = 'root/B/BB/BBB/aabb.txt'
	# name = 'aabb.txt'
	# date = '2016/5/27'
	# kind = '1'
	# contents = u'这是一个准备被删除的测试文件4'
	# fo.createFile(path, name, date, kind, contents)
	# path = 'root/B/BB/BBB'
	# name = 'BBB'
	# date = '2016/5/27'
	# kind = '0'
	# contents = ''
	# fo.createFile(path, name, date, kind, contents)
	
	# 删除文件
	# path = 'root/A/AA/AAA/cccc.txt'
	# fo.deleteFolder(path)

	# 修改文件
	# path = 'root/B/BB/BBB/aabb.txt'
	# contents = '这是被修改的文件'
	# fo.reviseFile(path, contents)

	# path = 'root/B/BB/BBB/aaaa.txt'
	# contents = u'这是一个准备被修改的测试文件aaaa'
	# fo.reviseFile(path, contents)

	# 重命名文件
	# path = 'root/A/AA/AAA/bbbb.txt'
	# newName = 'aaaa.txt'
	# fo.renameFile(path, newName)

	# 获取全部文件路径
	# fo.getTreeMenu()

	# 获取用户信息
	# fo.getUserInfo()