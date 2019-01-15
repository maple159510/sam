#coding:utf-8
import subprocess
import os
import time
from aiy.voice.audio import AudioFormat, play_wav, record_file, Recorder
# pygame.init()
# pygame.display.init()
# mixer.init()

		
def convert(word):
	person = "TW_SPK_AKoan" #人物
	vol = "100"   #音量 0~100
	speed = "-2"  #速度 -10~10
	subprocess.call( ["/usr/bin/php", "tts.php", word , person, vol, speed] ) 
	os.system('ffmpeg -y -i word.wav -ar 44100 word.wav')
	play_wav('word.wav')
	
def convert_chinese(word):
	person = "Bruce" #人物
	vol = "100"   #音量 0~100
	speed = "-2"  #速度 -10~10
	subprocess.call( ["/usr/bin/php", "tts.php", word , person, vol, speed] ) 
	os.system('ffmpeg -y -i word.wav -ar 44100 word.wav')
	play_wav('word.wav')
	
