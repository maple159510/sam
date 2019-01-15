from gtts import gTTS
import os
from subprocess import check_output
import time
import urllib
import socket

def get_host_ip():
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(('8.8.8.8', 80))
		ip = s.getsockname()[0]
	finally:
		s.close()

	return ip


while True:
	try:
		urllib.request.urlopen("http://www.google.com")
	except urllib.error.URLError:
		print("mpg321 noconnect.mp3")
		os.system("")
		time.sleep(1)
	else:
		print("Connected")
		ssid_clues = check_output(["iwconfig", "wlan0"])
		for line in ssid_clues.split():
			line = line.decode("utf-8")
			if line[:5]  == "ESSID":
				ssid = line.split('"')[1]
		ip = get_host_ip()
		tts = gTTS(text='已經連到無線網路'+str(ssid)+'，位址是'+ip, lang='zh-tw')
		tts.save("ip.mp3")
		os.system("mpg321 ip.mp3")
		break



