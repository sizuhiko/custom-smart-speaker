#!/usr/bin/env python3

import aiy.audio
import aiy.cloudspeech
import aiy.i18n
import aiy.voicehat

import snowboydecoder

from google.cloud import texttospeech
from mutagen.mp3 import MP3 as mp3
import pygame
import time

import os
import sys
import uuid

aiy.i18n.set_language_code('ja-JP')
myuuid = str(uuid.uuid4())
model = os.path.join(os.path.dirname(__file__), 'hotword.pmdl')
skills = {
  "テレビつけて": tv_on
}

def tv_on():
  say("TVの電源を入れます")

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
  response = client.synthesize_speech(synthesis_input, voice, audio_config)

  # The response's audio_content is binary.
  filename = 'output.mp3'
  with open(filename, 'wb') as out:
    # Write the response to the output file.
    out.write(response.audio_content)
    print('Audio content written to file "output.mp3"')

  pygame.mixer.init()
  pygame.mixer.music.load(filename)
  mp3_length = mp3(filename).info.length
  pygame.mixer.music.play(1)
  time.sleep(mp3_length + 0.25)
  pygame.mixer.music.stop()

def main():
  detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)
  recognizer = aiy.cloudspeech.get_recognizer()
  text_recognizer = detect_intent_texts.get_recognizer()
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
    else
    print('INFO:"', text, '"')
      
if __name__ == '__main__':
  main()