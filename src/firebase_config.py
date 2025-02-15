import firebase_admin
import os
from firebase_admin import credentials, storage, firestore

# Initialize Firebase 
cred = credentials.Certificate('firebase_credentials.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET')
})

# Firebase Storage and Firestore instances
bucket = storage.bucket()
db = firestore.client()