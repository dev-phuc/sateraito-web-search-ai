# メモリ使用量が大きいライブラリを使用している。現状未使用なのでいったんコメントアウト
#from .vector_database import Redis
# メモリ使用量が大きいライブラリを使用している。現状未使用なのでいったんコメントアウト
#from .firestore import FirestoreDB
from .realtime_database import RealTimeDB
# メモリ使用量が大きいライブラリを使用している。現状未使用なのでいったんコメントアウト
#from .firebase_init import realtime_db, firestore_db
from .firebase_init import realtime_db