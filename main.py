# Planner Agent
from sarvamai import SarvamAI
from dotenv import load_dotenv
from pydantic import BaseModel ,ValidationError
import os ,json ,re

load_dotenv()
planner_model = "sarvam-105b"
client = SarvamAI(api_subscription_key=os.getenv("SARVAM_API_KEY"))

class Subsection(BaseModel):
    id: str
    title: str  # Title of the concept
    goal: str   # telling the writer what to cover

class Section(BaseModel):
    id: str
    title: str
    subsections: list[Subsection]

class Outline(BaseModel):
    title: str
    sections: list[Section]

# Trail prompt
planner_prompt = """ Your are a research planner agent for Indian community histories 
                    Community name will be given , output and outline for a history report
                    Rules:
                    - Output only Valid json, No prose and No markdown fences
                    - Schema: {"title": str, "sections": list[{"id": str ,"title": str ,
                    "subsections": [{"id": str, "title": str, "goal": str}]}]}
                    - Cover: Origin Theories and evidence ,role in regional/Indian histoty,
                      notable people ,genatical identies and origins ,cultures and traditions,
                      finally modern era
                    - order sections in cronologically where possible,
                    - 4-6 sections, 2-4 subsections each.
                    - Where evidence is contested (origins, genetics), say so in the goal."""