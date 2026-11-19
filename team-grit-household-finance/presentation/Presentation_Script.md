# Team Grit — Presentation Script

About 14 minutes, 16 slides. Slides: `Team_Grit_Presentation.pdf` in this folder.

| Presenter | Slides | Covers |
|---|---|---|
| Matthew Jones | 1–4 | Title, agenda, business problem, key findings |
| Maria Mummau | 5–7 | Data, research questions, method & tools |
| Kellen Gradisar | 8–9, 14 | RQ1 income & shocks; recommendations |
| Kiefer Cuppet | 10–11, 15 | RQ2 housing debt & credit; limitations |
| Team member 5 | 12–13, 16 | RQ3 savings & retirement; Q&A |

## Slide 1 — Title  ·  Matthew Jones

Good [morning/afternoon], everyone. We’re Team Grit. Our project looks at household financial resilience: how a family’s income, debt and savings shape three things — whether it saves or borrows, how risky its debt is, and when it can afford to retire. We used survey microdata from the Federal Reserve Bank of New York and built our analysis in Python and Tableau.

## Slide 2 — Agenda  ·  Matthew Jones

Here’s how we’ll walk through it. I’ll set up the business problem and give you the headline findings. Maria covers the data and our method. Then each research question has its own presenter: Kellen on income, saving and shocks; Kiefer on housing debt and credit; and [Team member 5] on savings and retirement. We’ll close with recommendations, limitations and your questions.

## Slide 3 — The business problem  ·  Matthew Jones

Why does this matter? Household balance sheets drive consumer spending, they drive credit losses for lenders, and they drive what employers and the public pay for retirement security. Three groups need the same answer: lenders deciding who to lend to and when to step in; employers and retirement plan providers designing benefits; and policymakers deciding where support does the most good. The question they share is: which households are most exposed, and where does an intervention actually move outcomes?

## Slide 4 — Key findings at a glance  ·  Matthew Jones

Here’s the short version before we dig in. First, income decides who saves: 62 percent of households earning $150,000 or more added to their savings last year, compared with just 15 percent of those earning under $35,000. Second, how people rate their credit is a strong warning light: people who rate it below 620 think they are about seven times as likely to go bankrupt as people above 760. Third, savings buy time in retirement: people with a million dollars or more expect their money to last 27 years; people with under $10,000 expect 11. Now Maria will explain where these numbers come from.

## Slide 5 — Data  ·  Maria Mummau

Thanks. Our data is the Survey of Consumer Expectations, Household Finance module, published by the Federal Reserve Bank of New York. It’s a nationally representative online panel of U.S. household heads. The file we used has 6,809 responses across six annual waves, each collected in August from 2014 to 2019, with 397 variables covering income, savings, debt, credit and retirement plans. We want to be upfront about its limits: it’s self-reported, so people may misremember amounts or under-report financial stress; the panel loses members over time; and it covers only U.S. households. Because each wave is a snapshot, what we show are associations, not proof of cause and effect.

## Slide 6 — Research questions  ·  Maria Mummau

We asked three research questions. RQ1: how does income affect whether a household saves or takes on debt, and what changes after an unexpected income or health shock? RQ2: how does what a household owes on its home relate to its other debts, and does how people rate their credit predict how likely they think they are to fall behind? RQ3: how do current savings and income affect when people plan to retire, and how long they expect their savings to last?

## Slide 7 — Method and tools  ·  Maria Mummau

Our process had four steps. First we extracted the data and codebook from the Fed’s workbook. Second we cleaned it, removing impossible values like incomes over five million dollars or retirement ages outside 40 to 90, and built the measures we needed: income groups, saving behavior, shock flags, mortgage tiers, debt by type, and total savings across bank accounts, 401(k)s and IRAs. Third we computed survey-weighted shares, averages and medians, so results represent U.S. households, not just the people who answered; we used medians and rank correlations because dollar amounts are very skewed. Fourth we visualized it: one cleaned file feeds both our Python charts and our Tableau dashboards, so the numbers match. One note: the survey has no direct ‘will you miss a payment’ question, so for RQ2 we used people’s own estimate of their chance of bankruptcy and checked it against whether they had actually been three months late on a housing payment. Over to Kellen for the first question.

## Slide 8 — RQ1: Higher income turns households into net savers  ·  Kellen Gradisar

Thanks. Our first question is about income. Each bar is an income group, and the colors show what households did with their savings last year. Blue is households that added more than they took out. Look how it grows: 15 percent at the bottom, 62 percent at the top. The bigger story is the dark gray on the right: households with no savings account at all. That’s half of the under-$35,000 group, versus 8 percent at the top. And debt isn’t just a low-income issue: 75 to 85 percent of every income group carries some non-housing debt. The difference is cushion: 92 percent of top earners would cover a surprise $2,000 bill from their own savings, compared with 42 percent of the lowest earners.

## Slide 9 — RQ1: A shock erases much of the income advantage  ·  Kellen Gradisar

Now, what happens when something goes wrong? On the left, blue is households with no shock and orange is households that had a large income drop or a decline in health. At every income level the orange line is lower. In the $100,000 to $150,000 group, the share of net savers falls from 57 percent to 32 percent: a shock wipes out much of what higher income buys. On the right: among households that pulled money out of savings, 68 percent of those whose health got worse named health as a reason, compared with 30 percent of everyone else. Health problems show up directly as drained savings. Now Kiefer takes us to debt.

## Slide 10 — RQ2: Big mortgages come with more consumer debt, not less  ·  Kiefer Cuppet

Thanks. RQ2 starts with the home. We grouped households by what they owe on their home — renters, owners with no mortgage, and three mortgage sizes — and looked at their other debt by type. A common assumption is that a big mortgage squeezes out other borrowing. We found the opposite: households with a mortgage over $250,000 carry about $73,000 in other debt on average, roughly double the other groups, mostly credit cards, auto loans and student loans. Two things put that in context. Those households earn much more, so that debt is a smaller share of their income: about 17 percent, against 47 percent for renters. And among mortgage holders, mortgage size and other debt barely move together, with a correlation of just 0.06. So big mortgages don’t force households into card or medical debt; both scale with income. Medical debt is small in dollars in every group.

## Slide 11 — RQ2: How people rate their credit predicts expected default  ·  Kiefer Cuppet

The second half of RQ2 is about how people see their own credit. We grouped people by the credit score they think they have. On the left is their own estimate of the chance they’ll go bankrupt in the next year. It falls at every step: 15.7 percent for people below 620, down to 2.2 percent above 760, about seven times lower. And it isn’t just pessimism: 26 percent of the below-620 group had actually been three months late on a housing payment in the past year, compared with under one percent of the top group. On the right is their chance of coming up with $2,000 in a month: 31 percent versus 88 percent. Weak credit and thin cushions go together. Now [Team member 5] will cover retirement.

## Slide 12 — RQ3: Money buys an earlier, longer-lasting retirement  ·  Team member 5

Thanks. RQ3 looks at people who aren’t retired yet. Blue lines group them by total savings, orange by income. On the left is planned retirement age: higher income means retiring earlier, from about 68 at the bottom to 65 and a half at the top, almost three years. Savings follow the same direction until the very top group, which is small and may include wealthy people who simply choose to keep working. On the right is how long people expect their savings to last after they retire. This is where savings really matter: 11 years for people with under $10,000, rising to 27 years for people with a million or more. And the two are linked: people with thin savings plan to work longer and still expect their money to run out sooner.

## Slide 13 — RQ3: Most households with under $50k saved expect to fall short  ·  Team member 5

Here’s the consequence. We asked people whether they expect to have too little saved for retirement. That’s 63 percent of households with under $10,000, and 56 percent of those with $10,000 to $50,000, compared with 12 percent of those with a million or more. Most households with modest savings already know they’re behind. Kellen will now share what we recommend.

## Slide 14 — Recommendations  ·  Kellen Gradisar

Pulling it together, one lever shows up in every question: a liquid emergency cushion. Here’s what we recommend. First, employers and banks should offer automatic emergency savings, such as a payroll split or a ‘sidecar’ account next to a 401(k), with $2,000 as the first goal. Second, because health shocks drain savings directly, pair health benefits with HSA contributions and short-term disability coverage. Third, lenders should treat weak or unknown credit as an early-warning sign: offer free score access and hardship plans before a payment is 90 days late. Fourth, underwrite on debt-to-income and liquidity, not mortgage size alone. And fifth, use auto-enrollment and auto-escalation in retirement plans, with extra outreach to households with under $50,000 saved.

## Slide 15 — Limitations and next steps  ·  Kiefer Cuppet

A few honest limits. This is self-reported survey data, so some amounts are estimates and some financial stress is probably under-reported. Each wave is a snapshot, so we show associations, not causes. And this extract has no age variable, so some of what looks like an income effect could be life stage. For next steps, we’d add age and education from the core survey; build a simple risk score from credit, liquidity and shocks and test it against actual delinquency; and extend the data past 2019 to see how households came through COVID.

## Slide 16 — Questions  ·  Team member 5

That’s our project. Everything — the data, our code, the charts, the Tableau workbook and the full report — is in our public GitHub repository. Thank you, and we’re happy to take your questions.
