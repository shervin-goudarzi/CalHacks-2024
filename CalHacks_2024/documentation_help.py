import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def get_immigration_info(status):
    # Create the model
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro-002",
        generation_config=generation_config,
    )

    prompt = f"""
        Given the immigration status {status}, provide a detailed, step-by-step guide on the next steps in the immigration process or the required documentation.
    Format the response as a JSON object with the following structure:
    {{
    "current_status": "Description of the current status",
    "next_steps": [
    {{
    "step": "Step 1",
    "description": "Detailed description of step 1"
    }},
    {{
    "step": "Step 2",
    "description": "Detailed description of step 2"
    }},
    ...
    ],
    "required_documents_to_fill": [
    "Document 1 needed to maintain immigration status or continue through a permanent residency/citizenship": "Description of Document 1 and detailed instructions on how to access this document",
    "Document 2 needed to maintain immigration status or continue through a permanent residency/citizenship ": "Description of Document 2 and detailed instructions on how to access this document",
    ...
    ],
    "required_documents_download_link": [
    "Document 1": "Download Blank Document Link or Example Document Download Link",
    "Document 2": "Download Blank Document Link or Example Document Download Link",
    ...
    ],
    "additional_info": "Any additional relevant information"
    }}
    """

    response = model.generate_content(prompt)
    return response.text

def display_immigration_info(info):
    print(info)
    # print("\n=== Immigration Information ===\n")
    # print(f"Current Status: {info['current_status']}\n")
    
    # print("Next Steps:")
    # for i, step in enumerate(info['next_steps'], 1):
    #     print(f"{i}. {step['step']}")
    #     print(f"   {step['description']}\n")
    
    # print("Required Documents:")
    # for doc in info['required_documents']:
    #     print(f"- {doc}")
    
    # print(f"\nAdditional Information: {info['additional_info']}")

def main():
    status = input("Enter your immigration status: ")
    info = get_immigration_info(status)
    display_immigration_info(info)

if __name__ == "__main__":
    main()