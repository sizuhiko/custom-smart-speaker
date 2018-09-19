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

aiy.i18n.set_language_code('ja-JP')
myuuid = str(uuid.uuid4())
model = os.path.join(os.path.dirname(__file__), 'hotword.pmdl')

# SKILL's function
def tv_on():
  say("TVの電源を入れます")

# SKILL map
skills = {
  "テレビつけて": tv_on
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
  detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)
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