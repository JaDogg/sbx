@echo off
python -m unittest
pyinstaller sbx\__main__.py --icon images\clubs.ico -n sbx
