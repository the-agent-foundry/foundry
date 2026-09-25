# Specialist model appendix

The main roster is intentionally limited to agent-capable language-model candidates. Specialist models deserve separate decisions because their units, quality criteria, and operational risks differ.

**Snapshot date:** 2026-08-11. This separately dated historical appendix is not part of the September language-roster refresh; its prices and availability need their own current source check before use. The validator rejects a missing, duplicate, or future-to-roster appendix date. Public documentation snapshots are not local entitlement proof.

## Image and video examples

| Provider | Model | Public list price | Editorial starting use | Price evidence |
|---|---|---:|---|---|
| OpenAI | `gpt-image-2` | image input $8/MTok; image cached input $2; image output $30; text input $5; text cached input $1.25 | image generation/editing where token-level controls fit | Official: [pricing](https://developers.openai.com/api/docs/pricing) |
| OpenAI | `sora-2` | from $0.10/sec standard at 720p | cost-conscious generated video | Official: [pricing](https://developers.openai.com/api/docs/pricing) |
| OpenAI | `sora-2-pro` | $0.30 to $0.70/sec standard by resolution | higher-quality generated video | Official: [pricing](https://developers.openai.com/api/docs/pricing) |
| xAI | `grok-imagine-image-2.0` | media input $0.01/image; output $0.04 at 1K low, $0.06 at 2K low or 1K medium, $0.08 at 2K medium | variable-quality image generation | Official: [pricing](https://docs.x.ai/developers/pricing) |
| xAI | `grok-imagine-image-quality` | media input $0.01/image; output $0.05 at 1K or $0.07 at 2K | higher-quality image generation | Official: [pricing](https://docs.x.ai/developers/pricing) |
| xAI | `grok-imagine-video-1.5` | media input $0.01/image; output $0.08/sec at 480p, $0.14 at 720p, $0.25 at 1080p | generated video | Official: [pricing](https://docs.x.ai/developers/pricing) |
| Google | `gemini-omni-flash-preview` | multimodal input $1.50/MTok; text output $9; video output $17.50, effectively about $0.10/sec at 720p | multimodal generation/editing evaluation | Official: [pricing](https://ai.google.dev/gemini-api/docs/pricing) |

## Audio examples

| Provider | Route | Public list price | Editorial starting use | Price evidence |
|---|---|---:|---|---|
| OpenAI | `gpt-transcribe` | estimated $0.0045/min | asynchronous speech transcription | Official: [pricing](https://developers.openai.com/api/docs/pricing) |
| OpenAI | `gpt-live-transcribe` | estimated $0.017/min | live transcription | Official: [pricing](https://developers.openai.com/api/docs/pricing) |
| xAI | speech to text | $0.10/hr REST; $0.20/hr streaming | low-cost transcription evaluation | Official: [pricing](https://docs.x.ai/developers/pricing) |
| xAI | `grok-voice-think-fast-2.0` | $0.08/min audio plus $0.004 per text input | speech-to-speech agents | Official: [pricing](https://docs.x.ai/developers/pricing) |
| Google | `gemini-3.5-live-translate-preview` | documented effective combined audio price about $0.0368/min | live speech translation | Official: [pricing](https://ai.google.dev/gemini-api/docs/pricing) |

## Selection rules for specialists

Do not rank specialist models using only price per image, second, minute, or token. Add task-specific quality and safety measures:

- **Image:** prompt adherence, text rendering, identity/brand consistency, edit fidelity, safety rejection rate, and human revision time.
- **Video:** motion coherence, scene continuity, audio alignment, usable seconds per generated second, and retry cost.
- **Audio:** word error rate by accent/noise/domain, diarization, latency, interruption handling, and privacy/retention.
- **Embeddings/retrieval:** recall at the operating cutoff, ranking quality, dimensional/storage cost, re-index cost, language/domain coverage, and migration compatibility.
- **Moderation/classification:** false-negative floor, false-positive burden, calibration, explanation contract, and appeal path.

Keep specialist routes in your private overlay only after exact-route tests. A language model that can accept an image is not automatically the best image model. A very 2026 sentence, but apparently one we need.
