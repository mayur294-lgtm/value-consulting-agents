# IGNITE AI AGENT - CONVERSATION STARTERS

Use these prompts to start new conversations within the Ignite AI Agent project.

---

## 🚀 GENERIC STARTER (Copy this to start any new conversation)

```
I'm continuing work on the Ignite AI Agent system for Backbase value consulting.

Current engagement: [CLIENT NAME]
Client type: [Credit Union / Bank]
Stage: [Pre-workshop / Post-workshop / ROI]

What I need: [describe task]

Attached: [list any files you're attaching]
```

---

## 📋 AGENT-SPECIFIC STARTERS

### Agent 1: Strategy Workshop
```
Acting as Agent 1 (Strategy Workshop), generate the facilitation deck.

Client: [NAME]
Type: [Credit Union / Bank]  
Size: [X members/customers], [$X assets]
Region: [Location]

Include:
- Competitive benchmarking against [Competitor 1, Competitor 2, Competitor 3]
- Specific, quantified hypotheses with business impact
- Validation questions for each hypothesis

Attached: [strategy documents]
```

### Agent 2: Member/Customer Experience Workshop
```
Acting as Agent 2 (Member Experience Workshop), generate the facilitation deck.

Use the attached ENGAGEMENT_CONTEXT.md for background.
This is a [Credit Union / Bank] - use [Member / Customer] terminology.

Focus areas: [specific journeys or personas if known]

Attached: 
- ENGAGEMENT_CONTEXT.md
- [any persona research or journey maps]
```

### Agent 3: Employee Experience Workshop
```
Acting as Agent 3 (Employee Experience Workshop), generate the facilitation deck.

Use the attached ENGAGEMENT_CONTEXT.md for background.

Focus on these roles:
- [Branch Teller / Universal Banker / Contact Center / etc.]

Attached:
- ENGAGEMENT_CONTEXT.md  
- [any systems inventory or employee feedback]
```

### Agent 4: IT Architecture Workshop
```
Acting as Agent 4 (IT Architecture Workshop), generate the facilitation deck.

Use the attached ENGAGEMENT_CONTEXT.md for background.

Core banking: [Symitar / Fiserv / Jack Henry / FIS / etc.]
Key systems to assess: [list known systems]

Attached:
- ENGAGEMENT_CONTEXT.md
- [technology landscape documents]
```

### Agent 5: Use Case Design + Prototypes
```
Acting as Agent 5 (Use Case Design), create use case documents and prototypes.

Use the attached ENGAGEMENT_CONTEXT.md and workshop findings.

P1 Use Cases to document:
1. [Use Case 1]
2. [Use Case 2]
3. [Use Case 3]

Generate interactive prototypes for each P1 use case.

Attached:
- ENGAGEMENT_CONTEXT.md
- [workshop transcripts or validated findings]
```

### Agent 6: Ignite Presentation Compiler
```
Acting as Agent 6 (Presentation Compiler), create the Ignite Day presentation.

Compile all findings into a 60-90 slide executive presentation.

Attached:
- ENGAGEMENT_CONTEXT.md (fully populated)
- Use Case Design Documents
- Business Case summary
- Prototype screenshots
```

### /generate-roi-questionnaire - ROI Questionnaire Generation

**Phase A - Questionnaire:**
```
/generate-roi-questionnaire

Engagement directory: [path to engagement folder]

Pre-populate with known data from the attached context.
Focus on these use cases: [list in-scope use cases]
```

### roi-business-case-builder - ROI Business Case

**Phase B - Business Case:**
```
Acting as roi-business-case-builder agent, build the business case.

Use the completed questionnaire to calculate ROI.

Attached:
- Completed questionnaire (Excel)
- ENGAGEMENT_CONTEXT.md
```

---

## 📁 FILES TO UPLOAD TO PROJECT KNOWLEDGE

Upload these ONCE to Project Knowledge (they persist across all conversations):

1. ✅ agent-1-strategy/CLAUDE.md
2. ✅ agent-2-member/CLAUDE.md
3. ✅ agent-3-employee/CLAUDE.md
4. ✅ agent-4-architecture/CLAUDE.md
5. ✅ agent-5-usecase/CLAUDE.md
6. ✅ agent-6-presentation/CLAUDE.md
7. ✅ agent-7-roi/CLAUDE.md
8. ✅ ENGAGEMENT_CONTEXT_TEMPLATE.md
9. ✅ CONSULTANT_GUIDE.md
10. ✅ QUICK_REFERENCE.md

Optional (if you have them):
- Backbase capability documentation
- Sample deliverables for reference
- Brand guidelines

---

## 📎 FILES TO ATTACH PER CONVERSATION

Attach these to individual conversations (they change per engagement):

- Client's ENGAGEMENT_CONTEXT.md (updated version)
- Client strategy documents
- Workshop transcripts
- Completed questionnaires
- Any client-specific materials

---

## ✅ VERIFY PROJECT SETUP

Start a new conversation with this to confirm everything is loaded:

```
Confirm you have access to the Ignite AI Agent system.
List all 7 agents and their purposes.
What files do you see in Project Knowledge?
```
