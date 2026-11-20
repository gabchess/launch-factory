# launch-factory

Choose a meaningful product change, turn it and your brand context into six launch drafts, then redraft from your notes.

## What it does

You give it a briefing, PRs, links, a pasted team thread, or a mix. Launch Factory reads the sources and your team's positioning and voice, then chooses a coherent launch story. It shows which changes belong, which need more evidence, and which do not need an announcement. A merged PR alone does not prove that a feature is available. If there is no supported launch, it explains that decision instead of producing filler.

For a supported launch it shows a plan and writes six draft types: a short blog post, a changelog entry, an FAQ update, social posts, a launch map and an explainer. These are seven files because the explainer includes a script. The last two draft types use single HTML files you open in a browser. Press Play to start the explainer's captioned scenes. It has no rendered video or audio. Files go in `launch/<name>/` where the host can save files, or are offered as downloads in Claude chat. It then waits for your feedback.

Every claim in a draft carries a number that points to a Sources list, and a "Not traced" list shows what it could not match to a source. The two HTML files draw both lists on the page. Ask for a change and it writes a new version next to the old one, such as `blog-v2.md` beside `blog.md` or `launch-map-v2.html` beside `launch-map.html`. A changed explainer comes as `explainer-v2.html` and `explainer-script-v2.md` together. It leaves everything else alone. It never publishes, posts, sends, merges or spends. A person does that.

## Two ways to install

Launch Factory comes as a plugin or as a skill. Both write the same six drafts. Pick one. On claude.ai, install one or the other, because both use the name launch-factory; remove the plugin before uploading the skill.

| | Plugin | Skill |
|---|---|---|
| File | `launch-factory.zip` | `launch-factory-skill.zip` |
| Made for | Claude Code and Cowork | Claude Code, Claude chat and Cowork |
| Start | `/launch-factory:launch` | `/launch-factory` in Claude Code; explicit request in Claude chat/Cowork |
| Starts | only when you type the command | when you type the command, or when you paste a briefing and ask for launch drafts. It then asks one yes before it writes them. |

Use the packaged ZIP supplied with your release. A GitHub release page may also offer "Source code (zip)", which is not the standalone skill archive. Version 0.3.0 adds change selection and portable client context. A source version is not a claim that a matching GitHub release has been published.

The standalone folder includes `QUICKSTART.md` and a fictional `examples/briefing.md` you can use without connecting any service.

Skill in Claude Code:

1. Unzip `launch-factory-skill.zip` into your personal skills folder, so that you have `~/.claude/skills/launch-factory/SKILL.md`. Copy the whole folder, including references, templates and license. Back up any earlier folder before replacing it.
2. Start a new Claude Code session and type `/launch-factory`.
3. To remove it, delete the `~/.claude/skills/launch-factory` folder.

Skill on Claude chat or Cowork:

1. Turn on code execution in your settings. Skills need it.
2. Open **Customize > Skills**, click **+**, then **Create skill**, then **Upload a skill**.
3. Choose `launch-factory-skill.zip`. Do not unzip it first.
4. Enable it. Start a fresh chat or Cowork task and say, "Use Launch Factory with this briefing and brand context." It asks one yes before drafting when started without its slash command. Do not assume that every surface has the same slash-command picker.
5. To remove it, open **Customize > Skills** and turn it off or delete it.

A local Claude Code skills folder does not enable the skill in Cowork. Share the ZIP with teammates or use the organization's supported skill-sharing controls. Account policies can restrict uploads. See [Claude's skill guide](https://support.claude.com/en/articles/12512180-use-skills-in-claude) for current requirements.

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

1. Use the packaged `launch-factory.zip` you were sent or download a matching release asset. GitHub's **Code > Download ZIP** button gives a source archive rather than the tested package layout.
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

It reads the briefing, links, attachments and client context you provide. In a working folder it can reuse `.launch-factory/preferences.md` and `.claude/product-marketing-context.md`. In chat, attach or paste an equivalent document. If you have connected a tool such as a code host, an issue tracker, team chat or web fetch, it uses that tool to read supplied sources. It does not monitor repositories in the background.

It writes files to `launch/<name>/` in your working folder.

It sends nothing to anyone and posts nothing. Your text goes only to the Claude session you are already using, and to the connected tools you chose to read links. Launch Factory holds no keys and asks for none.

## Validation history

The following entries are historical v0.2.0 records, not fresh tests of v0.3.0. Their recorded browser session did not establish whether the web run was a true Cowork task. Treat current-host loading, draft quality and a real client trial as separate checks. Version 0.3.0 needs a fresh host trial before claiming it has been tested in each environment.

- Claude Code: verified 2026-11-18, one run of the first prompt without its example link, with `--plugin-dir`
- Cowork: verified 2026-11-17, uploaded as a zip and run with the first prompt without its example link
- Skill in Claude Code: verified 2026-11-18, one run of the first prompt without its example link, with `/launch-factory` loaded from a project `.claude/skills` folder, and one run from a pasted briefing alone, which asked one yes and wrote nothing
- Skill on claude.ai: verified 2026-11-18, uploaded as a zip and run with `/launch-factory`
- Plugin 0.2.0 on claude.ai: verified 2026-11-18, uploaded as a zip over 0.1.0 and run with `/launch-factory:launch`

## Rollback

- Cowork and claude.ai: open **Customize > Plugins**, open `launch-factory`, then turn on **Disable plugin**, or choose **Remove** from its menu. A claude.ai skill is removed under **Customize > Skills**.
- Claude Code with `--plugin-dir`: close the session. Nothing was installed.
- Delete the `launch-factory` folder and the zip to remove every file. Drafts in your `launch/` folder stay until you delete them.
