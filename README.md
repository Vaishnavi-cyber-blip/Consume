# Flask Backend for Consume Wisely only text version

### Flask App Setup:  
The Flask application is initialized to create an API. CORS is enabled to allow requests from a specific frontend URL (https://friendly-spork-2.onrender.com).  

### Google API Key:  
The Google API key is fetched from environment variables and used to configure the Gemini model.  

### Gemini Model Setup:  
The Google Gemini model ('gemini-pro') is configured to analyze text and generate content.  

### /analyze_claim Endpoint:  
The endpoint listens for POST requests and expects JSON data with a product claim and nutritional text.  
A prompt is generated based on this data and sent to the Gemini model for analysis.  

### Response Parsing:  
After generating content from the model, the response is parsed using regular expressions to extract specific sections: claim, claim accuracy, ingredient review, nutritional facts, overall observation, and conclusion.  

### JSON Response:  
The extracted information is packaged into a JSON response and returned to the client.  

### Flask App Run:
The Flask app runs in debug mode on port 5000.  

### Interface:
![consume2](https://github.com/user-attachments/assets/0dec74a4-b3ce-4cef-90b7-71456f1e87cd)
