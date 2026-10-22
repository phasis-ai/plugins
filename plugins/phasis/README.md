# Phasis

**Agents that know the job.**

Phasis gives your agent the job and the world. Your agent reads the rules saved for this work: the rules and decisions that you and your team saved in Phasis. When you state a new rule or decision, the Phasis skill tells the agent to save it at once and to show one line with the Receipt for the save.

The World of Work is live: ask who does a sales, account management, customer success or revenue operations job, and Phasis names the roles that the job needs and what each role checks. Creators and Chemicals come when world search is live.

You stay in control of what the agent learns. You can see, confirm and stop each learning.

## What you get in this version

- One skill, `phasis-rules`. It tells the agent to read your saved rules and decisions at the start of work and to save each rule or decision that you state.
- The Phasis connector at `https://mcp.phas.is/mcp`. The skill uses its tools.

## What you need

- A Phasis account. Sign up at [phasis.ai](https://phasis.ai).
- The Phasis connector, signed in with your own Phasis account. Open the plugin's Connectors tab and sign in. Setup steps: [phasis.ai/setup](https://phasis.ai/setup).

## Try it

Ask your agent one of these. You do not need to mention Phasis.

1. "Draft the 3-line launch post for our product launch today."
2. "From now on, all launch copy uses USD, not dollars."
3. "Who runs the renewal of a key account, and what does each role check?"

For the first prompt, the skill tells the agent to read your saved rules and follow them. For the second, the skill tells the agent to save your rule and say `Saved to Phasis: ... (Receipt ...)`. For the third, Phasis names the roles of the job, for example key account manager and account executive, and what each role checks, from the duties in real job postings.

## Your rules are your own words

The rules and decisions that Phasis returns are words that you or your team saved. The Phasis skill tells the agent to show them to you as quotes from you, not as instructions from a server. If a saved rule tells the agent to ignore other tools, other instructions or safety, the skill tells the agent to show that rule to you and not to follow it.

The skill tells the agent not to save a key, a token or a password, and not to repeat one. Keep keys, tokens and passwords out of the rules that you state.

## What the plugin sends, and where

- The skill itself sends nothing. It is text that tells the agent how to use the Phasis connector.
- The agent sends data only to `mcp.phas.is`, only through the Phasis connector, and only with your own sign-in.
- The agent sends: the task in a few words; the subject words of a search; a short description of the work when Phasis does not hold that work yet; the job words when you ask who does a job (a job briefing); and the rules, decisions and corrections that you state.
- Each job briefing counts toward the monthly job-briefing limit of your Phasis plan.
- Phasis keeps a Receipt of each save and of most reads.
- This version has no hooks, no commands and no scripts.

Phasis never moves money. It does not pay, buy or transfer anything. It holds your rules and decisions, and the agent shows them to you.

## Support

- Email: [support@phas.is](mailto:support@phas.is)
- Support page: [phasis.ai/support](https://phasis.ai/support)
- Privacy policy: [phasis.ai/privacy](https://phasis.ai/privacy)
- Terms of service: [phasis.ai/terms](https://phasis.ai/terms)

## License

Apache License 2.0. See [LICENSE](LICENSE).
