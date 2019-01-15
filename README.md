# WMMKSLab 智慧音箱專案

整合盧文祥教授發展的台語辨識 API, 以及使用 Google-Aiy-Project 的 Voice ，在Raspberry pi 上面建置智慧音箱


## Getting started

### Prerequisites

1. Raspberry pi zero or 3
2. USB audio plus microphone and speaker,  or google voicehat
3. Container box
4. The allowance of the taiwanese recognization API or Google Voice API for Traditional Chinese

### Installing

1. Download the lateset [AIY project image](https://github.com/google/aiyprojects-raspbian/releases) and use the Etcher app to burn it to the SD card.

2. After finishing writing down the image file, if WIFI pre-configure needed, write the wpa_supplicant.conf to the mounted boot volume. (this wifi configuration file will be written to the /etc/wpa_supplicant/wpa_supplicant.conf during boot)

   ```
   ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev 
   
   update_config=1 
   
   country=TW 
   
   network={ 
   
       ssid="Your WIFI SSID" 
   
       psk="wifi password" 
   
       priority=1 
   
   }  
   # allow multiple wifi configuration, and set priority
   ```

3. After first booting, ssh into it and `sudo raspi-config` to configure the timezone, enable vnc to connect, or you can just use HDMI and keyboard to control it. 

4. Till now, you can just excute python scripts, however, if you want to run the script in this project completely, these packages are recommended:

   1. python3-scipy (used to count cosine vectors)
   2. mpg321 (used to play mp3 audio)
   3. gtts (by pip3 install)

5. Put the script in `~/AIY-projects-python/src/`, and you can now run it! 

6. If you want to enable the script autostart aftet boot, please edit the `/etc/rc.local` like this:

   ```bash
   cd /home/pi/
   su pi -c "python3 ip.py"  #report ip in our project
   cd /home/pi/AIY-projects-python/src/
   su pi -c "python3 loop.py" #the main script 
   ```

7. If you adopted the google voice-hat, you may need to exec check audio script on the Desktop, it will tell you what to do if audio not working. However, if you need to configure the USB Audio and separate the speaker and the microphone, then you need to disable pulseaudio and configure the alsaaudio

   1. `sudo nano /etc/pulse/client.conf` and set `autospawn = no` 

   2. `nano ~/.asoundrc` and add:

      ```bash
      pcm.!default {
        type asym
        capture.pcm "mic"
        playback.pcm "speaker"
      }
      pcm.mic {
        type plug
        slave {
          pcm "hw:<card number>,<device number>"
        }
      }
      pcm.speaker {
        type plug
        slave {
          pcm "hw:<card number>,<device number>"
        }
      }
      ```

      You can print hw info by command  `aplay -l` and `arecord -l` 

   3. `sudo reboot` 



## Notes

1. 目前實驗最適合辨識的音檔格式是16000k, 單聲道
2. alsamixer 可以在ssh 內調音量，但是每次重開機都會跑掉，所以調完音量後要下 `sudo alsactl store`
3. pi 0. 的記憶體較小，耗盡後有可能會發生aplay 無法播放的問題，故需要調整swap 設定 `/etc/dphys-swapfile `
4. ip.py 經回報開機啟動時有機率無法回報 ip, 有可能卡住，請在 rc.local 先加 sleep 試試看

## Changelog

### 2018.12.18 Edge computing 已經成功，撰寫在另外一個專案，目前由紹全嘗試將此專案連接至本地辨識

### 2018.12.09 添加自動開機啟動以及自動報ip 和語音關機功能，唯語音辨識無法辨識到關機中

### 2018.12.07  採用新版image 並嘗試撰寫 loop主程式架構以利整合其他收音機、煩惱音樂推薦程式

### 2018.12.05 在 AIY github 討論區發現官方認為pyaudio 太雷，改採用 aplay and arecord

### 2018.11 俊榕接手，把症狀特徵以及上傳程序先移除以簡化程式碼以利 Demo

### 2018.09 初版台語問診音箱發展 by 育霖，已封存到別的專案



## Authors

* Gbanyan 黃俊榕


