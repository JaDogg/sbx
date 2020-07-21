@echo off
python -m unittest
pyinstaller sbx\sbx_main.py --icon images\clubs.ico -n sbx
