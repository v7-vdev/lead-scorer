import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal
from groq import Groq
from dotenv import load_dotenv

from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Lead Scorer API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Helper to get Groq client safely
def get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        return None
    return Groq(api_key=api_key)

# Global client initialization (will be None if key is missing)
client = get_client()

class LeadRequest(BaseModel):
    name: str
    company: str
    budget: float
    requirements: str

class LeadResponse(BaseModel):
    lead_score: int
    urgency: Literal["low", "medium", "high"]
    summary: str
    recommended_action: str

@app.get("/")
async def root():
    return {"message": "Lead Scorer API is running"}

@app.post("/score-lead", response_model=LeadResponse)
async def score_lead(lead: LeadRequest):
    # Ensure client is available
    global client
    if client is None:
        # Try to re-initialize in case .env was updated
        client = get_client()
        if client is None:
            raise HTTPException(
                status_code=500, 
                detail="GROQ_API_KEY is missing or not configured. Please add your key to the .env file."
            )

    prompt = f"""
    Evaluate the following business lead and provide a structured scoring.
    
    Lead Details:
    - Name: {lead.name}
    - Company: {lead.company}
    - Budget: ${lead.budget}
    - Requirements: {lead.requirements}
    
    Scoring Criteria:
    - lead_score: 1-10 (10 being highest potential). Consider budget, company profile, and requirements clarity.
    - urgency: "low", "medium", or "high" based on language and budget.
    - summary: A concise 1-2 sentence overview of the lead.
    - recommended_action: The best next step for the sales team.
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a professional lead scoring assistant. Respond with a valid JSON object matching the following structure: {\"lead_score\": int, \"urgency\": \"low\"|\"medium\"|\"high\", \"summary\": str, \"recommended_action\": str}"},
                {"role": "user", "content": prompt}
            ],
            response_format={
                "type": "json_object"
            }
        )
        
        # Parse the JSON response
        response_content = completion.choices[0].message.content
        return json.loads(response_content)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling Groq API: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
