# Atlas Video Engine V1

Purpose: assemble a zero/near-zero-cost short-form video pipeline from mature open-source components instead of rebuilding an editor from scratch.

## Architecture

MUSE brief -> scene plan -> Short Video Maker-compatible render adapter -> narration/captions/B-roll -> Atlas FFmpeg preflight -> publisher.

## Donor stack

- gyoridavid/short-video-maker: MIT-licensed architecture/reference for MCP/REST short-video generation, Kokoro TTS, Whisper captions, Pexels footage, Remotion/FFmpeg rendering.
- FFmpeg/ffprobe: Atlas-owned normalization and launch gate.
- Future donors are admitted only after license/security review.

## Security rule

Do NOT deploy short-video-maker <=1.3.4 as a network-accessible service. CVE-2026-8115 reports path traversal in its REST tmp-file route and no patched release is listed. V1 therefore borrows architecture/components while keeping Atlas's initial runner non-public. If the upstream service is integrated later, Atlas must patch/sandbox the vulnerable route first.

## Launch gate

Every output must pass ffprobe checks before it can enter Metricool:
- 1080x1920
- H.264
- yuv420p
- constant 30 FPS
- valid duration
- audio stream when narration/music is expected

A failed gate triggers normalize -> verify -> retry, never publish-and-hope.
