# The gates

The author is asked at the three gates, and once more for a topic only when he brought no seed. Step 1 is a conversation with him, not a gate: the writer asks him one question at a time before research (`write.md`, step 1). Two stops come only when review finds them: grading puts a finding at 动骨架, or the editor's second pass says 建议推翻 ("When review stops the route" below). Everything else runs without asking; questions that can wait go into the next gate's message. After every answer, append the author's decision and his verbatim words to the decision log.

## The shape of every message

Run every check first, then show the result in plain words, never the machinery:

1. One plain sentence: what I recommend, in the author's terms.
2. One natural question: "Is this what you mean?"
3. At most four small decisions, one line each, each with my recommendation.
4. Where the full record is: a link, written in the reply text itself, to a file that exists and that the author's own tool opens with one click; text that appears only in tool output has not been shown. A whole article is linked, not pasted into the reply. When the configuration sets a `preview_folder` (the author's tool cannot open the article folder), copy the file there and link the copy, named by the full title with its punctuation as is plus a plain suffix after a hyphen (`<title>-Opus写的初稿.md`), with no added full-width brackets.
5. A last line of progress: which step the route has reached, which steps were skipped and why. A draft whose steps 6 to 8 have not all run is called a first draft in this line, never a final.

No bold. Run `audit_draft.py --card` on the message (it keeps the wording checks and drops the article-shape ones). The judgment record, the point-map table and the review sheet stay in the article folder and are shown when asked. Name things by what they are, in the author's everyday words; a label the organizer made up ("the ten questions", "draft A") means nothing to the author. Never make the author compare abstract labels or near-identical judgments, or carry text between models.

Any other request for the author's go-ahead (overwrite a file, re-export, download, spend money) says in plain words what will be done, why, and which file it touches, never a bare command word.

## Topic (only when the author brought no seed)

Three topics, six lines each (`1-topic.md`), and the source receipt in one line. One question: which one. The topic the author picks is the seed.

Two batches in a row rejected means the scan failed, not the author: invalidate both, widen the source families or the account's own material, and scan again. The author is not asked for the thesis here.

## Gate 1: the thinking-through and the three questions

Sent after research, when the writer has read the whole material pack (`write.md`, "The end of step 2"). One message:

1. The thinking-through page as a file the author opens with one click; it is the thing he reads.
2. The three answers, one line each; the expert's field in one line ("专家身份：××行当的从业者"), which the author changes when it is wrong.
3. Where it may still be shallow, two or three lines, marked as the writer's view. Also the sentences the seed check flagged (`write.md`, end of step 2): each original sentence with the range word, and one question, whether it says more or less than the author's own words. Nothing flagged, nothing written.
4. One question: "想透了吗？哪里还浅？"

When he says a part is shallow, the writer asks about that part only, or researches that part only, and sends the page again; nothing is built before he says it is thought through. If research overturned the core, the message is short: the evidence, one proposed direction, the question.

## Gate 2: title, outline, opening and first section

The last place anything is overturned, except by the two stops review can raise ("When review stops the route"). One message:

1. Three title candidates, each with its method (the standard's 第六节) and one line on why the reader opens it; one recommended. Each already passed both checks (`write.md`, step 3); say so in one line each.
2. How the piece moves: the one plain paragraph (`write.md`, step 3), then the outline: the spine in one sentence, one line per section (its judgment, and what it stands on). Say where in the whole piece the most valuable point lands (as a share of the length, the standard's 第二节 item 3). For a piece that does not use the author's experience, say which section stands on a specific person or scene, and whether it is a real case or a hypothetical example. A section with nothing under it is said plainly. Then one line: the title's question followed by the subheads in order, joined by commas into one sentence. It is shown for the author to judge whether it turns; the writer sets no pass line on it.
3. The opening and first section, written in full (`write.md`, step 3, item 7), as a file the author opens with one click; the first 200 characters quoted in the message. He judges here whether it reads, before the rest is written.
4. Two or three exemplar candidates, each with where it came from and one line on what to learn from it, the writer's recommended ones marked (the opening and first section were written after them); the author picks one or two, and when he picks others the opening and first section are rewritten after his picks. With none found anywhere, say so plainly: the draft will lean on the model's average shape.
5. At most two decisions, one line each with a recommendation, drawn only from these three kinds: the type, a real story the author might add, research that came back thin. A quote or a case the writer wants to add is the writer's own call (`write.md`, step 3), never a decision for the author.

The author approves or reshapes. His words go into the decision log and to the writer as they are.

## When review stops the route

Two stops between gate 2 and gate 3, each only when review finds it:

1. **Grading puts a finding at 动骨架** (`5-review.md`, "Grading"), before the editor runs. The message says: what was found, in the finder's own words (the expert's verdict with its counter-example and what the re-check found; the reader's sentence; the two judgments side by side); how the organizer graded it; where the organizer recommends going back (gate 1 when the judgment itself is wrong, gate 2 when the draft wandered off a sound judgment), and that the author decides. For an expert 站不住 the author picks one of three: rewrite; no rewrite, the editor runs; the expert is overruled, with the reason on the review sheet.
2. **The editor's second pass says 建议推翻**: its reason verbatim, and the same recommendation on where to go back.

## Gate 3: final

Sent after the revision, the facts pass and the editor's second pass has said 过 (or the author has ruled on what it raised). The author reads the revised draft, not a draft with four lists, and decides whether it ships.

It takes the shape of every message (above): one sentence of recommendation, one question, at most four small decisions, and the full article as a link the author's tool opens with one click (a `preview_folder` copy when needed). The decisions are drawn only from what the author alone can settle: an expert 站不住 he has not yet ruled on; a fact still 查不到 or [待确认]; anything the draft says about the author that needs his confirmation; the title, from three candidates for the finished article with the current one among them. Everything else stays in the review sheet in the article folder, opened when he asks: the expert's verdict and how it was graded, the writer's change list (`write.md`, step 7), the reader's spots still there, what the second pass recorded as 第一遍漏了, the reader items not adopted with their reasons. The author judges whether the stance is right, the angle good and the piece worth publishing; a request to overturn the core means an earlier gate missed it, and the route goes back there.

The author's comments are revised by size (`6-deliver.md`); after an edit the writer rereads only the changed passage and its neighbours, unless paragraphs or subheads moved. The author's 定稿 sentence goes verbatim to the export as `--approval`. When the author edits the text by hand, save the writer's draft and the author's version and write the edit pairs (`write.md`, "After 定稿").
