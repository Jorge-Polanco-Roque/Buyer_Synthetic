<h1 align="center">Buyer Synthetic</h1>

<p align="center">
  <strong>AI agents that act as synthetic survey respondents — grounded in real data, answering a questionnaire as if they were real people.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-blue?logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/LangGraph-agentic-ff6f00" alt="LangGraph">
  <img src="https://img.shields.io/badge/LLM-personas-412991?logo=openai&logoColor=white" alt="LLM">
  <img src="https://img.shields.io/badge/pandas-data-150458?logo=pandas&logoColor=white" alt="pandas">
</p>

---

## Overview

Buyer Synthetic is an experimental framework that replaces (or augments) traditional survey
fieldwork with **AI agents that behave as synthetic respondents**. Given a target audience and
a questionnaire, the system builds synthetic personas grounded in real survey data and has them
answer as if they were real people, producing consistent, structured results in a fraction of
the time and cost of in-person surveys.

It is a study of a simple question: **how far can LLM-driven agents reproduce the responses of a
defined population**, and can synthetic panels stand in for costly field studies for early
validation, market exploration, and scenario testing?

## Approach

| Step | What happens |
|---|---|
| **Persona grounding** | Synthetic profiles built from real survey data and contextual sources (demographics, segments; the case study uses Peru's 2025–2026 electoral context) |
| **Agentic response flow** | A LangGraph pipeline (`agentes/flujo.py`) orchestrates persona construction, questionnaire application, and answer generation |
| **Structured output** | Questionnaires are converted to JSON, answers collected per persona, and results exported as CSV panels with an auditing layer |

## What's inside

The repository is organized as successive research iterations:

- **`Iteración #1/`** — first prototype: synthetic base, persona profiles, political context,
  prompts, and exploratory notebooks (`test_310525.ipynb`, `test_perú_01.ipynb`).
- **`Iteración #2/` and `#3/`** — modular refactor:
  - `agentes/` — the agentic flow and panel logic.
  - `funciones/` — helper functions (LLM calls, context loading, CSV filling, math).
  - `prompts/` — questionnaire-to-JSON and scenario prompts.
  - `viz/` + `output/` — flow visualization and result CSVs.

## Tech Stack

Python · LangGraph · LLM APIs · pandas.

> Applied R&D project. "Buyer Synthetic" is a product concept by IMA.GO; this repository holds
> the research and engineering iterations behind it.
