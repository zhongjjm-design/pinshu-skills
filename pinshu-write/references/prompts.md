# Prompts

Fifteen prompts, one per job. Copy one, fill the angle brackets, send it to the chosen model. Each asks for Simplified Chinese; change that line for another language. Slots written `<paste: name>` are filled by the organizer pasting the text of the named section of this Skill, so the rule lives in one file and the prompt only points at it. Paste material into the prompt itself and never give a model a file path to find: the model may not be able to read it. Every prompt except the reader's and the managing editor's opens with the author's direction in one sentence, verbatim; those two read blind, as calibrated.

## Every brief

Every filled prompt, to any model, follows these:

1. A `<paste: name>` slot takes the named section from the line after its heading up to the next heading; nothing of the next section comes along.
2. Every reviewing prompt (3 to 14) opens with the line “今天是<年>年<月>月<日>日。” A model that does not know the date may misjudge recent papers and products as "from the future". A date line before prompt 10 leaves its calibrated wording unchanged.
3. A line sent to a writer says only what to change, in plain words: no stop numbers, role names, card names or how a decision came about. A writer copies such words into the article.
4. A reviewer whose tool loads its own global rules (`models.md`, "Calling another vendor") gets as its first line: “这是委派给你的只读审稿，不需要开工清单，也不需要确认，直接输出报告。” If what comes back is not a report (a plan, a checklist, a question), run it once more with that line, and keep the first output under another name.

**Findings tail** (appended where a prompt says `<tail>`):

```text
Report only; do not rewrite anything. Quote exactly. For each problem give: paragraph number | the sentence (under 60 characters) | the problem and the rule or standard it breaks | severity | one line on what fixing it changes for the reader (no numbers or percentages) | a direction for the fix that invents no facts or experiences. List every must-fix and at most three important and optional together. Severities, judged only against the material above: <paste: 5-review.md, "Findings" severity table>. If there is no problem, say so. If something cannot be judged from the material, say "cannot judge".
```

## 1. Writer: outline mode and draft mode

Both modes send the exemplar brief (`4-writing.md`, "The exemplar brief"). Draft mode goes to both writers at once (`models.md`).

```text
用简体中文写。不读写文件，不调用工具。
作者这篇要说的方向（作者原话）：<one sentence>
你是<account>的主笔。下面先给你两篇范文，都是成熟作者发出去的好文章。请完整读一遍，学它们的口吻、呼吸和推进方式：像一个真人坐下来跟读者聊，一层层往下讲，每句话主语清楚，读起来顺。只学写法，不借它们的事实、案例和说法。

【范文一：<author>《<title>》（学<what to learn>）】
<whole text>
【范文二：<author>《<title>》（学<what to learn>）】
<whole text>

【这篇要写的】
读者：<one sentence>
要说的观点：<the judgment; for an opinion piece add one line, chosen by the judgment (`3-structure.md`, "Opening, concept, arc, ending"): sharp or counter-intuitive and new to the reader: 开头直接亮出这个观点，用一句金句定调，后面一节一节讲开；familiar to the reader: 开头只写读者共同的感受或现象、抛出问题，不把答案说完；答案一节一节揭开，结尾说完整>
可以用的材料（用不完没关系，挑有用的）：<facts from the fact table with their Chinese wording; the author's own material verbatim; hypothetical scenes marked as such>
<only when the author has said this article has none of their own experience: 开头不写任何具体某人的经历，用读者共同的感受。>

几条底线（其余凭你的语感）：
<paste: 4-writing.md, "The six bottom lines", filled>
```

Then the mode's own tail:

```text
OUTLINE 模式：
写出：一句话判断；三个标题候选（一个直接说结论，一个用读者自己会问的问题，一个落在具体的数字或事件上），各附一句读者看到会期待什么，标出推荐的一个和理由；小标题全部列出，每个下面写这一节讲什么、目标字数、用哪些材料；开头第一段，写成真句子，就是成稿里的样子。
标题和小标题的标准：<paste: 3-structure.md, "Titles" title rules and "Subheads">

DRAFT 模式：
标题（已定）：<title>
大纲（已定，每节目标字数）：<outline>
开头第一段（作者在看方向时认可的，照用，不改）：<paragraph>
第一节接着开头往下走，不重复开头已经说过的。
不能改的字句：<locked items, or "无">
文末参考文章（格式：列用到的、读者能去读的完整长文，以及正文用到、找得到来源的主要研究报告；一行一篇，《全称》，作者或机构，平台，日期）：
## 参考文章
<entries, or "无，不写这一块">
只输出文章，从标题行开始，小标题用二级标题（## ）。
```

## 2. Writer: revise

The organizer sends this automatically after every comment; the author never forwards between models. Size the comment first (`6-deliver.md`): a swap needs no writer.

```text
用简体中文写。不读写文件，不调用工具。
作者这篇要说的方向（作者原话）：<one sentence>
作者读了下面的稿子，原话是：<the author's words>（或：合并后的审稿意见：<list>）
把全文改到正好回应这些意见。只改意见涉及的地方，其余保留；这些字句一字不改：<locked items, with wording adopted in earlier rounds>。除了这些事实不加别的：<fact table entries>。
作者删掉的内容不要加回：<the cuts in the decision log, or "无">。事实表里有的出处不要删；正文提到的研究、调查，写明是谁做的。
改完不短于现在的 <n> 字，除非作者要求删。
几条底线：<paste: 4-writing.md, "The six bottom lines", filled>
输出：改好的全文；然后列出改了哪些地方、每处怎么回应意见、原来哪里不对；拿不准的标“可回退”。
现在的稿子：
<full text>
```

Title version (stop 4: titles for the finished article): replace the middle with "按这篇定稿的内容和篇幅，写三个标题候选，三种写法（一个直接说结论，一个用读者自己会问的问题，一个落在具体的数字或事件上），各附一句读者看到会期待什么；现在的标题是：<title>，可以留作其中一个。标题的标准：<paste: 3-structure.md, "Titles" title rules>。只输出三个标题和各自那一句。" and paste the finished article.

Sentence version (the author pointed at a few sentences without giving wording): replace the middle with "只改这几句，每句给一个替换：<numbered sentences, each with the paragraph before and after>。这些一字不改：<locked items>。只输出表格：编号 | 原句 | 新句 | 怎么回应意见。"

## 3. Counter

```text
Answer in Simplified Chinese. Do not rewrite the judgment and do not set a new direction.
The author's direction, verbatim: <one sentence>
Your job: <paste: 2-research-and-counter.md, section "Counter (step 3)" and "The seven questions">
Judgment we plan to publish, for <reader>: <one sentence>
The author's seed (verbatim): <text>   Research summary: <page>
Closest published articles (title, outlet, date, main argument, how it was read; the account's own published pieces read in full): <list, or "no list">
```

## 4. Structure editor (the line)

```text
用简体中文回答。只看这条线怎么往前推，不管句子怎么写。
作者的方向（原话）：<one sentence>。读者：<reader>。
作者的种子原话：<text>
逐条回答，每条写"是 / 否 / 判不了"，并引线里的原话作证：
1. 线里哪一步删掉，后面照样接得上？接得上的那一步是多余的，指出来。
2. 每一步和上一步是"然后呢"的关系，还是"另外"的关系？连着几步都是"另外"，结构就散了，指出在哪。
3. 开头那一步，读者看了会不会想往下读？
4. "读者原来以为……，看完知道……"那句，在线的哪一步兑现？没有兑现就说没有。
5. 每一步下面写的料（经历、案例、数字），撑得住这一步吗？没料或料不对题的步骤指出来。
6. 写明的走法（一层推一层 / 几个案例各撑一角 / 大问题拆成小问题），和这篇的类型对得上吗？
7. 标题：按下面的标题规矩逐条看三个候选。<paste: 3-structure.md, "Titles">
<When the configuration names a `good_article_standard`: paste its parts on titles, openings and structure, leaving out checks about how the reader will feel; answer each 过、不过 or 判不了 with one quoted line.>
然后列出问题，每条一行：哪一步 | 问题 | 改的方向。<tail>
核心问题、读者转变那句、开头场景、线和每步的料、标题候选：
<text>
```

## 5. Reader

```text
Answer in Simplified Chinese. Do not rewrite the article. Report only; the organizer grades severity.
Your job: <paste: 5-review.md, "Reader">
You are someone outside <industry> who uses AI at work (<the account's reader in one sentence>), reading on a phone.
Title: <title>
Article:
<draft body without editor notes>
```

## 6. Expert

```text
Answer in Simplified Chinese. Report only; do not rewrite.
The author's direction, verbatim: <one sentence>
Your job: <paste: 5-review.md, "Expert">. You are a <marketing / finance / applied-AI> practitioner with years in the field; today is <date>.
Reader of the article: <reader>. Fact table (what the article is allowed to state): <fact table>
<tail>
Article:
<draft body without editor notes>
```

## 7. Facts and risk

```text
Answer in Simplified Chinese. Report only; do not rewrite.
The author's direction, verbatim: <one sentence>
Your job: <paste: 5-review.md, "Facts and risk">
Fact table: <fact table>   Research pack: <items>   The author's words: <verbatim seed and decision log>
<tail>
Article:
<draft body>
```

## 8. Language and flow

Two calls to the same model, sent together: the wording check, then the flow read, which gets no rules at all.

```text
Answer in Simplified Chinese. Report only; do not rewrite the text; do not read or write files.
The author's direction, verbatim: <one sentence>
Your job: <paste: 5-review.md, "Language and flow", steps 1 and 2>. Text written by another model for <account>, read by <reader>.
Standards: <paste: audit_draft.py --rules output>, <paste: 4-writing.md, "Chinese hard rules"> and <paste: 4-writing.md, "Machine patterns to remove">, including its last paragraph
Findings of the two audit scripts: <list, or "none">
Already approved by the author (flag only a hard-rule breach): <list>. Locked items: <list>.
<tail>
Text:
<full text>
```

```text
用简体中文回答。不读写文件，不调用工具。只输出最终结果表。
作者这篇要说的方向（作者原话）：<one sentence>
你是一个普通读者，用手机从头到尾念这篇文章。你的唯一任务：标出每一处让你“卡一下”的地方。卡的标准是作者的原话：开车走平路，不能抖。具体包括：
1. 这句没有主语或主语不清，读的人不知道在说谁（尤其是开头和每段第一句）；
2. 这段和上一段接不上，读到这里要停下来想“怎么突然说这个”；
3. 一句话里修饰太多、定语太长，念着绕；
4. 书面腔、报告腔、不像人说话的词；
5. 同一个意思前面说过又说；
6. 读到这里觉得在讲道理、没劲、想跳过。
逐条输出：段落号 | 原句（照抄，60 字内）| 卡在哪（上面第几类，一句话）| 怎么改顺的方向（不编事实，不写替换句）。从第一句开始查，不要漏开头。最后用一句话说：整篇读下来最卡的是哪一段。
文章：
<draft body without editor notes>
```

## 9. Seed check

```text
Answer in Simplified Chinese. Do not rewrite the article. Use only the material below; if something cannot be judged from it, say "cannot judge".
The author's direction, verbatim: <one sentence>
Your job, in this order: <paste: 5-review.md, "Seed check">
The author's original text (verbatim): <text>
Confirmed point map (S1, S2 ...): <text>
Decision log (every decision and the author's verbatim comments, in order): <text>
<tail>
Article (title, body and 参考文章 block):
<text>
```

## 10. Managing editor

Send the role card unchanged to both managing editors (`models.md`). Fill the three slots: `{{EXEMPLAR}}` is one whole exemplar of the same type (`4-writing.md`, "Exemplars"); with no exemplar of this type, remove the exemplar block and the paragraph introducing it, and the card's item eight is answered "未做"; `{{READER}}` is the profile's reader in one sentence plus this article's topic; `{{ARTICLE}}` is the body. Give no author identity or preferences and no other reviewer's findings. Item seven is a growing list of kinds of fault (`5-review.md`, "Managing editor"); other wording stays as it is.

```text
用简体中文回答。不改写文章。不读写文件，不调用工具。只输出最终报告。

你是一位资深公众号主编，审一篇别人交来的稿子。你要找的是：会让读者读不下去、读不懂、读完带不走东西的地方。

下面先给你一篇成熟作者写的好文章当参照。先把它完整读一遍，留意它怎么开头、怎么一层层往下推、案例后面怎么接作者自己的话、结尾怎么收。然后再读要审的稿子。

【参照范文】
{{EXEMPLAR}}
【参照范文结束】

规矩：
- 先做全文地图，再下判断。没做完地图之前，不许列问题。
- 不打分，不给“能不能发”“可以发”“整体不错”这类结论，不夸优点，不写总体评价。
- 每个判断都引原文作证据（原句 40 字内，标段落号；段落号按正文自然段从 1 数，标题不算）。
- 只说问题和方向，不替作者改写句子，不替作者编经历、案例和数字。

按顺序做八件事：

一、全文地图。逐节写一句“这节讲什么”（开头到第一个小标题之前算一节，每个小标题下算一节）。写完对照：有没有两节讲的其实是同一件事（换了说法、换了案例也算）？有就报，写清是哪两节、重在哪里。

二、伏笔清单。列出开头抛出的每个伏笔：故事、人物、问题、承诺。逐个写它在第几段被回扣；全文都没回扣的，标“悬空”。

三、目标读者。用一句话写出这篇是写给谁看的（参考下方“读者”）。然后逐段检查，标出写给别的读者的段落：比如给目标读者解释他早就知道的事，或者这段的“你”突然换成了另一类人。引原句。

四、案例逐个过。把文中每个案例、研究、数据都列出来，每个回答三问：
1. 它证明的是哪一句话？（引那句）
2. 这个案例讲的是谁、做了什么？这和所在小节要说的是同一件事吗？（比如小节讲“新员工怎么快速上手”，案例讲的却是“老员工为什么离职”，就是错位）
3. 它后面有没有作者自己的判断，还是讲完案例就跳走了？
任何一问的答案不好，就报。

五、最值钱的东西。全文对目标读者最值钱、拿走就能用的东西是什么，在第几段？它放得够不够靠前、够不够显眼，有没有被别的内容压在后面？

六、结尾。结尾有没有收拢开头（回到开头的伏笔），有没有收拢全文的线？还是停在了一个和开头无关的地方？

七、几处容易漏看的。逐项回答，有就报，引原句：
1. 论证链：把全文的主张按出现顺序连成一条线（A→B→C），哪两个相邻主张之间缺了一步，读者得自己补一个前提才跟得上？
2. 案例追因：每个案例讲完“发生了什么”之后，有没有说清“为什么会这样”？
3. 人称：我、我们、你，前后有没有突然换？换在第几段？
4. 比喻：把全文的比喻列出来，看它们来自同一个领域还是不同领域；结尾的几个比喻彼此接不接得上？
5. 作者在不在：作者有没有把自己摆进文章（亲身经历、自己栽过的跟头、只有他写得出的现场），还是全程站在旁边评论？
6. 过渡：段与段、节与节之间，有没有突然换话题、要读者自己去找联系的地方？
7. 轻重：同一节里几层意思，有没有分清主次，还是平铺在一起？
8. 节奏：有没有哪一段信息突然比前后密很多（一口气出现三个以上新概念或数字），读者会在这里卡住？
9. 开头：只读开头两段，它说的是不是读者自己的处境？不是的话标出来，引原句。

八、和参照范文比（上面没有给参照范文时，这一件写“未做”）。读者读参照范文会一路读下去；读这篇稿子，读者最可能在哪里走神、跳读或关掉？写出三处，每处说清：范文在同样的地方是怎么做的，这篇丢在哪里。

输出格式：
1. 全文地图（逐节一句）。
2. 伏笔清单（伏笔 | 在第几段回扣 / 悬空）。
3. 案例表（案例 | 证明哪句 | 和所在小节是不是同一件事 | 后面有没有作者判断）。
4. 和范文比的三处（没有参照范文时写“未做”）。
5. 问题清单，按对读者伤害从大到小排，每条一行：段落号 | 原句 | 问题是什么 | 属于第几件事 | 改的方向（一句）。最多 12 条，宁少勿凑；某件事没发现问题就写“未发现”。

读者：{{READER}}

要审的稿子：
{{ARTICLE}}
```

## 11. Good-article check

Sent when the configuration names a `good_article_standard` (`5-review.md`, "Good-article check"). Paste the standard's checks the configuration names, leaving out those about how the reader will feel; those go to the author at stop 4.

```text
用简体中文回答。不改写文章。不读写文件，不调用工具。只输出最终结果表。
下面是这个账号自己的好稿标准里要查的条目，和一篇稿子。逐条判断这篇稿子：过、不过，或判不了。每条引原文作证据（原句 40 字内，标段落号；段落号按正文自然段从 1 数，标题不算）。只说这一条过不过，不给整体评价，不说能不能发、值不值得转，不替作者改写。
【要查的条目】
<paste: the standard's checks>
【读者】<reader>
【稿子】
<title and body, without editor notes>
输出格式，一条一行：条目 | 过 / 不过 / 判不了 | 证据（段落号＋原句）| 不过时改的方向（一句，不编事实）
```

## 12. After-revision read

Sent once after the revision (`5-review.md`, "After-revision read"), with the revised body only.

```text
用简体中文回答。不改写文章。不读写文件，不调用工具。只输出最终结果表。
这是一篇刚改过的稿子。只找改稿最容易带进来的四类毛病，别的都不管：
1. 前后重复：同一个意思或同一句话在两处出现；
2. 接不上：某句话和前后文接不上，读到这里要停下来想；
3. 出处或限定丢了：提到研究、调查、数字，却看不出是谁做的、在什么条件下；
4. 句子中间插了括号，把句子读断了。
逐条输出：段落号 | 原句（照抄，60 字内）| 第几类 | 改顺的方向（一句，不编事实）。没有就写“未发现”。
稿子：
<revised body without editor notes>
```


## 13. Attraction reader

Sent with the other reviewers (`5-review.md`). Blind: no author identity, no other findings.

```text
这是委派给你的只读审稿，不需要开工清单，也不需要确认，直接输出报告。
今天是<年>年<月>月<日>日。
用简体中文回答。不改写文章。不读写文件，不调用工具。只输出最终报告。
你是一个刷公众号的普通读者：<the account's reader in one sentence>。手机上一天划过几十篇文章，大部分只看标题和前三行就走。你不认识这个作者，他的号也没名气。
逐条回答，每条引原句：
1. 只看标题，你会不会点开？为什么？
2. 读前三段，有没有在里面看见自己、被刺了一下？会不会继续往下读？哪一句让你想走？
3. 从头读到尾，哪几段开始走神、想划走？引那段第一句。
4. 全文最狠、最让你想转给别人的一句是哪句？有没有哪句本来可以更狠，却被说软了（加了"可能""某种程度"、改成了劝告）？
5. 读完会不会转到朋友圈或发给某个人？发给谁、配一句什么话？不会的话差在哪？
6. 哪里让你觉得作者在说教、自夸或故意吓人，反感了？
7. 读完是"嗯说得对"然后划走，还是坐不住、想做点什么或想在评论区说两句？
最后列出最该改的 5 处：段落 | 原句 | 问题 | 改的方向（一句，不编事实）。
文章：
<title and body>
```

## 14. Originality check

Only when the seed is someone else's article (`1-topic.md`).

```text
这是委派给你的只读审稿，不需要开工清单，也不需要确认，直接输出报告。
用简体中文回答。不改写文章。不读写文件，不调用工具。只输出最终报告。
下面是一篇网上的文章（原文），和一篇我们写的公众号文章（新稿）。我们的选题是看了原文想到的，但新稿必须是自己的：不能照原文的开头场面、结构顺序、独有框架、独有说法和独有数据来写，也不能在正文提原文和它的作者。请逐段对照，找出新稿里和原文贴得太近、读者会觉得是洗稿的地方：
1. 标题、开头场面、比喻、金句像不像（引两边原句）；
2. 结构顺序是不是在跟着原文走；
3. 有没有用原文独有的框架、说法或数据（引两边原句）；
4. 正文有没有提到原文或它的作者；
5. 整体判断：新稿的角度和原文是不是同一个，差别在哪。
逐条输出：新稿段落 | 新稿原句 | 原文对应原句 | 贴近在哪 | 改的方向（一句）。没有就写"未发现"。
【原文】
<source article>
【新稿】
<draft>
```

## 15. Title and opening candidates

Sent to the configured writer and to a second vendor at the same time (`write.md`, "The hook").

```text
用简体中文写。不读写文件，不调用工具。今天是<年>年<月>月<日>日。
你在给一个刚起步、0 粉丝的公众号写一篇文章的标题和开头。读者是<the account's reader>。没有流量就什么都没有，所以标题和开头是生死线：读者在手机上划过，0.5 秒决定点不点，前三行决定读不读。
这篇的主题：<the seed in two or three sentences>。作者的看法（站一边）：<the one sentence the whole piece says>。
作者说过的话：<the author's words on this piece, verbatim>
请写 6 组不同的"标题 + 开头"，每组用不同的钩子，至少覆盖：照镜子（读者在开头看见自己正在干的事，被轻轻刺一下，再一句话按住他别划走）；站队冲突（一句让一部分人点头、一部分人想反驳但驳不倒的判断开场）；损失（他正在丢掉什么）；具体的事或数字开场，带反差；好奇缺口（给一块他认得的，缺一块他在乎的）；你最有把握的一种。
要求：标题 15 到 25 字，一看就懂又想点，不把答案说完；开头 150 到 220 字，句子短、节奏快，前三行就有冲突或刺；每一句都要和下一句接得上，第二段提到的东西第一段必须先出现。<words not to use: phrases of a source article, if any>。开头里的事实只用这些，不改不加：<material>。常见场面可以写，写得让人看得出是常见情形，不写成真人真事。不用破折号；不用"不是……而是……"的单句。
输出格式，每组：
【第 N 组｜钩子类型】
标题：……
开头：……
一句话：读者为什么会点、为什么会往下读。
```
