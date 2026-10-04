import os,asyncio
from sarvamai import SarvamAI,AsyncSarvamAI
from dotenv import load_dotenv
from planner import PlannerAgent
from writer import Writer

load_dotenv()
api_key = os.getenv("SARVAM_API_KEY")

planner_model = "sarvam-105b"
planner_prompt = """You are a research planner for community history reports.
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

writer_model = "sarvam-105b"
writer_retry_token_schedule = [3000, 5000, 8000]
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


client = SarvamAI(api_subscription_key = api_key)
async_client = AsyncSarvamAI(api_subscription_key = api_key)

plan = PlannerAgent(
    client = client ,
    planner_model = planner_model ,
    planner_prompt = planner_prompt
)
writer = Writer(
    client = async_client ,
    writer_model = writer_model ,
    writer_retry_token_schedule = writer_retry_token_schedule ,
    writer_prompt = writer_prompt
)

community = "Give a community name in here"
planned_outline_json = plan.planner(community=community)
planned_outline = planned_outline_json.model_dump()

result = asyncio.run(writer.write_all_sections(planned_outline,community=community))
for r in result:
    print(f"\n-> {r.title}\n\t{r.content}\n")