from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch

tokenizer = GPT2Tokenizer.from_pretrained('Qwen/QwQ-32B-Preview')
tokenizer.pad_token = tokenizer.eos_token

model = GPT2LMHeadModel.from_pretrained('Qwen/QwQ-32B-Preview')
model.eval()  # Set model to evaluation mode

# Calculation functions
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
    # Assume 50% carbs, 20% protein, 30% fat
    macros = {
        'carbs': (tdee * 0.5) / 4,    # grams of carbs
        'protein': (tdee * 0.2) / 4,  # grams of protein
        'fat': (tdee * 0.3) / 9       # grams of fat
    }
    return macros

def generate_diet_plan(user_data):
    bmr = calculate_bmr(user_data)
    tdee = calculate_tdee(bmr, user_data['exercise_level'])
    macros = calculate_macros(tdee)
    
    # Construct a detailed prompt
    prompt = f"""
    Create a personalized and detailed diet plan for the following individual:

    - Age: {user_data['age']} years old
    - Gender: {user_data['gender'].capitalize()}
    - Weight: {user_data['weight']} kg
    - Height: {user_data['height']} cm
    - Vegan: {'Yes' if user_data['vegan'].lower() == 'yes' else 'No'}
    - Exercise Level: {user_data['exercise_level'].capitalize()}

    Calculated nutritional needs:

    - Basal Metabolic Rate (BMR): {bmr:.2f} kcal/day
    - Total Daily Energy Expenditure (TDEE): {tdee:.2f} kcal/day
    - Macronutrient Breakdown:
        - Carbohydrates: {macros['carbs']:.0f} grams/day
        - Protein: {macros['protein']:.0f} grams/day
        - Fat: {macros['fat']:.0f} grams/day

    Please provide a meal plan for one day that meets these nutritional requirements, including breakfast, lunch, dinner, and snacks. The meal plan should be tailored to the individual's preferences. Each meal should include portion sizes and brief preparation instructions.

    Diet Plan:
    """

    # Tokenize and encode the prompt
    inputs = tokenizer.encode(prompt, return_tensors='pt', truncation=True, max_length=1024, padding=True)
    inputs = inputs.to(model.device)

    # Generate text using the model
    outputs = model.generate(
        inputs,
        max_length=1024,
        do_sample=True,
        top_p=0.9,
        temperature=0.8,
        num_return_sequences=1,
        pad_token_id=tokenizer.eos_token_id
    )

    # Decode and process the generated text
    diet_plan = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Extract the generated diet plan portion
    diet_plan = diet_plan[len(prompt):].strip()

    return diet_plan