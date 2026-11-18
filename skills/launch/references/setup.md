# Setup

Launch Factory works with no connected tool at all. A connected tool lets it read a link on its own, so you do not have to paste the text. This page says what each kind adds and how to connect it. It never tests a connection. If a link cannot be read, Launch Factory asks you to paste its text.

No product is required. Any tool of the right kind works.

| Tool kind | What it adds | Connect in Claude Code | Connect in Cowork |
|---|---|---|---|
| Code host | Reads a pull request, repository or commit link. | Add a connector (an MCP server) for your code host with the `/mcp` command or the `claude mcp add` command, then sign in when it asks. | Open Customize, then Connectors, add the connector for your code host and sign in. |
| Issue tracker | Reads an issue link, its description and comments. | Same as above, with the connector for your issue tracker. | Same as above, with your issue tracker. |
| Team chat | Reads a thread link from your team chat. | Same as above, with the connector for your team chat. | Same as above, with your team chat. |
| Docs lookup | Reads current documentation for a library or service the launch names. | Same as above, with a documentation connector. | Same as above, with a documentation connector. |
| Web search | Reads a public page and checks a public fact. | Web search is built in on most plans. If it is off, turn it on in settings. | Turn on web search in the task settings, or add a search connector under Customize. |

Connector names and menu labels change over time. If a label differs, look for the connector or integration list in the app, or in the official Claude documentation.

## Make a preferences file

A preferences file tells Launch Factory how your team writes. It is optional. If it is missing, the run goes ahead with a neutral voice.

1. In the folder you work in, make a folder named `.launch-factory`.
2. In it, make a text file named `preferences.md`.
3. Paste this and change the lines:

```
# Preferences

## Brand voice
Plain, warm, short sentences. Address the reader as "you".

## Product names to spell right
- ExampleApp (one word, capital E and A)

## Phrases to avoid
- game-changing
- seamless
```

4. Save it. Launch Factory reads it at the start of every run and applies it to all six drafts.
