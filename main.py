#!/usr/bin/env python3

import aiy.audio
import aiy.cloudspeech
import aiy.i18n
import aiy.voicehat
import aiy.assistant.auth_helpers
import aiy.assistant.device_helpers

import google.auth.transport.grpc
import google.auth.transport.requests
from googlesamples.assistant.grpc.textinput import SampleTextAssistant

import snowboydecoder

from google.cloud import texttospeech
from mutagen.mp3 import MP3 as mp3
import pygame
import time

import os
import sys
import uuid
import smbus

aiy.i18n.set_language_code('ja-JP')
myuuid = str(uuid.uuid4())
model = os.path.join(os.path.dirname(__file__), 'hotword.pmdl')

# for RPI version 1, use "bus = smbus.SMBus(0)"
bus = smbus.SMBus(1)

# This must match in the Arduino Sketch
#SLAVE_ADDRESS = 0x04
SLAVE_ADDRESS = 0x52
data_numH = 0x31
data_numL = 0x32
data_numHL = [0x00,0x31,0x32]
data_num = 10
memo_no = 0
block = []

#command
R1_memo_no_write = 0x15  #bus-write(ADR,cmd,1)
R2_data_num_read = 0x25 #bus-read(ADR,cmd,3)
R3_data_read           = 0x35 #bus-read(ADR,cmd,n)
W1_memo_no_write  = 0x19 #bus-write(ADR,cmd,1)
W2_data_num_write = 0x29 #bus-write(ADR,cmd,3)
W3_data_write           = 0x39 #bus-read(ADR,cmd,n)
W4_flash_write           = 0x49 #bus-read(ADR,cmd,n)
T1_trans_start             = 0x59 #bus-write(ADR,cmd,1)

def trans_command(block2):
  str_tmp = ""
  int_tmp = []
  for i in range(int(len(block2)//2)):
    str_tmp = block2[i*2] + block2[i*2+1]
    int_tmp.append( int(str_tmp, 16))
  # cmd W2_data_num_write 0x29 bus-write(ADR,cmd,3)
  data_num = int(len(int_tmp)//4)  #for test
  data_numHL = [0x31,0x32] #for test
  data_numHL[0] = int(data_num//256)
  data_numHL[1] = int(data_num%256)
  bus.write_i2c_block_data(SLAVE_ADDRESS, W2_data_num_write ,  data_numHL)   #= 
  data_numHL = [0x31,0x32,0x33,0x34] #for test 
  for i in range(data_num):
    data_numHL[0] = int_tmp[i*4+0]
    data_numHL[1] = int_tmp[i*4+1]
    data_numHL[2] = int_tmp[i*4+2]
    data_numHL[3] = int_tmp[i*4+3]
    bus.write_i2c_block_data(SLAVE_ADDRESS, W3_data_write , data_numHL)   #= 
  # cmd T1_trans_start             0x59 bus-write(ADR,cmd,1)
  memo_no = [0x00 ] #for dummy
  bus.write_i2c_block_data(SLAVE_ADDRESS, T1_trans_start,memo_no )   #= 

# SKILL's function
def tv_on():
  say("TVの電源を入れます")
  trans_command('5D0018002E001800180018002E001800180018002F00180017001800180018002F0018001700180018001800180018001700D7035D0018002E001800180018002E001800180018002F00180017001800180018002F0018001700180018001800180018001600D8035D0018002E001800180018002E001800180018002F00180017001800180018002F0018001700180018001800180018001700D9035D0018002E001800180018002E001800180018002F00180017001800180018002F0017001800180018001800180018001700D9035C0018002F001800180017002F001800180018002E00180018001800180018002E0018001800180017001800180018001800D8035D0018002E001800180018002F001800170018002F00180017001800180018002F0018001700180018001800180018001700D9035D0017002F001800180018002E001800180018002E00180018001800180018002E0018001800180018001800170018001800D9035C0018002F001800170018002F001800180018002E00180018001800180017002F0018001800180017001800180018001800D8035D0018002E001800180018002F001800170018002F00180017001800180018002F00180017001800180018001800180017004205')

def tv_off():
  say("TVの電源を消します")
  trans_command('5D0018002E001800180018002E001800180018002F00180017001800180018002F0018001700180018001800180018001700D7035D0018002E001800180018002E001800180018002F00180017001800180018002F0018001700180018001800180018001600D8035D0018002E001800180018002E001800180018002F00180017001800180018002F0018001700180018001800180018001700D9035D0018002E001800180018002E001800180018002F00180017001800180018002F0017001800180018001800180018001700D9035C0018002F001800180017002F001800180018002E00180018001800180018002E0018001800180017001800180018001800D8035D0018002E001800180018002F001800170018002F00180017001800180018002F0018001700180018001800180018001700D9035D0017002F001800180018002E001800180018002E00180018001800180018002E0018001800180018001800170018001800D9035C0018002F001800170018002F001800180018002E00180018001800180017002F0018001800180017001800180018001800D8035D0018002E001800180018002F001800170018002F00180017001800180018002F00180017001800180018001800180017004205')

def light_on():
  say("照明の電源を入れます")
  trans_command('850043001200120011001200110033001100330011001200110032001200120011001200110011001200330011001100120011001200320012001100120032001200110012003200120011001200110012003200120011001200110012001100120011001200320012001100120032001200320012001100120032001200110012001100120011001100120011003300120011001100120011003300110012001100120011004205')

def light_off():
  say("照明の電源を消します")
  trans_command('860043001100120011001200110033001100330011001200110033001100120011001200110012001100330011001100120012001100320012001200110032001200110012003200120012001100110012003200120012001100110012001100120011001200320012003200120032001200330011001200110033001100120011001100120011001200320012003300110011001200120011003200120011001200110012004205')

# SKILL map
skills = {
  "テレビつけて": tv_on,
  "テレビ消して": tv_off,
  "照明つけて": light_on,
  "照明消して": light_off
}

def callbacks():
  #snowboydecoder.play_audio_file(snowboydecoder.DETECT_DING)
  global interrupted
  interrupted = True

def interrupt_callback():
  global interrupted
  return interrupted

def say(text):
  # Instantiates a client
  client = texttospeech.TextToSpeechClient()

  # Set the text input to be synthesized
  synthesis_input = texttospeech.types.SynthesisInput(text=text)

  # Build the voice request, select the language code ("en-US") and the ssml
  # voice gender ("neutral")
  voice = texttospeech.types.VoiceSelectionParams(
    language_code='ja-JP',
    ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE)

  # Select the type of audio file you want returned
  audio_config = texttospeech.types.AudioConfig(
    audio_encoding=texttospeech.enums.AudioEncoding.MP3)

  # Perform the text-to-speech request on the text input with the selected
  # voice parameters and audio file type
  try:
    response = client.synthesize_speech(synthesis_input, voice, audio_config)
  except:
    pass

  # The response's audio_content is binary.
  filename = 'output.mp3'
  with open(filename, 'wb') as out:
    # Write the response to the output file.
    out.write(response.audio_content)
    print('Audio content written to file "output.mp3"')

  pygame.mixer.init()
  pygame.mixer.music.load(filename)
  mp3_length = mp3(filename).info.length
  pygame.mixer.music.set_volume(40 / 100)
  pygame.mixer.music.play(1)
  time.sleep(mp3_length + 0.25)
  pygame.mixer.music.stop()

def call_assistant(text):
  credentials = aiy.assistant.auth_helpers.get_assistant_credentials()
  http_request = google.auth.transport.requests.Request()
  grpc_channel = google.auth.transport.grpc.secure_authorized_channel(
    credentials, http_request, 'embeddedassistant.googleapis.com')
  model_id, device_id = aiy.assistant.device_helpers.get_ids_for_service(credentials)
  with SampleTextAssistant('ja-JP', model_id, device_id,
                           grpc_channel, 60 * 3 + 5) as assistant:
    response_text = assistant.assist(text_query=text)
    say(response_text)

def main():
  detector = snowboydecoder.HotwordDetector(model, sensitivity=0.6)
  recognizer = aiy.cloudspeech.get_recognizer()
  status_ui = aiy.voicehat.get_status_ui()
  aiy.audio.get_recorder().start()

  while True:
    print('INFO:Speak Wake Word and speak')
    status_ui.status('ready')

    global interrupted
    interrupted = False

    detector.start(detected_callback=callbacks,
                   interrupt_check=interrupt_callback,
                   sleep_time=0.03)

    print('INFO:Listening...')
    status_ui.status('thinking')
    text = recognizer.recognize()

    if not text:
      print('INFO:Sorry, I did not hear you.')
    elif text in skills:
      print('INFO:Skill:', text, '"')
      skills[text]()
    else:
      print('INFO:"', text, '"')
      call_assistant(text)
      
if __name__ == '__main__':
  main()