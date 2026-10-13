# Lab 10: AskIT Ops Control Room

**Session 10 · Observability, cost and evaluation: can you see it, afford it, prove it?** · about 2 hours in 3 parts · **no code to write**

| What we do | Why | Outcome | How |
|---|---|---|---|
| Record every step of the AskIT agent as a **trace**, find four hidden failures in recorded traces, measure **cost per ticket**, run an **exam** (evals) on 14 questions, and find your own model calls in **AWS CloudWatch**. | Clients ask "how do we know it works?", "what will it cost?" and "who can see what it did?". An agent that does not crash can still be wrong, slow or expensive. | You can read a trace, name the root cause of a failure, quote a cost per ticket, run a pass/fail exam before a release, and show the same call in your own tracer, Langfuse and AWS. | One command opens an app. Then buttons, and 6 clicks in the AWS console. |

---

## STEP 0. Open the right folder (do this first)

**We are doing Lab 10 · AskIT Ops Control Room now (`lab10-askit-ops-control-room`).**

1. Open **VS Code**.
2. Click **File** → **Open Folder**.
3. Paste this path and click **Select Folder**:

```
C:\AskIT\dxc-agentic-ai\Day10\Labs\lab10-askit-ops-control-room
```

4. Click **Terminal** → **New Terminal**. The prompt must end with **lab10-askit-ops-control-room**.

Folder not there? In File Explorer open `C:\AskIT\dxc-agentic-ai` and double-click **SYNC.bat**. Then repeat step 2.

## STEP 1. Start the app

Is the Lab 9 app still running? Click in its terminal and press **Ctrl+C** first.

In the VS Code terminal, type this line and press Enter:

```
python run.py
```

The first time it installs packages (a few minutes). The browser opens the app. If it does not, open:

```
http://localhost:8501
```

Keep the terminal open. In the sidebar (left) leave **1 · Model** on **AWS Bedrock** (or **Offline stand-in** if Bedrock shows a problem).

## STEP 2. Connect Langfuse (2 minutes, optional but recommended)

**Langfuse** is an open-source website where traces are stored and searched. Your trainer sends your team **3 lines of text** (LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST). Do not put them in GitHub.

1. In the app sidebar open **2 · Langfuse (your team)** → **Enter the team keys**.
2. Paste all 3 lines into the box and click **Save the keys**.
3. Click **Test the connection**. You should see "Connected to Langfuse".

No keys, or the test fails? Skip this. Everything in the lab still works; you only miss the Langfuse view in tab 1.

---

## The big picture (read once, 2 minutes)

```
Question -> AskIT agent -> model call -> tool call -> model call -> answer
                 |             every step is recorded as a SPAN by the tracer
                 +--> 1. this app (submission/traces.jsonl)
                 +--> 2. Langfuse (your team's project)
                 +--> 3. AWS CloudWatch (Bedrock logs each model call by itself)
```

- A **trace** is one run of the agent. A **span** is one step inside it: a model call or a tool call. Each span has start time, duration, input, output, tokens and cost.
- **Tokens** are the pieces of text a model reads and writes. You pay per token, for every model call.
- An **eval** is an exam for the agent: fixed questions, each checked PASS or FAIL for a named risk.

---

## Part A · Tabs 1 and 2 (40 min)

**Tab 1 · Run and trace**
1. Choose the question *My VPN shows error 809 - what should I try?* and click **▶ Run AskIT**.
2. Read the **waterfall**: each bar is one step. Purple is a model call, orange is a tool call. A wide bar is a slow step.
3. Under **Failure switches**, tick **🔁 Ticket system stuck**. Change the question to *Summarise ticket TKT-0004 and tell me the next step.* Click **▶ Run AskIT** again. What do you see in the waterfall? What happened to the status line?
4. Untick it. Tick **🐘 Huge search results**, choose the VPN question, run again. Which number changed most?
5. Look at **Compare your runs** at the bottom: your runs side by side.
6. If Langfuse is connected, click **Open this trace in Langfuse**. Find the same steps there.

**Tab 2 · Find the failure**
Four failures were recorded in production. For each: read the complaint, look at the waterfall, pick the root cause, click **Check my answer**, read the fix. About 4 minutes each. Which one had no error at all?

## Part B · Tab 3 (30 min)

1. Click **▶ Run the batch** (10 tickets). Read **cost per ticket**, **p50** (typical run time) and **p95** (the slowest 5% of runs).
2. Tick **📚 Padded instructions** and run the batch again. How many times more does a ticket cost?
3. Part C of the tab: type your monthly volume, move the **cache** slider to 60% and the **shorter prompts** slider to 30%. Which model fits a US$50 budget? Which one would you NOT recommend even if it fits, and why?
4. Click **💾 Save this table** (your evidence for GitHub).

## Part C · Tabs 4 and 5 (40 min)

**Tab 4 · Evals**
1. Prompt **v1**, click **▶ Run the exam**. Look for ❌. Which risk category fails most? Open **Look at the failing cases**.
2. Prompt **v2** (adds a VIP rule), run again. Which category changed?
3. Prompt **v3** (adds a not-found rule), run again. Read **Compare all exams you ran**. Did anything get worse?
4. Click **Check the search on 10 knowledge-base questions**: is the search or the model the problem?
5. Stretch: open **Add a test question of your own**, add one, run again.

**Tab 5 · See it in AWS** (needs **AWS Bedrock** in the sidebar, not Offline)
1. In tab 1 run any question once.
2. Open the AWS console (region **N. Virginia**) → **CloudWatch** → **Logs** → **Logs Insights**. Choose the log group named in the tab. Paste the query from the tab (it already contains your user name). **Run query**.
3. Find your calls. Do the tokens match tab 1?
4. Open **CloudWatch → GenAI Observability → Model invocations** to see the team view.
5. Open your Day 9 Lambda → **Monitor** → **View CloudWatch Logs**.

## Team task · Tab 8 (Board 5: Ops and FinOps Review)

Pick your team, read your curveball, make your choices, click **📝 Create our design decision (ADR)**. The ADR is saved in `teams\<your team>\ADR-AskIT-05.md` with your lab numbers inside. Run **SYNC.bat** afterwards.

---

## What is saved for GitHub (folder `submission`)

| File | What |
|---|---|
| `traces.jsonl` | Every run you made (one line each) |
| `eval_runs.json` | Every exam you ran |
| `cost_report.csv` | Your cost table (if you clicked Save) |

Then double-click **SYNC.bat** in `C:\AskIT\dxc-agentic-ai`.

## If something goes wrong

| What you see | What to do |
|---|---|
| "python is not recognized" | Close VS Code, open it again, open the folder again, new terminal. |
| The install did not work | Check your VPN or internet, run `python run.py` again. Still stuck: tell the trainer "install failed". |
| Bedrock shows a problem in the sidebar | Choose **Offline stand-in**. The whole lab works; only tab 5 needs real Bedrock. |
| Port 8501 busy | Another lab app is running. Press Ctrl+C in its terminal, then run again. |
| Langfuse test fails | Skip it. Tell the trainer. The lab works without it. |
| Tab 5 query shows no rows | Wait one minute, run a question in tab 1 with **AWS Bedrock** (not Offline), query again. |
| Tab 5 "could not read the logs" | Use the console steps. Same query. |

## Files in this folder (you never edit them)

| File | What it does |
|---|---|
| `app.py` | The screen: tabs and buttons |
| `ops_agent.py` | The AskIT agent, with every step traced; the failure switches |
| `ops_trace.py` | The recorder: spans, saving, sending to Langfuse |
| `evals.py` | The 14 test questions and the PASS/FAIL checks |
| `mystery.py` | The four recorded failures |
| `prices.py` | Model prices (with the date they were checked) |
| `model_factory.py` | Gives the app a model: Bedrock, Azure, OpenAI or the Offline stand-in |
| `diagram.py` · `design_decision.py` | Pictures · your team ADR |
| `run.py` · `run.bat` | Start the lab (`python run.py`, or double-click `run.bat`) |

Prices are approximate and were checked on 12 Oct 2026. Always check the vendor's price page before you quote a client.
