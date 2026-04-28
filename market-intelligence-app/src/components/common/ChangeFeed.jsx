/**
 * ChangeFeed — Sprint 4.2 / 4.3
 * ─────────────────────────────
 * Unified "what changed" view. Renders a chronological (or significance-ranked)
 * stream of every meaningful delta across all of Nova's persistence layers:
 * new signals, meeting facts, patterns, pulse diffs, sentiment drift, edits.
 *
 * Two modes:
 *   <ChangeFeed bankKey="Nordea_Sweden" />  → per-bank
 *   <ChangeFeed />                          → portfolio-wide (no bankKey)
 *
 * Each event renders with its provenance chip so the AE never has to ask
 * "where did this come from" — tier + grade + click-through to source.
 *
 * The reframe behind the whole sprint: this should be the DEFAULT view of
 * Nova. Static profiles answer "what is"; the change feed answers "what
 * changed since I last looked" — which is the actual question an AE has
 * when they open the app.
 */

import { useEffect, useState } from 'react';
import {
  Loader2, Newspaper, MessageSquare, Link2, RefreshCw, TrendingUp, History,
  Zap, ChevronRight, ExternalLink, Filter,
} from 'lucide-react';
import { getBankChangeFeed, getPortfolioChangeFeed, fetchRegionChangeFeed } from '../../data/api';
import { ProvenanceChip } from './Provenance';

const TYPE_META = {
  NEW_SIGNAL:        { label: 'Signal',     Icon: Newspaper,    tone: 'bg-blue-50 text-blue-800 border-blue-200' },
  NEW_MEETING_FACT:  { label: 'Meeting',    Icon: MessageSquare, tone: 'bg-emerald-50 text-emerald-800 border-emerald-200' },
  NEW_PATTERN:       { label: 'Pattern',    Icon: Link2,        tone: 'bg-purple-50 text-purple-800 border-purple-200' },
  PULSE_DIFF:        { label: 'Pulse Diff', Icon: RefreshCw,    tone: 'bg-amber-50 text-amber-800 border-amber-200' },
  STAKEHOLDER_DRIFT: { label: 'Drift',      Icon: TrendingUp,   tone: 'bg-indigo-50 text-indigo-800 border-indigo-200' },
  ENTITY_HISTORY:    { label: 'Edit',       Icon: History,      tone: 'bg-slate-50 text-slate-700 border-slate-200' },
};

function shortDate(iso) {
  if (!iso) return '—';
  const d = new Date(String(iso).replace(' ', 'T') + (String(iso).includes('T') ? '' : 'Z'));
  if (isNaN(d)) return iso.slice(0, 10);
  const now = Date.now();
  const diffMs = now - d.getTime();
  const days = Math.floor(diffMs / 86400000);
  if (days <= 0) return 'today';
  if (days === 1) return 'yesterday';
  if (days < 7) return `${days}d ago`;
  if (days < 30) return `${Math.floor(days / 7)}w ago`;
  return d.toLocaleDateString('en-US', { day: '2-digit', month: 'short' });
}

function SignificanceBar({ value }) {
  // Visual bar 0-10. We use 10 cells, filled to value.
  return (
    <div className="flex items-center gap-px shrink-0" title={`Significance: ${value}/10`}>
      {Array.from({ length: 10 }).map((_, i) => (
        <span
          key={i}
          className={`block w-1 h-2.5 rounded-sm ${
            i < value
              ? value >= 8 ? 'bg-rose-500' : value >= 5 ? 'bg-amber-500' : 'bg-slate-400'
              : 'bg-slate-100'
          }`}
        />
      ))}
    </div>
  );
}

function EventRow({ event, showBank }) {
  const meta = TYPE_META[event.type] || TYPE_META.ENTITY_HISTORY;
  const Icon = meta.Icon;
  return (
    <div className="flex items-start gap-2 p-2 border-b border-slate-100 hover:bg-slate-50 transition-colors">
      <SignificanceBar value={event.significance} />
      <span className={`shrink-0 inline-flex items-center gap-1 px-1.5 py-0.5 rounded border text-[9px] font-bold ${meta.tone}`}>
        <Icon size={9} /> {meta.label}
      </span>
      <div className="flex-1 min-w-0">
        <div className="flex items-baseline gap-1.5 flex-wrap">
          {showBank && (
            <span className="text-[10px] font-bold text-slate-700">{event.bank_key}</span>
          )}
          <span className="text-[10px] text-slate-500">{shortDate(event.timestamp)}</span>
          {(event.source_grade || event.confidence_tier) && (
            <ProvenanceChip source={{
              source_type: event.type.toLowerCase(),
              source_url: event.citation?.url,
              source_date: event.timestamp,
              confidence_tier: event.confidence_tier,
              source_grade: event.source_grade,
              publisher_name: event.detail?.signal_publisher || event.citation?.label,
              verifier: 'auto',
              label: event.citation?.label,
              evidence_quote: event.citation?.evidence_quote,
            }} size="xs" showDate={false} />
          )}
        </div>
        <div className="text-[11px] text-slate-800 mt-0.5 leading-snug">{event.headline}</div>
        {event.detail?.topic && event.type === 'NEW_PATTERN' && (
          <div className="text-[9px] text-slate-500 mt-0.5">
            {event.detail.pattern_type} · {event.detail.topic} · {event.detail.confidence} · gap: {event.detail.gap_days}d
          </div>
        )}
        {event.citation?.url && (
          <a href={event.citation.url} target="_blank" rel="noopener noreferrer"
             className="inline-flex items-center gap-0.5 text-[9px] text-blue-700 hover:underline mt-0.5">
            <ExternalLink size={8} /> source
          </a>
        )}
      </div>
    </div>
  );
}

function FilterBar({ counts, activeTypes, onToggleType, sort, onChangeSort, lookback, onChangeLookback }) {
  return (
    <div className="flex items-center gap-2 flex-wrap p-2 bg-slate-50 border-b border-slate-200 text-[10px]">
      <Filter size={11} className="text-slate-500" />
      {Object.keys(TYPE_META).map(t => {
        const meta = TYPE_META[t];
        const Icon = meta.Icon;
        const active = activeTypes.includes(t);
        const c = counts?.[t] || 0;
        return (
          <button
            key={t}
            onClick={() => onToggleType(t)}
            disabled={c === 0}
            className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded border text-[9px] font-bold transition-colors ${
              c === 0 ? 'opacity-40 cursor-not-allowed' :
              active ? meta.tone : 'bg-white text-slate-500 border-slate-200 hover:bg-slate-100'
            }`}
          >
            <Icon size={9} /> {meta.label} <span className="opacity-60">{c}</span>
          </button>
        );
      })}
      <span className="text-slate-300">·</span>
      <label className="text-slate-500">Sort:</label>
      <select value={sort} onChange={e => onChangeSort(e.target.value)}
        className="text-[10px] border border-slate-200 rounded px-1 py-0.5 bg-white">
        <option value="time">Newest first</option>
        <option value="significance">Significance</option>
      </select>
      <span className="text-slate-300">·</span>
      <label className="text-slate-500">Look back:</label>
      <select value={lookback} onChange={e => onChangeLookback(parseInt(e.target.value, 10))}
        className="text-[10px] border border-slate-200 rounded px-1 py-0.5 bg-white">
        <option value="7">7 days</option>
        <option value="30">30 days</option>
        <option value="90">90 days</option>
      </select>
    </div>
  );
}

export default function ChangeFeed({
  bankKey = null,
  // Region/country scope (post-B-series). When `kind` + `identifier` are
  // provided, the feed routes to /api/{kind}/{identifier}/change-feed
  // instead of the per-bank or portfolio endpoints.
  kind = null,        // 'regions' | 'countries' | null
  identifier = null,  // market key or country name
  defaultLookback = null, defaultSort = null, defaultMinSig = null,
  title: customTitle = null,
}) {
  // Defaults differ between per-bank and portfolio. Per-bank: 30d / time / 0.
  // Region/country: 30d / significance / ≥0. Portfolio: 7d / significance / ≥5.
  const isRegionScope = !!(kind && identifier);
  const isPerBank = !!bankKey;
  const [lookback, setLookback] = useState(defaultLookback ?? ((isPerBank || isRegionScope) ? 30 : 7));
  const [sort, setSort] = useState(defaultSort ?? (isPerBank ? 'time' : 'significance'));
  const [minSig] = useState(defaultMinSig ?? (isPerBank ? 0 : isRegionScope ? 0 : 5));
  const [activeTypes, setActiveTypes] = useState(Object.keys(TYPE_META));
  const [events, setEvents] = useState([]);
  const [counts, setCounts] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const opts = { lookback, sort, minSignificance: minSig, limit: 100, include: activeTypes };
    const fetchFn = isRegionScope
      ? fetchRegionChangeFeed.bind(null, kind, identifier)
      : isPerBank
        ? getBankChangeFeed.bind(null, bankKey)
        : getPortfolioChangeFeed;
    fetchFn(opts)
      .then(d => {
        setEvents(d?.events || []);
        setCounts(d?.counts || {});
      })
      .catch(() => { setEvents([]); setCounts({}); })
      .finally(() => setLoading(false));
  }, [bankKey, kind, identifier, lookback, sort, minSig, activeTypes]);

  const toggleType = (t) => {
    setActiveTypes(prev => prev.includes(t) ? prev.filter(x => x !== t) : [...prev, t]);
  };

  return (
    <div className="border border-slate-200 rounded-lg overflow-hidden bg-white">
      <div className="flex items-center justify-between px-3 py-2 bg-slate-100 border-b border-slate-200">
        <div className="flex items-center gap-1.5">
          <Zap size={12} className="text-slate-700" />
          <span className="text-[11px] font-bold text-slate-900 uppercase tracking-wider">
            {customTitle || (isRegionScope
              ? `What changed in ${identifier}`
              : isPerBank ? 'What changed' : 'Portfolio changes')}
          </span>
          <span className="text-[10px] text-slate-500">· {counts.total || 0} event{counts.total === 1 ? '' : 's'}</span>
        </div>
        {loading && <Loader2 size={11} className="animate-spin text-slate-500" />}
      </div>
      <FilterBar
        counts={counts}
        activeTypes={activeTypes}
        onToggleType={toggleType}
        sort={sort}
        onChangeSort={setSort}
        lookback={lookback}
        onChangeLookback={setLookback}
      />
      {!loading && events.length === 0 && (
        <div className="p-6 text-center text-[11px] text-slate-500 italic">
          No changes in the last {lookback} day{lookback === 1 ? '' : 's'} matching the active filters.
        </div>
      )}
      {events.map(e => (
        <EventRow key={e.id} event={e} showBank={!bankKey} />
      ))}
    </div>
  );
}
