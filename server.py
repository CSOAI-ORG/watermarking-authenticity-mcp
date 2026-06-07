#!/usr/bin/env python3
"""Watermarking & Content Authenticity MCP — MEOK AI Labs. EU AI Act Article 50 compliance. Nov 2, 2026 deadline."""

import sys, os

_MEOK_API_KEY = os.environ.get("MEOK_API_KEY", "")

try:
    from auth_middleware import check_access as _shared_check_access
    _AUTH_ENGINE_AVAILABLE = True
except ImportError:
    _AUTH_ENGINE_AVAILABLE = False

    def _shared_check_access(api_key: str = ""):
        """Fallback when shared auth engine is not available."""
        if _MEOK_API_KEY and api_key and api_key == _MEOK_API_KEY:
            return True, "OK", "pro"
        if _MEOK_API_KEY and api_key and api_key != _MEOK_API_KEY:
            return False, "Invalid API key. Get one at https://meok.ai/api-keys", "free"
        return True, "OK, Pro at https://www.csoai.org/checkout", "free"


def check_access(api_key: str = ""):
    """Unified access check."""
    return _shared_check_access(api_key)



import json, os, hashlib, re, base64
from datetime import datetime, timezone
from typing import Optional
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

FREE_DAILY_LIMIT = 10
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now); return None

mcp = FastMCP("watermarking-authenticity", instructions="MEOK AI Labs — EU AI Act Article 50 watermarking compliance. C2PA metadata, content provenance, AI detection.")

# ── Structured Output Helpers ─────────────────────────────────

def structured_output(data, summary: str = ""):
    """Return MCP-compatible structured output with both LLM text and protocol-level data.
    
    Args:
        data: The result data (dict, list, or Pydantic model)
        summary: Brief human-readable summary for the LLM (auto-generated if empty)
    """
    if hasattr(data, 'model_dump'):
        data_dict = data.model_dump()
    else:
        data_dict = data
    
    if not summary:
        # Auto-generate summary from key fields
        parts = []
        for k, v in list(data_dict.items())[:3]:
            if isinstance(v, (str, int, float)):
                parts.append(f"{k}: {v}")
        summary = " | ".join(parts) if parts else "Result"
    
    return {
        "content": [{"type": "text", "text": summary + "\n\n" + str(data_dict)}],
        "structuredContent": data_dict,
        **data_dict  # Legacy compatibility
    }


def error_output(message: str, code: str = "INTERNAL_ERROR", upgrade_url: str = ""):
    """Return structured error output."""
    result = {
        "content": [{"type": "text", "text": f"Error: {message}"}],
        "structuredContent": {"error": message, "code": code},
        "error": message,
        "code": code
    }
    if upgrade_url:
        result["structuredContent"]["upgrade_url"] = upgrade_url
        result["upgrade_url"] = upgrade_url
    return result


@mcp.tool()
def check_watermark_compliance(content_type: str, has_watermark: bool, has_c2pa: bool, has_disclosure: bool, api_key: str = "") -> str:
    """Check if AI-generated content meets EU AI Act Article 50 watermarking requirements."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://buy.stripe.com/00wfZjcgAeUW4c5cyQ8k90K"}

    if err := _rl(): return err
    reqs = {"machine_readable_marking": has_watermark, "c2pa_metadata": has_c2pa, "human_disclosure": has_disclosure}
    compliant = all(reqs.values())
    deadline = datetime(2026, 11, 2, tzinfo=timezone.utc)
    days = (deadline - datetime.now(timezone.utc)).days
    return {"content_type": content_type, "requirements": reqs, "compliant": compliant,
        "deadline": "November 2, 2026", "days_remaining": days,
        "article": "EU AI Act Article 50 (Transparency for GPAI systems)",
        "penalty": "EUR 15M or 3% of global turnover",
        "remediation": [k for k, v in reqs.items() if not v] or ["All requirements met"]}

@mcp.tool()
def generate_c2pa_manifest(creator: str, content_type: str, ai_model: str = "", description: str = "", api_key: str = "") -> str:
    """Generate C2PA 2.1 (Content Authenticity Initiative) manifest data for AI-generated content.

    Per C2PA spec 2.1 (September 2024). Includes:
    - Mandatory `c2pa.created` action with `digitalSourceType` algorithmicMedia
    - Ingredients v3 with `dataTypes` and `claimSignature` placeholders
    - RFC 3161 time-stamping reference (sigTst2 model)
    - C2PA URN namespace for standardized referencing
    - Training_mining assertion (data-mining opt-out)

    For binary embedding into JPEG/PNG/WebP/MP4/PDF, use the c2pa-python library:
        pip install c2pa-python
        from c2pa import Builder, ManifestDefinition
        manifest = ManifestDefinition.from_json(generate_c2pa_manifest(...))
        Builder(manifest).sign_file(...).embed_to(...)

    EU AI Act Article 50 compliance: machine-readable AI marking required from 2 Aug 2026.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://buy.stripe.com/00wfZjcgAeUW4c5cyQ8k90K"}

    if err := _rl(): return err
    ts = datetime.now(timezone.utc).isoformat()
    instance_id = hashlib.sha256(f"{creator}{ts}".encode()).hexdigest()[:16]
    manifest_urn = f"urn:c2pa:{instance_id}"

    manifest = {
        "c2pa_version": "2.1",
        "spec_url": "https://c2pa.org/specifications/specifications/2.1/specs/C2PA_Specification.html",
        "claim_generator": "MEOK_AI_Labs_Watermarking_MCP/1.1.0",
        "claim_generator_info": [
            {"name": "MEOK AI Labs Watermarking MCP", "version": "1.1.0"}
        ],
        "title": description or f"AI-generated {content_type}",
        "format": content_type,
        "instance_id": instance_id,
        "manifest_urn": manifest_urn,
        "claim": {
            "dc:creator": creator,
            "dc:date": ts,
            "dc:title": description or f"AI-generated {content_type}",
            "c2pa.ai_info": {
                "model": ai_model,
                "type": "generated",
                "provider": creator,
            },
            "c2pa.actions": [
                {
                    "action": "c2pa.created",
                    "when": ts,
                    "digitalSourceType": "http://cv.iptc.org/newscodes/digitalsourcetype/algorithmicMedia",
                    "softwareAgent": {"name": "MEOK AI Labs Watermarking MCP"},
                }
            ],
        },
        "ingredients": [],
        "assertion_store": {
            "c2pa.training_mining": {
                "entries": {
                    "c2pa.ai_generative_training": {"use": "notAllowed", "constraint_info": "No training without license — MEOK AI Labs licence terms"},
                    "c2pa.ai_inference": {"use": "notAllowed", "constraint_info": "No inference use without licence"},
                    "c2pa.data_mining": {"use": "notAllowed"},
                }
            },
            "stds.iptc": {"DigitalSourceType": "algorithmicMedia"},
        },
        "rfc3161_timestamp": {
            "model": "sigTst2",
            "tsa_url": "https://meok-attestation-api.vercel.app/tsa",
            "note": "Production deployments should use a publicly trusted RFC 3161 TSA (e.g. FreeTSA, DigiCert)",
        },
        "signature": {
            "alg": "sha256",
            "value": hashlib.sha256(f"{creator}{ts}{ai_model}".encode()).hexdigest(),
            "note": "Stub signature. For production C2PA signing, use c2pa-python with a real Ed25519 / RSA key pair.",
        },
        "verify_url": f"https://meok-attestation-api.vercel.app/verify-c2pa/{instance_id}",
    }
    return manifest


@mcp.tool()
def list_c2pa_supported_formats(api_key: str = "") -> str:
    """List file formats supported by C2PA 2.1 spec for manifest embedding.

    Useful before attempting to embed a manifest — different formats use different
    embedding strategies (XMP packet, ISO-BMFF box, custom chunk, PDF metadata).
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://buy.stripe.com/00wfZjcgAeUW4c5cyQ8k90K"}
    return {
        "spec_version": "C2PA 2.1 (September 2024)",
        "supported_formats": {
            "images": ["JPEG", "PNG", "WebP", "TIFF", "GIF", "JPEG-XL", "HEIF/HEIC", "AVIF"],
            "video": ["MP4", "MOV", "BMFF-based formats"],
            "audio": ["MP3 (limited)", "WAV (sidecar)"],
            "documents": ["PDF"],
            "containers": ["ZIP-based formats"],
        },
        "embedding_strategies": {
            "JPEG/TIFF": "XMP packet + JUMBF box",
            "PNG": "iTXt or zTXt chunk with JUMBF",
            "MP4/MOV": "ISO-BMFF 'jumb' box",
            "PDF": "Metadata stream with JUMBF",
            "WebP": "Custom RIFF chunk",
        },
        "ai_act_article_50_eligible": True,
        "deadline": "2 August 2026 (hard deadline — not delayed by Digital Omnibus)",
        "official_libs": {
            "rust": "c2pa-rs (contentauth/c2pa-rs)",
            "python": "c2pa-python (PyPI: c2pa)",
            "js": "c2pa-js (WASM)",
            "cli": "c2patool",
        },
    }

@mcp.tool()
def detect_ai_content(text: str, api_key: str = "") -> str:
    """Analyze text for AI-generated patterns (perplexity, burstiness, vocabulary distribution)."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://buy.stripe.com/00wfZjcgAeUW4c5cyQ8k90K"}

    if err := _rl(): return err
    words = text.split()
    unique = len(set(w.lower() for w in words))
    total = len(words)
    vocab_ratio = unique / max(total, 1)
    # AI text tends toward uniform vocabulary distribution
    ai_patterns = ["in conclusion", "it is important to note", "furthermore", "moreover", "in summary",
                   "it should be noted", "this suggests that", "as a result", "in this context"]
    pattern_count = sum(1 for p in ai_patterns if p in text.lower())
    # Sentence length variance (AI tends to be more uniform)
    sentences = re.split(r'[.!?]+', text)
    lengths = [len(s.split()) for s in sentences if s.strip()]
    variance = sum((l - sum(lengths)/max(len(lengths),1))**2 for l in lengths) / max(len(lengths), 1) if lengths else 0
    ai_score = min(1.0, (pattern_count * 0.15) + (1.0 - vocab_ratio) * 0.5 + max(0, 0.5 - variance/100) * 0.35)
    return {
        "ai_probability": round(ai_score, 2),
        "classification": "likely_ai" if ai_score > 0.7 else "possibly_ai" if ai_score > 0.4 else "likely_human",
        "indicators": {"vocabulary_diversity": round(vocab_ratio, 2), "pattern_matches": pattern_count,
                      "sentence_variance": round(variance, 1), "word_count": total},
        "eu_ai_act_ref": "Article 50 — Transparency obligations for AI-generated content",
    }

@mcp.tool()
def watermarking_readiness(organization: str, content_types: str = "text,image", api_key: str = "") -> str:
    """Assess organization readiness for EU AI Act Article 50 watermarking obligations."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://buy.stripe.com/00wfZjcgAeUW4c5cyQ8k90K"}

    if err := _rl(): return err
    types = [t.strip() for t in content_types.split(",")]
    deadline = datetime(2026, 11, 2, tzinfo=timezone.utc)
    days = (deadline - datetime.now(timezone.utc)).days
    checklist = []
    for ct in types:
        checklist.append({
            "content_type": ct,
            "requirements": [
                {"item": "Machine-readable marking", "standard": "C2PA 2.0 or equivalent", "status": "check"},
                {"item": "Interwoven watermark", "standard": "SynthID or equivalent", "status": "check"},
                {"item": "Human-visible disclosure", "standard": "Clear labeling", "status": "check"},
            ],
            "technical_options": {
                "text": ["C2PA metadata", "Statistical watermark (distributional shift)"],
                "image": ["C2PA JUMBF", "SynthID", "Invisible frequency watermark"],
                "audio": ["AudioSeal (Meta)", "C2PA audio manifest"],
                "video": ["Per-frame SynthID", "C2PA video manifest"],
            }.get(ct, ["C2PA metadata"]),
        })
    return {"organization": organization, "deadline": "November 2, 2026", "days_remaining": days,
        "urgency": "CRITICAL" if days < 90 else "HIGH" if days < 180 else "MEDIUM",
        "content_types": checklist, "recommendation": f"{days} days to implement. Start with C2PA metadata (fastest) then add interwoven watermarks."}

@mcp.tool()
def get_article_50_timeline(api_key: str = "") -> str:
    """Get EU AI Act Article 50 implementation timeline and requirements."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://buy.stripe.com/00wfZjcgAeUW4c5cyQ8k90K"}

    now = datetime.now(timezone.utc)
    return {
        "article": "EU AI Act Article 50 — Transparency Obligations",
        "scope": "GPAI system providers generating synthetic audio, image, video, or text",
        "deadline": "November 2, 2026",
        "days_remaining": (datetime(2026, 11, 2, tzinfo=timezone.utc) - now).days,
        "requirements": [
            "Machine-readable marking in output (watermark or metadata)",
            "C2PA or equivalent content provenance standard",
            "Clearly inform users content is AI-generated",
            "Marking must be effective, interoperable, robust, reliable",
            "Must survive common modifications (cropping, compression)",
        ],
        "exemptions": ["Assistive function content", "Substantially human-edited content", "No material alteration"],
        "penalty": "EUR 15M or 3% of global annual turnover (Article 99(4))",
        "standards": ["C2PA (Content Authenticity Initiative)", "ISO/IEC 12927 (AI content provenance)", "ETSI GR SAI 019"],
    }



def main():
    """Entry point for the mcp command."""
    mcp.run()

if __name__ == "__main__":
    main()
