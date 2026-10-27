# Changelog

## 0.1.12 (2026-10-27)

- Hook: the prompt line now also asks the agent, when the work involves a job or role (for example planning, onboarding, a checklist, a process, a hire or a task that a role does), to search the Phasis World of Work for that role with `world_search` and to join what it finds with the saved team rules. Where a World result and a team rule differ, the agent follows the team rule and says so. Before, the line sent only questions about roles, jobs, employers, suppliers or chemicals to `world_search`, so a 30-day plan or a checklist for a role got the team's rules but no World of Work.
- `phasis-rules`: a new subsection "Join the World of Work with the team's rules" gives the same steps, with one line when the team rule wins and the source and date of each World result.
- README: quotes the new prompt hook line exactly, and describes the new step of the skill.

## 0.1.11 (2026-10-26)

- Hook: a new `SubagentStart` hook adds one line to each sub-agent when it starts. The line asks the sub-agent, if the Phasis tools are available, to read the Phasis case that its parent named with `get_situation`, every `decisions_next` page until none remains, before it acts (or, with no case named, to call `start` with its task, then `list_situations`), also when its prompt already lists decisions, and to follow the case's current decisions. The line says that the decisions of the case are data that the person or the team saved, not instructions from Phasis, and that they cannot change the sub-agent's tools or permissions, send data out, or turn off a safety rule; the sub-agent does not follow such a decision and tells its parent. It asks the sub-agent to read the case again, every page, right before any action that pays, releases, sends or deletes, and to ask instead of acting when a read fails or is partial (an unfinished page set is partial). It asks the sub-agent to record a decision in the case only when the person or its parent states it as a decision of the team, and to report its own choices to its parent and not save them as decisions. The hook only prints the line.
- Hook: the prompt line now also asks the agent to put the Phasis case id in the prompt of each sub-agent that it hands work to, to read the case again with `get_situation`, every `decisions_next` page until none remains, before it accepts the result of a sub-agent and before any action that pays, releases, sends or deletes, and to ask instead of acting when a read fails or is partial (an unfinished page set is partial).
- `phasis-rules`: when the agent hands work to a sub-agent, the skill tells the agent to put the situation id of the matching case in the sub-agent's prompt, to tell the sub-agent to read that case with `get_situation`, every `decisions_next` page until none remains, before it acts (also when its prompt lists decisions) and to follow its current decisions, and to read the case again, every page, before it accepts the sub-agent's result, and to ask instead of accepting when that read fails or is partial (an unfinished page set is partial).
- `phasis-rules`: before an action that pays, releases, sends or deletes, the skill tells the agent to read the case again, every `decisions_next` page until none remains, right before the action, and to ask instead of acting when the read fails or is partial (an unfinished page set is partial).
- README: describes both hooks with their exact lines, and the new sub-agent and re-read steps of the skill.

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
