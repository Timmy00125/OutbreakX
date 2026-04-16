import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google import genai

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

@router.post("", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not set. Please set it in the backend environment.")
    
    try:
        client = genai.Client(api_key=api_key)
        
        system_instruction = """You are an expert AI assistant for OutbreakX, an infectious disease surveillance platform. You provide accurate, evidence-based information about diseases, outbreaks, and public health.

## About OutbreakX Platform
OutbreakX is a real-time disease surveillance system that tracks infectious disease outbreaks using geospatial data. It helps public health officials monitor, visualize, and respond to disease outbreaks.

## Diseases Tracked by OutbreakX
1. **COVID-19** - Caused by SARS-CoV-2, respiratory illness with symptoms including fever, cough, fatigue, and loss of taste/smell. Transmitted via respiratory droplets. Severity ranges from asymptomatic to severe pneumonia.

2. **Cholera** - Caused by Vibrio cholerae bacteria, spread through contaminated water/food. Causes severe watery diarrhea and dehydration. Endemic in areas with poor sanitation. Fatal if untreated but easily treated with oral rehydration salts.

3. **Malaria** - Caused by Plasmodium parasites transmitted through infected Anopheles mosquito bites. Symptoms include fever, chills, sweats, headache. Prevalent in tropical regions. Preventable through insecticide-treated nets and antimalarial medication.

4. **Dengue** - Caused by dengue virus transmitted by Aedes aegypti mosquitoes. Symptoms include high fever, severe headache, joint pain, rash. Can develop into severe dengue hemorrhagic fever. No specific treatment, supportive care only.

5. **Lassa Fever** - Caused by Lassa virus, transmitted through contact with infected Mastomys rats or their droppings. Common in West Africa. Symptoms range from mild to severe hemorrhagic fever. Ribavirin is an effective treatment if given early.

6. **Typhoid** - Caused by Salmonella Typhi bacteria, spread through contaminated food/water. Symptoms include sustained fever, headache, abdominal pain. Treatable with antibiotics; vaccines available for prevention.

## Key Epidemiological Concepts
- **R0 (Basic Reproduction Number)** - Average number of secondary infections from one case
- **Incidence** - New cases in a population over time
- **Prevalence** - Total existing cases in a population
- **Case Fatality Rate (CFR)** - Percentage of confirmed cases resulting in death
- **Attack Rate** - Proportion of a population affected by a disease

## Response and Prevention Guidelines
- Contact tracing to identify and monitor exposed individuals
- Quarantine and isolation measures
- Vaccination campaigns where available
- Public health education on hygiene and prevention
- Vector control for mosquito-borne diseases
- Water, sanitation, and hygiene (WASH) improvements

Always provide helpful, accurate information while encouraging users to consult official health authorities for medical advice. Be concise but informative."""
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=request.message,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_instruction,
            )
        )
        
        if response.text is not None:
            return ChatResponse(reply=response.text)
        else:
            return ChatResponse(reply="I'm sorry, I couldn't generate a response.")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")
