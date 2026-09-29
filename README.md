# Plan 
    Planner Agent → outline JSON (fixed schema, reusable across communities)
        ↓
    Section Writers (N leaf nodes, run concurrently, semaphore-limited)
        ↓
    Timeline Synthesizer (cheap pass — reorders using short summaries, not raw text)
        ↓
    Source Compiler (dedupe citations collected from each section call)
        ↓
    Document Assembler → final markdown/PDF


# Problems Faced First time trying to create an AI Agent
    1.  API gives us default limit it is not enough for bigger questions, 
        so we need give a bigger limit and keep reasoning effort at high or None

    2.  code is reaching HTTP client but waiting too long to get return from Sarvam(API)
        We need to Divide the problem into sub problems

    3. We are succefully dividing the problem to subproblem but the responses are
        not as deep as we intented , so we need to change the prompt of planner_agent
        and we need to give the model little freedom to explore little further than recent
        times (e.g. 300 BCE - modern era) or (inscriptions, copper plates, medieval
        literature, colonial gazetteers and ethnographies)
