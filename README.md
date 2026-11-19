# launch-factory

Turn a briefing and a few links into six launch drafts in one chat, then redraft from your notes.

## What it does

You type one command and give it a briefing, links, a pasted team thread, or all three. Launch Factory reads each source, shows you a plan, and writes six drafts: a blog post, a changelog entry, an FAQ update, social posts, a launch map and an explainer. The last two are single HTML files you open in a browser. In the explainer you press Play to start it. It saves them in a `launch/<name>/` folder, shows them in the chat and waits for your feedback.

Every claim in a draft carries a number that points to a Sources list, and a "Not traced" list shows what it could not match to a source. The two HTML files draw both lists on the page. Ask for a change and it writes a new version next to the old one, such as `blog-v2.md` beside `blog.md` or `launch-map-v2.html` beside `launch-map.html`. A changed explainer comes as `explainer-v2.html` and `explainer-script-v2.md` together. It leaves everything else alone. It never publishes, posts, sends, merges or spends. A person does that.

## Two ways to install

Launch Factory comes as a plugin or as a skill. Both write the same six drafts. Pick one.

| | Plugin | Skill |
|---|---|---|
| File | `launch-factory.zip` | `launch-factory-skill.zip` |
| Made for | Claude Code and Cowork | Claude Code and claude.ai |
| Command | `/launch-factory:launch` | `/launch-factory` |
| Starts | only when you type the command | when you type the command, or when you paste a briefing and ask for launch drafts. It then asks one yes before it writes them. |

Both zips are attached to the v0.2.0 release on the Releases page of this repository. A release page also offers "Source code (zip)", which is not either of these. The plugin steps follow below. The skill steps are here.

Skill in Claude Code:

1. Unzip `launch-factory-skill.zip` into your personal skills folder, so that you have `~/.claude/skills/launch-factory/SKILL.md`.
2. Start a new Claude Code session and type `/launch-factory`.
3. To remove it, delete the `~/.claude/skills/launch-factory` folder.

Skill on claude.ai:

1. Turn on code execution in your settings. Skills need it.
2. Open **Customize > Skills**, click **+**, then **Create skill**, then **Upload a skill**.
3. Choose `launch-factory-skill.zip`. Do not unzip it first.
4. Start a new chat and type `/launch-factory`, or paste a briefing and ask for launch drafts.
5. To remove it, open **Customize > Skills** and turn it off or delete it.

## Install in Claude Code

You need a Claude Code account. The plugin runs nothing when you install it.

From the GitHub repository:

1. Clone it:

   ```
   git clone https://github.com/gabchess/launch-factory.git
   ```

2. Start Claude Code with the folder:

   ```
   claude --plugin-dir ./launch-factory
   ```

From a local folder or a zip:

1. Unzip the file. A zip named `launch-factory.zip` gives a folder named `launch-factory`. GitHub's **Code > Download ZIP** button gives `launch-factory-main` instead, so use that name in the next step.
2. Start Claude Code with the folder, as above. Claude Code also takes the zip itself: `claude --plugin-dir ./launch-factory.zip`.

Then type `/launch-factory:launch`. You should see Claude ask what you are launching, or start on what you gave it. The folder loads for that session only.

## Install in Cowork

1. Download `launch-factory.zip` from the v0.2.0 release on the Releases page, or use the one you were sent. GitHub's **Code > Download ZIP** button gives a different zip, `launch-factory-main.zip`, which has not been tested in Cowork.
2. Open the Claude desktop app or claude.ai and sign in.
3. Go to **Customize > Plugins**.
4. Select **Add > Upload plugin** and choose the zip.
5. Start a new Cowork task. The plugin loads when the task starts.
6. Type `/launch-factory:launch`. That command is the only way to start a run.

## First prompt

Copy this into Claude after the install:

```
/launch-factory:launch Briefing: Ledgerly, a small invoicing app for freelancers, ships "Recurring invoices" on 3 December. Freelancers can set an invoice to repeat weekly or monthly and Ledgerly sends it for them. It is free on every plan. Audience: freelance designers and writers. Tone: friendly and plain. Link: https://github.com/example/ledgerly/pull/42
```

You should see Claude read your briefing, try the link, show a short plan, then show six drafts with a status line each. The message starts with what waits on you, and it ends by asking what you think. If the example link cannot be read, Claude lists it there and asks you to paste its text.

## Data

It reads what you give it: the text of your briefing, any text you paste, the links you provide, and the optional file `.launch-factory/preferences.md` in your working folder. If you have connected a tool such as a code host, an issue tracker, team chat, docs lookup or web search, it uses that tool to read the links you gave it, and only those.

It writes files to `launch/<name>/` in your working folder.

It sends nothing to anyone and posts nothing. Your text goes only to the Claude session you are already using, and to the connected tools you chose to read links. Launch Factory holds no keys and asks for none.

## Tested on

- Claude Code: verified 2026-11-18, one run of the first prompt without its example link, with `--plugin-dir`
- Cowork: verified 2026-11-17, uploaded as a zip and run with the first prompt without its example link
- Skill in Claude Code: verified 2026-11-18, one run of the first prompt without its example link, with `/launch-factory` loaded from a project `.claude/skills` folder, and one run from a pasted briefing alone, which asked one yes and wrote nothing
- Skill on claude.ai: not verified

## Rollback

- Cowork and claude.ai: open **Customize > Plugins**, open `launch-factory`, then turn on **Disable plugin**, or choose **Remove** from its menu.
- Claude Code with `--plugin-dir`: close the session. Nothing was installed.
- Delete the `launch-factory` folder and the zip to remove every file. Drafts in your `launch/` folder stay until you delete them.
