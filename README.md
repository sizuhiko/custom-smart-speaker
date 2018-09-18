# mr.concie

Custom Smart Speaker made by [AIY Voice Kit](https://aiyprojects.withgoogle.com/voice/)

## Requirements

- Node.js (>= v6.11.5)
- Python (>= v3.5.3)
  - pip (>= v6.1)
  - pip-tools

### Raspberry Pi 3

Please see [Installing Python 3.6 on Raspbian](https://gist.github.com/dschep/24aa61672a2092246eaca2824400d37f) if you use Raspberry Pi 3.

## Platform Dependencies

Followings dependencies requires library depends each platform.
Please check and install the libraries.

- [snowboy](https://github.com/Kitt-AI/snowboy)
  - install npm
  - [Install Dependencies](https://github.com/Kitt-AI/snowboy#dependencies)
- Google AIY Voice Kit
  - [Setup the Assistant](https://aiyprojects.withgoogle.com/voice/#google-assistant)
  - [CUSTOM VOICE USER INTERFACE](https://aiyprojects.withgoogle.com/voice/#makers-guide--custom-voice-user-interface)

### Raspberry Pi 3

## Install

### Install additional dependencies

```
# install snowboy
$ npm install
# install text to speech dependencies
$ pip install -r requirements.txt
```

### Compile Snowboy Python3 Wrapper

```
$ cd node_modules/snowboy/swig/Python3

# Please change line #5 of Makefile if you use Ubuntu/Raspberry Pi/Pine64/Nvidia Jetson TX1/Nvidia Jetson TX2
# #SWIG := swig
# SWIG := swig3.0

$ make
```

### Generate credentials

Check [Generate credentials](https://developers.google.com/assistant/sdk/guides/library/python/embed/install-sample#generate_credentials) page.
`Authorization tool` has installed by `install application dependencies`.
Only use `google-oauthlib-tool`, can generate credentials.

### Generate your HOTWORD

Generate your HOTWORD for starting your google assistant app. 
HOTWORD can generate with [snowboy HOTWORD DETECTION](https://snowboy.kitt.ai/).
Generate and download your HOTWORD, rename to `hotword.pmdl` and put to the app root.

## Run

```
$ main.py
```

Please say your HOTWORD like a `OK, Google`.
Enjoy !

