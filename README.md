# BharatChronicle

An AI agent that writes a structured, sourced history report for any community — built on the Sarvam AI API, as a learning project and portfolio piece.

You give it a community name. It plans out the report, writes every section, checks the writing against real sources, and gives you back a full report broken into eras — ancient, medieval, colonial, modern — each one backed by the kind of evidence a historian would actually look for.

---

## What it does

1. You type in a community name (example used throughout development: **Padma Velama**).
2. The agent plans an outline: 4-5 sections (one per historical era), each with 2-3 smaller topics.
3. Each small topic gets written by the agent, in parallel, as its own short, focused piece of text.
4. A final agent searches the web and checks every section against what it finds — fixing anything that's wrong or mixed up.
5. You get back a full report, section by section.

---

## How it works

```
Planner Agent → outline (JSON): eras, topics, time periods, what kind of
                evidence to use for each
      ↓
Writer Agents → one small piece of writing per topic, all running at the
                same time (not one after another)
      ↓
Fact Checker  → searches the web once for the whole report, compares every
                section against what it finds, fixes mistakes directly
```

**Planner Agent** (`planner.py`)
Takes just a community name. Asks the model to return a JSON outline — never plain writing — with a fixed shape: a list of sections (eras), each with a list of topics. Every topic also says which time period it covers and what kind of evidence should be used for it (inscriptions, old texts, colonial records, oral tradition, or modern research). This shape is checked with Pydantic, so if the model returns something broken, it's caught immediately instead of breaking something later in the pipeline.

**Writer Agent** (`writer.py`)
Takes one small topic at a time — title, what to cover, time period, allowed evidence types — and writes about 200-300 words on just that. Every topic is written by its own separate call to the model, and all of them run **at the same time** instead of one after another (more on why below). Each one also has a few retries, giving it more room to answer if it runs out of space the first time.

**Fact Checker** (`fact_checker.py`)
Once every section is written, this agent searches the web one time for general information about the community, then hands the model the whole report plus what it found online, and asks it to fix anything that's wrong — especially cases where the writing describes a different (but similarly named) community by mistake.

**Shared pieces** (`utils.py`)
Small helper used by every agent that returns JSON — pulls the JSON out of the model's reply and turns it into a proper Python object.

---

## Setup

```bash
python -m pip install -r requirements.txt 
```

Create a `.env` file in the project folder:
```
SARVAM_API_KEY=your_key_here
```

Run it:
```bash
python src/main.py
```

### Project structure
```
BharatChronicle/
├── src/
│   ├── main.py         # wires everything together, holds the prompts
│   ├── planner.py       # Planner Agent
│   ├── writer.py         # Writer Agent
│   ├── fact_checker.py   # Fact Checker Agent
│   └── utils.py          # shared JSON-parsing helper
├── .env
└── README.md
```

---

## Problems faced while building this, and how each was fixed

**1. The model's answers kept getting cut off**
By default, the API only gives the model a small amount of room to answer in. For a history section with real depth, that wasn't enough — answers were coming back cut off halfway. Fixed by explicitly setting a bigger `max_tokens` limit on every call instead of relying on the default.

**2. One slow API call was blocking everything else**
Early on, the whole program would just sit and wait on one single call to Sarvam before doing anything else — meaning a report with several sections took far longer than it needed to, one section at a time. Fixed by breaking the big task into small, independent sub-tasks (one Writer call per topic) and running them **at the same time** using Python's `asyncio`, instead of one after another. A limit (a "semaphore") caps how many run at once, so it doesn't overload the API.

**3. The outlines were too shallow**
The first version of the Planner only thought about recent history. Fixed by rewriting its instructions to explicitly ask for every era from ancient times to the present, and to name what kind of real evidence (inscriptions, old texts, colonial records, oral tradition, modern research) should back each section — instead of just asking for "history" in general.

**4. Reasoning eats into the same token budget as the answer**
The model can "think" before answering, and that thinking uses up the same token budget as the actual answer — so a high amount of thinking could use up the whole budget before any real answer was written. Fixed two ways: turning reasoning off for straightforward tasks (`reasoning_effort=None`), and for the Writer, using a growing list of token budgets across retries (`[3000, 5000, 8000]`) — so if a topic needs more room, it gets more room on the next try instead of failing outright.

**5. The model stated wrong facts confidently**
The most serious issue: the model would sometimes write about the wrong community entirely — in testing, it mixed up "Padma Velama" with the separate, similarly-named "Koppula Velama." This is a known weakness of language models — they're recalling bits of training data, not looking anything up, so similar names can blend together. Fixed by building the **Fact Checker**: it searches the web for real information first, then checks the written report against that real information and fixes anything that doesn't match, instead of trusting the model's memory alone.

**6. Code written in a notebook had hidden bugs**
The early version was built and tested inside a Jupyter notebook, which made it easy to run cells out of order, leave stale code running, or copy-paste a mistake (wrong variable name, arguments passed in the wrong order, a typo in a method name) without noticing right away. Moving the code into proper `.py` files and testing it for real surfaced several of these bugs, which were then fixed one by one.

**7. The subject matter needed careful, neutral writing**
Since this tool can be used to write about caste communities — a genuinely sensitive subject in India — there was a real risk of it sounding like a one-sided "pride" piece instead of a fair historical account. Fixed by rewriting both the Planner's and Writer's instructions to require a neutral, academic tone: no celebratory language, no claiming any community is superior to another, individual people's actions are never turned into "traits of the whole group," and anything politically or socially disputed (caste rank, modern classification debates) is written as a reported claim or a fair account of different views — never stated as settled fact.

---

## Disclaimer
This tool uses AI to write historical content, and AI can make mistakes —
including stating things confidently that aren't true. Treat every report as
a draft to be checked, not a finished source. This project is not meant to
favor or offend any community. See [DISCLAIMER.md](DISCLAIMER.md).

## Known limitations

- Web search (via `ddgs`, a free tool) is not fully reliable and can occasionally fail or get rate-limited — the Fact Checker is built to carry on without reference material rather than crash when this happens, but reference material is sometimes thin.
- The model can still make mistakes the Fact Checker doesn't catch. This tool is an assistant for drafting a first pass, not a replacement for an actual historian's review.
- Currently tested in depth on one community (Padma Velama) — results on other communities haven't been checked as thoroughly yet.

## Possible next steps

- Let the Writer Agent search the web itself while writing (instead of only checking afterward), using Sarvam's built-in support for tool calls.
- Swap the free search tool for a paid search API for more reliable results.
- Export the final report to a PDF or a nicely formatted document instead of plain console output.