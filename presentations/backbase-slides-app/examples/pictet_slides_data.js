/* Pictet × Backbase — QBR deck, 25 June 2026  (v2 — RE-SPINED 2026-06-12)
   Frontline 2026 Slide Engine. Strategy: ENGAGEMENT_CONTEXT.md §9 (reframe) + Oum v0 harvest.
   THESIS: the real ceiling is that Backbase is a view-only app → the prize is doing MORE,
   not just a cheaper upgrade. The upgrade follows the ambition. Economics adopted from Oum v0.
   Guardrail: depth + activate-licensed + advisor efficiency, anchored in THEIR strategy. No client robo/AI.
   Sources labelled inline. No fabricated Pictet ROI — benchmarks flagged; "sized in Ignite". */

const NAVY='#041326', BLUE='#3367FF', CYAN='#69FEFF', RED='#FF503C',
      LBLUE='#E5EBFF', OFF='#F3F6F9', GREEN='#2ECC71', MUTE='#6B7786', BORD='#CED2D7';

const SLIDES = [

  /* ── 0. OPEN ── */
  { layout:'cover-color-block', label:'QUARTERLY BUSINESS REVIEW · GENEVA',
    title:'Pictet ×\nBackbase', date:'Five years, and the next five · 25 June 2026', partner:true },

  { layout:'toc', label:'AGENDA', title:'Six movements', numbered:true, items:[
    'Five years, reviewed — honestly',
    'The ceiling we’ve hit — one channel, view-only',
    'What staying here costs — the economics',
    'Doing more, on one platform — the ambition',
    'The path & the commitment — Ignite and renewal',
    'The horizon — Wealth 2.0 and Banking OS, at your pace'
  ]},

  /* ════ 01 · FIVE YEARS, REVIEWED ════ */
  { layout:'chapter-numbered', theme:'navy', number:'01', label:'WHERE WE STAND',
    title:'Five years,\nreviewed', subtitle:'Live, used, delivering — and one hard chapter we own.' },

  { layout:'overview-stats', label:'THE PARTNERSHIP TODAY', title:'Not a shelf-ware deployment',
    subtitle:'Chosen over Temenos and Avaloq in 2021. Today the digital front door for Pictet private-banking clients worldwide and Swiss staff of the Bank — a private-banking app in daily use across four regulatory geographies.',
    stats:[
      { value:'2021', label:'Live partnership since' },
      { value:'~15k', label:'Active users · and counting' },
      { value:'4', label:'Geographies · CH·EU·Nassau·Asia' },
      { value:'€1.19M', label:'Software ARR · Tier 1' }
    ]},

  { layout:'content-standard', theme:'light', label:'WHAT’S WORKING', title:'You raised a need — the platform, and the team, responded',
    subtitle:'Recent wins came from listening to Swiss clients and staff, and shipping fast.',
    body:`<div style="display:flex;gap:0.5em;margin-top:0.1em">
      ${[['SwissQR Bill','Shipped <b>ahead of schedule</b> after Swiss client &amp; staff feedback.',OFF],
         ['Internal transfers','Fast-tracked to <b>avoid SWIFT / SIC cost</b>. Live and used.',OFF],
         ['Through the cyber issue','Daily support Nov–Dec ’25 — partnership that lifted satisfaction.',OFF],
         ['The reset','Local Geneva presence (Piotr) steadied the relationship.',LBLUE]
        ].map(c=>`<div style="flex:1;background:${c[2]};border-radius:0.3em;padding:0.7em 0.8em">
        <div style="font-size:0.6em;font-weight:700;color:${BLUE};text-transform:uppercase;letter-spacing:0.05em">${c[0]}</div>
        <div style="font-size:0.58em;font-weight:300;color:${NAVY};line-height:1.5;margin-top:0.35em">${c[1]}</div></div>`).join('')}
    </div>
    <div style="background:${OFF};border-radius:0.3em;padding:0.6em 0.9em;margin-top:0.7em">
      <span style="font-size:0.55em;font-weight:700;color:${NAVY}">Cost already avoided.</span>
      <span style="font-size:0.55em;font-weight:300;color:${NAVY}"> Internal transfers replace interbank routing — <b>$15–50 saved per transaction</b> otherwise sent via SWIFT. × your volume = annual fees avoided; we’d size it in Ignite. <span style="color:${MUTE}">(Industry, 2026)</span></span>
    </div>` },

  { layout:'statement', accent:'red', label:'THE PART WE OWN',
    text:'The 2024.03 upgrade ran <span class="hl">12 months instead of three</span>, over budget, with development frozen. It cannot happen again — and the rest of today is the <span class="hl">mechanism</span> that makes sure it doesn’t, not a promise on trust.' },

  /* ════ 02 · THE CEILING ════ */
  { layout:'chapter-numbered', theme:'blue', number:'02', label:'THE CEILING WE’VE HIT',
    title:'One channel,\nview-only', subtitle:'The honest reason the next upgrade feels hard to justify — and the real opportunity hiding behind it.' },

  { layout:'content-standard', theme:'light', label:'WHERE BACKBASE SITS TODAY', title:'A window, not yet a workplace',
    subtitle:'Pictet uses Backbase for one thing: a mobile app that is almost entirely view-only. That is a narrow base — and it is why an upgrade can look like cost without reward.',
    body:`<div style="display:flex;gap:0.6em;align-items:stretch;margin-top:0.1em">
      <div style="flex:1;background:${OFF};border-left:3px solid ${MUTE};border-radius:0.2em;padding:0.75em 0.95em">
        <div style="font-size:0.58em;font-weight:700;color:${MUTE};text-transform:uppercase;letter-spacing:0.05em">Today — view & inform</div>
        <ul style="font-size:0.58em;font-weight:300;color:${NAVY};line-height:1.7;margin:0.4em 0 0 1em;padding:0">
          <li>See portfolios, statements, documents</li>
          <li>Payments (the one transactional step — added 2025)</li>
          <li>Notifications &amp; secure messaging</li>
        </ul>
      </div>
      <div style="flex:1.1;background:${LBLUE};border-left:3px solid ${BLUE};border-radius:0.2em;padding:0.75em 0.95em">
        <div style="font-size:0.58em;font-weight:700;color:${BLUE};text-transform:uppercase;letter-spacing:0.05em">Not yet — act, serve, advise</div>
        <ul style="font-size:0.58em;font-weight:300;color:${NAVY};line-height:1.7;margin:0.4em 0 0 1em;padding:0">
          <li><b>Servicing</b> — the requests handled by phone &amp; email today</li>
          <li><b>Advice journeys</b> — proposals, suitability, RM-led</li>
          <li><b>The advisor</b> — no employee workspace</li>
        </ul>
      </div>
    </div>` },

  { layout:'statement', accent:'blue', label:'THE PIVOT',
    text:'A cheaper, safer upgrade of a view-only app is <span class="hl">still a view-only app</span>. The question worth answering together isn’t “how do we upgrade” — it’s <span class="hl">“what could Pictet do with this platform that it doesn’t today.”</span>' },

  /* ════ 03 · WHAT STAYING HERE COSTS ════ */
  { layout:'chapter-numbered', theme:'navy', number:'03', label:'THE ECONOMICS',
    title:'What staying\nhere costs', subtitle:'The run-cost you can’t see — structural, and reversible.' },

  { layout:'content-standard', theme:'light', label:'THE RUN-COST YOU CAN’T SEE', title:'Pictet sits at the worst end of every curve — by design',
    subtitle:'Not a platform problem — a consequence of heavy customisation and on-premise choices.',
    body:`<div style="display:flex;gap:0.5em;margin-top:0.1em">
      ${[['~11%','of bank IT budget reaches innovation','≈67% keeps systems alive · Gartner 2024',OFF],
         ['70–90%','of TCO is maintenance','for complex on-prem (vs 30–60% platform/cloud) · ScienceSoft/IEEE',OFF],
         ['4×','app variants maintained separately','on-prem · 82% of journeys customised',LBLUE]
        ].map(c=>`<div style="flex:1;background:${c[3]};border-radius:0.3em;padding:0.85em 0.9em">
        <div style="font-size:1.25em;font-weight:800;color:${c[3]===LBLUE?BLUE:NAVY}">${c[0]}</div>
        <div style="font-size:0.58em;font-weight:600;color:${NAVY};line-height:1.4;margin-top:0.25em">${c[1]}</div>
        <div style="font-size:0.5em;font-weight:300;color:${MUTE};margin-top:0.35em">${c[2]}</div></div>`).join('')}
    </div>
    <div style="background:${NAVY};border-radius:0.3em;padding:0.6em 0.9em;margin-top:0.7em">
      <span style="font-size:0.56em;font-weight:300;color:#fff">Every euro maintaining custom-built parity features is run-cost that <span style="color:${CYAN};font-weight:700">no longer needs to exist</span>.</span>
    </div>` },

  { layout:'content-standard', theme:'light', label:'RUN → CHANGE', title:'The same spend, redeployed to your roadmap',
    subtitle:'Returning parity features to product shrinks the customisation surface — the real driver of upgrade pain — and frees capacity. Redeploy, not reduce.',
    body:`<div style="display:flex;gap:0.6em;align-items:stretch;margin-top:0.1em">
      <div style="flex:1;background:${OFF};border-radius:0.3em;padding:0.75em 0.9em">
        <div style="font-size:0.58em;font-weight:700;color:${RED};text-transform:uppercase;letter-spacing:0.05em">Today — run-heavy</div>
        <ul style="font-size:0.57em;font-weight:300;color:${NAVY};line-height:1.65;margin:0.4em 0 0 1em;padding:0">
          <li>Maintenance runs 2–4× build over a lifecycle</li>
          <li>Four custom flavours = up to 4× the change surface</li>
          <li>15 of 21 custom back-end services are integration shims</li>
        </ul>
      </div>
      <div style="flex:1.1;background:${LBLUE};border-radius:0.3em;padding:0.75em 0.9em">
        <div style="font-size:0.58em;font-weight:700;color:${BLUE};text-transform:uppercase;letter-spacing:0.05em">Returning to product</div>
        <ul style="font-size:0.57em;font-weight:300;color:${NAVY};line-height:1.65;margin:0.4em 0 0 1em;padding:0">
          <li>Move shims to product → smaller surface, easier upgrade</li>
          <li>Freed capacity → advisor differentiation, not removed</li>
          <li>Run:change shifts toward the <b>50:50</b> top-decile</li>
        </ul>
      </div>
    </div>
    <div style="font-size:0.5em;font-weight:300;color:${MUTE};margin-top:0.55em">Typical bank run:change ≈ 60:40; top-decile ≈ 50:50. Pictet’s start point = the joint gap analysis. <span style="color:${BORD}">McKinsey 2024</span></div>` },

  { layout:'content-standard', theme:'light', label:'CUSTOM → PRODUCT', title:'Your customisation surface — and what returns cleanly',
    body:`<table style="width:100%;border-collapse:collapse;font-weight:300;margin-top:0.1em">
      <tr style="text-align:left">${['Component','Why you built it (2022)','What product does now','Move'].map(h=>`<th style="font-size:0.5em;font-weight:700;color:${MUTE};text-transform:uppercase;letter-spacing:0.05em;padding:0.3em 0.5em;border-bottom:1px solid ${BORD}">${h}</th>`).join('')}</tr>
      ${[
        ['Integration shims (15 of 21)','No standard connectors then','Standardised connectors to Avaloq XPI, portfolio, payments','<b style="color:'+BLUE+'">Retire to product</b>'],
        ['In-house secure chat','Couldn’t route to a named advisor','Secure Messaging — advisor-specific, OOTB','<b style="color:'+BLUE+'">Retire to product</b>'],
        ['SwissSign e-signature','Cloud was a no-go in 2022','In-platform e-sign — or keep SwissSign via integration','<b style="color:'+NAVY+'">Your choice</b>'],
        ['Front-end “Pictet Touch”','No config theming back then','Experience Manager — brand by config, not code','<b style="color:'+BLUE+'">Biggest lever</b>']
      ].map(r=>`<tr>${r.map((c,i)=>`<td style="font-size:${i===0?'0.55em':'0.53em'};color:${i===0?NAVY:(i===1?MUTE:NAVY)};font-weight:${i===0?'600':'300'};padding:0.4em 0.5em;border-bottom:1px solid ${OFF}">${c}</td>`).join('')}</tr>`).join('')}
    </table>
    <div style="font-size:0.5em;font-weight:300;color:${MUTE};margin-top:0.5em">We don’t rip out what works. Each row is a choice — and 82% of journeys carry customisation the next upgrade must otherwise re-test and carry. <span style="color:${BORD}">Source: your component list</span></div>` },

  /* ════ 04 · DOING MORE, ON ONE PLATFORM ════ */
  { layout:'chapter-numbered', theme:'blue', number:'04', label:'THE AMBITION',
    title:'Doing more,\non one platform', subtitle:'You already crossed this line once — with payments. Here’s what the rest looks like.' },

  { layout:'content-standard', theme:'light', label:'FROM VIEW-ONLY TO A FULL RELATIONSHIP', title:'The line you already crossed — and the road beyond it',
    subtitle:'Payments took the app from view-only to transactional in 2025 — and it worked. The same move, into servicing and advice, is where the platform earns its place.',
    body:`<div style="display:flex;align-items:stretch;gap:0.4em;margin-top:0.2em">
      ${[['View','Portfolios · statements · documents','done',MUTE],
         ['Transact','Payments · SwissQR · transfers','done · 2025',GREEN],
         ['Serve','Requests, change-of-circumstance, documents — digital, not phone/email','next',BLUE],
         ['Advise','RM-led proposals · suitability · e-sign','next',BLUE]
        ].map((c,i)=>`<div style="flex:1;background:${i<2?OFF:LBLUE};border-radius:0.3em;padding:0.7em 0.75em;position:relative">
        <div style="font-size:0.5em;font-weight:700;color:${c[3]};text-transform:uppercase;letter-spacing:0.06em">${c[2]}</div>
        <div style="font-size:0.7em;font-weight:800;color:${NAVY};margin-top:0.2em">${c[0]}</div>
        <div style="font-size:0.5em;font-weight:300;color:${NAVY};line-height:1.4;margin-top:0.3em">${c[1]}</div></div>${i<3?`<div style="display:flex;align-items:center;font-size:0.9em;color:${MUTE}">→</div>`:''}`).join('')}
    </div>
    <div style="font-size:0.54em;font-weight:300;color:${NAVY};line-height:1.55;margin-top:0.7em">Each step is <b>depth in the channel you already have</b> — advisory-led, never self-directed. The point isn’t more apps; it’s that Backbase becomes the place work happens, not just where balances are viewed.</div>` },

  { layout:'content-standard', theme:'light', label:'BEFORE YOU BUY ANYTHING', title:'Some of “more” is already yours — switch it on first',
    subtitle:'A surprising amount of capability is licensed but never deployed. Step one of doing more isn’t a purchase — it’s activation.',
    body:`<div style="display:flex;gap:0.5em;align-items:stretch;margin-top:0.1em">
      ${[['Licensed · dormant','Capability you already pay for, not yet switched on','#fff',MUTE,'Activate — no new licence'],
         ['Activate','Turn on servicing, messaging, journeys you own','— '],
         ['Net-new','The genuine expansion — onboarding, advisor cockpit, advice','— ']
        ].map((c,i)=>`<div style="flex:1;background:${i===0?OFF:(i===1?LBLUE:'#fff')};border:1px solid ${i===2?BORD:'transparent'};border-radius:0.3em;padding:0.8em 0.85em">
        <div style="font-size:0.55em;font-weight:700;color:${i===1?BLUE:(i===2?NAVY:MUTE)};text-transform:uppercase;letter-spacing:0.05em">${c[0]}</div>
        <div style="font-size:0.56em;font-weight:300;color:${NAVY};line-height:1.5;margin-top:0.4em">${c[1]}</div></div>${i<2?`<div style="display:flex;align-items:center;font-size:0.9em;color:${MUTE}">→</div>`:''}`).join('')}
    </div>
    <div style="background:${NAVY};border-radius:0.3em;padding:0.55em 0.9em;margin-top:0.6em">
      <span style="font-size:0.54em;font-weight:700;color:${CYAN}">Lowest-friction first.</span>
      <span style="font-size:0.54em;font-weight:300;color:#fff"> Ignite produces the licensed-vs-deployed map — so “doing more” starts with value you’ve already bought, then the net-new. <span style="color:rgba(255,255,255,.6)">(Entitlement to be confirmed with the account team.)</span></span>
    </div>` },

  { layout:'content-standard', theme:'light', label:'ONE PLATFORM · EVERY CLIENT', title:'Configured by segment — not rebuilt, and not only the 50M+',
    subtitle:'The same component library renders a segment-appropriate experience for rising, core, family-office and alternatives clients — and an advisor cockpit. See the live prototype.',
    body:`<div style="display:flex;gap:0.45em;margin-top:0.1em">
      ${[['Rising / Next-gen','Mobile-first, guided'],['Core HNW','Full hybrid'],['UHNW / Family','Entities &amp; proxies'],['Alternatives','Calls &amp; illiquids'],['RM Cockpit','Admin → advice']
        ].map((c,i)=>`<div style="flex:1;background:${i===4?LBLUE:OFF};border-radius:0.3em;padding:0.65em 0.6em;text-align:center">
        <div style="font-size:0.55em;font-weight:700;color:${i===4?BLUE:NAVY}">${c[0]}</div>
        <div style="font-size:0.48em;font-weight:300;color:${MUTE};margin-top:0.25em">${c[1]}</div></div>`).join('')}
    </div>
    <div style="font-size:0.54em;font-weight:300;color:${NAVY};line-height:1.55;margin-top:0.7em">One library, configured five ways — the “Pictet Touch” lives in <b>configuration, not code</b>, so brand and segment differentiation survive every release. The RM cockpit is optional, employee-side efficiency — whether it fits Pictet is a question for Ignite.</div>
    <a href="prototype/" target="_blank" style="display:inline-block;margin-top:0.55em;background:${BLUE};color:#fff;text-decoration:none;border-radius:0.45em;padding:0.45em 1em;font-size:0.5em;font-weight:700;letter-spacing:0.02em">▶&nbsp;&nbsp;Open the live prototype&nbsp;&nbsp;→</a>` },

  /* ════ 05 · THE PATH & THE COMMITMENT ════ */
  { layout:'chapter-numbered', theme:'navy', number:'05', label:'THE PATH & THE COMMITMENT',
    title:'How we get there —\nand what we ask', subtitle:'Your 2026 priorities already fit. The next step is small, joint and funded.' },

  { layout:'content-columns', label:'YOUR 2026 PRIORITIES — ALREADY IN PRODUCT', title:'We heard them; here’s where each already lives',
    columns:[
      { subtitle:'Harmonisation', body:'Even out the end-user experience — payments &amp; e-sign — across CH · EU · Nassau · Asia (PSD2 AISP/PISP, instant). Multi-region journeys are standard in product.' },
      { subtitle:'Complex accounts', body:'Multiple signatories, e-callback, permissioning for legal entities &amp; proxies — the Entitlements engine’s core job.' },
      { subtitle:'Onboarding & channels', body:'Digital onboarding, e-IDV, secure document upload, qualified signature — product today, and a natural new footprint.' }
    ]},

  { layout:'content-standard', theme:'light', label:'STEP 1 · THE IGNITE WORKSHOP', title:'The Ignite Workshop — a joint gap analysis, funded this summer',
    subtitle:'1–2 days onsite, Value Consulting with your COO PWM team. The missing data becomes the workshop’s first deliverable — not a gap, a starting point. Co-design, not a pitch.',
    body:`<div style="display:flex;gap:0.5em;margin-top:0.1em">
      ${[['1 · Map the surface','Classify every custom component together: keep, standardise, or retire to product.'],
         ['2 · Size the prize','Turn the run-cost estimate into your real number — capacity and value, not guesswork.'],
         ['3 · De-risk the upgrade','A documented readiness plan — so Wealth 2.0 is a planned project, not another exhausting upgrade with feature delivery frozen.']
        ].map(c=>`<div style="flex:1;background:${OFF};border-radius:0.3em;padding:0.75em 0.85em">
        <div style="font-size:0.58em;font-weight:700;color:${BLUE}">${c[0]}</div>
        <div style="font-size:0.55em;font-weight:300;color:${NAVY};line-height:1.5;margin-top:0.35em">${c[1]}</div></div>`).join('')}
    </div>
    <div style="background:${NAVY};border-radius:0.3em;padding:0.55em 0.9em;margin-top:0.6em">
      <span style="font-size:0.54em;font-weight:700;color:${CYAN}">Backbase-funded · a workshop, not a procurement event.</span>
      <span style="font-size:0.54em;font-weight:300;color:#fff"> It honours what you built, makes the cost visible on your terms, and turns the next upgrade into a planned, jointly-owned project.</span>
    </div>` },

  { layout:'content-standard', theme:'light', label:'RENEWAL · HOLD OR COMMIT', title:'Your choice, de-risked',
    subtitle:'Renewal 7 Dec 2026; supported to at least 31 Mar 2027. One way to hold, two depths of partnership — every commit path is Backbase-led, never self-run.',
    body:`<div style="display:flex;gap:0.5em;margin-top:0.1em;align-items:stretch">
      <div style="flex:1;background:${OFF};border:1px solid ${BORD};border-radius:0.3em;padding:0.7em 0.8em;display:flex;flex-direction:column">
        <div style="font-size:0.5em;font-weight:700;color:${MUTE};text-transform:uppercase">Stay</div>
        <div style="font-size:0.6em;font-weight:600;color:${NAVY};margin-top:0.2em">Tacit renewal + extended LTS</div>
        <div style="font-size:0.5em;font-weight:300;color:${NAVY};line-height:1.5;margin-top:0.35em;flex:1">Roll the 12-month renewal and stay on 2024.03 with extended support (fees beyond 2027). Stability you control — but the custom stays your liability, and no new value.</div>
        <div style="font-size:0.5em;font-weight:700;color:${RED};margin-top:0.5em;padding-top:0.4em;border-top:1px solid ${BORD}">Led by: you — alone</div>
      </div>
      <div style="flex:1;background:${LBLUE};border:1px solid rgba(51,103,255,.25);border-radius:0.3em;padding:0.7em 0.8em;display:flex;flex-direction:column">
        <div style="font-size:0.5em;font-weight:700;color:${BLUE};text-transform:uppercase">Wealth 2.0 · 3-year</div>
        <div style="font-size:0.6em;font-weight:600;color:${NAVY};margin-top:0.2em">Partnership</div>
        <div style="font-size:0.5em;font-weight:300;color:${NAVY};line-height:1.5;margin-top:0.35em;flex:1">Backbase-led &amp; funded — Ignite, AI upgrade agents, on-prem, references, upgrade credits. Unlocks the run→change reallocation and doing more.</div>
        <div style="font-size:0.5em;font-weight:700;color:${BLUE};margin-top:0.5em;padding-top:0.4em;border-top:1px solid rgba(51,103,255,.25)">Led by: Backbase</div>
      </div>
      <div style="flex:1.06;background:${LBLUE};border:1.5px solid ${BLUE};border-radius:0.3em;padding:0.7em 0.8em;display:flex;flex-direction:column;position:relative">
        <div style="position:absolute;top:-0.55em;right:0.6em;background:${BLUE};color:#fff;font-size:0.4em;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;padding:0.3em 0.6em;border-radius:0.6em">Recommended</div>
        <div style="font-size:0.5em;font-weight:700;color:${BLUE};text-transform:uppercase">Wealth 2.0 · 5-year</div>
        <div style="font-size:0.6em;font-weight:700;color:${NAVY};margin-top:0.2em">Partnership — best economics</div>
        <div style="font-size:0.5em;font-weight:300;color:${NAVY};line-height:1.5;margin-top:0.35em;flex:1">Everything in the 3-year, plus deeper investment, upgrade credits and locked economics for the longer commitment.</div>
        <div style="font-size:0.5em;font-weight:700;color:${BLUE};margin-top:0.5em;padding-top:0.4em;border-top:1px solid rgba(51,103,255,.3)">Led by: Backbase — your pace</div>
      </div>
    </div>
    <div style="font-size:0.5em;font-weight:300;color:${MUTE};margin-top:0.55em">Our ask: a multi-year renewal — 3 years minimum, ideally 5 — with Backbase investment behind the upgrade. Reference-backed (Danske live).</div>` },

  /* ════ 06 · THE HORIZON ════ */
  { layout:'content-standard', theme:'dark', label:'THE HORIZON · AT YOUR PACE', title:'Where the platform is going',
    subtitle:'Not a decision for today — context for the multi-year conversation.',
    body:`<div style="display:flex;gap:0.6em;margin-top:0.2em">
      <div style="flex:1;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.12);border-radius:0.3em;padding:0.8em 0.9em">
        <div style="font-size:0.62em;font-weight:700;color:${CYAN}">Wealth 2.0</div>
        <ul style="font-size:0.55em;font-weight:300;color:rgba(255,255,255,.85);line-height:1.65;margin:0.4em 0 0 1em;padding:0">
          <li>Standardises today’s integration shims — the enabler of run→change</li>
          <li>Advisor cockpit &amp; richer client journeys</li>
          <li>On-premise <b>or</b> Azure CH — your deployment choice</li>
          <li>You won’t be first mover — Danske live, and further wealth references maturing in the UK</li>
        </ul>
      </div>
      <div style="flex:1;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.12);border-radius:0.3em;padding:0.8em 0.9em">
        <div style="font-size:0.62em;font-weight:700;color:#fff">Banking OS</div>
        <div style="font-size:0.55em;font-weight:300;color:rgba(255,255,255,.85);line-height:1.6;margin-top:0.4em">The longer arc: one platform across onboarding, e-banking, advisor tooling and AI — modular, adopted only when it solves a Pictet pain point. <b style="color:#fff">Digital onboarding</b> is the one piece already on your 2026 list — the natural first step, when you’re ready.</div>
      </div>
    </div>` },

  { layout:'content-columns', label:'WHERE WE GO FROM HERE', title:'Three things, before the renewal',
    columns:[
      { subtitle:'1 · Book Ignite this summer', body:'1–2 days, joint, Value Consulting + COO PWM. The missing data becomes our first deliverable.' },
      { subtitle:'2 · Size the reallocation', body:'Turn the customisation surface into your real run-cost number — and the value of doing more.' },
      { subtitle:'3 · Open the renewal', body:'Signal appetite for a multi-year commitment — to land at London in the autumn.' }
    ]},

  { layout:'thank-you' }
];

const SPEAKER_NOTES = {
  1: 'Set tone in 20 seconds: a partner reviewing five years honestly, and opening a bigger conversation than “upgrade”. The subtitle — five years, and the next five — signals ambition, not maintenance.',
  2: 'Walk the six movements. Flag the shift: we earn the right with honesty (01–02), make the cost visible (03), then open the ambition (04) before we ever ask for anything (05–06).',
  3: 'Open generously. Five years, live, daily use. This is the foundation we build ON, not a problem to apologise for.',
  4: 'Credit: chosen over Temenos & Avaloq, ~13k users, four geographies, 15+ capabilities live. Frame as a real, working footprint — sets up “but it’s narrow” next.',
  5: 'These are THEIR wins. Land the cost-avoided line on internal transfers as the FIRST taste of “doing more pays” — we’ll quantify in Ignite. Don’t over-claim; it’s benchmark × their volume.',
  6: 'Say the 12-months line slowly, own it. Then pivot hard to the mechanism: the upgrade was hard BECAUSE of accumulated customisation — reduce it and the next one is structurally easier. This is the bridge to the economics.',
  7: 'The pivot chapter. This is Piotr’s insight made into strategy — say it plainly and without blame.',
  8: 'The honest reframe: Backbase is a window, not yet a workplace. View-only is why an upgrade looks like cost without reward. Note payments is the ONE transactional step they already took — foreshadow the ambition act.',
  9: 'The single most important line of the day: a cheaper upgrade of a view-only app is still view-only. Reframe the whole conversation from “how to upgrade” to “what to do with the platform.” Pause here.',
  10: 'Transition to economics — this is where Oum’s rigour lands. Keep it factual, sourced, non-accusatory.',
  11: 'Benchmarks, clearly sourced (Gartner, ScienceSoft/IEEE). The controlling insight: high run-cost traces to customisation + on-prem, NOT the platform. Every euro on custom parity is run-cost that needn’t exist.',
  12: 'Run→change is the money frame for a COO (Gallaird). “Redeploy, not reduce” — freed capacity goes to advisor differentiation. 60:40 → 50:50 is McKinsey, not a Pictet promise.',
  13: 'From their own component list: 82% of journeys customised, 15 of 21 backend services are integration shims — exactly the layer newer product standardises. This makes “return to product” concrete, not abstract.',
  14: '(Chapter — the ambition act.) Energy lifts: the honest case is made, now the prize. We move from cost to possibility.',
  15: 'Payments proved view→transact works — and they loved it. Serve and Advise are the next steps. Emphasise DEPTH in the channel they already have, advisory-led — not new apps, not client robo/AI.',
  16: 'The shelfware move — disarms the “vendor upsell” reflex. Step one is “use what you already pay for.” Be honest the licensed-vs-deployed map is an Ignite deliverable (confirm entitlement with Ernst/Piotr).',
  17: 'Point to the live prototype. Lead with “configure, don’t rebuild” + segments beyond 50M+. RM cockpit = optional, employee-side efficiency, never a footprint push (they have Pictet Connect — respect it).',
  18: '(Chapter.) Transition to the ask — small, joint, funded. Their priorities already fit product; we’re not inventing an agenda.',
  19: 'Their own three priorities, mapped to product. Onboarding flagged as the natural new footprint — plants the expansion seed gently.',
  20: 'Ignite = the low-commitment yes: Map / Size / De-risk. Backbase-funded, a workshop not procurement. The one thing we most want to leave with.',
  21: 'Hold or commit. ONE "Stay" (tacit + extended LTS, merged) stated respectfully, not a threat. Then two partnership depths — 3-year and 5-year — BOTH Backbase-led & funded. Deliberately NO "self-led upgrade" option: a Pictet-run re-platform isn’t a realistic setup for success (their only bank-led delivery, the 2024.03 upgrade, ran 12 months over budget) — so we don’t offer a path we know fails; we use that fact as the reason the commit paths are Backbase-led. 5-year badged best-value; 3-year is the floor (one-line change if Piotr prefers 3-yr badged). Reference = Danske live.',
  22: 'Horizon, at their pace. Wealth 2.0 = enabler of run→change; on-prem OR Azure CH (cloud is now on the table). Banking OS = longer modular arc, only-when-it-solves-a-pain. Onboarding = the bridge.',
  23: 'Close on three asks. Biggest yes today = Book Ignite + a renewal direction. Confirm owner + a date before London (29 Sep–1 Oct).',
  24: 'Thank them. Reaffirm the tone: a partner opening the next five years, not a vendor selling an upgrade.'
};
