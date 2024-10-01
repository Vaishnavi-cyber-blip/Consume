from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import re
import google.generativeai as genai

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://friendly-spork-2.onrender.com"}})

google_api_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=google_api_key)
model = genai.GenerativeModel('gemini-pro')

@app.route('/analyze_claim', methods=['POST'])
def analyze_claim():
    data = request.json
    claim = data.get('claim')
    nutrition_text = data.get('nutritionText')

    prompt = f"""
        You are given the following product claim: "{claim}".
        The product description extracted from its label is: "{nutrition_text}".

        ### Instructions:
        1. Analyze the accuracy of the claim based on the extracted text.
        2. Provide an in-depth, step-by-step breakdown with facts.
        3. Ensure the analysis includes:
            - Claim accuracy check
            - Ingredient review
            - Nutritional facts review
            - Overall observations
            - Final conclusion with a verdict (Accurate, Partially Accurate, or Inaccurate)
        4. Use the format given to display the output.


        **Example Analysis:**
        ---
        **Claim:**
        "{claim}"

        **🔍 Claim Accuracy:**
        - Bullet-pointed facts based on comparison with extracted text.

        **🧪 Ingredient Review:**
        - Bullet-pointed review of the ingredients.

        **📊 Nutritional Facts Review:**
        - Bullet-pointed nutritional facts related to the claim.

        **🔍 Overall Observation:**
        - General summary of findings.

        **⚖️ Conclusion:**
        - Verdict and reasons for the accuracy of the claim.

        ### Now analyze the claim: "{claim}"
        ---
        """

    response = model.generate_content(prompt)
    analysis_text = response.text
    print(analysis_text)

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
