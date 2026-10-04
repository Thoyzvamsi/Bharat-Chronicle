# Writer Agent
import asyncio
from pydantic import BaseModel

SEM = asyncio.Semaphore(5)  # 5 processes at syncronization

class SectionResult(BaseModel):
    id: str
    title: str
    content: str

class Writer:
    # Client in here should be Async
    def __init__(self ,client ,writer_model ,writer_retry_token_schedule ,writer_prompt):
        self.client = client
        self.writer_model = writer_model
        self.writer_retry_token_schedule = writer_retry_token_schedule
        self.writer_prompt = writer_prompt
        self.retries = len(writer_retry_token_schedule)

    async def writer(self,node: dict ,community: str) -> SectionResult:
        prompt = f"""Community : {community}
        Section : {node['title']}
        Goal : {node['goal']}
        Period : {node['period']}
        Allowed source types : {", ".join(node['source_types'])}"""

        async with SEM:
            for attempt in range(self.retries):
                try:
                    response = await self.client.chat.completions(
                        model=self.writer_model,
                        messages=[
                            {'role':'system','content':self.writer_prompt},
                            {'role':'user','content':prompt}
                        ],
                        temperature = 0.3,
                        reasoning_effort = None,
                        max_tokens = self.writer_retry_token_schedule[attempt]
                    )
                    choice = response.choices[0]
                    text = choice.message.content
                    if text:
                        return SectionResult(
                            id = node['id'] ,
                            title = node['title'] ,
                            content = text
                        )
                    #print(f"[{node['id']}] empty content, finish_reason={choice.finish_reason}")

                except Exception as e:
                    print(f"[{node['id']}] attempt {attempt} error: {e}")
                    if attempt == 2: raise
                await asyncio.sleep(2 ** attempt)

        raise RuntimeError(f"Writer failed for {node['id']}, see logs above")


    async def write_all_sections(self,outline: dict ,community: str) -> list[SectionResult]:
        leaves = [sub for section in outline['sections'] for sub in section['subsections']]
        return await asyncio.gather(*[self.writer(node ,community) for node in leaves])