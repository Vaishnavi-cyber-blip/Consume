from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from groq import Groq
import re

app = Flask(__name__)
# CORS(app3, resources={r"/*": {"origins": "http://localhost:5173"}})  # Allow only your frontend
CORS(app, resources={r"/*": {"origins": "https://friendly-spork-vecd.onrender.com"}})

groq_api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_api_key)

@app.route('/analyze_claim', methods=['POST'])
def analyze_claim():
    data = request.json
    claim = data.get('claim')
    nutrition_text = data.get('nutritionText')

    # Define the prompt for LLaMA model
    prompt = f"""
    Compare the following product claim against the extracted text: "{nutrition_text}". 
    The claim to verify is: "{claim}". 
    Is the claim accurate? Provide a detailed and interactive analysis using the format below:

    **Example Analysis:**
    ---
    **Claim:**
    This product is 100% organic.

    **🔍 Claim Accuracy:**
    - The product contains some ingredients that are not certified organic.
    - The packaging does not specify certification for organic ingredients.
    - **🟡 Verdict**: This claim is **inaccurate** as not all ingredients are organic.

    **🧪 Ingredient Review:**
    - No evidence of added sugar in the ingredients list.
    - Nutritional facts confirm no sugars listed.
    - **🟢 Verdict**: The product is free from added sugars.

    **📊 Nutritional Facts Review:**
    - The product is low in carbohydrates and fats, supporting the claim of being healthy.
    - **🟡 Verdict**: The product is healthy but not organic as claimed.

    **🔍 Overall Observation:**
    - The product appears to be a processed fruit drink with a combination of fruit concentrates and purees, rather than being made with 100% original fruits.
    - The added sugar and processing steps do not align with the claim of being 100% pure or natural.

    **⚖️ Conclusion:**
    - The claim "Made with 100 percent original fruits" is **inaccurate**.
    - The product's ingredients and nutritional facts do not support this claim.
    - The presence of processed fruit concentrates, purees, and added sugar contradicts the idea of it being made with 100% original fruits.

    Now analyze the claim: "{claim}"
    ---
    """

    # Use Groq's API to process the text with the LLaMA model
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama3-8b-8192",
        max_tokens=500,
    )

    # Get the processed analysis from the response
    analysis_text = chat_completion.choices[0].message.content
    print("Full analysis_text from LLM:", analysis_text)

    # Now parse the response text to match the sections
    # Using simpler regex patterns to capture content after symbols
    claim_match = re.search(r'\*\*Claim:\*\*\n(.*?)\n', analysis_text, re.S)
    claim_accuracy_match = re.search(r'\*\*🔍 Claim Accuracy:\*\*\n(.*?)\n\*\*🧪', analysis_text, re.S)
    ingredient_review_match = re.search(r'\*\*🧪 Ingredient Review:\*\*\n(.*?)\n\*\*📊', analysis_text, re.S)
    nutritional_facts_match = re.search(r'\*\*📊 Nutritional Facts Review:\*\*\n(.*?)\n\*\*🔍', analysis_text, re.S)
    overall_observation_match = re.search(r'\*\*🔍 Overall Observation:\*\*\n(.*?)\n\*\*⚖️', analysis_text, re.S)
    conclusion_match = re.search(r'\*\*⚖️ Conclusion:\*\*\n(.*)', analysis_text, re.S)

    # Extract the groups and assign them to your response
    claim = claim_match.group(1).strip() if claim_match else ''
    claim_accuracy = claim_accuracy_match.group(1).strip() if claim_accuracy_match else ''
    ingredient_review = ingredient_review_match.group(1).strip() if ingredient_review_match else ''
    nutritional_facts = nutritional_facts_match.group(1).strip() if nutritional_facts_match else ''
    overall_observation = overall_observation_match.group(1).strip() if overall_observation_match else ''
    conclusion = conclusion_match.group(1).strip() if conclusion_match else ''

    # Create the response dictionary
    analysis_response = {
        "claim": claim,
        "claimAccuracy": claim_accuracy,
        "ingredientReview": ingredient_review,
        "nutritionalFactsReview": nutritional_facts,
        "overallObservation": overall_observation,
        "conclusion": conclusion
    }

    # Return the JSON response
    return jsonify({'analysis': analysis_response})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
