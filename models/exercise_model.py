import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the Inference Client
# client = InferenceClient(api_key=os.getenv("HUGGINGFACE_API_KEY"))
API_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"
headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}


def generate_exercise_plan(user_data):
    prompt = f"""As a professional fitness trainer, create a detailed weekly exercise plan for:

Age: {user_data['age']} years
Gender: {user_data['gender'].capitalize()}
Weight: {user_data['weight']} kg
Height: {user_data['height']} cm
Fitness Level: {user_data['exercise_level'].capitalize()}

Create a 7-day exercise program including:
1. Types of exercises for each day
2. Sets, reps, and duration
3. Rest periods
4. Intensity levels
5. Warm-up and cool-down routines

Focus on:
- Cardiovascular health
- Strength training
- Flexibility
- Rest and recovery

Provide specific instructions for form and technique for each exercise.
"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 500,
            "do_sample": True,
            "temperature": 0.7,
            "top_p": 0.9,
            "repetition_penalty": 1.15,
        },
        "options": {
            "use_cache": True,
            "wait_for_model": True
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        if isinstance(result, list) and 'generated_text' in result[0]:
            generated_text = result[0]['generated_text']
            # Extract the generated exercise plan portion
            exercise_plan = generated_text[len(prompt):].strip()
            return exercise_plan
        else:
            error_message = result.get('error', 'Unknown error occurred.')
            return f"Error: {error_message}"
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except Exception as err:
        return f"Error generating exercise plan: {err}"