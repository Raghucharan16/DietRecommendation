import requests
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

API_URL = "https://router.huggingface.co/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {os.environ['HF_TOKEN']}",
}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

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

def clean_response(text):
    """Clean the AI response to maintain professional medical tone"""
    if not text:
        return text
    
    # Remove casual phrases
    casual_phrases = [
        "Absolutely!", "Hey there", "Great question", "Of course!", 
        "Sure thing", "No problem", "Definitely", "For sure",
        "Totally", "Amazing", "Awesome", "Perfect", "Excellent question"
    ]
    
    cleaned_text = text
    for phrase in casual_phrases:
        cleaned_text = re.sub(r'\b' + re.escape(phrase) + r'\b[!,.]?\s*', '', cleaned_text, flags=re.IGNORECASE)
    
    # Remove exclamation marks at the beginning of sentences
    cleaned_text = re.sub(r'^\s*!+\s*', '', cleaned_text)
    cleaned_text = re.sub(r'\n\s*!+\s*', '\n', cleaned_text)
    
    # Ensure professional medical tone
    if cleaned_text and not cleaned_text.strip().startswith(('Based on', 'According to', 'Your', 'As a', 'Given')):
        cleaned_text = "Based on your health profile, " + cleaned_text.lstrip()
    
    return cleaned_text.strip()

def generate_diet_plan(user_data):
    bmr = calculate_bmr(user_data)
    tdee = calculate_tdee(bmr, user_data['exercise_level'])
    macros = calculate_macros(tdee)
    output_goal = user_data['output']

    goal_description = "Weight Loss" if output_goal == "weight_loss" else "Weight Gain"
    
    prompt = f"""Create a 7-day diet plan for {goal_description} for a {user_data['age']}-year-old {user_data['gender']} ({user_data['weight']}kg, {user_data['height']}cm, {user_data['exercise_level']} activity, maintain the tone in second person as you are suggesting).

Target: {tdee:.0f} calories daily | Macros: {macros['carbs']:.0f}g carbs, {macros['protein']:.0f}g protein, {macros['fat']:.0f}g fat
{"Note: Vegan options only" if user_data['vegan'].lower() == 'yes' else ""}

Format exactly as HTML:

<h3>Health Summary</h3>
<p>BMI: [calculate and state]. [Brief recommendation in 2-3 sentence]</p>

<h3>Weekly Diet Plan</h3>
<p><strong>Monday:</strong></p>
<ul>
<li>Breakfast: [meal]</li>
<li>Lunch: [meal]</li>
<li>Dinner: [meal]</li>
<li>Snack: [snack]</li>
</ul>

<p><strong>Tuesday:</strong></p>
<ul>
<li>Breakfast: [meal]</li>
<li>Lunch: [meal]</li>
<li>Dinner: [meal]</li>
<li>Snack: [snack]</li>
</ul>

[Continue for Wednesday through Sunday with same format]

Keep meals simple and practical."""

    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]

    try:
        response = query({
            "messages": messages,
            "model": "Qwen/Qwen3-Next-80B-A3B-Instruct:together",
            "max_tokens": 2400,
            "temperature": 0.7
        })
        
        if "choices" in response and len(response["choices"]) > 0:
            diet_plan = response["choices"][0]["message"]["content"]
            return clean_response(diet_plan)
        elif "error" in response:
            return f"Unable to generate diet plan at this time. Error: {response['error']}"
        else:
            return "Unable to generate diet plan due to unexpected response format."
            
    except Exception as err:
        return f"Unable to generate diet plan. Please try again later. Technical details: {err}"