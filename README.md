# Buyer Synthetic — AI Agents as Synthetic Survey Respondents

An experimental framework that replaces (or augments) traditional survey fieldwork
with **AI agents that act as synthetic respondents**. Given a target audience and a
questionnaire, the system generates synthetic personas grounded in real data and has
them answer as if they were real people, producing consistent, structured results in
a fraction of the time and cost of in-person surveys.

## Objective

Explore how far LLM-driven agents can reproduce the responses of a defined population
to a questionnaire, and whether synthetic panels can stand in for costly field studies
for early validation, market exploration, and scenario testing.

## Approach

- **Persona grounding** — synthetic profiles are built from real survey data and
  contextual sources (demographics, segments, and, in the included case study, the
  political context of Peru's 2025–2026 electoral cycle).
- **Agentic response flow** — a LangGraph-based pipeline (`agentes/flujo.py`) orchestrates
  persona construction, questionnaire application, and answer generation.
- **Structured output** — questionnaires are converted to JSON, answers are collected
  per persona, and results are exported as CSV panels with an auditing layer.

## What's inside

The repo is organized as successive iterations:

- **`Iteración #1/`** — first prototype: synthetic base, persona profiles, political
  context, prompts, and exploratory notebooks (`test_310525.ipynb`, `test_perú_01.ipynb`).
- **`Iteración #2/`** and **`#3/`** — refactored, modular version:
  - `agentes/` — the agentic flow and panel logic.
  - `funciones/` — helper functions (LLM calls, context loading, CSV filling, math).
  - `prompts/` — questionnaire-to-JSON and scenario prompts.
  - `viz/` + `output/` — flow visualization and result CSVs.

## Stack

Python · LLM APIs · LangGraph · pandas.

> Note: developed as an applied R&D project. "Buyer Synthetic" is a product concept
> by IMA.GO; this repository holds the research and engineering iterations behind it.
