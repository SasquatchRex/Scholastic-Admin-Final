@echo off

cd "backend/project"
start "django" /B python manage.py runserver localhost:8000

cd ".."
cd ".."

cd "dist"
python -m webbrowser "http://localhost:8080" && start "backend" /B python -m http.server 8080
