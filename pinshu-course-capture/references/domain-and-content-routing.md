# Domain and Content Routing

Purpose: load only the professional boundaries and content anchors required by the current lesson. Do not duplicate the whole pipeline for every domain.

## Shared rules

- A domain adapter may add authoritative terminology sources, source hierarchy, risk triggers, and hard boundaries.
- A content adapter may add only the structures, evidence, and presentation details that must be preserved.
- Neither adapter type may weaken the core quality contract, change the four core results, or enable extension assets by default.
- One lesson may combine several content types. Record only selected adapters in the Worker Spec.

## Domain routing

| Domain | Primary authorities and boundaries | Default risk triggers |
|---|---|---|
| General or cross-domain | Original material and the course glossary | Identity conflict, truncated source, conflicting key numbers |
| Business and management | Original operating material, contracts, and financial definitions | Revenue attribution, extrapolated cases, internal data |
| Brand marketing and sales | Platform rules, advertising law, and original cases | Performance promises, attribution, gray-area acquisition |
| AI, software, and technology | Official documentation, versions, and real execution results | Missing code or commands, outdated versions, unsafe operations |
| Finance, investment, and economics | Regulatory disclosures, audited definitions, and dated evidence | Return promises, timeliness, valuation, and metric definitions |
| Medicine, health, nutrition, and traditional medicine | Textbooks, guidelines, pharmacopeias, and identified original cases | Dosage, contraindications, emergencies, treatment advice, causal efficacy claims |
| Law, compliance, and public policy | Current law, official documents, and applicable jurisdiction | Timeliness, jurisdiction, rights and obligations, overconfident conclusions |
| Education and learning | Course objectives, assessment criteria, and original responses | Reporting exposure as mastery, fabricating learning records |
| Psychology, relationships, and personal development | Original accounts and professional boundaries | Diagnosis, labeling, high-risk intervention |
| History, humanities, philosophy, and religion | Primary texts, editions, and historical context | Anachronism, merged schools, fabricated quotations |
| Art, design, media, and content | Original works, rights, and creative process | Rights ownership, visual evidence, style misattribution |
| Science, engineering, manufacturing, and supply chain | Standards, experiment or production records, and specifications | Units, parameters, safety conditions, reproducibility |
| Client-specific domain | Client-provided authoritative glossary and business rules | Unauthorized data, internal definitions, delivery boundaries |

## Content-type routing

| Content type | Must preserve |
|---|---|
| Viewpoint or theory lesson | Claims, evidence, rebuttals, qualifications, and reasoning chain |
| Case, clinical case, or retrospective | Context, process, adjustments, outcome, and limits; do not turn correlation into causation |
| Procedure or demonstration | Preconditions, actions, interface or tool feedback, exceptions, correction, and result |
| Code or technical lesson | Code, commands, parameters, dependencies, versions, errors, and runtime results |
| Interview or multi-speaker discussion | Speakers, follow-up questions, disagreements, and contextual continuity; never merge viewpoint owners |
| Q&A | Original question intent, answer, follow-ups, exceptions, and unresolved items |
| Visually dependent lesson | Correspondence among slides, whiteboard, charts, screen content, and narration |
| Data- or fact-dense lesson | Date, definition, unit, source identity, and conflicts |
| Module summary | Links to prior lessons, core relationships, changes, and unresolved disagreements |

## Escalate to independent QA

Escalate when any condition applies: unresolved uncertainty; medical, legal, financial, safety, or real operational consequences; conflicts in speaker relationships, visuals, code, commands, or key numbers; a semantic-risk warning in the mechanical report; formal external use; a matching recent `high`; or stable sampling under the assurance mode.
