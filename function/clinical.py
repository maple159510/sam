#!/usr/bin/env python3
# Copytight Gbanyan
import sys,os
import argparse
import threading
import time
from datetime import datetime
import wave
import requests
import http.client, urllib.request
import json
import io
from scipy import spatial
import json
from collections import OrderedDict
import socket
import struct
import online_T2C_trans
import re

from aiy.board import Board
from aiy.voice.audio import AudioFormat, play_wav, record_file, Recorder

Lab = AudioFormat(sample_rate_hz=16000, num_channels=1, bytes_per_sample=2)

data_list=[]    #原資料
cos_list = []   #計算cos用
symptom_list=[] #症狀陣列
sym_name=[]     #症狀名稱(問診)
yesno=[]        #是否
score = [0]*9   #病症分數
patient = [0]*39
sym_list=[]     #目前症狀
sym_nolist=[]   #not症狀
ill_list=[]     #目前可能疾病
sym_count = 0   #症狀次數
ill_sym_num = [6,4,5,10,4,8,9,6,10] #每個疾病的症狀數

def askForService(token, data):
	# HOST, PORT 記得修改
	HOST = "140.116.245.149"
	PORT = 2802
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	model = "main"
	try:
		sock.connect((HOST, PORT))
		msg = bytes(token+"@@@", "utf-8")+struct.pack("8s", bytes(model, encoding="utf8"))+b"R"+data
		msg = struct.pack(">I", len(msg)) + msg
		sock.sendall(msg)
		received = str(sock.recv(1024), "utf-8")
	finally:
		sock.close()

	return received

def process(token, data):
	# 可在此做預處理
	# 送出
	result = askForService(token, data)
	# 可在此做後處理
	return result

def record():
	parser = argparse.ArgumentParser()
	parser.add_argument('--filename', '-f', default='clinical.wav')
	args = parser.parse_args()

	with Board() as board:
		print('請按下按鈕開始錄音.')
		board.button.wait_for_press()

		done = threading.Event()
		board.button.when_pressed = done.set

		def wait():
			start = time.monotonic()
			while not done.is_set():
				duration = time.monotonic() - start
				print('錄音中: %.02f 秒 [按下按鈕停止錄音]' % duration)
				time.sleep(0.5)

		record_file(Lab, filename=args.filename, wait=wait, filetype='wav')

def taiwanese_recognize():
	token = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJzY29wZXMiOiIwIiwic3ViIjoiIiwiZXhwIjoxNTY5ODk4MjE5LCJhdWQiOiJ3bW1rcy5jc2llLmVkdS50dyIsImlhdCI6MTUzODM2MjIxOSwic2VydmljZV9pZCI6IjMiLCJpZCI6NDksImlzcyI6IkpXVCIsIm5iZiI6MTUzODM2MjIxOSwidmVyIjowLjEsInVzZXJfaWQiOiIwIn0.BZw0abkTwDbl494J_RAlpGRGJKfOgzRjvLzTF3aR0l66xgpfj7L_DOeab1dmaiCXdWvQR2QgvVmuHg-CihLrM99ssbgXGpBc_agxCNMIWVh5Uw6gUjA3_mndyNrKIG9cKTHB402LhsotNtPanriWoEmg7pNPxq69U7hLFIdiML4"
	time.sleep(0.3)
	record()
	try:
		record_file = open('./clinical.wav','rb').read()
		text = process(token, record_file)
		pattern = 'result.+'
		text = re.findall(pattern,text)
		text = text[0].replace(' ','')
		text = text.replace('\n','')
		text = text.split(':')
		print("台語語音辨識", text[1] + " - ", text[0])
		c_text = online_T2C_trans.t2c_trans(text[1])
		
		return c_text
	except:
		return ""

def score_count(num):
	global sym_count
	patient[num-1] = 1
	sym_list.append(num)
	for i in range(len(data_list)):
		score[i] = 1 - spatial.distance.cosine(patient, cos_list[i])
		if int(data_list[i][num]) == 1 and i not in ill_list:
			ill_list.append(i)

	sym_count+=1
	print('症狀次數:',end='')
	print(sym_count)
	print('分數:',end='')
	print(score)
	print('目前症狀(對):',end='')
	print(sym_list)
	print('可能疾病:',end='')
	print(ill_list)

def score_change(num):
	patient[num-1] = -1
	sym_nolist.append(num)
	for i in range(len(data_list)):
		score[i] = 1 - spatial.distance.cosine(patient, cos_list[i])
	print('分數:',end='')
	print(score)
	print('目前症狀(錯):',end='')
	print(sym_nolist)

def symptom(word,sym_flag):
	if ('耳朵' in word and '癢' in word) or  sym_flag ==1:
		sym='耳朵癢'
		sym_name.append(sym)
		yesno.append('是')
		score_count(1)

	elif ('耳朵' in word  and '異物' in word) or  sym_flag ==2:
		sym='耳朵異物感'
		sym_name.append(sym)
		yesno.append('是')
		score_count(2)

	elif ('拉' in word and '耳' in word  and  '痛' in word) or  sym_flag ==3:
		sym='拉耳廓會痛'
		sym_name.append(sym)
		yesno.append('是')
		score_count(3)

	elif ('張嘴' in word and  '痛' in word) or  sym_flag ==4:
		sym='張嘴會疼痛'
		sym_name.append(sym)
		yesno.append('是')
		score_count(4)

	elif ('聽' in word and  '不清楚' in word) or  sym_flag ==5:
		sym='聽不清楚'
		sym_name.append(sym)
		yesno.append('是')
		score_count(5)

	elif ('臉' in word and '壓痛' in word) or  sym_flag ==6:
		sym='鼻竇壓痛'
		sym_name.append(sym)
		yesno.append('是')
		score_count(6)

	elif ('喉嚨' in word and  '痛' in word) or  sym_flag ==7:
		sym='喉嚨痛'
		sym_name.append(sym)
		yesno.append('是')
		score_count(7)
		
	elif '打噴嚏' in word or  sym_flag ==8:
		sym='打噴嚏'
		sym_name.append(sym)
		yesno.append('是')
		score_count(8)

	elif '流鼻水' in word or '流鼻' in word or '流(鼻)' in word or '鼻水' in word or  sym_flag ==9:
		sym='鼻水'
		sym_name.append('流'+sym)
		yesno.append('是')
		score_count(9)

	elif '鼻塞' in word or  sym_flag ==10:
		sym='鼻塞'
		sym_name.append(sym)
		yesno.append('是')
		score_count(10)

	  
	elif ('鼻子' in word and '癢' in word) or  sym_flag ==11:
		sym='鼻子癢'
		sym_name.append(sym)
		yesno.append('是')
		score_count(11)

	elif '結膜炎' in word or sym_flag ==12:
		sym='結膜炎'
		sym_name.append(sym)
		yesno.append('是')
		score_count(12)

	elif ('嗅覺' in word and '差' in word) or  sym_flag ==13:
		sym='嗅覺變差'
		sym_name.append(sym)
		yesno.append('是')
		score_count(13)


	elif '頭痛' in word or '頭(疼)' in word or '(頭)(疼)' in word or sym_flag ==14:
		sym='頭痛'
		sym_name.append(sym)
		yesno.append('是')
		score_count(14)

	elif '口臭' in word or  sym_flag ==15:
		sym='口臭'
		sym_name.append(sym)
		yesno.append('是')
		score_count(15)

	elif ('耳朵' in word and  '痛' in word) or  sym_flag ==16:
		sym='耳朵痛'
		sym_name.append(sym)
		yesno.append('是')
		score_count(16)

	elif ('最近' in word and  '感冒' in word) or  sym_flag ==17:
		sym='最近有感冒'
		sym_name.append(sym)
		yesno.append('是')
		score_count(17)

	elif '咳嗽' in word or  sym_flag ==18:
		sym='咳嗽'
		sym_name.append(sym) #症狀0
		yesno.append('是')
		score_count(18)

	elif '耳鳴' in word or  sym_flag ==19:
		sym='耳鳴'
		sym_name.append(sym)
		yesno.append('是')
		score_count(19)

	elif (('脖子' in word or'頸' in word) and '腫塊' in word) or  sym_flag ==20:
		sym='頸部腫塊'
		sym_name.append(sym)
		yesno.append('是')
		score_count(20)

	elif '流鼻血' in word or  sym_flag ==21:
		sym='流鼻血'
		sym_name.append(sym)
		yesno.append('是')
		score_count(21)

	elif ('臉' in word and '麻痺' in word) or  sym_flag ==22:
		sym='臉部麻痺'
		sym_name.append(sym)
		yesno.append('是')
		score_count(22)

	elif ('耳朵' in word and  '流膿' in word) or  sym_flag ==23:
		sym='流膿'
		sym_name.append(sym)
		yesno.append('是')
		score_count(23)

	elif '發燒' in word or  sym_flag ==24:
		sym='發燒'
		sym_name.append(sym)
		yesno.append('是')
		score_count(24)

	elif '畏寒' in word or  sym_flag ==25:
		sym='畏寒'
		sym_name.append(sym)
		yesno.append('是')
		score_count(25)


	elif '寒顫' in word or  sym_flag ==26:
		sym='寒顫'
		sym_name.append(sym)
		yesno.append('是')
		score_count(26)
	   

	elif '嘔吐' in word or  sym_flag ==27:
		sym='嘔吐'
		sym_name.append(sym)
		yesno.append('是')
		score_count(27)
	  

	elif ('淋巴結' in word and ('痛' in word and '腫大' in word)) or  sym_flag ==28:
		sym='頸部淋巴結腫大'
		sym_name.append(sym)
		yesno.append('是')
		score_count(28)
	  
	elif ('食慾' in word and ('不振' in word or '不好' in word or '不佳' in word)) or  sym_flag ==29:
		sym='食慾不振'
		sym_name.append(sym)
		yesno.append('是')
		score_count(29)
	  
	elif ('腮腺' in word and ('發炎' in word or '腫大' in word)) or  sym_flag ==30:
		sym='腮腺發炎腫大'
		sym_name.append(sym)
		yesno.append('是')
		score_count(30)

	elif ('腮腺' in word and  '痛' in word) or  sym_flag ==31:
		sym='腮腺疼痛'
		sym_name.append(sym)
		yesno.append('是')
		score_count(31)

	elif ('咀嚼' in word and  '困難' in word) or  sym_flag ==32:
		sym='咀嚼困難'
		sym_name.append(sym)
		yesno.append('是')
		score_count(32)

	elif '胃痛' in word or  sym_flag ==33:
		sym='胃痛'
		sym_name.append(sym)
		yesno.append('是')
		score_count(33)

	elif ('喉嚨' in word and ('熱' in word or '燙' in word)) or  sym_flag ==34:
		sym='喉嚨灼熱'
		sym_name.append(sym)
		yesno.append('是')
		score_count(34)

	elif ('清' in word and '喉嚨' in word) or  sym_flag ==35:
		sym='常清喉嚨'
		sym_name.append(sym)
		yesno.append('是')
		score_count(35)

	elif ('喉嚨' in word and '異物' in word) or  sym_flag ==36:
		sym='喉嚨有異物感'
		sym_name.append(sym)
		yesno.append('是')
		score_count(36)

	elif ('聲音' in word and '啞' in word) or  sym_flag ==37:
		sym='聲音乾啞'
		sym_name.append(sym)
		yesno.append('是')
		score_count(37)
	

	elif ('肌肉' in word and '痠痛' in word) or  sym_flag ==38:
		sym='肌肉痠痛'
		sym_name.append(sym)
		yesno.append('是')
		score_count(38)

	elif '拉肚子' in word or  sym_flag ==39:
		sym='拉肚子'
		sym_name.append(sym)
		yesno.append('是')
		score_count(39)
	   
	else:
		play_wav('../final2/無法判別症狀.wav')

def main():

	file = io.open('./illness.csv','r',encoding='utf-8')
	lines = file.readlines()
	i = 1
	while i<len(lines):
		data = lines[i].replace('\n','').split(',')
		data_list.append(data)
		data=data[1:]
		data = list(map(int, data))
		cos_list.append(data)
		i+=1
		symptom_list = lines[0].replace('\n','').split(',')
		
	while True:
		flag = 0
		play_wav('../final2/你有哪裡不舒服嗎.wav')
		text = taiwanese_recognize()

		if text is None:
			print('抱歉，我沒聽清楚。可以再說一次嗎?')    
		else:
			print('你說:', text, '"')
			symptom(text,0)

		while sym_count <=4 and max(score) <= 0.75 and flag==0: #問診數量6 相似度>0.75 症狀沒問完
			if len(ill_list)==1: #只有一病
				for i in range(1,39): #問39症狀 #下面的:症狀為沒問過且對應疾病
					if i not in sym_list and i not in sym_nolist and int(data_list[score.index(max(score))][i])==1:
						print('above_1s i : '+str(i))
						play_wav('../final2/那你會.wav')
						play_wav('../final2/'+ str(symptom_list[i])+'.wav')
						play_wav('../final2/嗎.wav')
						

						text = taiwanese_recognize()
						if text is None:
							play_wav('../final2/不好意思我聽不懂,請再說一次.wav')
						else:
							if '沒有' in text or '不會' in text or '沒' in text or '無' in text or '背' in text or '袂' in text or '咧' in text:
								score_change(i)
								sym_name.append(symptom_list[i])
								yesno.append('否')
								break
							elif '有' in text or '會' in text or '是' in text or '對' in text or '痛' in text or '會痛' in text or '有痛' in text or '嗚' in text or '呼' in text:
								symptom('',i)
								break
							else:
								play_wav('../final2/不好意思我聽不懂,請再說一次.wav')
								break
					elif i ==39: #症狀皆問完
						flag=1
						break

			else: #可能疾病有2個以上
				if len(sym_list)<2: #符合症狀只有一個
					play_wav('../final2/還有哪裡不舒服.wav')
					if '沒有' in text:
						play_wav('../final2/症狀過少無法判斷.wav')
					#button.wait_for_press()
					text = taiwanese_recognize()
					print(text)
					symptom(text,0)

				else: #符合症狀兩個以上
					for i in range(1,39):
						if i not in sym_list and i not in sym_nolist and int(data_list[score.index(max(score))][i])==1:
							print('above_2s i : '+str(i))
							play_wav('../final2/那你會.wav')
							play_wav('../final2/'+ str(symptom_list[i])+'.wav')
							play_wav('../final2/嗎.wav')

							#button.wait_for_press()
							text = taiwanese_recognize()
							if text is None:
								play_wav('../final2/不好意思我聽不懂,請再說一次.wav')
							else:
								if '沒有' in text or '不會' in text:
									score_change(i)
									sym_name.append(symptom_list[i])
									yesno.append('否')
									break
								elif '有' in text or '會' in text:
									symptom('',i)
									break
								else:
									play_wav('../final2/不好意思我聽不懂,請再說一次.wav')
									break
						elif i==39:
							flag=1
							break


		play_wav('../final2/診斷完畢.wav')
		print('No.\t症狀\t\t是\否')
		for i in range(len(sym_name)):
			print(str(i)+'\t'+sym_name[i]+'\t\t'+yesno[i])
			i+=1
		print('可能疾病:' + data_list[score.index(max(score))][0])
		play_wav('../final2/您可能患有的病症是.wav')
		play_wav('../final2/' + str(data_list[score.index(max(score))][0])+'.wav')
		play_wav('../final2/請盡速去耳鼻喉科掛號.wav')
		return False
	file.close()


if __name__ == '__main__':
	main()
