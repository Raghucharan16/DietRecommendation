import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_URL = "https://api-inference.huggingface.co/models/Qwen/QwQ-32B-Preview"
headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}


def generate_exercise_plan(user_data):

    output_goal = user_data['output'] 
    goal_description = "Weight Loss" if output_goal == "weight_loss" else "Weight Gain"
    prompt =  prompt = f"""As a professional body training expert and nutritionist, provide a personalized analysis and advice for the following individual, aiming for {goal_description}.

    **User Information:**
    - Age: {user_data['age']} years
    - Gender: {user_data['gender'].capitalize()}
    - Weight: {user_data['weight']} kg
    - Height: {user_data['height']} cm
    - Fitness Level: {user_data['exercise_level'].capitalize()}

    **Instructions:**
    1. Provide a brief analysis of the user's current fitness status based on the data above.
    2. Offer personalized advice to help them achieve their fitness goals.
    3. Create a structured 7-day exercise program including:
        - Types of exercises for each day
        - Sets, reps,duration, and rest intervals
        - Intensity levels
        - Warm-up and cool-down routines
    4. Provide specific instructions for form and technique for each exercise.

    **Begin with the analysis and advice:**
    """

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 1024,
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