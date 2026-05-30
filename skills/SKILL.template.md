---
name: <skill-name>
description: <one line: what this skill does and when it fires>
version: 1.0
owner: <YOUR_HANDLE>
tags: [<tag>, <tag>]
tools: [<tool-kind>, <tool-kind>]
---

# <Skill Name>

## When to use

<Describe the trigger. What kind of task makes the agent reach for this skill?>

<Also state when NOT to use it, so the agent does not over-apply it.>

## Inputs

- Required: <what the skill must have to start>
- Optional: <what improves the result if available>
- If missing: <what the agent should do when a required input is absent, e.g. ask, or fall back>

## Procedure

1. <First step. Be specific.>
2. <Next step.>
3. <Next step.>
4. <Final step, ending in a verifiable output.>

## What good looks like

<The concrete definition of done. This is the section that matters most, because the agent enforces it. Describe the quality bar like you are briefing a sharp but inexperienced new hire. Be specific about structure, completeness, tone, and the checks that prove it is right.>

## Landmines

- <Known failure mode>: <the guardrail that prevents it>
- <Add a new entry every time this skill bites you. This is the scar tissue that makes it compound.>
