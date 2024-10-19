import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai
import os
import career_resources
from dotenv import load_dotenv

#Loading the environment variables
load_dotenv()

#Initializing firebase cuz i have no life(commented out for now)
# cred = credentials.Certificate("path to json file")
# firebase_admin.initialize_app(cred)
# db = firestore.client()

#Configuring the Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

#Dummy user data for testing cuz we got no firebase yet lmfao
user_profiles = {
    "random_user_id": {
        "skills": ["Python", "Data Analysis"],
        "education": ["Computer Science"],
        "desired_industry": "AI",
        "immigration_status": "Permanent Resident"
    }
}

def load_user_profile(user_id):
    """Load user data (dummy implementation for testing)"""
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
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-002",
        generation_config=generation_config,
    )

    # chat_session = model.start_chat(history=[])

    prompt = f"""Given the user's skills: {skills}, education: {education}, desired industry:
      {desired_industry}, and immigration status: {immigration_status}, suggest potential career paths."""
    response = model.generate_content(prompt)

    # if response and 'choices' in response:
    #     career_paths.extend([choice['message'] for choice in response['choices']])
    
    # return career_paths
    return response


def generate_career_growth_plan(user_data, career_paths):
    """Generate short and long-term career growth plans"""
    career_growth_plan = {}
    skills = user_data.get('skills', [])

    for career in career_paths:
        #fetching the missing career skills for each career
        required_skills = get_required_skills_for_career(career) #placeholder function for now
        missing_skills = [skill for skill in required_skills if skill not in skills]

        #Suggesting the courses to bridge the skill gaps
        suggested_courses = []
        for skill in missing_skills:
            suggested_courses.extend(career_resources.fetch_courses(skill))

        #Creating the action plan
        action_plan = {
            'short_term_goals': [f"Take course: {course['name']}" for course in suggested_courses],
            'long_term_goals': [f"Get an entry-level job in {career}"]
        }
        career_growth_plan[career] = action_plan
    
    return career_growth_plan

def get_required_skills_for_career(career):
    """Placerholder function to get required skills for a given career"""
    career_skill_mapping = {
        "Data Scientist": ["Python", "Data Analysis", "Machine Learning"],
        "Business Analyst": ["Excel", "Data Analysis", "Business Modeling"],
        "Front-End Developer": ["HTML", "CSS", "JavaScript"],
        "Machine Learning Engineer": ["Python", "TensorFlow", "Deep Learning"]
    }
    return career_skill_mapping.get(career, [])

#Testing whatever the hell this code is
user_id = "random_user_id"
user_data = load_user_profile(user_id)

if user_data:
    career_paths = recommend_career_path(user_data)
    career_growth_plan = generate_career_growth_plan(user_data, career_paths)

    #Displaying the results
    print("Career Recommendations:", career_paths)
    print("Career Growth Plan:", career_growth_plan)
else:
    print("User profile not found")