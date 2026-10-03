import asyncio ,os
from pydantic import BaseModel
from dotenv import load_dotenv
from sarvamai import AsyncSarvamAI
from src.planner import PlannerAgent

TOKEN_SCHEDULE = [3000, 5000, 8000]
writer_model = "sarvam-105b"
load_dotenv()
client = AsyncSarvamAI(api_subscription_key=os.getenv("SARVAM_API_KEY"))

retries = 3

SEM = asyncio.Semaphore(5)

writer_prompt = """You are a history section writer. You will be given a section
title, a goal, a historical period, and allowed source types.
Rules:
- Write ~200-300 words covering ONLY that period. Do not drift into other eras.
- Use ONLY the given source_types as your evidence basis. If source_types is
  ["oral_tradition"], say so explicitly — do not invent inscriptions or texts.
- Separate established fact from tradition/theory using phrasing like
  "According to X" or "Oral tradition holds that Y", never state theories as fact.
- Cite claims inline as [1], [2], matching a "Sources:" list at the end
  describing what each source is (e.g. "[1] Colonial-era gazetteer record").
- If evidence for this period is genuinely thin, say so rather than padding."""

class SectionResult(BaseModel):
    id: str
    title: str
    content: str

class Writer:
    async def writer(node: dict ,community: str) -> SectionResult:
        prompt = f"""Community : {community}
        Section : {node['title']}
        Goal : {node['goal']}
        Period : {node['period']}
        Allowed source types : {", ".join(node['source_types'])}"""

        async with SEM:
            for attempt in range(retries):
                try:
                    response = await client.chat.completions(
                        model=writer_model,
                        messages=[
                            {'role':'system','content':writer_prompt},
                            {'role':'user','content':prompt}
                        ],
                        temperature = 0.3,
                        max_tokens = TOKEN_SCHEDULE[attempt]
                    )
                    choice = response.choices[0]
                    text = choice.message.content
                    if text:
                        return SectionResult(id = node['id'] ,title = node['title'] ,content = text)
                    print(f"[{node['id']}] empty content, finish_reason={choice.finish_reason}")

                except Exception as e:
                    print(f"[{node['id']}] attempt {attempt} error: {e}")
                    if attempt == 2:
                        raise
                await asyncio.sleep(2 ** attempt)
        raise RuntimeError(f"Writer failed for {node['id']}, see logs above")

    async def write_all_sections(self,outline: dict ,community: str) -> list[SectionResult]:
        leaves = [
            sub
            for section in outline['sections']
            for sub in section['subsections']
        ]
        return await asyncio.gather(*[self.writer(node ,community) for node in leaves])

plan = PlannerAgent()
res_outline = plan.planner("Padma Velama")
res = res_outline.model_dump()
result = asyncio.run(Writer.write_all_sections(res,"Padma Velama"))

for r in result:
    print(f"\n-> {r.title}\n\t{r.content}\n")