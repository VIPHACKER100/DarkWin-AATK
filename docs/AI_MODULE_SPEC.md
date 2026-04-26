# DARKWIN AI Module Specification — Phase 2

**Status:** TODO — Phase 2 (Not implemented in v1.0.0)

---

## Overview

This document specifies the planned AI-powered modules for DARKWIN v2.0.
These modules will layer intelligent analysis on top of the existing tool outputs.

---

## 1. False Positive Filter

### Purpose
Automatically classify scan results as true positives or false positives using an LLM.

### Input Format
```json
{
  "tool": "dalfox",
  "vulnerability_type": "xss",
  "target_url": "https://example.com/page?q=PAYLOAD",
  "raw_output": "...",
  "payload_used": "<script>alert(1)</script>",
  "http_response_snippet": "..."
}
```

### Output Format
```json
{
  "classification": "true_positive" | "false_positive" | "uncertain",
  "confidence": 0.0–1.0,
  "reasoning": "...",
  "recommended_action": "report" | "retest" | "discard"
}
```

### Integration Hook
Module: `modules/ai/false_positive_filter.py`
Called after: each vulnerability scanner's `run()` function.

---

## 2. Payload Suggestion API

### Purpose
Given a vulnerability type and target context, suggest optimised attack payloads.

### Input Format
```json
{
  "vulnerability_type": "sqli" | "xss" | "ssrf" | "rce",
  "context": {
    "parameter_name": "id",
    "response_behavior": "time_delay_observed",
    "db_type_hint": "mysql"
  }
}
```

### Output Format
```json
{
  "payloads": ["payload1", "payload2", "..."],
  "technique": "time_based_blind",
  "confidence": 0.85,
  "notes": "..."
}
```

### Integration Hook
Module: `modules/ai/payload_suggester.py`
Called before: fuzzing and vulnerability scanner runs.

---

## 3. Auto-Exploit Suggestion Pipeline

### Purpose
Chain recon findings → vulnerability findings → suggest exploitation path.

### Pipeline Hooks
1. Receive structured scan results from `report_builder.collect_results()`
2. LLM analyses the attack surface and identifies chaining opportunities
3. Output a prioritised exploitation roadmap

### Output Format
```json
{
  "target": "example.com",
  "attack_chains": [
    {
      "severity": "critical",
      "chain": ["subdomain_takeover → ssrf → rce"],
      "tools_needed": ["nuclei", "ffuf", "msfconsole"],
      "estimated_complexity": "medium"
    }
  ]
}
```

### Integration Hook
Module: `modules/ai/auto_exploit_suggester.py`
Called after: `full_scan_pipeline.run()` completes.

---

## Implementation Notes

- All AI modules will use an LLM API (OpenAI / Anthropic / local Ollama) configured via `core/config.yaml`
- Rate limiting and cost controls must be implemented
- AI outputs are advisory only — human verification is always required
- Privacy: no raw target data should be sent to external AI APIs without explicit user consent flag in config

---

*Phase 2 implementation timeline: TBD — pending v1.0.0 field validation.*
