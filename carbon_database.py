import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, db, auth
from datetime import datetime

# Initialize Firebase only once
if not firebase_admin._apps:
    cred_dict = json.loads(st.secrets["FIREBASE_KEY"])
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred, {
        'databaseURL': st.secrets["FIREBASE_DB_URL"]
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
