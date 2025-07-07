@echo off
cd /d "C:\Users\VIKI\Desktop\Diplomna-source\balanced_nutrition"
call venv\Scripts\activate.bat
python manage.py update_water_once_daily >> logs\water_log.txt 2>&1
