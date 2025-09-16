SET PROJECT=vn-sateraito-apps-timecard2
SET VERSION=aisearch

TITLE %PROJECT% ver=%VERSION%(gcloud)

cd .\backend\src

call gcloud app deploy index.yaml --project=%PROJECT% --version=%VERSION% --no-cache --no-promote --no-stop-previous-version

cd ..\..\
