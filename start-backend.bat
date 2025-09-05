@echo off
echo Starting Sateraito Web Search AI...

cd backend

call code .

cd src
docker-compose down
docker-compose up --build

cd ..
echo Flask app started. Press any key to stop.