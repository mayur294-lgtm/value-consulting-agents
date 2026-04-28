/**
 * BankStakeholderIntelPanel — Sprint 2 surfacing fix
 * ───────────────────────────────────────────────────
 * Promotes the meeting intelligence layer (Sprint 2.2-2.4) to a first-class
 * section on the bank profile, so AEs see attributed stakeholder positions
 * and corroborated patterns WITHOUT having to drill into individual
 * PersonIntelCard slide-outs.
 *
 * Two columns side by side:
 *   • Stakeholder positions — sentiment ladder per (speaker, topic)
 *   • Corroborated patterns — fact↔signal pairings with provenance chips
 *
 * Empty-state: when a bank has no attributed facts yet, surfaces actionable
 * guidance ("log a meeting → run extract-facts") rather than rendering blank.
 */

import { useEffect, useState } from 'react';
import {
  MessageSquare, Link2, Loader2, TrendingUp, TrendingDown, Minus, Sparkles, Activity, ExternalLink,
} from 'lucide-react';
import { getStakeholderDrift, getBankPatterns } from '../../data/api';
import { ProvenanceChip } from '../common/Provenance';

const TOPIC_LABEL = {
  budget: 'Budget', vendors: 'Vendors', timeline: 'Timeline', politics: 'Politics',
  technical: 'Technical', blockers: 'Blockers', other: 'Other',
};

const TREND_META = {
  improving:     { label: 'improving',     Icon: TrendingUp,   tone: 'text-emerald-700 bg-emerald-50 border-emerald-200' },
  deteriorating: { label: 'deteriorating', Icon: TrendingDown, tone: 'text-rose-700 bg-rose-50 border-rose-200' },
  mixed:         { label: 'mixed',         Icon: Activity,     tone: 'text-amber-700 bg-amber-50 border-amber-200' },
  stable:        { label: 'stable',        Icon: Minus,        tone: 'text-slate-700 bg-slate-50 border-slate-200' },
  single_point:  { label: 'new',           Icon: Sparkles,     tone: 'text-blue-700 bg-blue-50 border-blue-200' },
};

const SENTIMENT_DOT = {
  positive: 'bg-emerald-500',
  neutral:  'bg-slate-400',
  mixed:    'bg-amber-500',
  negative: 'bg-rose-500',
};

const PATTERN_TONE = {
  corroborates: 'text-emerald-700 bg-emerald-50 border-emerald-200',
  contradicts:  'text-rose-700 bg-rose-50 border-rose-200',
  evolves:      'text-blue-700 bg-blue-50 border-blue-200',
};

function SentimentLadder({ series }) {
  return (
    <div className="flex items-center gap-1 mt-1">
      {(series || []).map((s, i) => (
        <div key={i} className="flex items-center gap-1">
          <div className="flex flex-col items-center" title={`${s.sentiment} on ${s.meeting_date}\n${s.position}\n\nVerbatim: ${s.evidence_quote}`}>
            <span className={`block w-2 h-2 rounded-full ${SENTIMENT_DOT[s.sentiment] || 'bg-slate-300'}`} />
            <span className="text-[8px] text-slate-400 mt-0.5 leading-none">{String(s.meeting_date).slice(5)}</span>
          </div>
          {i < series.length - 1 && <span className="block w-3 h-px bg-slate-300" />}
        </div>
      ))}
    </div>
  );
}

function DriftCell({ cell }) {
  const meta = TREND_META[cell.trend] || TREND_META.single_point;
  const TrendIcon = meta.Icon;
  const last = cell.series?.[cell.series.length - 1];
  return (
    <div className="p-2 rounded border border-slate-200 bg-white">
      <div className="flex items-center justify-between mb-1 flex-wrap gap-1">
        <div className="flex items-center gap-1.5">
          <span className="text-[10px] font-semibold text-slate-900">{cell.speaker_name}</span>
          {cell.speaker_role && <span className="text-[9px] text-slate-500">· {cell.speaker_role}</span>}
        </div>
        <span className={`inline-flex items-center gap-1 text-[9px] font-bold px-1.5 py-0.5 rounded border ${meta.tone}`}>
          <TrendIcon size={9} /> {TOPIC_LABEL[cell.topic] || cell.topic} · {meta.label}
          {cell.n_facts > 1 && <span className="opacity-70">· n={cell.n_facts}</span>}
        </span>
      </div>
      <SentimentLadder series={cell.series} />
      <div className="text-[10px] text-slate-700 italic leading-snug mt-1" title={last?.evidence_quote || ''}>
        "{last?.position}"
      </div>
    </div>
  );
}

function PatternCard({ p }) {
  const gapText = p.time_gap_days >= 0
    ? `signal ${p.time_gap_days}d AFTER meeting`
    : `signal ${Math.abs(p.time_gap_days)}d BEFORE meeting (reactive)`;
  return (
    <div className="p-2 rounded border border-slate-200 bg-white">
      <div className="flex items-center gap-1.5 mb-1 flex-wrap">
        <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded border ${PATTERN_TONE[p.pattern_type] || 'border-slate-200 bg-slate-50 text-slate-700'}`}>
          {p.pattern_type}
        </span>
        <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-slate-100 text-slate-700">{p.topic}</span>
        <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${
          p.confidence === 'high' ? 'bg-slate-900 text-white'
          : p.confidence === 'medium' ? 'bg-slate-200 text-slate-800'
          : 'bg-slate-100 text-slate-600'}`}>
          {p.confidence}
        </span>
        <span className="text-[9px] text-slate-500">· {gapText}</span>
      </div>
      <div className="text-[11px] text-slate-800 leading-snug mb-1">{p.summary}</div>
      <div className="flex items-center gap-1.5 text-[9px] text-slate-500 flex-wrap">
        <span className="font-semibold">Fact:</span>
        <ProvenanceChip source={{
          source_type: 'meeting_fact',
          source_date: p.fact_meeting_date,
          confidence_tier: p.fact_speaker_name ? 1 : 2,
          source_grade: 'A',
          verifier: 'auto',
          label: `${p.fact_speaker_name || '(unattributed)'} · ${p.topic}`,
          evidence_quote: p.fact_quote,
        }} size="xs" showDate={false} />
        <span>{p.fact_speaker_name || '(unattributed)'} · {String(p.fact_meeting_date || '').slice(0, 10)}</span>
      </div>
      {p.signal_source_url && (
        <div className="flex items-center gap-1.5 text-[9px] text-slate-500 mt-0.5 flex-wrap">
          <span className="font-semibold">Signal:</span>
          <ProvenanceChip source={{
            source_type: 'news',
            source_url: p.signal_source_url,
            source_date: p.signal_detected_at,
            confidence_tier: p.confidence === 'high' ? 1 : 2,
            source_grade: p.signal_grade,
            publisher_name: p.signal_publisher,
            verifier: 'auto',
            label: p.signal_title,
          }} size="xs" showDate={false} />
          <a href={p.signal_source_url} target="_blank" rel="noopener noreferrer"
             className="inline-flex items-center gap-1 text-blue-700 hover:underline">
            <ExternalLink size={8} /> {(p.signal_title || '').slice(0, 70)}…
          </a>
        </div>
      )}
    </div>
  );
}

export default function BankStakeholderIntelPanel({ bankKey }) {
  const [drift, setDrift] = useState([]);
  const [patterns, setPatterns] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!bankKey) return;
    setLoading(true);
    Promise.all([
      getStakeholderDrift(bankKey, { view: 'cells', includeUnattributed: false }).catch(() => ({ data: [] })),
      getBankPatterns(bankKey, { minConfidence: 'medium' }).catch(() => ({ patterns: [] })),
    ])
      .then(([d, p]) => {
        setDrift(d?.data || []);
        setPatterns(p?.patterns || []);
      })
      .finally(() => setLoading(false));
  }, [bankKey]);

  const totalCount = drift.length + patterns.length;

  return (
    <div className="border border-slate-200 rounded-lg overflow-hidden bg-white mb-4">
      <div className="flex items-center justify-between px-3 py-2 bg-slate-100 border-b border-slate-200">
        <div className="flex items-center gap-1.5">
          <MessageSquare size={12} className="text-slate-700" />
          <span className="text-[11px] font-bold text-slate-900 uppercase tracking-wider">
            Stakeholder Intelligence
          </span>
          <span className="text-[10px] text-slate-500">
            · {drift.length} attributed position{drift.length === 1 ? '' : 's'}
            · {patterns.length} corroborated pattern{patterns.length === 1 ? '' : 's'}
          </span>
        </div>
        {loading && <Loader2 size={11} className="animate-spin text-slate-500" />}
      </div>

      {!loading && totalCount === 0 && (
        <div className="p-4 text-[11px] text-slate-600">
          <div className="font-semibold mb-1">No attributed stakeholder positions yet for this bank.</div>
          <div className="text-slate-500">
            Stakeholder Intelligence surfaces here once meeting facts are extracted.
            To populate: log meetings on the <span className="font-mono bg-slate-100 px-1 rounded">Prepare</span> tab,
            then run <span className="font-mono bg-slate-100 px-1 rounded">npm run extract-facts</span> from the CLI.
          </div>
        </div>
      )}

      {!loading && totalCount > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-0">
          {/* LEFT: Drift cells */}
          <div className="p-2 md:border-r border-slate-200">
            <div className="text-[9px] font-bold text-slate-600 uppercase tracking-wider mb-2">
              Positions across meetings ({drift.length})
            </div>
            {drift.length === 0 ? (
              <div className="text-[10px] text-slate-500 italic">No attributed positions yet.</div>
            ) : (
              <div className="space-y-1.5">
                {drift.map((cell, i) => <DriftCell key={i} cell={cell} />)}
              </div>
            )}
          </div>

          {/* RIGHT: Patterns */}
          <div className="p-2">
            <div className="text-[9px] font-bold text-slate-600 uppercase tracking-wider mb-2 flex items-center gap-1">
              <Link2 size={9} /> Corroborated patterns ({patterns.length})
            </div>
            {patterns.length === 0 ? (
              <div className="text-[10px] text-slate-500 italic">
                No medium+ confidence patterns yet. Patterns surface when meeting facts are corroborated by external signals.
              </div>
            ) : (
              <div className="space-y-1.5">
                {patterns.slice(0, 6).map((p) => <PatternCard key={p.id} p={p} />)}
                {patterns.length > 6 && (
                  <div className="text-[9px] text-slate-500 italic pt-1">
                    + {patterns.length - 6} more patterns. Open the Pulse to see all.
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
