@ cd /D %~dp0

setlocal

set frontendDir=frontend\dist
set backendDir=backend\src\static\frontend
set backendTemplateDir=backend\src\templates

call rimraf .\backend\src\static\frontend\

cd frontend
call npm run clean
call npm run build
call echo D
cd ..

@REM cd backend

xcopy /S /H /E /R /C /Y /D %frontendDir% %backendDir%
copy %frontendDir%\index.html %backendTemplateDir%\reactjs_frontend.html

@REM pause
@REM cd ..