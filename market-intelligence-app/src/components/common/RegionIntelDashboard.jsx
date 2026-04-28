/**
 * RegionIntelDashboard — Tier 1+2+3 region/country page upgrade
 * ─────────────────────────────────────────────────────────────
 * Composite component that drops into MarketPage and CountryPage. Surfaces
 * the same Sprint 1-5 intelligence as the bank/portfolio surfaces, scoped
 * to a region's bank set or a single country's bank set.
 *
 * Layout (top → bottom):
 *   1. Region Pulse summary card (Tier 2): avg engagement, Δ vs prior, drift mix
 *   2. Computed opportunities (Tier 3): data-driven cluster cards
 *   3. Source grade distribution (Tier 1): A/B/C/D histogram
 *   4. Top corroborated patterns across the bank set (Tier 1)
 *   5. Stakeholder drift heatmap — banks ranked by intel density (Tier 2)
 *   6. Query shortcuts — three pre-built deep-links into /query (Tier 1)
 *   7. Region-filtered ChangeFeed (Tier 1)
 *
 * Props:
 *   kind: 'regions' | 'countries'
 *   identifier: market key OR country name
 *   period?: '2026-Q2' (default)
 */

import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Loader2, Sparkles, Zap, MessageSquare, Filter, ExternalLink, AlertTriangle,
  ChevronRight, BarChart3, TrendingUp, TrendingDown, Activity, Minus,
} from 'lucide-react';
import { fetchRegionIntel, fetchRegionPulse } from '../../data/api';
import { ProvenanceChip } from './Provenance';
import ChangeFeed from './ChangeFeed';

const GRADE_TONE = {
  A: 'bg-slate-900 text-white',
  B: 'bg-blue-700 text-white',
  C: 'bg-slate-300 text-slate-800',
  D: 'bg-rose-200 text-rose-900',
};

const TREND_TONE = {
  improving: 'text-emerald-700 bg-emerald-50',
  deteriorating: 'text-rose-700 bg-rose-50',
  mixed: 'text-amber-700 bg-amber-50',
  stable: 'text-slate-700 bg-slate-100',
  single_point: 'text-blue-700 bg-blue-50',
};

const PATTERN_TONE = {
  corroborates: 'text-emerald-700 bg-emerald-50 border-emerald-200',
  contradicts: 'text-rose-700 bg-rose-50 border-rose-200',
  evolves: 'text-blue-700 bg-blue-50 border-blue-200',
};

function shortDate(d) {
  if (!d) return '';
  return String(d).slice(0, 10);
}

// ──────────────────────────────────────────────────────────────────────
// Tier 2 — Region Pulse summary card
// ──────────────────────────────────────────────────────────────────────

function RegionPulseSummary({ pulse, label }) {
  if (!pulse) return null;
  if (pulse.coverage_warning) {
    return (
      <div className="border border-amber-200 bg-amber-50 rounded-lg p-3 mb-3 text-[11px] text-amber-800">
        <strong>{label} Pulse — coverage gap.</strong> {pulse.coverage_warning}
      </div>
    );
  }
  const eng = pulse.sections?.engagement_trend?.data || {};
  const grade = pulse.metrics?.grade_distribution || {};
  const drift = eng.drift_summary || {};
  const arrowFor = (delta) => delta > 0 ? '↑' : delta < 0 ? '↓' : '→';
  return (
    <div className="border border-slate-200 rounded-lg bg-white p-4 mb-4">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-1.5">
          <BarChart3 size={14} className="text-slate-700" />
          <span className="text-[12px] font-bold text-slate-900 uppercase tracking-wider">{label} Pulse · {pulse.period}</span>
        </div>
        <span className="text-[10px] text-slate-500">{pulse.banks_with_pulse}/{pulse.banks_in_scope} banks</span>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
        <div>
          <div className="text-[9px] uppercase text-slate-500 tracking-wider">Engagement</div>
          <div className="text-lg font-bold text-slate-900">
            {eng.avg_score ?? '—'}<span className="text-xs text-slate-400">/10</span>
          </div>
          {eng.delta != null && (
            <div className={`text-[10px] font-bold ${eng.delta >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
              {arrowFor(eng.delta)} {Math.abs(eng.delta)} vs {pulse.prior_period}
            </div>
          )}
        </div>
        <div>
          <div className="text-[9px] uppercase text-slate-500 tracking-wider">Source mix</div>
          <div className="flex items-center gap-1 mt-0.5">
            {['A','B','C','D'].map(g => (
              <span key={g} className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${GRADE_TONE[g]}`}>
                {g} {grade[g] ?? 0}
              </span>
            ))}
          </div>
        </div>
        <div>
          <div className="text-[9px] uppercase text-slate-500 tracking-wider">Drift</div>
          <div className="text-[11px] text-slate-700">
            <span className="text-emerald-600 font-bold">{drift.improving || 0}</span> ↑
            <span className="mx-1">·</span>
            <span className="text-rose-600 font-bold">{drift.deteriorating || 0}</span> ↓
            <span className="mx-1">·</span>
            <span className="text-amber-600 font-bold">{drift.mixed || 0}</span> mixed
            <span className="mx-1">·</span>
            <span className="text-blue-600 font-bold">{drift.new_positions || 0}</span> new
          </div>
        </div>
        <div>
          <div className="text-[9px] uppercase text-slate-500 tracking-wider">Patterns</div>
          <div className="text-lg font-bold text-slate-900">
            {pulse.sections?.dmu_changes?.data?.top_patterns?.length || 0}
          </div>
          <div className="text-[10px] text-slate-500">corroborated</div>
        </div>
      </div>
      {pulse.metrics?.lint_warning_count > 0 && (
        <div className="text-[10px] text-amber-700 bg-amber-50 border border-amber-200 rounded px-2 py-1 inline-flex items-center gap-1">
          <AlertTriangle size={10} /> {pulse.metrics.lint_warning_count} provenance lint warnings across the region's pulses
        </div>
      )}
    </div>
  );
}

// ──────────────────────────────────────────────────────────────────────
// Tier 3 — Computed opportunities
// ──────────────────────────────────────────────────────────────────────

function ComputedOpportunities({ opportunities }) {
  if (!opportunities?.length) {
    return (
      <div className="border border-slate-200 bg-slate-50 rounded-lg p-3 mb-3 text-[11px] text-slate-600">
        <strong>No opportunity clusters detected</strong> in the last 60 days. As more signals + facts accumulate, clusters surface here.
      </div>
    );
  }
  return (
    <div className="mb-4">
      <div className="text-[10px] font-bold text-slate-600 uppercase tracking-wider mb-2 flex items-center gap-1">
        <Sparkles size={11} /> Computed opportunities (data-driven, last 60d)
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
        {opportunities.map((o, i) => (
          <div key={i} className="border border-slate-200 bg-white rounded-lg p-3">
            <div className="flex items-center justify-between mb-1">
              <span className="text-[11px] font-bold text-slate-900">{o.title}</span>
              <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-slate-900 text-white">
                {o.significance}/10
              </span>
            </div>
            <div className="text-[10px] text-slate-700 leading-snug mb-2">{o.detail}</div>
            <div className="flex flex-wrap gap-1">
              {o.banks.slice(0, 6).map((b, j) => (
                <Link
                  key={j}
                  to={`/bank/${encodeURIComponent(b.bank_key)}`}
                  className="inline-flex items-center gap-0.5 text-[9px] font-bold px-1.5 py-0.5 rounded bg-slate-100 hover:bg-slate-200 text-slate-700"
                >
                  {b.bank_name || b.bank_key} <ChevronRight size={9} />
                </Link>
              ))}
              {o.banks.length > 6 && (
                <span className="text-[9px] text-slate-500 self-center">+{o.banks.length - 6}</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ──────────────────────────────────────────────────────────────────────
// Tier 1 — Top corroborated patterns
// ──────────────────────────────────────────────────────────────────────

function RegionPatternsPanel({ patterns }) {
  if (!patterns?.length) {
    return (
      <div className="border border-slate-200 bg-slate-50 rounded-lg p-3 mb-3 text-[11px] text-slate-600 italic">
        No corroborated patterns surfaced yet. Patterns emerge as meeting facts get cross-referenced with external signals.
      </div>
    );
  }
  return (
    <div className="mb-4">
      <div className="text-[10px] font-bold text-slate-600 uppercase tracking-wider mb-2 flex items-center gap-1">
        <MessageSquare size={11} /> Top corroborated patterns ({patterns.length})
      </div>
      <div className="border border-slate-200 rounded-lg bg-white overflow-hidden">
        {patterns.map((p, i) => (
          <div key={p.id || i} className={`p-2.5 ${i > 0 ? 'border-t border-slate-100' : ''}`}>
            <div className="flex items-center gap-1.5 flex-wrap mb-1">
              <Link to={`/bank/${encodeURIComponent(p.bank_key)}`}
                    className="text-[10px] font-bold text-blue-700 hover:underline">
                {p.bank_name || p.bank_key}
              </Link>
              <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded border ${PATTERN_TONE[p.pattern_type] || 'border-slate-200 bg-slate-50 text-slate-700'}`}>
                {p.pattern_type}
              </span>
              <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-slate-100 text-slate-700">{p.topic}</span>
              <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${p.confidence === 'high' ? 'bg-slate-900 text-white' : p.confidence === 'medium' ? 'bg-slate-200 text-slate-800' : 'bg-slate-100 text-slate-600'}`}>
                {p.confidence}
              </span>
              {p.signal_grade && (
                <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${GRADE_TONE[p.signal_grade]}`}>
                  signal {p.signal_grade}
                </span>
              )}
            </div>
            <div className="text-[11px] text-slate-800 leading-snug mb-1">{p.summary}</div>
            <div className="flex items-center gap-1.5 text-[9px] text-slate-500 flex-wrap">
              <span><strong>Fact:</strong> {p.fact_speaker_name || '(unattributed)'} · {shortDate(p.fact_meeting_date)}</span>
              {p.signal_source_url && (
                <a href={p.signal_source_url} target="_blank" rel="noopener noreferrer"
                   className="inline-flex items-center gap-1 text-blue-700 hover:underline">
                  <ExternalLink size={8} /> {(p.signal_title || '').slice(0, 60)}…
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ──────────────────────────────────────────────────────────────────────
// Tier 1 — Source grade distribution histogram
// ──────────────────────────────────────────────────────────────────────

function GradeDistribution({ dist }) {
  if (!dist || dist.total === 0) return null;
  const grades = [
    { key: 'A', label: 'Primary' },
    { key: 'B', label: 'Tier-1 press' },
    { key: 'C', label: 'Trade press' },
    { key: 'D', label: 'Low authority' },
  ];
  return (
    <div className="border border-slate-200 rounded-lg bg-white p-3 mb-4">
      <div className="text-[10px] font-bold text-slate-600 uppercase tracking-wider mb-2">
        Source grade mix · {dist.total} signals
      </div>
      <div className="space-y-1">
        {grades.map(g => {
          const count = dist[g.key] || 0;
          const pct = dist.total > 0 ? Math.round(count / dist.total * 100) : 0;
          return (
            <div key={g.key} className="flex items-center gap-2 text-[10px]">
              <span className={`shrink-0 inline-block w-12 px-1.5 py-0.5 rounded text-center font-bold ${GRADE_TONE[g.key]}`}>
                {g.key}
              </span>
              <span className="shrink-0 w-20 text-slate-600">{g.label}</span>
              <div className="flex-1 h-2 bg-slate-100 rounded overflow-hidden">
                <div className={`h-full ${GRADE_TONE[g.key]}`} style={{ width: `${pct}%` }} />
              </div>
              <span className="shrink-0 text-slate-700 font-mono w-16 text-right">{count} <span className="text-slate-400">({pct}%)</span></span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ──────────────────────────────────────────────────────────────────────
// Tier 2 — Drift heatmap (banks ranked by intel density)
// ──────────────────────────────────────────────────────────────────────

function DriftHeatmap({ rows }) {
  if (!rows?.length) return null;
  return (
    <div className="mb-4">
      <div className="text-[10px] font-bold text-slate-600 uppercase tracking-wider mb-2">
        Stakeholder intel density (top {rows.length})
      </div>
      <div className="border border-slate-200 rounded-lg bg-white overflow-hidden">
        <table className="w-full text-[10px]">
          <thead className="bg-slate-50 text-slate-600 text-[9px] uppercase tracking-wider">
            <tr>
              <th className="text-left px-2 py-1.5">Bank</th>
              <th className="text-right px-2 py-1.5">Facts</th>
              <th className="text-right px-2 py-1.5">Speakers</th>
              <th className="text-right px-2 py-1.5">Topics</th>
              <th className="text-left px-2 py-1.5">Drift mix</th>
              <th className="text-left px-2 py-1.5">Last fact</th>
              <th className="text-right px-2 py-1.5"></th>
            </tr>
          </thead>
          <tbody>
            {rows.map(r => (
              <tr key={r.bank_key} className="border-t border-slate-100 hover:bg-slate-50">
                <td className="px-2 py-1.5 font-semibold text-slate-900">{r.bank_name}</td>
                <td className="px-2 py-1.5 text-right">{r.total_facts}</td>
                <td className="px-2 py-1.5 text-right">{r.attributed_speakers}</td>
                <td className="px-2 py-1.5 text-right">{r.topics_touched}</td>
                <td className="px-2 py-1.5">
                  <div className="flex items-center gap-1">
                    {r.trends.improving > 0 && <span className={`text-[9px] px-1 rounded ${TREND_TONE.improving}`}><TrendingUp size={8} className="inline" /> {r.trends.improving}</span>}
                    {r.trends.deteriorating > 0 && <span className={`text-[9px] px-1 rounded ${TREND_TONE.deteriorating}`}><TrendingDown size={8} className="inline" /> {r.trends.deteriorating}</span>}
                    {r.trends.mixed > 0 && <span className={`text-[9px] px-1 rounded ${TREND_TONE.mixed}`}><Activity size={8} className="inline" /> {r.trends.mixed}</span>}
                    {r.trends.stable > 0 && <span className={`text-[9px] px-1 rounded ${TREND_TONE.stable}`}><Minus size={8} className="inline" /> {r.trends.stable}</span>}
                    {r.trends.single_point > 0 && <span className="text-[9px] px-1 rounded bg-blue-50 text-blue-700">{r.trends.single_point} new</span>}
                  </div>
                </td>
                <td className="px-2 py-1.5 text-slate-500">{shortDate(r.last_fact_date)}</td>
                <td className="px-2 py-1.5 text-right">
                  <Link to={`/bank/${encodeURIComponent(r.bank_key)}`}
                        className="inline-flex items-center gap-0.5 text-blue-700 hover:underline">
                    open <ChevronRight size={9} />
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ──────────────────────────────────────────────────────────────────────
// Tier 1 — Query shortcuts (deep-link into /query with predicates)
// ──────────────────────────────────────────────────────────────────────

function QueryShortcuts({ kind, identifier }) {
  // Deep-link strategy: navigate to /query with the predicate set in URL state.
  // For now, link to /query and let the user click an example. A future
  // enhancement could pass predicate JSON via query string.
  const country = kind === 'countries' ? identifier : null;
  return (
    <div className="mb-4">
      <div className="text-[10px] font-bold text-slate-600 uppercase tracking-wider mb-2 flex items-center gap-1">
        <Filter size={11} /> Query shortcuts
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
        <Link to="/query" className="border border-slate-200 bg-white hover:bg-slate-50 rounded-lg p-2.5 text-[11px] transition-colors">
          <div className="font-semibold text-slate-900 mb-0.5">Deteriorating CFOs {country ? `in ${country}` : 'in this region'}</div>
          <div className="text-[10px] text-slate-500">drift_trend = deteriorating, topic = budget</div>
        </Link>
        <Link to="/query" className="border border-slate-200 bg-white hover:bg-slate-50 rounded-lg p-2.5 text-[11px] transition-colors">
          <div className="font-semibold text-slate-900 mb-0.5">Urgent signals (last 30d)</div>
          <div className="text-[10px] text-slate-500">has_signal · severity = urgent · within_days = 30</div>
        </Link>
        <Link to="/query" className="border border-slate-200 bg-white hover:bg-slate-50 rounded-lg p-2.5 text-[11px] transition-colors">
          <div className="font-semibold text-slate-900 mb-0.5">Engagement score dropped Q1→Q2</div>
          <div className="text-[10px] text-slate-500">pulse_score_change · op = lt · value = 0</div>
        </Link>
      </div>
    </div>
  );
}

// ──────────────────────────────────────────────────────────────────────
// Top-level dashboard
// ──────────────────────────────────────────────────────────────────────

export default function RegionIntelDashboard({ kind, identifier, period = '2026-Q2', label = null }) {
  const [intel, setIntel] = useState(null);
  const [pulse, setPulse] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!kind || !identifier) return;
    setLoading(true);
    Promise.all([
      fetchRegionIntel(kind, identifier, { period }).catch(() => null),
      fetchRegionPulse(kind, identifier, { period }).catch(() => null),
    ]).then(([intelData, pulseData]) => {
      setIntel(intelData);
      setPulse(pulseData);
    }).finally(() => setLoading(false));
  }, [kind, identifier, period]);

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-[11px] text-slate-500 my-4">
        <Loader2 size={12} className="animate-spin" /> Loading {label || identifier} intelligence…
      </div>
    );
  }
  if (!intel || intel.bank_count === 0) {
    return (
      <div className="border border-amber-200 bg-amber-50 rounded-lg p-3 my-4 text-[11px] text-amber-800">
        No banks resolved for {label || identifier}. Region intelligence requires at least one bank in scope.
      </div>
    );
  }

  const displayLabel = label || identifier;

  return (
    <div>
      <RegionPulseSummary pulse={pulse} label={displayLabel} />
      <ComputedOpportunities opportunities={intel.computed_opportunities || []} />
      <GradeDistribution dist={intel.grade_distribution} />
      <RegionPatternsPanel patterns={intel.top_patterns || []} />
      <DriftHeatmap rows={intel.drift_heatmap || []} />
      <QueryShortcuts kind={kind} identifier={identifier} />
      <div className="mb-2 text-[10px] font-bold text-slate-600 uppercase tracking-wider flex items-center gap-1">
        <Zap size={11} /> Change feed · {displayLabel}
      </div>
      <ChangeFeed kind={kind} identifier={identifier} />
    </div>
  );
}
