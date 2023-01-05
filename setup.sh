#!/usr/bin/env bash
sudo apt update
sudo apt --fix-broken install
sudo apt install pip -y
sudo apt install ffmpeg -y
python3 -m pip install -r requirements.txt