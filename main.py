from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
import shap

# 1. Initialize the web server
app = FastAPI(title="Explainable Hiring API")

# 2. Load the AI Brain we built in Phase 2
model = joblib.load("hiring_model.pkl")
features = ['experience_years', 'technical_score', 'certifications']

# 3. Define what an incoming "Resume" looks like
class CandidateData(BaseModel):
    experience_years: int
    technical_score: int
    certifications: int

# 4. Create the web endpoint
@app.post("/analyze_candidate")
def analyze_candidate(candidate: CandidateData):
    # Convert the incoming web data into a pandas dataframe
    input_data = pd.DataFrame([[
        candidate.experience_years, 
        candidate.technical_score, 
        candidate.certifications
    ]], columns=features)
    
    # Get the AI's prediction (1 = Hire, 0 = Reject)
    prediction = int(model.predict(input_data)[0])
    
    # Get the SHAP explanation
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(input_data)
    
    if isinstance(shap_values, list):
        contributions = shap_values[1][0].tolist()
    else:
        contributions = shap_values[0].tolist()
        
    # Package the math into a neat dictionary
    explanation = {
        features[i]: round(contributions[i], 2) for i in range(len(features))
    }
    
    return {
        "status": "success",
        "hired": prediction,
        "shap_explanation": explanation
    }