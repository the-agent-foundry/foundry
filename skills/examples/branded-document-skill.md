---
name: branded-document
description: Produces on-brand PDFs and HTML from a style guide and assets, with clean pagination and reliable delivery.
version: 1.1
owner: <YOUR_HANDLE>
tags: [documents, branding, pdf, html]
tools: [document-renderer]
data_sensitivity: internal
approval_required: before_external_send
---

# Branded Document

Default document generation struggles with pagination, asset handling, and clean delivery. This skill stores the fixes so the agent produces documents that look finished, on brand, and readable instead of repeatedly stepping on the same rendering landmines.

## When to use

Use this when the agent needs to produce a polished, branded deliverable: a briefing, research roundup, one-pager, proposal, founder memo, or board-style package.

Do not use it for quick internal notes, scratch drafts, or content that lives inside a chat. Branding overhead is wasted on throwaway output.

## Inputs

- Required: final or near-final content, brand rules, logo files, font rules, color palette, and desired output format.
- Optional: cover page spec, target audience, page-size preference, source links, chart assets, and delivery channel.
- If missing: if brand assets are not available, ask for them or produce a clearly labeled unbranded draft. Do not invent brand rules.

## Procedure

1. Load the brand rules: typography, colors, spacing, logo placement, and any layout constraints.
2. Structure the content into sections with a clear hierarchy before styling anything.
3. Apply the brand without improvising new fonts, colors, or logo treatments.
4. Render with explicit pagination control: avoid orphaned headings, broken tables, clipped content, and awkward page breaks.
5. Check the first page, a middle page, and the last page for layout breaks.
6. Check links, image paths, headings, and file size.
7. Deliver the rendered file with a sensible filename. Do not paste raw markup as the deliverable.
8. If external send is requested, pause for approval unless a documented pre-approval record covers the exact destination, action type, data class, scope, and expiry.

## What good looks like

A document that could go to a client, investor, board member, or senior operator without a human reformatting it. Specifically:

- On brand: correct fonts, colors, spacing, and logo usage.
- Clean pagination: no orphaned headings, clipped sections, or broken tables.
- Clear hierarchy: the reader can scan it and find what matters.
- Source material is represented accurately.
- Delivered as a proper file in the requested format.
- Looks finished, not auto-generated.

## Output contract

- Primary output: rendered HTML, PDF, or both.
- Required fields/sections: title, audience, source summary, content sections, source links where appropriate, and delivery file path or public link.
- Required tool capabilities: local asset loading, HTML/PDF export, link checking, page inspection, and deterministic filename output.
- Destination: local file, document store, or approved delivery channel.
- Example skeleton:

```md
File: <safe filename>
Format: <HTML|PDF>
Audience: <audience>
Template: <template name>
Checks: brand, pagination, links, file opens
Delivery: <path or approved destination>
```

## Privacy and approval

- Data allowed: approved brand assets, approved source copy, public claims, internal notes appropriate for the audience.
- Data blocked: credentials, raw logs, private memory, sensitive customer material, and private internal strategy unless explicitly approved for the document.
- Redaction rule: replace private names, metrics, and identifiers with placeholders in public examples.
- Approval required before: sending externally, publishing, or using restricted brand/customer examples.

## Verification

- Open the rendered file and inspect representative pages.
- Verify links resolve or are intentionally plain text.
- Verify no raw template markers remain.
- Run the repo or content QA gate when the document is public-facing.
- Return the file path or public link, plus a short note on what was checked.

## Maintenance

- Update this skill when brand rules change, rendering tools change, or a layout bug appears twice.
- Keep asset locations and template variants documented in a private companion note, not in public examples.
- Add screenshots or fixture outputs in a private repo if visual regressions become common.

## Landmines

- **Pagination breaks**: default renderers orphan headings and clip content at page edges. Control page breaks and verify across multiple pages.
- **Improvised branding**: the agent invents colors or fonts because it did not load the style guide. Load real brand rules first, or produce a labeled unbranded draft.
- **Raw markup delivery**: pasting HTML or markdown into a message is not a deliverable. Render and attach a real file.
- **Asset drift**: stale logos or palette values quietly make documents look off. Keep brand assets in one source of truth.
- **Styled wall of text**: branding does not save poor structure. Structure first, then style.
