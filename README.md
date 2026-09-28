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
        We need Divide the problem into sub problems
