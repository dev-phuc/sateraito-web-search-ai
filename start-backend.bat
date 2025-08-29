@echo off
echo Starting Sateraito Web Search AI...

cd /d %~dp0backend/src
docker-compose down
docker-compose up --build

cd ..
echo Flask app started. Press any key to stop.