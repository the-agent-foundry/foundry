---
name: branded-document
description: Produces perfectly on-brand PDFs and HTML from a style guide and brand assets, with clean pagination and reliable delivery.
version: 1.0
owner: <YOUR_HANDLE>
tags: [documents, branding, pdf, html]
tools: [document-renderer]
---

# Branded Document

Default document generation struggles with pagination, asset handling, and clean delivery. This skill hardcodes the fixes so the agent produces documents that look like a finished product, on brand, every time, instead of stepping on the same rendering landmines repeatedly.

## When to use

Use this when the agent needs to produce a polished, branded deliverable: a briefing, a research roundup, a one-pager, a proposal, anything that should arrive looking finished rather than as a wall of text.

Do not use it for quick internal notes or for content that lives inside a chat. Branding overhead is wasted on throwaway output.

## Inputs

- Required: the content to render, and the brand assets (style guide rules, fonts, logos, color palette).
- Optional: a target format (PDF or HTML), a template variant, a cover page spec.
- If missing: if brand assets are not available, ask for them or fall back to a clearly-labeled unbranded draft rather than guessing at the brand.

## Procedure

1. Load the brand rules: fonts, colors, spacing, logo placement, and any layout constraints from the style guide.
2. Structure the content into sections with a clear hierarchy before styling anything.
3. Apply the brand: typography, palette, and logo per the style guide. Do not improvise brand decisions.
4. Render with explicit pagination control: avoid orphaned headings, broken tables across pages, and clipped content.
5. Verify the output renders cleanly: check the first page, a middle page, and the last page for layout breaks.
6. Deliver the file in the requested format with a sensible filename, never as raw markup pasted into a message.

## What good looks like

A document that could go straight to a client or board member without a human reformatting it. Specifically:

- On brand: correct fonts, colors, and logo placement, matching the style guide exactly.
- Clean pagination: no orphaned headings, no content clipped at a page boundary, no tables split badly.
- Clear hierarchy: the reader can scan it and find what matters.
- Delivered as a proper file, named sensibly, in the right format.
- Looks finished, not auto-generated.

## Landmines

- **Pagination breaks**: default renderers orphan headings and clip content at page edges. Always control page breaks explicitly and verify across multiple pages.
- **Improvised branding**: the agent inventing colors or fonts because it did not load the style guide. Always load real brand rules first, or produce a labeled unbranded draft.
- **Raw markup delivery**: pasting HTML or markdown into a message instead of rendering and attaching a file. Always deliver a real file.
- **Asset drift**: stale logos or old palette values. Keep brand assets in one place and reference that, do not hardcode old values.
- **Heavy content, no structure**: styling a wall of text does not make it readable. Structure first, then brand.
