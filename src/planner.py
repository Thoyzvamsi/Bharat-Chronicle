# Planner Agent
from pydantic import BaseModel ,ValidationError
import json ,re
from typing import Literal

class Subsection(BaseModel):
    id: str
    title: str  # Title of the concept
    goal: str   # telling the writer what to cover
    period: str  # e.g. "c. 300 BCE - 500 CE"
    source_types: list[Literal[
        "inscription", "literary_text", "colonial_record",
        "oral_tradition", "modern_scholarship"
    ]]

class Section(BaseModel):
    id: str
    title: str
    subsections: list[Subsection]

class Outline(BaseModel):
    title: str
    sections: list[Section]

class PlannerAgent:
    def __init__(self,client ,planner_model ,planner_prompt):
        self.client = client
        self.planner_model = planner_model
        self.planner_prompt = planner_prompt

    def planner(self ,community: str ,retries: int = 2) -> Outline:
        last_error = None

        for _ in range(retries+1):
            response = self.client.chat.completions(
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