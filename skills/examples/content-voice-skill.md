---
name: content-voice
description: Drafts content from a voice corpus and anti-slop corpus while preserving claims, taste, and human editability.
version: 1.0
owner: <YOUR_HANDLE>
tags: [writing, voice, content, editing]
tools: [document-reader, web-search]
data_sensitivity: confidential
approval_required: before_external_send
---

# Content Voice

Voice is trained by examples and protected by taste. This skill uses a positive corpus of strong writing and a negative corpus of slop to draft content that sounds like the author without faking claims or flattening the edge.

## When to use

Use this for founder posts, essays, field guides, memos, speeches, newsletter drafts, and lightly edited thought leadership.

Do not use it for legal language, financial claims, medical claims, customer statements, or crisis communication without a separate expert review path.

## Inputs

- Required: topic, audience, desired channel, source material, claim boundaries, and voice corpus or style notes.
- Optional: anti-slop examples, prior drafts, target length, examples to emulate, examples to avoid, and factual source links.
- If missing: ask for the missing source material or label the result as a speculative draft. Do not invent anecdotes, metrics, or quotes.

## Procedure

1. Identify the point of the piece in one sentence.
2. Pull voice patterns from the positive corpus: sentence rhythm, argument style, humor level, and typical structure.
3. Pull anti-patterns from the negative corpus: phrases, cadence, fake depth, generic endings, and vendor-sounding claims to avoid.
4. Draft from source material only. Separate facts from interpretation.
5. Run a self-critique pass for slop, unsupported claims, voice mismatch, and boring structure.
6. Revise once or twice. Do not keep looping until the draft becomes over-polished mush.
7. Return the draft plus a short editor note: strongest section, weakest section, claims that need verification, and suggested human edits.
8. Pause for approval before posting or sending externally.

## What good looks like

A draft that is 80 to 90 percent useful to the author. Specifically:

- It has a clear point of view.
- It sounds like a person with taste, not a generic content engine.
- It avoids filler, fake authority, and tidy corporate endings.
- Claims are sourced, known, or explicitly labeled as opinion.
- It preserves rough edges where they carry voice.
- It is easy for a human to finish.

## Output contract

- Primary output: draft plus editor package.
- Required sections:
  - Draft: the proposed piece.
  - Editor note: strongest section, weakest section, and suggested human edits.
  - Claim ledger: claim, source, status, and verification need.
  - Voice check: what matched the voice corpus.
  - Anti-slop check: what was removed or avoided.
  - Human review asks: decisions the author must make.
- Required tool capabilities: read approved corpus, track sources, preserve draft versions, and block external posting without approval.
- Example skeleton:

```md
Draft:
<content>
Editor note:
- Strongest: <section>
- Weakest: <section>
Claim ledger:
- <claim> | source: <source> | status: <verified|known|opinion|needs check>
```

## Privacy and approval

- Data allowed: approved writing samples, approved source notes, public sources, and private drafts intended for this workflow.
- Data blocked: private customer stories, employee details, investor material, raw transcripts, and unpublished sensitive strategy unless approved for the specific piece.
- Redaction rule: public examples must replace real names, numbers, company details, and private anecdotes with placeholders.
- Approval required before: posting, sending externally, quoting a private person, using a customer story, or making a factual claim that has not been verified.

## Verification

- Run a claim check: every concrete claim is sourced, known, or labeled opinion.
- Run an anti-slop pass: remove generic phrases, fake contrast formulas, and empty calls to action.
- Compare against two or three voice examples for rhythm and stance.
- Return unresolved claim checks in the editor note.

## Maintenance

- Add new strong examples to the private voice corpus after publication.
- Add bad drafts to the anti-slop corpus when they reveal a recurring machine-writing habit.
- Update the skill when the author's public voice evolves.
- Keep private corpus files out of public repos.

## Landmines

- **Voice mimicry without substance**: sounding right while saying nothing is worse than a plain draft. Start with the argument.
- **Invented anecdotes**: never create stories, metrics, quotes, or customer examples to make the piece stronger.
- **Over-sanitized prose**: removing every sharp edge makes the author sound like a committee.
- **Recursive mush**: too many revision loops smooth away voice. Limit passes.
- **Public leak through examples**: voice samples can contain private facts. Public examples must be sanitized or synthetic.
