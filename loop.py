#copyrught WMMKSLab Gbanyan
import argparse
import time
import threading
import socket
import struct
import re
import online_T2C_trans
import os
from subprocess import call

from aiy.board import Board
from aiy.voice.audio import AudioFormat, play_wav, record_file, Recorder

Lab = AudioFormat(sample_rate_hz=16000, num_channels=1, bytes_per_sample=2)

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

def taiwanese_recognize():
	token = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJzY29wZXMiOiIwIiwic3ViIjoiIiwiZXhwIjoxNTY5ODk4MjE5LCJhdWQiOiJ3bW1rcy5jc2llLmVkdS50dyIsImlhdCI6MTUzODM2MjIxOSwic2VydmljZV9pZCI6IjMiLCJpZCI6NDksImlzcyI6IkpXVCIsIm5iZiI6MTUzODM2MjIxOSwidmVyIjowLjEsInVzZXJfaWQiOiIwIn0.BZw0abkTwDbl494J_RAlpGRGJKfOgzRjvLzTF3aR0l66xgpfj7L_DOeab1dmaiCXdWvQR2QgvVmuHg-CihLrM99ssbgXGpBc_agxCNMIWVh5Uw6gUjA3_mndyNrKIG9cKTHB402LhsotNtPanriWoEmg7pNPxq69U7hLFIdiML4"
	time.sleep(0.3)
 
	record_file = open('./recording.wav','rb').read()
	text = process(token, record_file)
	pattern = 'result.+'
	text = re.findall(pattern,text)
	text = text[0].replace(' ','')
	text = text.replace('\n','')
	text = text.split(':')
	print("台語語音辨識", text[1] + " - ", text[0])
	c_text = online_T2C_trans.t2c_trans(text[1])
	
	return c_text

def record():
	parser = argparse.ArgumentParser()
	parser.add_argument('--filename', '-f', default='recording.wav')
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
		
		# print('Press button to play recorded sound.')
		# board.button.wait_for_press()

		# print('Playing...')
		# play_wav(args.filename)
		# print('Done.')

def tending_justify(text):
	if "舒服" in text or "痛苦" in text or "艱苦" in text or "(艱)(苦)" in text:
		return 1
	elif "醫生" in text or "科" in text:
		return 1
	elif "廣播" in text or "收音" in text:
		return 2
	elif "煩惱" in text or "難過" in text:
		return 3
	elif "(看)" in text:
		return 10
	else:
		return 4

def function_select(index):
	if index == 1: 
		print("啟動問診程式")
		os.chdir('function/')
		os.system('python3 clinical.py')
		os.chdir('../')
	elif index == 2:
		print("啟動收音機")
		os.system('function/radio.py')
	elif index == 3:
		print("啟動煩惱音樂推薦")
		os.system('function/depression_music.py')
	elif index == 4:
		print("抱歉沒有你要的功能喔，請按鈕重新選擇")
	elif index == 10:
		print("關機中...")
		call("sudo nohup shutdown -h now", shell=True)
	else:
		return 0

def main():
	# play_wav('機器已啟動，按鈕開始啟動功能')
	firsttime = True
	while True:
		# play_wav("請按鈕呼叫機器人")
		with Board() as button_ready:
			print("請按開關開始")
			play_wav("final2/start.wav")
			button_ready.button.wait_for_press()
			if firsttime == True:
				play_wav('final2/button.wav')
			firsttime = False
		record()
		try:
			user_speak_text = taiwanese_recognize()
		except:
			return 0
		print(user_speak_text)
		intend = tending_justify(user_speak_text)
		function_select(intend)
		
if __name__ == '__main__':
	main()

# recognizer()


