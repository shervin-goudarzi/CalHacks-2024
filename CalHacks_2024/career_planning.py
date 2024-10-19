import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai
import os

cred = credentials.Certificate("path to json file")
firebase_admin.initialize_app(cred)
db = firestore.client()
def load_user_profile(user_id):
