# Discovery Call Transcript — Zenith Bank Digital Banking Assessment

**SYNTHETIC FIXTURE — all names, contact details, and account numbers below are
invented for the pii-anonymizer eval gate (#127). No real client data.**

Date: 2026-03-12
Attendees: Maria Chen (VP Digital Banking, Zenith Bank), David Cole (Head of
Operations, Zenith Bank), Priya Rao (Data & Analytics Lead, Zenith Bank),
Alex Rivera (Backbase Consultant, facilitator)

Alex Rivera: Thanks everyone for joining. Let's start with introductions and a
quick overview of what Zenith Bank is trying to solve for this year.

Maria Chen: Sure. I'm Maria Chen, VP of Digital Banking here at Zenith Bank.
Our biggest issue right now is onboarding drop-off — we're seeing about 38% of
applicants abandon the flow before completing KYC.

Alex Rivera: That's a significant number. Can you tell me more about where in
the flow people are dropping off?

Maria Chen: Mostly at the document upload step. If you want to follow up with
me directly, my email is jt.moreno@meridianadvisors.example.com, or you can
reach me at (212) 555-0148.

David Cole: I'm David Cole, Head of Operations. From my side, the call center
is drowning in password reset and account lookup requests. Last month we
logged over 4,200 calls just for account status checks.

Alex Rivera: Do you have a specific case you can point to?

David Cole: Sure — last week we had an escalation on Account #4471982 where
the member couldn't verify identity over the phone and had to be routed to a
branch. We also flagged Member ID: 8823410 as a repeat caller, six times in
two months.

Priya Rao: We logged a related case too — Account #44719825 — a different
member, but it hit the exact same identity-verification wall during a
callback attempt.

Priya Rao: I'm Priya Rao, I lead Data & Analytics. One thing worth noting —
for compliance testing we use a synthetic customer record with SSN
512-34-6789 to validate the KYC pipeline end to end. It's a test fixture, not
a live customer, but it flows through the same systems.

Alex Rivera: Understood, we'll treat that the same as any other PII in our
notes. David, you mentioned reachability — what's the best way to loop you in?

David Cole: You can email me at dataops@fieldpartner.example.net, or call the
operations line directly at 415-555-0173.

Alex Rivera: Got it. And Priya, if I need to follow up on the analytics side?

Priya Rao: Use support.desk@vendorhub.example.org for anything
analytics-related — that inbox is monitored by my team.

Maria Chen: One more thing — if you want to see what the current experience
looks like, the staging environment is at
https://portal.zenithbank.example.com/login. I can get you a test account.

Alex Rivera: Perfect, that helps a lot. So just to confirm the pattern here —
this is a Zenith problem across the whole onboarding and servicing chain, not
isolated to one channel?

Maria Chen: Correct. At Zenith, we've tried a couple of point fixes over the
past year, but nothing has moved the needle on the abandonment rate.

David Cole: Agreed. Operationally, Zenith is still routing too much through
the call center for things that should be self-service.

Priya Rao: And from a data standpoint, we don't have a single view of the
customer across servicing and onboarding — that's part of why the numbers are
hard to pin down precisely.

Alex Rivera: This is really useful context. Let me also confirm — if I need to
reach Maria again for a follow-up, is jt.moreno@meridianadvisors.example.com
still the best address?

Maria Chen: Yes, that one works, or the phone number I gave earlier.

Alex Rivera: Great, I have everything I need for this session. We'll compile
these findings and come back with a capability assessment for Zenith Bank next
week.

Maria Chen: Sounds good, thank you.

David Cole: Thanks, talk soon.

Priya Rao: Appreciate the time.
