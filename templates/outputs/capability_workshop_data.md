# Capability Workshop Data Structure

**Purpose:** This template defines the data structure for capability assessment workshop outputs. The structured data can be consumed by interactive dashboards (like the NFIS workshop tool) for heatmap visualization, drill-down navigation, and CSV export.

**Usage:** After a capability assessment workshop, the agent exports structured data in this format. The data can then be loaded into an interactive HTML dashboard for stakeholder review.

---

## Workshop Metadata

```json
{
  "engagement": {
    "client": "[Client Name]",
    "domain": "[Retail Banking / Wealth Management / SME / Commercial / Corporate]",
    "date": "[YYYY-MM-DD]",
    "facilitator": "[Consultant Name]",
    "mode": "workshop | transcript_inference",
    "region": "[US / EMEA / APAC / LATAM / Global]"
  }
}
```

---

## Problem Statements Structure

```json
{
  "problems": [
    {
      "id": "CN-01",
      "title": "[Short problem title]",
      "subtitle": "[One-line description]",
      "description": "[2-3 sentence detailed description]",
      "type": "considered",
      "severity": "critical | high | medium | low",
      "impact": "[Quantified business impact]",
      "metrics": ["[Observable metric 1]", "[Observable metric 2]"],
      "evidence": ["E1", "E3"],
      "stakeholderQuote": "[Direct quote if available]",
      "stakeholderRole": "[Role]",
      "relatedCapabilities": ["CAP-X-XX-01", "CAP-X-XX-03"]
    },
    {
      "id": "UN-01",
      "title": "[Unconsidered need title]",
      "subtitle": "[One-line description]",
      "description": "[2-3 sentence description]",
      "type": "unconsidered",
      "severity": "high",
      "whyMissed": "[Why the organization hasn't thought of this]",
      "indicators": "[Evidence suggesting this problem exists]",
      "relatedCapabilities": ["CAP-X-XX-02", "CAP-X-XX-05"]
    }
  ]
}
```

---

## Capabilities Data Structure

```json
{
  "capabilities": [
    {
      "id": "CAP-X-XX-01",
      "domain": "[Backbase Capability Domain]",
      "bianArea": "[BIAN Business Area]",
      "name": "[Capability Name]",
      "description": "[Brief description]",
      "linkedProblems": ["CN-01", "UN-02"],
      "frontLayer": [
        "[Front layer component 1]",
        "[Front layer component 2]",
        "[Front layer component 3]"
      ],
      "middleLayer": [
        "[Middle layer component 1]",
        "[Middle layer component 2]",
        "[Middle layer component 3]"
      ],
      "backLayer": [
        "[Back layer component 1]",
        "[Back layer component 2]",
        "[Back layer component 3]"
      ],
      "questions": [
        {
          "gate": "0→1",
          "question": "[Probing question text]",
          "answer": "[Workshop answer or inferred answer]",
          "evidence": "E1",
          "result": "pass | fail"
        },
        {
          "gate": "1→2",
          "question": "[Probing question text]",
          "answer": "[Answer]",
          "evidence": "E3, Assumed",
          "result": "pass | fail"
        },
        {
          "gate": "2→3",
          "question": "[Probing question text]",
          "answer": "[Answer]",
          "evidence": null,
          "result": "fail"
        },
        {
          "gate": "3→4",
          "question": "[Probing question text]",
          "answer": "[Answer]",
          "evidence": null,
          "result": "fail"
        }
      ],
      "scores": {
        "front": 2,
        "middle": 1,
        "back": 1,
        "overall": 1
      },
      "confidence": "high | medium | low",
      "expectedMaturity": 1,
      "strengths": ["[Strength 1]", "[Strength 2]"],
      "gaps": [
        {
          "description": "[Gap description]",
          "rootCause": "[Why this gap exists]",
          "businessImpact": "[Impact]"
        }
      ],
      "assumptions": [
        {
          "text": "[Assumption text]",
          "basis": "[Why assumed]",
          "sensitivity": "high | medium | low",
          "validationOwner": "[Suggested owner]"
        }
      ],
      "notes": "[Workshop notes or additional context]"
    }
  ]
}
```

---

## Score Labels and Colors

```json
{
  "scoreLabels": {
    "0": "Absent",
    "1": "Fragmented",
    "2": "Defined",
    "3": "Orchestrated",
    "4": "Intelligent"
  },
  "scoreColors": {
    "0": "#E63946",
    "1": "#F4A261",
    "2": "#E9C46A",
    "3": "#2A9D8F",
    "4": "#0066FF"
  },
  "scoreDescriptions": {
    "0": "Capability doesn't exist. No process, no tool, no person performing this function.",
    "1": "Exists but ad-hoc. Person-dependent, inconsistent, manual workarounds.",
    "2": "Standardized process. Tooling supports it. Roles clear. Repeatable. But handoffs manual, measurement limited.",
    "3": "End-to-end orchestrated. Automated where possible. Measured with KPIs. Cross-system integration works.",
    "4": "AI-native. Predictive, self-optimizing. Agentic workflows. Real-time decisioning. Human-in-the-loop for exceptions only."
  }
}
```

---

## Heatmap Summary Structure

```json
{
  "heatmap": [
    {
      "domain": "[Capability Domain]",
      "capabilities": [
        {
          "id": "CAP-X-XX-01",
          "name": "[Name]",
          "front": 2,
          "middle": 1,
          "back": 1,
          "overall": 1,
          "keyGap": "[One-line gap description]",
          "problemCount": 3
        }
      ]
    }
  ]
}
```

---

## Traceability Matrix Structure

```json
{
  "traceability": [
    {
      "problemId": "CN-01",
      "problemTitle": "[Title]",
      "type": "considered",
      "severity": "critical",
      "capabilities": [
        {
          "id": "CAP-X-XX-01",
          "name": "[Name]",
          "currentScore": 1,
          "targetScore": 3
        }
      ],
      "weakestScore": 1,
      "readiness": "at_risk | well_positioned | blocked",
      "requiredImprovement": "[What needs to change]"
    }
  ]
}
```

---

## Export Format

The workshop data should be exportable in two formats:

### 1. JSON (for dashboard consumption)
Complete data structure as defined above, saved as `[engagement]_workshop_data.json`.

### 2. CSV (for spreadsheet analysis)
Flat export with one row per capability:

```
Domain, Capability ID, Capability Name, Front Score, Middle Score, Back Score, Overall Score, Confidence, Linked Problems, Key Gap, Notes
```

---

## Dashboard Views (Reference)

When building an interactive dashboard from this data, support these views:

1. **Home / Problem View:** Start with problems, show severity and related capabilities
2. **Capability Overview:** Domain-grouped capability grid with RAG colors
3. **Heatmap View:** Full Front/Middle/Back heatmap with drill-down
4. **Workshop View:** Per-capability scoring interface with probing questions
5. **Traceability View:** Problem → Capability → Journey mapping

---

*This template aligns with `knowledge/standards/capability_taxonomy.md` and the capability assessment agent methodology.*
*Version: 1.0*
*Last Updated: 2026-02-04*
