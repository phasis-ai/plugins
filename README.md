# Phasis

**Agents that know the job.**

Phasis gives your agent the job and the world. Your agent reads the rules saved for this work: the rules and decisions that you and your team saved in Phasis. When you state a new rule or decision, the Phasis skill tells the agent to save it at once and to show one line with the Receipt for the save.

The World of Work is live: ask who does a sales, account management, customer success or revenue operations job, and Phasis names the roles that the job needs and what each role checks. Creators and Chemicals come when world search is live.

You stay in control of what the agent learns. You can see, confirm and stop each learning.

## The plugin

The Phasis plugin is in [plugins/phasis](plugins/phasis). Its [README](plugins/phasis/README.md) says what you need, how to try it, what it sends and where.

## Org charts

Ask for the org chart of a company, and your agent draws a department view from the company's current job postings. It reads the company's own public job feed, keeps each department and team exactly as the company names it, and lists every open role. You get a chart file and the list of roles.

- What it needs: Claude Code with web access.
- Every role comes from a public job posting, with its link and the date it was read. The chart shows how the company groups its open jobs. It does not show who reports to whom.

## Evolution

Ask how a company's homepage changed, and your agent shows how the headline, description, buttons and prices changed over time. It reads saved copies of the homepage from the Internet Archive (Wayback Machine) and compares them. You get a card that shows the changes and short quotes of the copy.

- What it needs: Claude Code with web access.
- Every quote comes from a public Internet Archive copy, with its link and its date.

## Support

- Email: [support@phas.is](mailto:support@phas.is)
- Support page: [phasis.ai/support](https://phasis.ai/support)
- Privacy policy: [phasis.ai/privacy](https://phasis.ai/privacy)
- Terms of service: [phasis.ai/terms](https://phasis.ai/terms)

## License

Apache License 2.0. See [plugins/phasis/LICENSE](plugins/phasis/LICENSE).
