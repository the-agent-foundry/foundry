---
name: skillify-loop
description: Converts repeated successes, failures, and workflows into durable skills, scripts, gates, or references.
version: 1.0
owner: <YOUR_HANDLE>
tags: [skills, codification, improvement, operations]
tools: [file-editor, test-runner, task-manager]
data_sensitivity: internal
approval_required: before_write
---

# Skillify Loop

The compounding loop is simple: when the agent learns something useful or fails in a repeatable way, write the lesson down where it will fire next time. This skill prevents one-off fixes from evaporating.

## When to use

Use this after a repeated request, a painful failure, a successful complex workflow, a new operating pattern, or a correction the user should never need to repeat.

Do not use it for temporary task progress, one-off facts that will be stale soon, or session logs that belong in an archive rather than a reusable procedure.

## Inputs

- Required: the workflow or failure, trigger conditions, desired future behavior, and the likely owner skill or artifact.
- Optional: examples, test fixtures, commands, source notes, screenshots, and prior related skills.
- If missing: ask what should happen next time before codifying. Do not infer a new policy from a single ambiguous correction.

## Procedure

1. Classify the lesson: failure, success, workflow, external idea, or style preference.
2. Decide the right artifact: skill, reference note, template, script, test, gate, memory, task, or no-op.
3. Search existing skills before creating a new one. Prefer extending the closest owner.
4. Define trigger, inputs, output, quality bar, privacy boundary, approval requirement, and verification step.
5. Add or patch the artifact.
6. Add tests or fixtures if the failure can recur mechanically.
7. Run the relevant gates.
8. Report what changed and how future runs will behave differently.

## What good looks like

The next similar request is easier, safer, and less dependent on the user's memory. Specifically:

- The lesson lands in the artifact that will actually be loaded next time.
- The update is broad enough to cover the class, not just the instance.
- The skill gains scar tissue, not vague advice.
- Tests or checks exist when the failure is mechanical.
- No stale session progress is saved as durable memory.
- The user does not have to repeat the correction.

## Output contract

- Primary output: artifact decision plus patch or draft.
- Required fields:
  - Lesson type: failure, success, workflow, external idea, style preference, or no-op.
  - Owner artifact: skill, reference, template, script, test, memory, task, or none.
  - Trigger: when it should fire next time.
  - Change made: exact file or artifact changed.
  - Verification: gate, fixture, read-back, or test.
  - Future behavior: what will happen differently.
- Required tool capabilities: search existing artifacts, edit target file, run validation, and return diff or path.
- Example skeleton:

```md
Lesson type: <type>
Owner artifact: <artifact/path>
Trigger: <future trigger>
Change made: <summary>
Verification: <command or check>
Future behavior: <what changes next time>
```

## Privacy and approval

- Data allowed: generalized lesson, sanitized examples, commands without secrets, and public-safe references.
- Data blocked: credentials, private memory dumps, raw chat logs, customer details, and private source files unless they are the approved owner artifact.
- Redaction rule: turn private examples into generalized failure cases before adding them to public docs.
- Approval required before: changing active runtime behavior, adding scheduled automation, writing shared docs, or creating a new skill category that changes routing.

## Verification

- Confirm the target artifact exists and contains the new trigger or guardrail.
- Run syntax, lint, or test gates for changed files.
- If a failure was fixed, run a negative fixture proving it now fails or routes correctly.
- Search for duplicate or competing skills that could bypass the new owner.

## Maintenance

- Revisit when the skill fires incorrectly, fails to fire, overlaps another skill, or grows too broad.
- Merge overlapping skills rather than building a graveyard of tiny procedures.
- Archive stale skills with a clear replacement instead of deleting institutional memory blindly.

## Landmines

- **Skill sprawl**: creating a new micro-skill for every session makes the catalog unusable. Extend an owner skill first.
- **Saving progress as memory**: `finished PR X` is stale. Procedures belong in skills; temporary state belongs in session history or task systems.
- **No verification**: a skill update that was never tested may only document the next failure.
- **Wrong owner**: if the future task loads a different skill, your fix will not fire.
- **Over-codifying one-offs**: not every clever workflow deserves a permanent slot.
