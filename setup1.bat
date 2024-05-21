@echo off

cd "python"
installer

cd ".."
cd "backend"
pip install -r requirements.txt
timeout /t 5
cd ".."
