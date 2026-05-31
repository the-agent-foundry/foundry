---
name: <skill-name>
description: <one line: what this skill does and when it fires>
version: 1.0
owner: <YOUR_HANDLE>
tags: [<tag>, <tag>]
tools: [<tool-kind>, <tool-kind>]
data_sensitivity: <public|internal|confidential|restricted>
approval_required: <none|before_write|before_external_send|before_live_change>
---

# <Skill Name>

## When to use

<Describe the trigger. What kind of task makes the agent reach for this skill?>

<Also state when NOT to use it, so the agent does not over-apply it.>

## Inputs

- Required: <what the skill must have to start>
- Optional: <what improves the result if available>
- Required tool capabilities:
  - <tool-kind>: must support <read/create/update/dry-run/read-back/status/etc.>
- If missing: <what the agent should do when a required input is absent, e.g. ask, use a safe fallback, or stop>

## Procedure

1. <First step. Be specific.>
2. <Next step.>
3. <Next step.>
4. <Final step, ending in a verifiable output.>

## What good looks like

<The concrete definition of done. This is the section that matters most, because the agent enforces it. Describe the quality bar like you are briefing a sharp but inexperienced new hire. Be specific about structure, completeness, tone, and the checks that prove it is right.>

## Output contract

- Primary output: <file/message/task/summary/etc.>
- Required fields/sections: <exact structure>
- Destination: <where it goes>
- Example skeleton: <safe placeholder example>

## Privacy and approval

- Data allowed: <what this skill may read or process>
- Data blocked: <what must never be included>
- Redaction rule: <what gets replaced with placeholders before sharing or logging>
- Pre-approved routes: <none by default, or exact policy/source of truth>
- Approval evidence: <approver, destination, content/data class, scope, timestamp, expiry>
- Approval required before: <external sends, writes, live changes, deletes, or other risky actions>

## Verification

- <How the agent proves the output is correct>
- <What command, review, link, file, dry-run, or artifact backs the done claim>

## Maintenance

- Update this skill when <trigger>.
- Add a Landmine every time <failure case> happens.
- Re-review every <cadence or trigger>.

## Landmines

- <Known failure mode>: <the guardrail that prevents it>
- <Add a new entry every time this skill bites you. This is the scar tissue that makes it compound.>
