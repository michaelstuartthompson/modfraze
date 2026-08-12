# Building the ModFraze Trend Scout

A working agent, and an explanation of every piece of it.

Read this top to bottom once. Then run the demo. Then read `agent.py`.

---

## 1. What this is

An agent that pulls posts and search data from multiple platforms, finds words
and phrases that are surfacing on more than one platform at once, and reports
back a short ranked list of the ones worth designing merchandise around.

It runs in three stages, and **the split between them is the whole lesson**:

```
  STAGE 1  collect     sources.py    dumb pipes, ~1,500 items
     ↓
  STAGE 2  score       scoring.py    pure Python counting, ~1,500 → ~40
     ↓
  STAGE 3  agent       agent.py      the LLM, judgment only, ~40 → ~5
     ↓
           report      reports/YYYY-MM-DD-shortlist.md
```

### Why not just send everything to the model?

That is what most first attempts do: dump 1,500 headlines into a prompt and ask
"what's trending?" It produces something that looks right and is quietly wrong.

Three reasons it fails:

1. **Cost.** 1,500 headlines is a large prompt. Daily, that adds up fast — and
   it scales linearly with how many sources you add, which punishes you for
   improving the system.
2. **No memory.** "Trending" means *compared to yesterday*. A model handed one
   day of data has no yesterday. It will pattern-match on what *sounds* trendy
   instead of what actually accelerated. `scoring.py` keeps a JSON file of daily
   counts, so "rising" is a measured fact rather than a vibe.
3. **Counting is not a language task.** Tallying which of three platforms
   mentioned a phrase is something Python does perfectly, for free, every time.
   Asking a language model to do arithmetic over 1,500 rows is paying a premium
   for a worse answer.

**The rule to internalize:** use deterministic code for anything with a right
answer. Use the model only where the task requires judgment or language. That
sentence is most of what separates people who ship agents from people who
demo them.

Here, the judgment is real and the model earns its cost: *is "quiet cracking"
a phrase people are actually using, or three unrelated posts that happen to
share words? Is it a ModFraze phrase or just a popular one? Is it early enough
that merch would land before it dies?* No amount of counting answers those.

---

## 2. Setup

### Python

You already have it — the project has a `.venv` and `.pyc` files from 3.13.
Confirm in PowerShell:

```powershell
python --version
```

### The API key

You have `test_openai.py` in the project, so you've done this before with
OpenAI. This agent uses Anthropic (Claude), because its tool-use API is the
cleanest example of the pattern and it's what you'd want to show an employer.

1. Go to **console.anthropic.com** → sign in → **API Keys** → **Create Key**
2. Copy it (starts with `sk-ant-`). You only see it once.
3. Add ~$5 of credit under **Billing**. A run of this agent costs a few cents.
4. Add it to the project `.env`:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**This is separate from your Claude subscription.** The subscription pays for
you talking to Claude in the app. The API key pays for *your code* talking to
Claude. Different meters.

### Install

```powershell
cd C:\Users\miket\iCloudDrive\04_Projects\ModFraze
.\.venv\Scripts\Activate.ps1
pip install anthropic python-dotenv
```

Everything else in this folder uses only the standard library on purpose, so
there is less to break.

---

## 3. Run it

Start with the demo. No network, no key, fake data with two planted fads:

```powershell
cd agents\trend_scout
python run.py --demo --collect-only
```

You should see it isolate `quiet cracking` and `loud budgeting` and correctly
ignore `nfl scores` (one platform) and `Weekly discussion thread` (noise).

Now live collection, still no key needed:

```powershell
python run.py --collect-only
```

Then the full thing once your key is set:

```powershell
python run.py
```

`--collect-only` is your friend. Run it for a week before you ever spend a
token. It builds the history file the scoring depends on, and it lets you tune
`brand.md` and the noise list for free.

---

## 4. The loop, explained

Open `agent.py`. Strip the comments and it is this:

```python
messages = [{"role": "user", "content": the_candidate_table}]

for turn in range(1, MAX_TURNS + 1):
    response = client.messages.create(
        model=MODEL,
        system=SYSTEM_PROMPT,
        tools=ToolBox.SCHEMAS,
        messages=messages,
    )
    messages.append({"role": "assistant", "content": response.content})

    tool_uses = [b for b in response.content if b.type == "tool_use"]
    if not tool_uses:
        break                        # model had nothing left to do

    results = []
    for tu in tool_uses:
        output = getattr(box, tu.name)(**tu.input)   # run YOUR python function
        results.append({
            "type": "tool_result",
            "tool_use_id": tu.id,
            "content": json.dumps(output),
        })

    messages.append({"role": "user", "content": results})
```

That's the agent. About twenty lines. Five things to notice:

**The model never runs anything.** It returns a request: *"call
`inspect_candidate` with `term='quiet cracking'`."* Your code decides whether
to honor it. Everything you'll read about agent safety, sandboxing, and
human-in-the-loop approval lives in that gap — it's where you'd insert
"ask Michael before spending money."

**`messages` grows every turn.** The conversation carries the whole history, so
the model can reason across turns. It also means cost grows every turn, which
is why `MAX_TURNS` exists. An agent without an iteration cap is a bug with a
credit card.

**Tool descriptions are prompts.** Look at `inspect_candidate`'s description in
`ToolBox.SCHEMAS`. It doesn't just say what the function does — it says *"Call
this before shortlisting anything — the summary table alone is not enough."*
That sentence changes the model's behavior more than any code in the file. When
your agent misbehaves, rewrite the tool description before you touch the loop.

**Tools return errors instead of raising.** `inspect_candidate` on an unknown
term returns `{"error": ..., "did_you_mean": [...]}`. The model reads that and
corrects itself. A raised exception kills the run; a returned error becomes a
recovery. Design tool outputs for a reader who can adapt.

**`save_shortlist` is the terminal tool.** Rather than parsing prose for an
answer, the run ends when the model *records* one in a structured shape you
defined. You get validated JSON instead of a paragraph you have to regex.
Use this pattern every time you need structured output from an agent.

---

## 5. What's weak about it right now

Being able to say this about your own system is the actual senior-level skill.

**Only two sources work out of the box.** Google Trends RSS and Hacker News are
free and keyless. Reddit's `.json` endpoints work from a home IP but get `403`
from datacenters — you'll likely see it work on your laptop. Etsy, X, TikTok,
and Amazon all need credentials. Since breadth across platforms is the core
signal, **two sources is a weak system.** Adding a real third source is the
highest-value improvement available, and Reddit is it.

**Day one output is bad, by design.** Velocity is measured against a term's own
history, and on day one there is none, so everything looks like it's exploding.
The system needs roughly a week of daily `--collect-only` runs before its
rankings mean anything. Build the habit before you judge the output.

**N-gram matching is literal.** "quiet cracking" and "quiet-cracking" are
different terms to it. Embeddings would fix this and would be the right upgrade
*after* you've proven the simple version is worth improving — not before.

**The weights are guesses.** `W_BREADTH`, `W_VELOCITY`, `W_NOVELTY`,
`W_PHRASE` in `scoring.py` are my invented starting numbers. Run it for two
weeks, look at what it surfaced versus what actually popped, and adjust. That
tuning loop *is* the job.

---

## 6. How to extend it

### Add a source

The whole point of the `Signal` shape. In `sources.py`:

```python
def etsy(query: str = "trending") -> list[Signal]:
    raw = _get(f"https://openapi.etsy.com/v3/...&api_key={os.environ['ETSY_KEY']}")
    if not raw:
        return []
    return [
        Signal(platform="etsy", text=item["title"], url=item["url"],
               score=float(item.get("num_favorers", 0)))
        for item in json.loads(raw)["results"]
    ]
```

Add it to the `SOURCES` dict. Done. Nothing in `scoring.py` or `agent.py`
changes. That's what a good abstraction buys you.

Etsy is the most valuable one to add next, for a non-obvious reason: it tells
you what phrasing is *already selling on merch*, which is your best saturation
check. If a phrase is on 400 Etsy listings, you're late — and that's a fact the
agent can use to reject a trend rather than chase it.

### Change its taste

Edit `brand.md`. Do not touch the code. When the agent surfaces something
wrong, ask "what rule would have caught this?" and add that rule. Over a few
weeks that file becomes genuinely valuable — an encoded version of your
judgment that runs without you.

### Add the next pipeline node

You now have the pattern. The design node is the same three stages: collect
(approved trends from the shortlist), deterministic work (prompt assembly,
naming, SKU generation via your existing `Schemas/`), agent (art direction and
copy). Its tools would be your existing `Tools/dalle_client.py` and
`Tools/printify_client.py`.

**Build it as a separate agent with its own loop.** One giant agent that scouts
*and* designs *and* launches is the most common architecture mistake — it's
harder to debug, harder to test, and when it fails you can't tell which part
failed. Small agents that hand structured output to each other beat one big one
essentially always.

---

## 7. Why this makes you hireable

You didn't just call an API. Point at these specifically:

- **You separated deterministic work from model work** — the single clearest
  marker of someone who has actually run an agent in production versus someone
  who has followed a tutorial. Nearly every "our AI feature is too expensive
  and too flaky" postmortem comes down to this.
- **You built a no-key demo mode** — makes the system testable, and makes logic
  bugs distinguishable from API bugs.
- **You bounded the loop** and made tools fail soft.
- **You used a terminal tool for structured output** instead of parsing prose.
- **You can name your system's weaknesses** — which is what a technical
  interviewer is actually probing for.

Write it up as a case study in `11_Portfolio_Case_Study` per your architecture
doc. Include a real report the agent produced, one trend it got right, and one
it got wrong with your analysis of why. **The failure analysis is worth more
than the success.** Anyone can show a demo that worked.

---

## 8. Staying current

You asked how to keep up. The field moves fast in surface detail and slowly in
fundamentals, and the ratio matters — most "news" is a framework release you
can safely ignore. Weight your time accordingly.

**Read (high signal, low volume):**

- Anthropic's engineering blog — particularly their writing on building
  effective agents and on context engineering. The most useful non-hype
  material published on this.
- OpenAI's practical guide to building agents.
- Model provider docs when a model ships. Read the *tool use* and *prompt
  caching* pages specifically; they change what's economically possible.

**Watch, don't chase:** LangGraph, CrewAI, the Claude Agent SDK, OpenAI's
Agents SDK, MCP. Know what each is *for*. Having written the raw loop, you can
now read a framework's docs and tell whether it's solving a problem you have.
Most of the time it isn't. Adopt one when you feel a specific pain — durable
execution across restarts, or multi-agent handoffs — not because it trended.

**The one to actually learn: MCP (Model Context Protocol).** It standardizes
how agents connect to tools and data. It's the thing in this space most likely
to still matter in three years, and it shows up in job postings now.

**Build, on a cadence.** One small agent a month, each solving a real problem
you have. Four working agents with honest write-ups beats any certificate.
Reading about agents transfers almost nothing; the knowledge lives in having
debugged a loop that wouldn't terminate.

**Skills that transfer, in order of how much they matter:**

1. Evaluation — how do you know your agent got better? Almost nobody does this
   and everybody needs it. This is the highest-leverage thing on this list.
2. Context management — what goes in the window, what stays out, what gets
   summarized. This is where cost and quality both live.
3. Tool design — the schemas and descriptions, not the loop.
4. Failure design — retries, fallbacks, human checkpoints, budget caps.
5. Knowing when *not* to use an agent. Most tasks are a single prompt or a
   plain script. Saying so in an interview reads as judgment, not laziness.

Frameworks will churn. Those five don't.
