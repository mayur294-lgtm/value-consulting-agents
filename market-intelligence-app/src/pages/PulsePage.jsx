/**
 * PulsePage — Strategic Repositioning Sprint 1, Day 4
 * ────────────────────────────────────────────────────
 * The flagship Nova surface: quarterly pulse review for one account.
 *
 * AE workflow:
 *   1. Land on /bank/:key/pulse
 *   2. Generate (or view existing) pulse for the active period
 *   3. Review each section's synthesis + sources + freshness
 *   4. Edit any cell with one click; the override is logged to
 *      pulse_overrides (telemetry → we learn where the synthesizer is weak)
 *   5. Confirm → lock for export
 *   6. Export to JSON / Markdown
 *
 * Critical UX principle: every visible fact carries source + confidence + date.
 * The AE never sees a claim without provenance attached.
 */

import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Loader2, RefreshCw, CheckCircle, AlertTriangle, ChevronRight, ChevronDown,
  Edit3, Save, X, Clock, ExternalLink, Database,
} from 'lucide-react';
import {
  getReviewPeriods, getBankPulses, generatePulse, getPulse,
  overrideCell, confirmPulse,
} from '../data/api';
import { ProvenanceChip } from '../components/common/Provenance';
import { applyFloor, getFloor } from '../data/provenanceFloors';
import { pulseToMarkdown as pulseToMarkdownExport, pulseToHtml as pulseToHtmlExport } from '../utils/pulseExport';

// ─────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────

const SECTION_LABELS = {
  strategic_posture:     'Strategic Posture',
  quarterly_execution:   'Quarterly Execution',
  market_signals:        'Market Signals',
  engagement_trend:      'Engagement Trend',
  dmu_changes:           'DMU Changes',
  budget_cycles:         'Budget Cycles',
  blockers_asks_actions: 'Blockers / Asks / Actions',
};

const FRESHNESS_STYLE = {
  green:  { color: 'text-emerald-700', bg: 'bg-emerald-100', label: 'Green' },
  yellow: { color: 'text-amber-700',   bg: 'bg-amber-100',   label: 'Yellow' },
  stale:  { color: 'text-red-700',     bg: 'bg-red-100',     label: 'Stale' },
};

const TIER_LABELS = { 1: 'Verified', 2: 'Inferred', 3: 'Estimated' };

// ─────────────────────────────────────────────────────────────────
// Sprint 2.6 — drift + patterns specialized renderers
// ─────────────────────────────────────────────────────────────────

const TREND_TONE = {
  improving:     'text-emerald-700 bg-emerald-50 border-emerald-200',
  deteriorating: 'text-rose-700 bg-rose-50 border-rose-200',
  mixed:         'text-amber-700 bg-amber-50 border-amber-200',
  stable:        'text-slate-700 bg-slate-50 border-slate-200',
  single_point:  'text-blue-700 bg-blue-50 border-blue-200',
};
const TREND_LABEL = {
  improving: 'improving', deteriorating: 'deteriorating', mixed: 'mixed',
  stable: 'stable', single_point: 'new',
};
const SENTIMENT_DOT = {
  positive: 'bg-emerald-500', neutral: 'bg-slate-400',
  mixed: 'bg-amber-500', negative: 'bg-rose-500',
};
const PATTERN_TONE = {
  corroborates: 'text-emerald-700 bg-emerald-50 border-emerald-200',
  contradicts:  'text-rose-700 bg-rose-50 border-rose-200',
  evolves:      'text-blue-700 bg-blue-50 border-blue-200',
};
const CONFIDENCE_TONE = {
  high:   'bg-slate-900 text-white',
  medium: 'bg-slate-200 text-slate-800',
  low:    'bg-slate-100 text-slate-600',
};

function StakeholderDriftCard({ cell }) {
  return (
    <div className="p-2 rounded border border-slate-200 bg-white">
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center gap-1.5">
          <span className="text-[10px] font-bold text-slate-900">{cell.speaker_name}</span>
          {cell.speaker_role && <span className="text-[9px] text-slate-500">· {cell.speaker_role}</span>}
          {cell.confidence_tier === 1 && <span className="text-[8px] font-bold px-1 py-0.5 rounded bg-slate-900 text-white">T1</span>}
          {cell.confidence_tier === 2 && <span className="text-[8px] font-bold px-1 py-0.5 rounded bg-slate-200 text-slate-700">T2</span>}
        </div>
        <span className={`inline-flex items-center gap-1 text-[9px] font-bold px-1.5 py-0.5 rounded border ${TREND_TONE[cell.trend] || TREND_TONE.single_point}`}>
          {cell.topic} · {TREND_LABEL[cell.trend] || cell.trend}{cell.n_facts > 1 ? ` · n=${cell.n_facts}` : ''}
        </span>
      </div>
      {/* Sentiment ladder */}
      <div className="flex items-center gap-1 my-1.5">
        {(cell.series || []).map((s, i) => (
          <div key={i} className="flex items-center gap-1" title={`${s.sentiment} on ${s.meeting_date}\n${s.position}\n\nVerbatim: ${s.evidence_quote}`}>
            <div className="flex flex-col items-center">
              <span className={`block w-2 h-2 rounded-full ${SENTIMENT_DOT[s.sentiment] || 'bg-slate-300'}`} />
              <span className="text-[8px] text-slate-400 mt-0.5 leading-none">{String(s.meeting_date).slice(5)}</span>
            </div>
            {i < cell.series.length - 1 && <span className="block w-3 h-px bg-slate-300" />}
          </div>
        ))}
      </div>
      <div className="text-[10px] text-slate-700 italic leading-snug" title={cell.series?.[cell.series.length - 1]?.evidence_quote || ''}>
        "{cell.series?.[cell.series.length - 1]?.position}"
      </div>
    </div>
  );
}

function StakeholderDriftPanel({ drift }) {
  const buckets = [
    { key: 'improving',     items: drift.improving || [],     label: 'Improving' },
    { key: 'deteriorating', items: drift.deteriorating || [], label: 'Deteriorating' },
    { key: 'mixed',         items: drift.mixed || [],         label: 'Mixed' },
    { key: 'new_positions', items: drift.new_positions || [], label: 'New positions' },
  ];
  const total = buckets.reduce((s, b) => s + b.items.length, 0);
  if (total === 0) {
    return (
      <div className="text-[10px] text-slate-500 italic">No stakeholder drift this period (positions are extracted from meeting notes).</div>
    );
  }
  return (
    <div className="space-y-2">
      {buckets.filter(b => b.items.length > 0).map(b => (
        <div key={b.key}>
          <div className="text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1">{b.label} ({b.items.length})</div>
          <div className="space-y-1.5">
            {b.items.map((c, i) => <StakeholderDriftCard key={i} cell={c} />)}
          </div>
        </div>
      ))}
    </div>
  );
}

function CorroboratedPatternsPanel({ patterns }) {
  // Sprint 3.5: apply patterns_panel floor (min_tier=2). Patterns can carry
  // their own confidence (high/medium/low) which we map to tier for the floor.
  const enriched = (patterns || []).map(p => ({
    ...p,
    confidence_tier: p.confidence === 'high' ? 1 : p.confidence === 'medium' ? 2 : 3,
    source_grade: p.signal_grade,
  }));
  const { kept, hidden } = applyFloor(enriched, 'patterns_panel');
  if (!enriched.length) {
    return <div className="text-[10px] text-slate-500 italic">No corroborated patterns this period.</div>;
  }
  if (!kept.length) {
    return <div className="text-[10px] text-slate-500 italic">{hidden.length} pattern{hidden.length === 1 ? '' : 's'} below confidence floor — none surfaced.</div>;
  }
  return (
    <div className="space-y-1.5">
      {hidden.length > 0 && (
        <div className="text-[9px] italic text-slate-500">
          {hidden.length} low-confidence pattern{hidden.length === 1 ? '' : 's'} hidden by floor (min: medium).
        </div>
      )}
      {kept.map((p) => {
        const gapText = p.gap_days >= 0
          ? `signal ${p.gap_days}d AFTER meeting`
          : `signal ${Math.abs(p.gap_days)}d BEFORE meeting (reactive)`;
        return (
          <div key={p.id} className="p-2 rounded border border-slate-200 bg-white">
            <div className="flex items-center gap-1.5 mb-1 flex-wrap">
              <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded border ${PATTERN_TONE[p.type] || 'border-slate-200 bg-slate-50 text-slate-700'}`}>
                {p.type}
              </span>
              <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-slate-100 text-slate-700">{p.topic}</span>
              <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${CONFIDENCE_TONE[p.confidence] || CONFIDENCE_TONE.low}`}>
                {p.confidence}
              </span>
              <span className="text-[9px] text-slate-500">· {gapText}</span>
            </div>
            <div className="text-[11px] text-slate-800 leading-snug mb-1">{p.summary}</div>
            <div className="flex items-center gap-1.5 text-[9px] text-slate-500">
              <span className="font-semibold">Fact:</span>
              <ProvenanceChip source={{
                source_type: 'meeting_fact',
                source_date: p.meeting_date,
                confidence_tier: p.speaker ? 1 : 2,
                source_grade: 'A',
                verifier: 'auto',
                label: `${p.speaker || '(unattributed)'} · ${p.topic}`,
              }} size="xs" />
              <span>{p.speaker || '(unattributed)'} · {p.meeting_date}</span>
            </div>
            {p.signal_url && (
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className="text-[9px] font-semibold text-slate-500">Signal:</span>
                <ProvenanceChip source={{
                  source_type: 'news',
                  source_url: p.signal_url,
                  source_date: p.signal_detected_at,
                  confidence_tier: p.confidence === 'high' ? 1 : p.confidence === 'medium' ? 2 : 3,
                  source_grade: p.signal_grade || null,
                  publisher_name: p.signal_publisher || null,
                  verifier: 'auto',
                  label: p.signal_title,
                }} size="xs" />
                <a href={p.signal_url} target="_blank" rel="noopener noreferrer"
                   className="inline-flex items-center gap-1 text-[9px] text-blue-700 hover:underline">
                  <ExternalLink size={8} /> {p.signal_title?.slice(0, 80)}…
                </a>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
function formatDate(s) {
  if (!s) return '—';
  try {
    const d = new Date(String(s).replace(' ', 'T') + (String(s).includes('T') ? '' : 'Z'));
    if (isNaN(d)) return s;
    return d.toLocaleDateString('en-US', { day: '2-digit', month: 'short', year: 'numeric' });
  } catch { return s; }
}

// ─────────────────────────────────────────────────────────────────
// Source records list — every cell uses this
// ─────────────────────────────────────────────────────────────────

function SourceList({ sources }) {
  // Sprint 3.3: SourceList now renders via the universal <ProvenanceChip> so
  // every Pulse cell shares the same tier+grade hover semantics that
  // PersonIntelCard / patterns / drift cells use. Single source of truth for
  // provenance display across all of Nova.
  if (!sources?.length) {
    return <div className="text-[10px] text-slate-400 italic">No source records — synthesis based on data gap (this section may need refresh).</div>;
  }
  return (
    <div className="space-y-1">
      {sources.map((s, i) => (
        <div key={i} className="flex items-start gap-1.5 text-[10px]">
          <ProvenanceChip source={s} size="sm" />
          {s.source_url ? (
            <a href={s.source_url} target="_blank" rel="noopener noreferrer"
              className="flex-1 min-w-0 text-blue-700 hover:underline truncate">
              {s.label || s.source_url} <ExternalLink size={8} className="inline ml-0.5" />
            </a>
          ) : (
            <span className="flex-1 min-w-0 text-slate-700 truncate">{s.label || '(no link)'}</span>
          )}
          {s.verifier === 'ae_confirmed' && (
            <span className="shrink-0 text-emerald-600 text-[8px] font-bold" title="Acknowledged by an AE">✓ AE</span>
          )}
        </div>
      ))}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────
// Editable cell — click to edit, save sends override, telemetry logged
// ─────────────────────────────────────────────────────────────────

function EditableCell({ pulseId, cellPath, value, onSaved, multiline = true }) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(value || '');
  const [saving, setSaving] = useState(false);
  const [reason, setReason] = useState('');

  const save = async () => {
    if (draft === value) { setEditing(false); return; }
    setSaving(true);
    try {
      await overrideCell(pulseId, {
        cell_path: cellPath,
        original_value: value,
        override_value: draft,
        reason: reason || null,
      });
      onSaved?.(draft);
      setEditing(false);
    } catch (err) {
      alert('Override failed: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  if (!editing) {
    return (
      <div className="group relative">
        <div className="text-[11px] text-slate-800 leading-relaxed pr-6">{value}</div>
        <button onClick={() => setEditing(true)}
          className="absolute top-0 right-0 opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-blue-600 transition-opacity"
          title="Override this cell">
          <Edit3 size={10} />
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-1.5">
      {multiline ? (
        <textarea autoFocus value={draft} onChange={e => setDraft(e.target.value)}
          rows={3} className="w-full px-2 py-1.5 text-[11px] border border-blue-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-200 resize-none" />
      ) : (
        <input autoFocus type="text" value={draft} onChange={e => setDraft(e.target.value)}
          className="w-full px-2 py-1 text-[11px] border border-blue-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-200" />
      )}
      <input type="text" value={reason} onChange={e => setReason(e.target.value)}
        placeholder="Why are you overriding? (optional — helps tune the synthesizer)"
        className="w-full px-2 py-1 text-[10px] italic text-slate-500 border border-slate-200 rounded focus:outline-none" />
      <div className="flex items-center gap-1">
        <button onClick={save} disabled={saving}
          className="inline-flex items-center gap-1 px-2 py-1 bg-blue-600 text-white text-[10px] font-bold rounded hover:bg-blue-700 disabled:opacity-50">
          {saving && <Loader2 size={10} className="animate-spin" />} <Save size={10} /> Save Override
        </button>
        <button onClick={() => { setEditing(false); setDraft(value); }}
          className="inline-flex items-center gap-1 px-2 py-1 text-slate-500 hover:text-slate-800 text-[10px] font-bold">
          <X size={10} /> Cancel
        </button>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────
// One section card
// ─────────────────────────────────────────────────────────────────

function SectionCard({ pulseId, sectionKey, section, onCellSaved }) {
  const [expanded, setExpanded] = useState(true);
  const fresh = FRESHNESS_STYLE[section.freshness] || FRESHNESS_STYLE.stale;

  return (
    <div className="border border-slate-200 rounded-lg overflow-hidden mb-3">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-2 px-3 py-2.5 bg-slate-50 hover:bg-slate-100 transition-colors"
      >
        {expanded ? <ChevronDown size={12} className="text-slate-500" /> : <ChevronRight size={12} className="text-slate-500" />}
        <span className="text-[12px] font-bold text-slate-900 flex-1 text-left">{SECTION_LABELS[sectionKey] || sectionKey}</span>
        <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${fresh.bg} ${fresh.color}`}>{fresh.label}</span>
        <span className="text-[9px] font-bold text-slate-400">{section.source_records?.length || 0} sources</span>
      </button>

      {expanded && (
        <div className="px-3 py-3 space-y-2.5 bg-white">
          {/* Synthesis — editable */}
          <div>
            <div className="text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1">Synthesis</div>
            <EditableCell
              pulseId={pulseId}
              cellPath={`sections.${sectionKey}.synthesis`}
              value={section.synthesis}
              onSaved={(newVal) => onCellSaved(`sections.${sectionKey}.synthesis`, newVal)}
            />
          </div>

          {/* Diff vs previous */}
          <div className="px-2 py-1 bg-blue-50 border border-blue-100 rounded">
            <span className="text-[9px] font-bold text-blue-700 uppercase tracking-wider">Diff vs. previous: </span>
            <span className="text-[10px] text-blue-900">{section.diff_vs_previous}</span>
          </div>

          {/* Sprint 3.4 — unsourced-claim lint warnings */}
          {Array.isArray(section._lint) && section._lint.length > 0 && (
            <div className="px-2 py-1.5 bg-amber-50 border border-amber-200 rounded">
              <div className="flex items-center gap-1 mb-0.5">
                <AlertTriangle size={10} className="text-amber-700" />
                <span className="text-[9px] font-bold text-amber-800 uppercase tracking-wider">
                  Provenance lint ({section._lint.length} warning{section._lint.length === 1 ? '' : 's'})
                </span>
              </div>
              <ul className="text-[10px] text-amber-900 space-y-0.5">
                {section._lint.map((w, i) => (
                  <li key={i}><span className="font-mono text-[9px] text-amber-700">{w.code}</span>: {w.message}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Sprint 2.6 — specialized panels for sections that carry meeting-intel payloads */}
          {sectionKey === 'engagement_trend' && section.data?.stakeholder_drift && (
            <div className="border border-slate-100 rounded p-2">
              <div className="text-[9px] font-bold text-slate-600 uppercase tracking-wider mb-1.5">Stakeholder Drift</div>
              <StakeholderDriftPanel drift={section.data.stakeholder_drift} />
            </div>
          )}
          {sectionKey === 'dmu_changes' && Array.isArray(section.data?.corroborated_patterns) && section.data.corroborated_patterns.length > 0 && (
            <div className="border border-slate-100 rounded p-2">
              <div className="text-[9px] font-bold text-slate-600 uppercase tracking-wider mb-1.5">Corroborated Patterns (internal × external)</div>
              <CorroboratedPatternsPanel patterns={section.data.corroborated_patterns} />
            </div>
          )}

          {/* Section-specific structured data preview (raw JSON fallback) */}
          {section.data && Object.keys(section.data).length > 0 && (
            <details className="border border-slate-100 rounded">
              <summary className="cursor-pointer px-2 py-1 text-[10px] font-bold text-slate-600 hover:bg-slate-50">
                <Database size={9} className="inline mr-1" />
                Structured data ({Object.keys(section.data).length} field{Object.keys(section.data).length === 1 ? '' : 's'})
              </summary>
              <pre className="px-2 py-1.5 text-[9px] text-slate-700 bg-slate-50 overflow-x-auto leading-tight">{JSON.stringify(section.data, null, 2)}</pre>
            </details>
          )}

          {/* Source records */}
          <div className="pt-2 border-t border-slate-100">
            <div className="text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1.5">Source records ({section.source_records?.length || 0})</div>
            <SourceList sources={section.source_records || []} />
          </div>
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────
// Main page
// ─────────────────────────────────────────────────────────────────

export default function PulsePage() {
  const { bankKey } = useParams();
  const decodedKey = decodeURIComponent(bankKey);

  const [periods, setPeriods] = useState([]);
  const [period, setPeriod] = useState('2026-Q2');
  const [pulse, setPulse] = useState(null);
  const [pulseList, setPulseList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [confirming, setConfirming] = useState(false);

  const refreshPulseList = useCallback(async () => {
    try { setPulseList(await getBankPulses(decodedKey)); } catch { /* silent */ }
  }, [decodedKey]);

  // Load periods + existing pulses on mount
  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const [perRows, pulseRows] = await Promise.all([
          getReviewPeriods(),
          getBankPulses(decodedKey),
        ]);
        setPeriods(perRows);
        setPulseList(pulseRows);
        // If a pulse exists for the active period, load it
        const activePulse = pulseRows.find(p => p.period_id === period);
        if (activePulse) {
          const full = await getPulse(activePulse.id);
          setPulse(full);
        }
      } catch { /* silent */ }
      setLoading(false);
    })();
  }, [decodedKey, period]);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const fresh = await generatePulse(decodedKey, period);
      // The generate endpoint returns the pulse payload but we need the stored
      // row for id+overrides — re-fetch the list and pull the matching row.
      await refreshPulseList();
      const list = await getBankPulses(decodedKey);
      const stored = list.find(p => p.period_id === period);
      if (stored) {
        const full = await getPulse(stored.id);
        setPulse(full);
      } else {
        setPulse(fresh);
      }
    } catch (err) {
      alert('Generation failed: ' + err.message);
    } finally {
      setGenerating(false);
    }
  };

  const handleCellSaved = (cellPath, newVal) => {
    // Optimistic update — mutate the loaded pulse in place
    if (!pulse) return;
    const parts = cellPath.split('.');
    const next = JSON.parse(JSON.stringify(pulse));
    let target = next;
    for (let i = 0; i < parts.length - 1; i++) {
      target = target[parts[i]];
    }
    target[parts[parts.length - 1]] = newVal;
    setPulse(next);
  };

  const handleConfirm = async () => {
    if (!pulse) return;
    setConfirming(true);
    try {
      const r = await confirmPulse(pulse.id, 'demo-ae');
      setPulse({ ...pulse, confirmed_by_ae_at: r.confirmed_by_ae_at, confirmed_by_ae: r.confirmed_by_ae });
    } catch (err) {
      alert('Confirm failed: ' + err.message);
    } finally {
      setConfirming(false);
    }
  };

  const handleExport = (format) => {
    if (!pulse) return;
    const safeBank = String(decodedKey).replace(/[^a-z0-9_-]+/gi, '_');
    let content, mime, ext;
    if (format === 'json') {
      content = JSON.stringify(pulse, null, 2);
      mime = 'application/json';
      ext = 'json';
    } else if (format === 'html') {
      // B4 — HTML export designed for sharing with leadership. Self-contained,
      // print-friendly, every claim retains tier+grade+publisher inline.
      content = pulseToHtmlExport(pulse);
      mime = 'text/html';
      ext = 'html';
    } else {
      // Enriched markdown — drift + patterns rendered alongside synthesis,
      // lint warnings surfaced before each section's claims.
      content = pulseToMarkdownExport(pulse);
      mime = 'text/markdown';
      ext = 'md';
    }
    const filename = `${safeBank}_${pulse.period}_pulse.${ext}`;
    const blob = new Blob([content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = filename; a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="flex items-center gap-2 p-8 text-slate-500">
        <Loader2 size={16} className="animate-spin" /> Loading pulse…
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-4">
      {/* Header */}
      <div className="mb-4">
        <Link to={`/bank/${encodeURIComponent(decodedKey)}`} className="text-[10px] text-slate-500 hover:text-slate-900">← Back to bank profile</Link>
        <div className="flex items-center justify-between mt-1 flex-wrap gap-2">
          <div>
            <h1 className="text-xl font-black text-slate-900">{pulse?.bank_name || decodedKey}</h1>
            <p className="text-[11px] text-slate-500">Quarterly Pulse — Sales Ops review format</p>
          </div>
          <div className="flex items-center gap-2">
            <select value={period} onChange={e => setPeriod(e.target.value)}
              className="px-2 py-1.5 border border-slate-200 rounded text-xs">
              {periods.map(p => (
                <option key={p.id} value={p.id}>{p.id} ({p.starts_at} – {p.ends_at}){p.status === 'closed' ? ' [closed]' : ''}</option>
              ))}
            </select>
            <button onClick={handleGenerate} disabled={generating}
              className="inline-flex items-center gap-1 px-3 py-1.5 bg-blue-600 text-white text-xs font-bold rounded hover:bg-blue-700 disabled:opacity-50">
              {generating ? <Loader2 size={12} className="animate-spin" /> : <RefreshCw size={12} />}
              {pulse ? 'Regenerate' : 'Generate Pulse'}
            </button>
          </div>
        </div>
      </div>

      {!pulse ? (
        <div className="text-center py-12 bg-white border border-slate-200 rounded-lg">
          <p className="text-sm font-bold text-slate-700 mb-1">No pulse generated for {period} yet.</p>
          <p className="text-[11px] text-slate-500 mb-4">Click "Generate Pulse" to synthesize one from existing intelligence.</p>
        </div>
      ) : (
        <>
          {/* Summary bar */}
          <div className="flex items-center gap-3 mb-4 px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg flex-wrap">
            <div className="flex items-center gap-1.5">
              <Clock size={11} className="text-slate-400" />
              <span className="text-[10px] text-slate-600">Generated {formatDate(pulse.generated_at)}</span>
            </div>
            <div className="text-[10px] text-slate-300">·</div>
            <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${FRESHNESS_STYLE[pulse.freshness?.overall]?.bg} ${FRESHNESS_STYLE[pulse.freshness?.overall]?.color}`}>
              Freshness: {pulse.freshness?.overall}
            </span>
            <div className="text-[10px] text-slate-300">·</div>
            <span className="text-[10px] text-slate-600">
              {pulse.metrics?.total_source_records || 0} sources
              {' · '}
              {pulse.metrics?.sections_with_internal_data || 0} sections with internal data
              {' · '}
              {pulse.metrics?.total_signals_in_period || 0} signals in period
            </span>
            <div className="flex-1" />
            {pulse.confirmed_by_ae_at ? (
              <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-700">
                <CheckCircle size={11} /> Confirmed by {pulse.confirmed_by_ae} · {formatDate(pulse.confirmed_by_ae_at)}
              </span>
            ) : (
              <button onClick={handleConfirm} disabled={confirming}
                className="inline-flex items-center gap-1 px-2 py-1 bg-emerald-600 text-white text-[10px] font-bold rounded hover:bg-emerald-700 disabled:opacity-50">
                {confirming && <Loader2 size={10} className="animate-spin" />} <CheckCircle size={10} /> Confirm
              </button>
            )}
            <button onClick={() => handleExport('html')} title="Download as HTML — designed for sharing with leadership"
              className="px-2 py-1 bg-blue-600 text-white text-[10px] font-bold rounded hover:bg-blue-700">
              ⬇ HTML (share)
            </button>
            <button onClick={() => handleExport('md')} title="Download as Markdown — drift + patterns inline"
              className="px-2 py-1 bg-white border border-slate-200 text-slate-700 text-[10px] font-bold rounded hover:bg-slate-50">
              ⬇ MD
            </button>
            <button onClick={() => handleExport('json')} title="Download as JSON (full payload)"
              className="px-2 py-1 bg-white border border-slate-200 text-slate-700 text-[10px] font-bold rounded hover:bg-slate-50">
              ⬇ JSON
            </button>
          </div>

          {/* Sections */}
          {Object.entries(pulse.sections || {}).map(([key, section]) => (
            <SectionCard
              key={key}
              pulseId={pulse.id}
              sectionKey={key}
              section={section}
              onCellSaved={handleCellSaved}
            />
          ))}

          {/* AE overrides log */}
          {pulse.ae_overrides?.length > 0 && (
            <div className="mt-4 p-3 border border-amber-200 bg-amber-50 rounded">
              <div className="text-[10px] font-bold text-amber-700 uppercase tracking-wider mb-1.5">
                <AlertTriangle size={10} className="inline mr-1" />
                AE Overrides ({pulse.ae_overrides.length})
              </div>
              <div className="space-y-1">
                {pulse.ae_overrides.map(o => (
                  <div key={o.id} className="text-[10px] text-amber-900">
                    <span className="font-bold">{o.cell_path}</span>
                    {o.reason && <span className="text-amber-700 italic"> — {o.reason}</span>}
                    <span className="text-amber-500 ml-1">{formatDate(o.created_at)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

// pulseToMarkdown / pulseToHtml moved to ../utils/pulseExport.js (B4)
