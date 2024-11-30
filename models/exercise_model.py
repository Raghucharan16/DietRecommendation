# exercise_model.py

from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch

tokenizer = GPT2Tokenizer.from_pretrained('distilgpt2')
tokenizer.pad_token = tokenizer.eos_token

model = GPT2LMHeadModel.from_pretrained('distilgpt2')
model.eval()
model.eval() 

def generate_exercise_plan(user_data):
    # Construct a detailed prompt
    prompt = f"""
    Create a personalized and detailed exercise plan for the following individual:

    - Age: {user_data['age']} years old
    - Gender: {user_data['gender'].capitalize()}
    - Weight: {user_data['weight']} kg
    - Height: {user_data['height']} cm
    - Exercise Level: {user_data['exercise_level'].capitalize()}

    The exercise plan should cover one week, detailing daily activities including type of exercise, duration, intensity, and any relevant notes. The plan should be appropriate for the individual's current fitness level and goals. Include a mix of cardio, strength training, and flexibility exercises.

    Exercise Plan:
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
    exercise_plan = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Extract the generated exercise plan portion
    exercise_plan = exercise_plan[len(prompt):].strip()

    return exercise_plan