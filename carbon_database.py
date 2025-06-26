import firebase_admin
from firebase_admin import credentials, db, auth
from datetime import datetime

import json
import os

cred_dict = json.loads(os.environ["FIREBASE_KEY"])
cred = credentials.Certificate(cred_dict)

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://console.firebase.google.com/project/carbon-emission-trac/overview' 
})

def sign_up(email, password):
    user = auth.create_user(email=email, password=password)
    print("User created:", user.uid)
    return user.uid

def log_emission(user_id, activity_data):
    date = datetime.now().strftime("%Y-%m-%d")
    total_emission = sum(activity_data.values())
    ref = db.reference(f'Users/{user_id}/emissions/{date}')
    ref.set({
        'activities': activity_data,
        'total_emission': total_emission,
        'timestamp': datetime.now().isoformat()
    })
    print("Emission logged successfully.")

def get_user_emissions(user_id):
    ref = db.reference(f'Users/{user_id}/emissions')
    return ref.get()