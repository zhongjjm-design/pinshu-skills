# Step 1: Topic and seed

A first idea is a seed, not a conclusion. Research sharpens what the author wants to say; it never swaps in a different article.

## The seed belongs to the author

A seed is what the author said, or a candidate the author explicitly accepted ("yes, write this"). A pattern the agent spots, a card from another agent or a scheduled task, a news item: these are candidates until the author accepts one. The direction of the seed (what the author wants to do with the article, for whom, what type) is the anchor for every later step.

## When the author brings words

An idea, topic, link, article or loose message. No stop; the point map reaches the author inside the stop 2 message.

1. **Keep the words.** Store the author's full text verbatim in the article folder. Corrected readings of misheard voice input go in a separate table beside it; the original is never edited.
2. **Number the points (the point map).** Every distinct meaning the author expressed gets a number: S1, S2, S3 ... A long seed with eight points has eight numbers. Points on one line of reasoning (one leads to or explains the next) share a number, with the items listed under it in the author's words; points on separate lines of reasoning get separate numbers. A run of items the author wrote as a list that all serve one meaning is one number. Points serve the judgment: the map tells the writer what to carry, never a checklist to spread out item by item (over-fragmenting the seed can turn prose into a checklist).
3. **List the author's own material separately**: passages that carry lived experience or a picture (a scene, a person, a moment), and insights only this author has (from their business, clients, years in the trade). Each keeps the author's words.
4. **Who benefits first.** If it is the author's own team, also produce a separate internal improvement list (what we do, where we fall short, what to try); it never goes into the article.
5. **One article, one line.** When the author's words hold several separate lines (a long voice message often does), the article follows the one the seed's own doubt points to; the others are offered at stop 2 as other articles (`stops.md`). Nothing is dropped silently: each stays in the point map with its destination.
6. **Opinion pieces need that material.** With none, the stop 2 message asks for one real story. If the author says "none, write it anyway", the review sheet records "no part only this author could write" (`5-review.md`, "Review sheet").

### Someone else's article as the seed

When the author brings another person's article (a post on X, a WeChat piece, a forum thread), it is the spark for a topic, not a ready-made frame or wording to copy. Keep the author's words about it as the seed and the article itself in the process folder as the source.

- Note what grips in it (its title, its opening, its sharpest lines, how it argues), so the hook candidates can learn from it.
- Do not import its scenes, frame, checklists, signature phrases or data into the material pack; research the topic again from its own sources. A fact that appears in it may be used only when found and read at its original source, and even then it is better left out when it was the source article's own find.
- The body never names the article or its author, and the 参考文章 block does not list it. The originality check (prompt 14) runs on every draft.
- "写简单一点" about such an article means shorter, with fewer cases and numbers; its sharpest points and its hook are what to keep in our own words, never what to cut.

## When the author brings nothing

The scan runs on this Skill alone. A dashboard, feed service or saved topic list only makes it faster.

**Window**: the last 7 days; widen to 30 only when the 7-day scan finds nothing that meets the entry rule below, and say so.

**Who scans.** The scan jobs go out at once to the models the configuration's `research` routing names (`models.md`, "Scan and research"); the organizer merges what comes back and writes stop 1.

**Source route**, first that applies:

1. Route 1: the configuration names a fresh `topic_pool` (it states a generation time inside the window). Open each lead that would be offered, confirm it is live and take its current numbers; then cover the families the pool leaves out. Without web access, list the pool's leads as it states them, marked "not rechecked this run". An undated or older pool holds historical leads, each checked online before use.
2. Route 2: the configuration names a `source_list`. Scan it, then add public families it does not cover.
3. Route 3: neither, and web access works. Run the public source map.
4. Route 4: no web access and no fresh pool or source list. Stop and say: "I cannot tell what readers are reading this week: I have no web access and no source list or topic pool." Offer three ways on: the author gives an idea or link, the configuration points at a source list or topic pool, or web access is allowed. Model memory supplies no recent signals.

`scripts/check_env.py` reports which route the configuration leads to and whether the pool is fresh. Relative paths in the configuration resolve from its folder.

**Public source map.** Cover families 1 to 3 in every run; family 4 only checks facts.

| Family | Shows | Examples |
|---|---|---|
| 1 Leading business, technology and brand media, named analysts | Which company and industry questions are written up and how widely read | 36氪, 虎嗅, 钛媒体, 晚点, 刘润, 哈佛商业评论中文版 |
| 2 Podcasts, video, long interviews | Which questions people spend an hour on | 小宇宙, Bilibili business and AI channels, YouTube interview shows |
| 3 Practitioner communities, Q&A, comments, reader questions | What readers get stuck on, in their words | 知乎, 即刻, industry communities, questions the author receives |
| 4 Primary sources | Whether the facts hold | Company announcements, earnings, regulators, statistics |

Start each family from what it ranks by reader behavior (hot list, most-read, most-played, top-voted) and open the list page itself; a search result describing a list is not the list. A keyword search shows what is written, not what is read: use it to find the same question in a second family. Outlets of one kind are one family. To widen a scan, add families, not reviewers.

**Entry rule.** A signal counts when its date is inside the window and at least two of families 1 to 3 touch the same question, or one source runs clearly above its own usual level. Anything else may appear only labeled "single lead".

**Before showing a topic**: open at least two sources from different families in full (a title or snippet is not reading), and search the author's side (`material_folders`, published articles, the author's earlier statements). The topic's core claim stands on a named source or on the author's material, with the quote and path or link. A claim that neither makes, reached by the agent stepping between them, is an inference: label it, and research later supports it or it counts as overturned.

**What a topic needs.** The reader is already asking about it, and the article gives at least one of: resonance ("said what I felt"), a new view ("showed what I had not seen"), use ("I can act on this"), forwardability. Topics may collide with other writers; angles may not. Written as the reader's question, in words anyone understands at first reading. Other people's articles are triggers, not sources; the account's own work appears only as evidence inside a reader's problem; no topic pulls readers with greed or fear; "is AI useful?" is not a topic.

**Stop 1 offers three topics**, each with exactly six lines:

- the topic in one sentence, as the reader would ask it (the core question);
- the reader's shift: "读者原来以为……，看完知道……";
- the concrete scene it would open on;
- source links;
- the evidence that readers care: reads, plays, saves, comments or rank, with the date seen, and whether interest is steady or rising (compare two readings; with one, write "no growth information");
- why it helps our readers: which real piece of their work it changes.

"Nothing this week is worth recommending" is a valid result, shown with the list of families and names checked, how many items were opened and what failed. Fewer than three families reached: label the run "narrow scan" and name the missing ones. Message form and what follows: `stops.md`.

**Hand-over.** The topic the author picks is the seed. Store the author's words of acceptance and the topic line, carry the core claim's grounding into the seed record, then build the point map and own-material list as above.
