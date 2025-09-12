import firebase_admin
from firebase_admin import credentials, db
# メモリ使用量が大きいライブラリを使用している。現状未使用なのでいったんコメントアウト
#from firebase_admin import firestore

# sateraito_inc.py から設定取得するように変更
#from dotenv import load_dotenv
import sateraito_inc
import os

# sateraito_inc.py から設定取得するように変更
#load_dotenv()

# sateraito_inc.py から設定取得するように変更
#cred = credentials.Certificate({
#    "type": "service_account",
#    "project_id": sateraito_inc.FIREBASE_PROJECT_ID'),
#    "private_key_id": sateraito_inc.FIREBASE_PRIVATE_KEY_ID'),
#    "private_key": sateraito_inc.FIREBASE_PRIVATE_KEY').replace('\\n', '\n'),
#    "client_email": sateraito_inc.FIREBASE_CLIENT_EMAIL'),
#    "client_id": sateraito_inc.FIREBASE_CLIENT_ID'),
#    "auth_uri": sateraito_inc.FIREBASE_AUTH_URI'),
#    "token_uri": sateraito_inc.FIREBASE_TOKEN_URI'),
#    "auth_provider_x509_cert_url": sateraito_inc.FIREBASE_AUTH_PROVIDER_X509_CERT_URL'),
#    "client_x509_cert_url": sateraito_inc.FIREBASE_CLIENT_X509_CERT_URL')
#},)
#firebase_app = firebase_admin.initialize_app(cred, {
#    "databaseURL": "https://sateraito-chatgpt-default-rtdb.firebaseio.com"
#})
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": sateraito_inc.FIREBASE_PROJECT_ID,
    "private_key_id": sateraito_inc.FIREBASE_PRIVATE_KEY_ID,
    "private_key": sateraito_inc.FIREBASE_PRIVATE_KEY.replace('\\n', '\n'),
    "client_email": sateraito_inc.FIREBASE_CLIENT_EMAIL,
    "client_id": sateraito_inc.FIREBASE_CLIENT_ID,
    "auth_uri": sateraito_inc.FIREBASE_AUTH_URI,
    "token_uri": sateraito_inc.FIREBASE_TOKEN_URI,
    "auth_provider_x509_cert_url": sateraito_inc.FIREBASE_AUTH_PROVIDER_X509_CERT_URL,
    "client_x509_cert_url": sateraito_inc.FIREBASE_CLIENT_X509_CERT_URL
},)
firebase_app = firebase_admin.initialize_app(cred, {
    "databaseURL": sateraito_inc.FIREBASE_DATABASE_URL
})

# メモリ使用量が大きいライブラリを使用している。現状未使用なのでいったんコメントアウト
#firestore_db = firestore.client()
realtime_db = db
