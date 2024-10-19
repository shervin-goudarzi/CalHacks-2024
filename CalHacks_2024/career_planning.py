import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai
import os

#Initializing firebase cuz i have no life(commented out for now)
# cred = credentials.Certificate("path to json file")
# firebase_admin.initialize_app(cred)
# db = firestore.client()

#Dummy user data for testing cuz we got no firebase yet lmfao
user_profiles = {
    "example_user_id": {
        "skills": ["Python", "Data Analysis"],
        "education": ["Computer Science"],
        "desired_industry": "AI",
        "immigration_status": "Permanent Resident"
    }
}


def load_user_profile(user_id):
    """Load user data from Firebase """
    return user_profiles.get(user_id, None)

def recommend_career_path(user_data):
    career_paths = []
    skills = user_data.get('skills', [])
    education = user_data.get('education', [])
    desired_industry = user_data.get('desired industry', '')
    immigration_status = user_data.get('immigration_status', '')

    # finna do simple logic-based rules for recs for now
    if "Computer Science" in education:
        if "Data Analysis" in skills:
            career_paths.append("Data Scientist")
            career_paths.append("Business Analyst")

        if "Web Development" in skills:
            career_paths.append("Front-End Developer")

    if desired_industry == "AI":
        career_paths.append("Machine Learning Engineer")

    #Using AI model for more personalized recs 
    prompt = f"Given the user's skills: {skills}, education: {education}, desired industry: {desired_industry}, and immigration status: {immigration_status}, suggest potential career paths."
    response = genai.chat(prompt)
    career_paths.extend(response.get('choices', []))

    return career_paths

def generate_career_growth_plan(user_data, career_paths):
    """Generate short and long-term career growth plans"""
    career_growth_plan = {}
    skills = user_data.get('skills', [])

    for career in career_paths:
        #fetching the missing career skills for each career
        required_skills = get_required_skills_for_career(career) #placeholder function for now
        