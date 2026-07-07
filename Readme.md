Pipeline ปัจจุบัน (qa-assistant)

INPUT
  Jira epic (PDT-XXXX)  +  PRD (HTML)  +  Figma (screenshots)
        │
        ▼
─────────────────────────────────────────────────────
  LAYER 1 — BA Skills (phases 1.x–2.x)          conversational
─────────────────────────────────────────────────────
  phase-1.1  Requirement Interrogation        Who/What/Why
  phase-1.2  Three-Layer Analysis             Goal/Need/Behavior
  phase-1.3  Happy Path AC Enrichment         enrich PM's AC
  phase-1.4  Edge & Error AC                  4 mental models
  phase-2.1  INVEST Check                     split decision
  phase-2.2  AC Writing                       all 4 scenario types
  phase-2.3  Business Rule Extraction         4 BR types
  phase-2.4  Elicitation Techniques           meeting/PM interrogation
  phase-2.5  Prioritization                   MoSCoW + QA effort
  phase-2.6  Scope & Gap Analysis             before sprint
        │
        │  open items → qa/<feature>/1_clarifications.json
        ▼
─────────────────────────────────────────────────────
  GATE — qa-clarifications-review  (ใหม่)        structured
─────────────────────────────────────────────────────
  ตรวจคำตอบ → resolved / followup / ac-change / still-ambiguous
  ถ้ามี still-ambiguous medium+ → STOP, รอ clarify ก่อน
        │
        ▼
─────────────────────────────────────────────────────
  LAYER 2 — QA Skills (phases 3.x)              analytical
─────────────────────────────────────────────────────
  phase-3.2  BR → Test Conditions      PRD+Jira+Figma → BR Catalog + TC table
  phase-3.1  Automation Judgment       TC list → automate/manual verdict
        │
        ▼
OUTPUT
  qa/<feature>/1_clarifications.json    (resolved)
  qa/<feature>/FOLLOWUPS.md             (deferred)
  products/PDT-XXXX/PDT-XXXX-open-items.md
  BR Catalog + Test Conditions          (ยังเป็น markdown ไม่มี schema)