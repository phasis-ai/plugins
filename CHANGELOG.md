# Changelog

## 0.1.10 (2026-10-25)

- `phasis-rules`: for questions about who does a kind of work, what a role does, who hires for it, or about suppliers, products or chemicals, the skill tells the agent to search the Phasis Worlds with `world_search` before web search or memory, and to show the source and date of each result. The person does not need to name a World.
- `phasis-rules`: after a shortlist check, the skill tells the agent to name the Receipt of the check in one line.
- `phasis-rules`: when Phasis is not connected and the person asks to stop a rule, the skill tells the agent to say in one line that Phasis did not stop it. The skill names the words to search for the Phasis tools.
- Hook: the line no longer says "Phasis is connected". It asks the agent to call `start` if the Phasis tools are available, and to use `world_search` for questions about roles, jobs, employers, suppliers or chemicals. It also asks the agent to name the Receipt id after a check and to show the source and date of each World result.

## 0.1.9 (2026-10-25)

- README: describes the hook that version 0.1.8 added (the 0.1.8 README said "no hooks"). "Job briefing" is now "role lookup".
- `phasis-rules`: when no Phasis tool is available and the person states a rule, the agent now says in one line that Phasis did not save it. Before, it could answer "Got it" with nothing saved.

## 0.1.8 (2026-10-25)

- A hook on each prompt asks the agent to read the saved Phasis rules before work.

## 0.1.7 (2026-10-23)

- Org charts now say on the chart that they come from current job postings, not an official org chart. Evolution now quotes copy that has quotation marks in it, and it reads only from the Internet Archive, also when a page points elsewhere. Both skills say that they need Claude Code with web access and Python 3.

## 0.1.6 (2026-10-23)

- New skill `phasis-org-charts`: a department view of a company from its current job postings, with the link and read date of every role.
- New skill `phasis-evolution`: how a website's homepage copy changed over time, from Internet Archive copies, with the link and date of every quote.
