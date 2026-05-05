import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowRight, Clock, AlertTriangle, CheckCircle2, TrendingUp, Zap, Target, BookOpen, ChevronRight, Plus, Brain, MessageSquare, FileText } from 'lucide-react';
import { deals, STAGE_CONFIG } from '../data/mockData';

interface CortexInsight {
  dealId: string;
  client: string;
  journeyStage: 'why_change' | 'why_now' | 'why_invest' | 'why_stay';
  headline: string;
  recommendation: string;
  workshopPlan: string[];
  graphEvidence: string;
  urgency: 'act_now' | 'this_week' | 'on_track';
  nextAction: string;
  nextActionRoute: string;
  similarWins: number;
  winRate: string;
  warning?: string;
}

const cortexInsights: CortexInsight[] = [
  {
    dealId: 'd2',
    client: 'SchoolsFirst FCU',
    journeyStage: 'why_change',
    headline: 'Client doesn\'t see the activation gap yet',
    recommendation: 'Start with Capability Assessment workshop — it creates the "mirror moment." SchoolsFirst has a 9-month activation dip they\'re not measuring. Show them the gap before proposing solutions.',
    workshopPlan: ['Capability Assessment', 'Customer Experience Deep Dive', 'Architecture Review'],
    graphEvidence: '5 similar CUs ($20-35B, retail) all had unmeasured activation gaps. 4 of 5 expanded scope after the capability mirror moment.',
    urgency: 'this_week',
    nextAction: 'Generate Capability Assessment workshop kit',
    nextActionRoute: '/scope',
    similarWins: 5,
    winRate: '80%',
    warning: 'Innovation Day is Apr 15 — workshop kits needed by Apr 10',
  },
  {
    dealId: 'd3',
    client: 'Allied Irish Banks',
    journeyStage: 'why_now',
    headline: 'They know they need to change — create the urgency',
    recommendation: 'Discovery sessions 1-3 revealed channel fragmentation and legacy pain. The CTO is the champion but the CFO hasn\'t seen the numbers. Run a CX Deep Dive to quantify the friction, then an Architecture session to show technical debt compounding.',
    workshopPlan: ['CX Deep Dive', 'Architecture & Technology', 'Use Case Validation', 'Executive Readout'],
    graphEvidence: '2 past EMEA retail banks on Temenos had integration pain in month 4. Both wished they\'d flagged architecture constraints earlier.',
    urgency: 'act_now',
    nextAction: 'Technology deep dive is Apr 4 — kit not generated yet',
    nextActionRoute: '/scope',
    similarWins: 7,
    winRate: '71%',
    warning: 'Temenos T24 integration: 2 past clients had 3× longer than estimated. Probe this in Architecture workshop.',
  },
  {
    dealId: 'd4',
    client: 'Mashreq Bank',
    journeyStage: 'why_invest',
    headline: 'Ready to invest — build the confidence',
    recommendation: 'Capability assessment is drafted. They need a defensible business case. Run Use Case Validation with Art of Possible demos, then Executive Readout structured around per-product ROI (not per-channel — that\'s what works for commercial banking).',
    workshopPlan: ['Use Case Validation + Demos', 'Executive Readout'],
    graphEvidence: '4 similar commercial banks in MEA: per-product ROI structure had 2.1× higher CFO approval rate than per-channel.',
    urgency: 'this_week',
    nextAction: 'Business case review with CFO — prepare ROI scenarios',
    nextActionRoute: '/engine',
    similarWins: 4,
    winRate: '75%',
  },
  {
    dealId: 'd1',
    client: 'Navy Federal CU',
    journeyStage: 'why_invest',
    headline: 'Assessment delivered — closing moment',
    recommendation: 'Full 7-Act assessment + ROI model delivered. Executive readout scheduled Apr 8. The conservative case shows $4.2M NPV. Prepare for the "cost of inaction" question — every quarter they wait costs $380K in activation leakage.',
    workshopPlan: ['Executive Readout'],
    graphEvidence: 'Pentagon FCU closed 3 weeks after readout. BECU expanded scope on the spot when they saw the activation numbers.',
    urgency: 'on_track',
    nextAction: 'Executive readout Apr 8 — review presentation',
    nextActionRoute: '/deal/d1',
    similarWins: 3,
    winRate: '92%',
  },
  {
    dealId: 'd6',
    client: 'DBS Bank',
    journeyStage: 'why_change',
    headline: 'Multi-country adds complexity — align before assessing',
    recommendation: 'This is a Why Change conversation across 3 countries with different priorities. Run Strategic Alignment first at group level, THEN country-specific CX workshops. Do NOT run a single capability assessment — priorities will differ by market.',
    workshopPlan: ['Strategic Alignment (Group)', 'CX Deep Dive — Singapore', 'CX Deep Dive — Hong Kong', 'CX Deep Dive — India', 'Consolidated Architecture', 'Regulatory Workshop'],
    graphEvidence: 'Only 2 multi-country rollouts in the graph. Both: country-specific CX was critical. One skipped regulatory and got burned by data residency in month 4.',
    urgency: 'this_week',
    nextAction: 'Country-specific discovery scoping — generate workshop kits per market',
    nextActionRoute: '/scope',
    similarWins: 2,
    winRate: '50%',
    warning: 'Low sample size (n=2). Add regulatory workshop — previous multi-country deal was blindsided by data residency requirements.',
  },
  {
    dealId: 'd5',
    client: 'Banco Santander Chile',
    journeyStage: 'why_change',
    headline: 'Early stage — build the initial brief',
    recommendation: 'Discovery call scheduled Apr 10. Before the call, generate a Client Market Brief from public data — annual report, competitive positioning, digital maturity signals. This shows preparation and earns trust.',
    workshopPlan: ['(No workshops yet — discovery call first)'],
    graphEvidence: '6 similar LATAM retail banks: deals that opened with a pre-built market brief had 34% shorter discovery-to-proposal cycle.',
    urgency: 'on_track',
    nextAction: 'Auto-generate Client Market Brief from public data',
    nextActionRoute: '/scope',
    similarWins: 6,
    winRate: '67%',
  },
];

const journeyConfig = {
  why_change: { label: 'Why Change?', color: '#E02020', bg: 'bg-red-50', text: 'text-bb-red', border: 'border-red-100', description: 'Destabilize status quo' },
  why_now: { label: 'Why Now?', color: '#D97706', bg: 'bg-amber-50', text: 'text-bb-amber', border: 'border-amber-100', description: 'Create urgency' },
  why_invest: { label: 'Why Invest?', color: '#2ECC71', bg: 'bg-green-50', text: 'text-bb-green', border: 'border-green-100', description: 'Justify the spend' },
  why_stay: { label: 'Why Stay?', color: '#1A5AFF', bg: 'bg-blue-50', text: 'text-bb-blue', border: 'border-blue-100', description: 'Prove & expand value' },
};

const urgencyConfig = {
  act_now: { label: 'Act Now', bg: 'bg-red-50', text: 'text-bb-red', dot: 'bg-bb-red' },
  this_week: { label: 'This Week', bg: 'bg-amber-50', text: 'text-bb-amber', dot: 'bg-bb-amber' },
  on_track: { label: 'On Track', bg: 'bg-green-50', text: 'text-bb-green', dot: 'bg-bb-green' },
};

export default function Pipeline() {
  const navigate = useNavigate();
  const [filter, setFilter] = useState<string | null>(null);

  const filtered = filter
    ? cortexInsights.filter(i => i.journeyStage === filter)
    : cortexInsights;

  return (
    <div className="h-full overflow-y-auto">
      {/* Header */}
      <header className="bg-white border-b border-gray-100 px-8 pt-7 pb-5">
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-bb-blue to-bb-purple flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-bb-dark tracking-tight">Cortex Intelligence</h1>
              <p className="text-sm text-gray-400 mt-0.5">What Cortex knows that Salesforce doesn't</p>
            </div>
          </div>
          <button
            onClick={() => navigate('/scope')}
            className="flex items-center gap-2 px-4 py-2.5 bg-bb-blue text-white rounded-xl text-sm font-semibold hover:bg-blue-600 transition-all shadow-sm shadow-bb-blue/20 hover:shadow-md hover:shadow-bb-blue/30 active:scale-[0.97]"
          >
            <Plus className="w-4 h-4" /> New Engagement
          </button>
        </div>

        {/* Journey stage summary cards */}
        <div className="grid grid-cols-4 gap-3">
          {(Object.entries(journeyConfig) as [keyof typeof journeyConfig, typeof journeyConfig[keyof typeof journeyConfig]][]).map(([key, cfg]) => {
            const count = cortexInsights.filter(i => i.journeyStage === key).length;
            const isActive = filter === key;
            return (
              <button
                key={key}
                onClick={() => setFilter(isActive ? null : key)}
                className={`p-4 rounded-xl border-2 transition-all duration-200 text-left ${
                  isActive
                    ? `${cfg.bg} ${cfg.border} shadow-sm`
                    : 'border-gray-100 bg-white hover:border-gray-200'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: cfg.color }} />
                    <span className={`text-sm font-black ${cfg.text}`}>{cfg.label}</span>
                  </div>
                  <span className="text-2xl font-black text-bb-dark">{count}</span>
                </div>
                <p className="text-[10px] text-gray-400">{cfg.description}</p>
              </button>
            );
          })}
        </div>
      </header>

      {/* Insights Feed */}
      <div className="p-8 max-w-[1100px] mx-auto">
        {/* Proactive alerts */}
        {cortexInsights.filter(i => i.warning && (filter === null || i.journeyStage === filter)).length > 0 && (
          <div className="mb-6">
            <div className="text-xs font-bold text-bb-red uppercase tracking-wide mb-3 flex items-center gap-1.5">
              <AlertTriangle className="w-3.5 h-3.5" /> Attention Required
            </div>
            <div className="grid grid-cols-2 gap-3">
              {cortexInsights
                .filter(i => i.warning && (filter === null || i.journeyStage === filter))
                .map(insight => (
                <div key={insight.dealId + '-warn'} className="bg-red-50/70 border border-red-100 rounded-xl p-4 flex items-start gap-3">
                  <AlertTriangle className="w-4 h-4 text-bb-red shrink-0 mt-0.5" />
                  <div>
                    <div className="text-xs font-bold text-bb-dark">{insight.client}</div>
                    <p className="text-[11px] text-gray-600 mt-0.5">{insight.warning}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Deal Intelligence Cards */}
        <div className="space-y-4">
          {filtered.map((insight, idx) => {
            const deal = deals.find(d => d.id === insight.dealId)!;
            const jCfg = journeyConfig[insight.journeyStage];
            const uCfg = urgencyConfig[insight.urgency];
            const sCfg = STAGE_CONFIG[deal.stage];

            return (
              <div
                key={insight.dealId}
                className="bg-white rounded-2xl border border-gray-100 overflow-hidden hover:shadow-lg hover:shadow-gray-100/80 transition-all duration-300 animate-slide-up"
                style={{ animationDelay: `${idx * 80}ms`, opacity: 0 }}
              >
                {/* Top accent */}
                <div className="h-1" style={{ background: `linear-gradient(90deg, ${jCfg.color}, ${jCfg.color}44)` }} />

                <div className="p-6">
                  {/* Row 1: Client + badges */}
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <div className="flex items-center gap-2.5 mb-1">
                        <h3 className="text-lg font-black text-bb-dark">{insight.client}</h3>
                        <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full ${jCfg.bg} ${jCfg.text}`}>
                          {jCfg.label}
                        </span>
                        <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full ${uCfg.bg} ${uCfg.text} flex items-center gap-1`}>
                          <span className={`w-1.5 h-1.5 rounded-full ${uCfg.dot}`} />
                          {uCfg.label}
                        </span>
                        <span className="text-[10px] font-medium px-2 py-0.5 rounded-full" style={{ backgroundColor: sCfg.bg, color: sCfg.color }}>
                          {sCfg.label}
                        </span>
                      </div>
                      <p className="text-sm text-gray-500">{deal.industry} · {deal.geography} · {deal.assetSize} · <span className="font-bold text-bb-dark">{deal.dealValue}</span></p>
                    </div>
                    <div className="text-right shrink-0">
                      <div className="text-xs text-gray-400">Similar wins</div>
                      <div className="text-xl font-black text-bb-dark">{insight.similarWins} <span className="text-xs font-semibold text-bb-green">({insight.winRate})</span></div>
                    </div>
                  </div>

                  {/* Row 2: Cortex intelligence */}
                  <div className="bg-gray-50/70 rounded-xl p-4 mb-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Sparkles className="w-4 h-4 text-bb-purple" />
                      <span className="text-xs font-bold text-bb-dark">{insight.headline}</span>
                    </div>
                    <p className="text-xs text-gray-600 leading-relaxed">{insight.recommendation}</p>
                  </div>

                  {/* Row 3: Workshop plan + graph evidence */}
                  <div className="grid grid-cols-[1fr_1fr] gap-4 mb-4">
                    {/* Recommended workshops */}
                    <div>
                      <div className="text-[10px] text-gray-400 font-semibold uppercase tracking-wide mb-2 flex items-center gap-1">
                        <Target className="w-3 h-3" /> Recommended Workshop Sequence
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {insight.workshopPlan.map((ws, i) => (
                          <span key={i} className="text-[10px] bg-bb-blue/8 text-bb-blue px-2.5 py-1 rounded-full font-medium flex items-center gap-1">
                            <span className="w-3.5 h-3.5 rounded-full bg-bb-blue/20 text-[8px] font-black flex items-center justify-center">{i + 1}</span>
                            {ws}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Graph evidence */}
                    <div>
                      <div className="text-[10px] text-gray-400 font-semibold uppercase tracking-wide mb-2 flex items-center gap-1">
                        <Brain className="w-3 h-3" /> From the Knowledge Graph
                      </div>
                      <p className="text-[11px] text-gray-500 leading-relaxed italic">"{insight.graphEvidence}"</p>
                    </div>
                  </div>

                  {/* Row 4: Actions */}
                  <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                    <button
                      onClick={() => navigate(insight.nextActionRoute)}
                      className="flex items-center gap-2 px-4 py-2 bg-bb-blue text-white rounded-lg text-xs font-semibold hover:bg-blue-600 transition-all"
                    >
                      <Zap className="w-3.5 h-3.5" />
                      {insight.nextAction}
                    </button>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => navigate(`/deal/${insight.dealId}`)}
                        className="flex items-center gap-1.5 px-3 py-2 text-xs text-gray-500 hover:text-bb-blue font-medium transition-colors"
                      >
                        <FileText className="w-3.5 h-3.5" /> Deal Intel
                      </button>
                      <button
                        onClick={() => navigate('/scope')}
                        className="flex items-center gap-1.5 px-3 py-2 text-xs text-gray-500 hover:text-bb-blue font-medium transition-colors"
                      >
                        <BookOpen className="w-3.5 h-3.5" /> Workshop Kits
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Bottom: Aggregate intelligence */}
        <div className="mt-8 bg-gradient-to-br from-bb-dark to-[#0F2B4F] rounded-2xl p-6 text-white">
          <div className="flex items-center gap-2 mb-4">
            <Brain className="w-5 h-5 text-bb-cyan" />
            <h3 className="font-black">Practice Intelligence</h3>
          </div>
          <div className="grid grid-cols-4 gap-4">
            {[
              { label: 'Active Deals', value: '6', sub: 'Across 4 regions', icon: Target },
              { label: 'Why Change', value: '3', sub: 'Need destabilization workshops', icon: MessageSquare },
              { label: 'Avg Win Rate', value: '68%', sub: '+5% when including business case', icon: TrendingUp },
              { label: 'Knowledge Events', value: '342', sub: 'From 28 past engagements', icon: Brain },
            ].map(item => (
              <div key={item.label} className="bg-white/8 rounded-xl p-4">
                <item.icon className="w-4 h-4 text-bb-cyan mb-2" />
                <div className="text-2xl font-black">{item.value}</div>
                <div className="text-[10px] text-white/50 mt-0.5">{item.label}</div>
                <div className="text-[10px] text-white/30 mt-0.5">{item.sub}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
