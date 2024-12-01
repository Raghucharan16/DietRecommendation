import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the Inference Client
# client = InferenceClient(api_key=os.getenv("HUGGINGFACE_API_KEY"))
API_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"
headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}

def calculate_bmr(user_data):
    gender = user_data['gender'].lower()
    if gender == 'male':
        bmr = 10 * user_data['weight'] + 6.25 * user_data['height'] - 5 * user_data['age'] + 5
    else:
        bmr = 10 * user_data['weight'] + 6.25 * user_data['height'] - 5 * user_data['age'] - 161
    return bmr

def calculate_tdee(bmr, exercise_level):
    activity_levels = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'very active': 1.9
    }
    factor = activity_levels.get(exercise_level.lower(), 1.2)
    return bmr * factor

def calculate_macros(tdee):
    macros = {
        'carbs': (tdee * 0.5) / 4,
        'protein': (tdee * 0.2) / 4,
        'fat': (tdee * 0.3) / 9
    }
    return macros

def generate_diet_plan(user_data):
    bmr = calculate_bmr(user_data)
    tdee = calculate_tdee(bmr, user_data['exercise_level'])
    macros = calculate_macros(tdee)
    
    # Construct your prompt
    prompt = f"""As a professional nutritionist, create a detailed one-day meal plan for:

Age: {user_data['age']} years
Gender: {user_data['gender'].capitalize()}
Weight: {user_data['weight']} kg
Height: {user_data['height']} cm
Vegan: {'Yes' if user_data['vegan'].lower() == 'yes' else 'No'}
Exercise Level: {user_data['exercise_level'].capitalize()}

Daily Requirements:
- Total Calories: {tdee:.0f} kcal
- Carbohydrates: {macros['carbs']:.0f}g
- Protein: {macros['protein']:.0f}g 
- Fat: {macros['fat']:.0f}g

Provide a structured meal plan with:
1. Breakfast
2. Morning Snack
3. Lunch
4. Afternoon Snack
5. Dinner

For each meal include:
- Specific foods and portions
- Calories per meal
- Preparation instructions
- Macronutrient breakdown
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
            # Extract the generated diet plan portion
            diet_plan = generated_text[len(prompt):].strip()
            return diet_plan
        else:
            error_message = result.get('error', 'Unknown error occurred.')
            return f"Error: {error_message}"
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except Exception as err:
        return f"Error generating diet plan: {err}"