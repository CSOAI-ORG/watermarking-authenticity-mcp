# Watermarking Authenticity

> By [MEOK AI Labs](https://meok.ai) — MEOK AI Labs — EU AI Act Article 50 watermarking compliance. C2PA metadata, content provenance, AI detection.

Watermarking & Content Authenticity MCP — MEOK AI Labs. EU AI Act Article 50 compliance. Nov 2, 2026 deadline.

## Installation

```bash
pip install watermarking-authenticity-mcp
```

## Usage

```bash
# Run standalone
python server.py

# Or via MCP
mcp install watermarking-authenticity-mcp
```

## Tools

### `check_watermark_compliance`
Check if AI-generated content meets EU AI Act Article 50 watermarking requirements.

**Parameters:**
- `content_type` (str)
- `has_watermark` (bool)
- `has_c2pa` (bool)
- `has_disclosure` (bool)

### `generate_c2pa_manifest`
Generate C2PA (Content Authenticity Initiative) manifest data for AI-generated content.

**Parameters:**
- `creator` (str)
- `content_type` (str)
- `ai_model` (str)
- `description` (str)

### `detect_ai_content`
Analyze text for AI-generated patterns (perplexity, burstiness, vocabulary distribution).

**Parameters:**
- `text` (str)

### `watermarking_readiness`
Assess organization readiness for EU AI Act Article 50 watermarking obligations.

**Parameters:**
- `organization` (str)
- `content_types` (str)

### `get_article_50_timeline`
Get EU AI Act Article 50 implementation timeline and requirements.


## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## Links

- **Website**: [meok.ai](https://meok.ai)
- **GitHub**: [CSOAI-ORG/watermarking-authenticity-mcp](https://github.com/CSOAI-ORG/watermarking-authenticity-mcp)
- **PyPI**: [pypi.org/project/watermarking-authenticity-mcp](https://pypi.org/project/watermarking-authenticity-mcp/)

## License

MIT — MEOK AI Labs
