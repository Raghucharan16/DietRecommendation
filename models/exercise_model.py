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

def clean_response(text):
    """Clean the AI response to maintain professional fitness advisor tone"""
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
    
    # Ensure professional fitness advisor tone
    if cleaned_text and not cleaned_text.strip().startswith(('Based on', 'According to', 'Your', 'As a', 'Given')):
        cleaned_text = "Based on your fitness profile, " + cleaned_text.lstrip()
    
    return cleaned_text.strip()

def generate_exercise_plan(user_data):
    output_goal = user_data['output'] 
    goal_description = "Weight Loss" if output_goal == "weight_loss" else "Weight Gain"
    
    prompt = f"""Create a 7-day exercise plan for {goal_description} for a {user_data['age']}-year-old {user_data['gender']} ({user_data['weight']}kg, {user_data['height']}cm, {user_data['exercise_level']} fitness level, maintain the tone in second person as you are suggesting).

Format exactly as HTML:
        
<h3>Fitness Assessment</h3>
<p>[Brief fitness level assessment in 2-3 sentences]</p>

<h3>Weekly Exercise Plan</h3>
<p><strong>Monday:</strong> [Focus: e.g., Upper Body]</p>
<ul>
<li>[Exercise 1] - [reps/duration]</li>
<li>[Exercise 2] - [reps/duration]</li>
<li>[Exercise 3] - [reps/duration]</li>
<li>[Exercise 4] - [reps/duration]</li>
</ul>

<p><strong>Tuesday:</strong> [Focus: e.g., Cardio]</p>
<ul>
<li>[Exercise 1] - [reps/duration]</li>
<li>[Exercise 2] - [reps/duration]</li>
<li>[Exercise 3] - [reps/duration]</li>
<li>[Exercise 4] - [reps/duration]</li>
</ul>

[Continue for Wednesday through Sunday with same format]

Include rest days. Keep exercises simple and achievable."""

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
            "max_tokens": 2000,
            "temperature": 0.7
        })
        
        if "choices" in response and len(response["choices"]) > 0:
            exercise_plan = response["choices"][0]["message"]["content"]
            return clean_response(exercise_plan)
        elif "error" in response:
            return f"Unable to generate exercise plan at this time. Error: {response['error']}"
        else:
            return "Unable to generate exercise plan due to unexpected response format."
            
    except Exception as err:
        return f"Unable to generate exercise plan. Please try again later. Technical details: {err}"