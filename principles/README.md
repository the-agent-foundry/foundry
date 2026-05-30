# Principles

Before you build a single cron job, skill, or sub-agent, rank-order your design principles.

## Why rank-ordering matters

Your principles are not a poster on the wall. They are the tiebreaker your agent reaches for every time two valid options compete. Should it spend a few more dollars of tokens on a task if it buys more reliability? When two skills both work but one keeps data more private, which wins? When speed and quality pull apart, which gives?

A flat list of values cannot answer those questions. A ranked list can. The rank order guides every future decision the agent makes on its own, and honestly, it clarifies the calls for you too.

The point is not to adopt someone else's order. The point is to decide yours, write it down, and give your agent something concrete to point back to when you say "check my design principles before you make this call."

## How to use this folder

1. Read `examples/darryl-ranked-principles.md` to see one founder's actual ranked six and the reasoning behind each.
2. Copy `PRINCIPLES.template.md` and fill it in for yourself. Force a strict order, no ties.
3. Put the result somewhere your agent reads on every task (its operating instructions, its system context, wherever your stack loads standing rules).
4. Reference it by name in specs: "rank against my principles before deciding."

The tradeoffs are real, and reasonable founders land in different places. Some only trust a major cloud to host their data. Others want full sovereignty on a private device even at a cost to reliability. Both are valid. What is not valid is leaving it unstated and hoping the agent guesses right.

## Pickup prompt

> Review this folder and tell me whether we should build a version of it for my company. Ask me for missing context first.
