# Ranked Design Principles (Template)

Fill this in for yourself. Force a strict rank order. No ties, no "they are all equally important." The whole value is in deciding what gives when two of them collide.

Keep it to five to eight principles. More than that and the ranking stops guiding anything.

---

## My ranked principles

Replace each item. The number is the priority. The one-line rule is how your agent should apply it when this principle is the deciding factor.

1. **<PRINCIPLE_1>:** <one line on what this means in practice and what it beats>
2. **<PRINCIPLE_2>:** <one line>
3. **<PRINCIPLE_3>:** <one line>
4. **<PRINCIPLE_4>:** <one line>
5. **<PRINCIPLE_5>:** <one line>
6. **<PRINCIPLE_6>:** <one line>

---

## How to apply this order

- When two valid options compete, choose the one that better serves the higher-ranked principle.
- Name the principle in the decision so the reasoning is auditable: "chose X over Y because reliability outranks cost here."
- Revisit the order when your situation changes (new regulation, a painful outage, a shift in what the business needs).

## Worked example to adapt

> Two libraries both solve the task. One is a maintained external dependency, the other I would own and host myself. If control outranks cost in my order, I build my own when it is feasible and worth it. If cost outranks control, I take the dependency and accept the tradeoff, and I write down the trigger that would make me revisit.

## Candidate principles to rank (not exhaustive)

Pick the ones that matter to you, add your own, then order them:

- Quality of output
- Reliability and uptime
- Privacy of sensitive data
- Control and sovereignty over your tools and data
- Cost
- Speed
- Auditability
- Simplicity and maintainability
- Reversibility (how easily can you undo a decision)
