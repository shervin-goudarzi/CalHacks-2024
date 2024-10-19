import os
import google.generativeai as genai
from apify_client import ApifyClient
import json

# Initialize the ApifyClient with your API token
client = ApifyClient("apify_api_wOIxO9ITqQ9N2SjXH1qybkDUeGDnw64gYhmC")

# Configure Gemini
genai.configure(api_key="AIzaSyBlkAovzBE3rN-nqeC66Itc7kjzeGIf1lc")

def run_indeed_scraper(skills, zipcode):
    # Join skills into a query string for the position
    skill_query = " OR ".join(skills)
    
    # Prepare the run input
    run_input = {
        "country": "US",
        "location": zipcode,
        "position": skill_query,
        "maxItems": 20,  # Limit the number of results for this example
        "includeUnfilteredResults": True
    }
    
    # Run the Indeed scraper
    run = client.actor("misceres/indeed-scraper").call(run_input=run_input)
    
    # Fetch job postings from the default dataset
    recommended_jobs = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        # You can add additional filtering here if needed
        recommended_jobs.append(item)
    
    return recommended_jobs

def format_jobs_for_gemini(recommended_jobs):
    job_strings = []
    for job in recommended_jobs:
        job_string = json.dumps({
            'positionName': job.get('positionName', 'N/A'),
            'salary': job.get('salary', 'N/A'),
            'description': job.get('description', 'N/A'),
            'company': job.get('company', 'N/A'),
            'location': job.get('location', 'N/A'),
            'url': job.get('url', 'N/A')
        })
        job_strings.append(job_string)
    return '#######'.join(job_strings)

def get_gemini_recommendations(formatted_job_string, education, immigration_status):
    # Create the model
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

    chat_session = model.start_chat(history=[])

    prompt = f"""The following is an aggregation JSON file of all potential jobs for an applicant. Each job is sepaarated by '#######'.
    The applicant's education is {education} and their current immigration status is {immigration_status}. 
    Out of these jobs find the top 10 jobs that are the most preferable for the given candidate given the education level and immigration status above. 
    For each chosen job, neatly organize and output the Job title ('positionName'), the salary ('salary'), 
    the job description ('description'), the company ('company'), the location ('location'), and the job URL ('url'). 
    Don't include any other extra information in the output. 

    Jobs: {formatted_job_string}"""

    response = chat_session.send_message(prompt)
    return response.text

# Example usage
skills = ["Construction", "Truck Driver"]
zipcode = "94103"
education = "High School Diploma"
immigration_status = "Permanent Resident"

try:
    # Fetch the recommended jobs
    recommended_jobs = run_indeed_scraper(skills, zipcode)
    
    # Format jobs for Gemini
    formatted_job_string = format_jobs_for_gemini(recommended_jobs)
    
    # Get Gemini recommendations
    gemini_recommendations = get_gemini_recommendations(formatted_job_string, education, immigration_status)
    
    # Print Gemini recommendations
    print(gemini_recommendations)

except Exception as e:
    print(f"An error occurred: {str(e)}")