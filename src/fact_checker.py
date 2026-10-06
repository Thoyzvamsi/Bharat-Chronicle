from ddgs import DDGS
from ddgs.exceptions import DDGSException
from pydantic import BaseModel, ValidationError
from utils import extract_json
from writer import SectionResult
import time

class FactCheckedOutline(BaseModel):
    sections: list[SectionResult]

class FactChecker:
    def __init__(self, client, fact_checker_model, fact_checker_prompt, retries=2):
        self.client = client
        self.fact_checker_model = fact_checker_model
        self.fact_checker_prompt = fact_checker_prompt
        self.retries = retries

    def internet_results(self, query: str, max_results=8) -> str:
        for attempt in range(3):
            try:
                with DDGS() as ddgs:
                    result = list(ddgs.text(query, max_results=max_results))
                return "\n\n".join(f"{r['title']} : {r['body']}" for r in result)
            except DDGSException as e:
                print(f"search failed (attempt {attempt}): {e}")
                time.sleep(3 * (attempt + 1))
        return ""

    def fact_check_all(self, sections: list[SectionResult], community: str) -> list[SectionResult]:
        reference_text = self.internet_results(f"{community} history and facts") or "No reference material found online."

        combined_text = "\n\n".join(f"[id={s.id}] {s.title}\n{s.content}" for s in sections)

        prompt = f"""Community this report is about: {community}

        Reference material found online:
        {reference_text}

        Full report to check, section by section:
        {combined_text}"""

        last_error = None
        for attempt in range(self.retries + 1):
            try:
                response = self.client.chat.completions(
                    model=self.fact_checker_model,
                    messages=[
                        {'role': 'system', 'content': self.fact_checker_prompt},
                        {'role': 'user', 'content': prompt},
                    ],
                    reasoning_effort=None,
                    max_tokens=10000,
                )
                text = response.choices[0].message.content
                if not text:
                    last_error = f"empty content, finish_reason={response.choices[0].finish_reason}"
                    continue
                parsed = FactCheckedOutline.model_validate(extract_json(text))
                return parsed.sections
            except Exception as e:
                last_error = e
                print(f"attempt {attempt} error: {e}")
        raise RuntimeError(f"Fact check failed: {last_error}")