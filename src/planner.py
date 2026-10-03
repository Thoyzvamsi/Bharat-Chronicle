# Planner Agent
from sarvamai import SarvamAI
from dotenv import load_dotenv
from pydantic import BaseModel ,ValidationError
import os ,json ,re

load_dotenv()
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

class PlannerAgent:
    def __init__(self):
        self.planner_model = "sarvam-105b"
        self.planner_prompt = """You are a research planner for community history reports.
        Given a community name, output an outline as JSON only. No prose, no fences.
        Schema: {"title": str, "sections": [{"id": "1", "title": str, "subsections":
        [{"id": "1.1", "title": str, "goal": str, "period": str, "source_types": [str]}]}]}

        Rules:
        - Sections are ERAS, ordered earliest to latest: earliest references and origin
        traditions, ancient, early medieval, medieval, colonial, post-independence.
        - Give most weight to the earliest periods. Modern (20th century+) origin theories
        get one subsection at most, labelled modern_scholarship or oral_tradition.
        - source_types: allowed values are inscription, literary_text, colonial_record,
        oral_tradition, modern_scholarship. Choose the evidence a historian would
        actually look for in that period (inscriptions, copper plates, medieval
        literature, colonial gazetteers and ethnographies).
        - If no written evidence is known for a period, still include it, use
        ["oral_tradition"], and say so in the goal.
        - 5-7 sections, 2-3 subsections each. Contested claims must be flagged in the goal."""

    def planner(self ,community: str ,retries: int = 2) -> Outline:
        last_error = None

        for _ in range(retries+1):
            response = client.chat.completions(
                model = self.planner_model,
                messages = [
                    {"role" : "system" ,"content" : self.planner_prompt},
                    {"role" : "user" ,"content": f"Community: {community}"}
                ],
                temperature = 0.2,
                reasoning_effort = None,
            )
            text = response.choices[0].message.content

            try:
                return Outline.model_validate(self.extract_json(text))
            except (ValueError, ValidationError) as e:
                last_error = e
        raise RuntimeError(f"Planner Failed error : {last_error}")


    def extract_json(self ,text : str) -> dict:
        match = re.search(r"\{.*\}",text,re.DOTALL)
        if not match:
            raise ValueError("No Json Found in the model output")
        return json.loads(match.group(0))