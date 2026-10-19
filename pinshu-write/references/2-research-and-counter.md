# Steps 2, 3 and 6: research, counter, fact table

## Research (step 2)

One run, three jobs, sent at once to the models the configuration's `research` routing names (`models.md`, "Scan and research"); without that routing, to helpers of your own, otherwise one after another. Each job brief says three things: what is wanted (which people, events, kinds of data or cases), which claim or step of the article it is meant to hold up, and how fine (a one-line finding, or material the writer can use as it stands). Each job says whether it read the full source or a fragment, and writes "not found" when it finds nothing.

1. **Facts**: names, numbers, quotes, dates, with links.
2. **Cases for and against**: real people and events doing concrete things, on both sides.
3. **The closest published articles**: list the few nearest to our angle, one line each: who wrote what, whether anyone argued it this way, what we add. The account's own published pieces are read in full. Drafts and ready-to-publish pieces are left out entirely: they are unfinished and do not speak for the account. Articles recalled from model memory go under "leads to check", never into this list.

Rules for the run:

- **The author's own material comes first.** If the author mentions conversations, notes or posts collected earlier, find those and go back to the original posts before any keyword search. Ask where they are if they cannot be found.
- **Start from the configured sources** (leading business, technology and brand media, the author's notes), then search the last three months. Without web access write "no web access"; items recalled from memory are "leads to check, from model memory, not verified" and never enter the article as facts.
- **Each item records**: date; source; its link and the exact sentence it is quoted for (so a screenshot can be taken straight from the list); what it supports; its status (independent report, company self-report, vendor press release, speaker's own account, repost of an unopened original); how it was read (original read in full, fragment only, paraphrased by a tool; never quote from a paraphrase).
- **Freshness**: the account profile's freshness rule (`4-writing.md`, Chinese hard rules, rule 3; six months where the profile says nothing) applies to everything collected; claims about AI tools must be current.
- **When the author names a source**, find the original and read the fullest version. A thing that cannot be found is written "cannot be found"; no date or number is filled from memory. Anything passed on by a helper, another conversation or another AI goes back to its original before use.
- **When the author asks to study a subject through this article** ("借这篇把 GEO 研究透"), that study is a fourth job: its notes are a document of their own, filed where the author says, and timed as their own stage. The three jobs above still prepare only the article.
- **Close with one short summary page** (the strongest items with status) so the author and the writer read one page.

### Paid data reference (market reference)

Off by default. It runs only when the author names it, once per article, by the organizer alone: `python3 scripts/market_reference.py --dir <process folder> --keyword <word> [--keyword ...]` with two or three keywords written the way a reader would search; pass the configuration's `market_reference` values as flags. It returns one page of real read counts of same-topic articles beside each account's usual level. How to read it: mark each row on topic, adjacent or off topic and count only on-topic rows; an article read at 2 times or more of its account's usual level and at least 2,000 reads is a "small account, big response" sample, and only these may inform titles or openings. It is reference beside the closest-articles list and the titles, never a score and never a reason to retitle a finished article. A failed or skipped fetch is written down and the article goes on.

## Seed outcomes

When research is done the seed stands (keep the direction; use the material to make the claim precise and write its limits), is partly wrong (keep the direction; fix that part and say in the article when it does not hold), or has its core overturned. The core is overturned only when several independent, recent, first-hand sources directly contradict it, or when it is an agent inference and nothing supports it. Then stop the route and bring the evidence and one proposed new direction to stop 2; the author decides. Someone else writing on the topic, a different mainstream view, a forceful objection without evidence and a model's common-sense answer do not overturn a seed.

## Counter (step 3)

The counter role argues the other side. It reads the seed (the author's words), the research summary and the candidate judgment in one sentence, written by the organizer in the author's terms. It assumes the article has been published and failed, and returns:

- the five likeliest reasons it failed;
- the strongest opposing argument, stated so well its holder would accept it;
- the conditions under which the judgment does not hold;
- which claims rest on a named source or the author's material and which on agent inference;
- when the judgment leans on an older principle (question 1's "old common sense"), name it: what it is called, who set it out, one sentence of it in our own words, how far it has been checked (original read in full, secondary source, from model memory), where it stops holding in this case, and whether the article's own recommendation would be caught by the same principle. A principle that cannot be named and bounded is written "common saying" and does not carry the argument. Drop a candidate principle that explains no part of the case; keep one principle per mechanism, and a second only for a mechanism the first cannot explain.
- the seven questions below, each answered with one line of evidence.

It does not rewrite the judgment and does not set the direction. A failed question sends the claim back for one sharpening inside the author's direction (what the new situation changed, what to do instead); if it still fails, the stop 2 message says plainly what looks familiar or unsupported. The strongest objection and the answer go into that message.

### The seven questions (provisional, pending verification)

Provisional: these seven questions are an editing checklist, not a proven universal writing standard. The final question draws on Paul Graham, "How to Write Usefully". Replace weak checks when real forward tests justify a better one.

1. **Only old common sense?** A classic principle may be the subject; the question is what the new situation (AI, the triggering event) changed about it: a condition it depends on, a new consequence, new evidence or a new way of acting. If none, it fails.
2. **Can the reader dismiss it in one sentence?** Being summarizable is no fault. It fails when the reader's one-sentence reply ("different tools give different results", "obviously") leaves nothing for the article to do. Go one level below that reply.
3. **Only describes, with no stance, or only makes the task sound harder?** State what the reader should do or stop doing; turn "harder" into "where to start".
4. **Is the selling point how much we installed or built?** Recast around the reader's problem; our work becomes evidence inside it.
5. **Only a method or checklist, with no "I thought A; it is actually B"?** Skip for practical how-to and integration pieces. Name what the reader believed before and what is true instead.
6. **How many recent articles took this same angle?** Answer from the closest-articles list: only articles with the same judgment, or the same structure, evidence and conclusion together, count against the claim. State how complete the list was (read in full, fragment, title only). Without a list, or with an incomplete one, the answer is "unverified", never "none"; the stop 2 message says "collisions unverified" and the author decides. An unverified answer is no reason to narrow the seed. When the angle is taken: write our own piece if we have an angle or the author's experience, an integration piece (type 10, `3-structure.md`) if we have neither, and only then, with the author, consider another topic.
7. **Does it lack importance, novelty, truth or force?** Name which. "Force" means the sentence still stands after removing every "maybe" and "to some extent"; keep only the qualifiers your certainty requires.

A judgment that only destroys and builds nothing fails too: the reader must leave knowing what to do instead. Record each answer with its evidence; an all-pass record with no evidence is not a pass.

## Fact table

Start it in step 2 as the research items are recorded; when the author has answered stop 2, lock every name, company, number, quote (with its Chinese wording), date and author experience the article may use into one table. The writers may use only the table for these. The table does not govern everyday description that anyone lives through (staying up late on a proposal) or a hypothetical scene marked as such.

- Two kinds of entry are copied as whole sentences, never paraphrased: the author's own experiences and statements, word for word from the author's messages and the decision log (a gap is "[to confirm]" and asked); key statements from the account's own earlier articles, with title and date.
- Each external entry keeps its link and quoted sentence. Mark the entries that need an evidence screenshot; the screenshot job captures from that column (`6-deliver.md`).
- Keep it complete: whenever a fact is checked or re-measured later, write it in at once with source and date. Before the seed check, every fact in the draft must be in the table.
