/**
 * PortfolioQueryPage — Sprint 5.3 / 5.4
 * ─────────────────────────────────────
 * Lets an AE compose structured queries across the portfolio without writing
 * SQL. Each predicate is one row in the builder; predicates AND together by
 * default. Results show matched banks + per-predicate trace so the AE can
 * see WHY each bank matched.
 *
 * The library is deliberately structured (not NL→SQL) so:
 *   - same query → same results, always
 *   - every match traces to the predicates that hit
 *   - no LLM in the query loop, no hallucinated banks
 *
 * Saved views (Sprint 5.4): named queries persisted server-side. Shareable
 * across the team — "open my deteriorating CFOs view" is a one-click.
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Loader2, Plus, X, Save, Trash2, Play, Sparkles, ChevronRight, BookmarkPlus, Bookmark, MessageSquare, Wand2,
} from 'lucide-react';
import {
  runPortfolioQuery, getPortfolioQueryExamples,
  listPortfolioSavedViews, createPortfolioSavedView, deletePortfolioSavedView,
  translatePortfolioQuery,
} from '../data/api';

const PREDICATE_DEFS = [
  {
    type: 'has_pattern',
    label: 'Has corroborated pattern',
    fields: [
      { key: 'grade',        label: 'Min grade',   type: 'select', options: ['A','B','C','D'], default: 'B' },
      { key: 'op',           label: 'Op',          type: 'select', options: ['eq','gte'],      default: 'gte', hidden: true },
      { key: 'topic',        label: 'Topic',       type: 'select', options: ['','budget','vendors','timeline','politics','technical','blockers','other'] },
      { key: 'confidence',   label: 'Confidence',  type: 'select', options: ['','high','medium','low'] },
      { key: 'within_days',  label: 'Within days', type: 'number', default: 60 },
    ],
  },
  {
    type: 'has_drift_trend',
    label: 'Stakeholder drift trend',
    fields: [
      { key: 'trend',     label: 'Trend',     type: 'select', options: ['improving','deteriorating','mixed'], default: 'deteriorating' },
      { key: 'topic',     label: 'Topic',     type: 'select', options: ['','budget','vendors','timeline','politics','technical','blockers','other'] },
      { key: 'min_facts', label: 'Min facts', type: 'number', default: 2 },
    ],
  },
  {
    type: 'has_signal',
    label: 'Has signal',
    fields: [
      { key: 'grade',       label: 'Min grade',   type: 'select', options: ['','A','B','C','D'] },
      { key: 'op',          label: 'Op',          type: 'select', options: ['eq','gte'], default: 'gte', hidden: true },
      { key: 'category',    label: 'Category',    type: 'select', options: ['','strategic','momentum','stakeholder','competitive','regulatory','market','internal'] },
      { key: 'severity',    label: 'Severity',    type: 'select', options: ['','urgent','attention','info'] },
      { key: 'within_days', label: 'Within days', type: 'number', default: 30 },
    ],
  },
  {
    type: 'pulse_score_change',
    label: 'Pulse score change',
    fields: [
      { key: 'section', label: 'Section', type: 'select', options: ['engagement_trend','market_signals','strategic_posture'], default: 'engagement_trend' },
      { key: 'op',      label: 'Op',      type: 'select', options: ['gte','lte','gt','lt'], default: 'lt' },
      { key: 'value',   label: 'Value',   type: 'number', default: 0 },
      { key: 'from',    label: 'From',    type: 'select', options: ['2026-Q1','2026-Q2','2026-Q3','2026-Q4'], default: '2026-Q1' },
      { key: 'to',      label: 'To',      type: 'select', options: ['2026-Q1','2026-Q2','2026-Q3','2026-Q4'], default: '2026-Q2' },
    ],
  },
  {
    type: 'has_meeting_fact',
    label: 'Has meeting fact',
    fields: [
      { key: 'topic',            label: 'Topic',            type: 'select', options: ['','budget','vendors','timeline','politics','technical','blockers','other'] },
      { key: 'sentiment',        label: 'Sentiment',        type: 'select', options: ['','positive','neutral','mixed','negative'] },
      { key: 'confidence_tier',  label: 'Confidence tier',  type: 'select', options: ['',1,2,3] },
      { key: 'within_days',      label: 'Within days',      type: 'number', default: 30 },
    ],
  },
  {
    type: 'country',
    label: 'Country',
    fields: [{ key: 'equals', label: 'Country', type: 'text', default: 'Sweden' }],
  },
  {
    type: 'qualification_score',
    label: 'Qualification score',
    fields: [
      { key: 'op',    label: 'Op',    type: 'select', options: ['gte','lte','gt','lt'], default: 'gte' },
      { key: 'value', label: 'Value', type: 'number', default: 6 },
    ],
  },
];

const DEFINITIONS_BY_TYPE = Object.fromEntries(PREDICATE_DEFS.map(d => [d.type, d]));

function defaultPredicate(type) {
  const def = DEFINITIONS_BY_TYPE[type];
  if (!def) return { type };
  const args = { type };
  for (const f of def.fields) {
    if (f.default !== undefined) args[f.key] = f.default;
  }
  return args;
}

function PredicateRow({ predicate, onChange, onRemove }) {
  const def = DEFINITIONS_BY_TYPE[predicate.type];
  if (!def) return null;
  const update = (k, v) => onChange({ ...predicate, [k]: v === '' ? undefined : v });

  return (
    <div className="flex items-start gap-2 p-2 bg-slate-50 border border-slate-200 rounded">
      <span className="text-[10px] font-bold text-slate-700 shrink-0 px-2 py-1 bg-white border border-slate-200 rounded">
        {def.label}
      </span>
      <div className="flex-1 flex flex-wrap gap-1.5">
        {def.fields.filter(f => !f.hidden).map(field => {
          const val = predicate[field.key];
          if (field.type === 'select') {
            return (
              <label key={field.key} className="flex items-center gap-1 text-[10px] text-slate-600">
                {field.label}:
                <select
                  value={val ?? ''}
                  onChange={e => update(field.key, e.target.value)}
                  className="text-[10px] border border-slate-200 rounded px-1 py-0.5 bg-white"
                >
                  {field.options.map(o => (
                    <option key={String(o)} value={o}>{o === '' ? '— any —' : String(o)}</option>
                  ))}
                </select>
              </label>
            );
          }
          if (field.type === 'number') {
            return (
              <label key={field.key} className="flex items-center gap-1 text-[10px] text-slate-600">
                {field.label}:
                <input
                  type="number"
                  value={val ?? ''}
                  onChange={e => update(field.key, e.target.value === '' ? undefined : parseFloat(e.target.value))}
                  className="w-16 text-[10px] border border-slate-200 rounded px-1 py-0.5 bg-white"
                />
              </label>
            );
          }
          return (
            <label key={field.key} className="flex items-center gap-1 text-[10px] text-slate-600">
              {field.label}:
              <input
                type="text"
                value={val ?? ''}
                onChange={e => update(field.key, e.target.value)}
                className="text-[10px] border border-slate-200 rounded px-1 py-0.5 bg-white"
              />
            </label>
          );
        })}
      </div>
      <button onClick={onRemove} className="shrink-0 p-1 text-slate-400 hover:text-rose-600">
        <X size={12} />
      </button>
    </div>
  );
}

function ResultsTable({ results }) {
  if (!results) return null;
  if (results.length === 0) return (
    <div className="p-6 text-center text-[11px] text-slate-500 italic">
      No banks match this filter. Loosen a predicate or check that the underlying data exists.
    </div>
  );
  return (
    <div className="border border-slate-200 rounded overflow-hidden">
      <table className="w-full text-[11px]">
        <thead className="bg-slate-100 text-slate-700 text-[10px] uppercase tracking-wider">
          <tr>
            <th className="text-left px-2 py-1.5">Bank</th>
            <th className="text-left px-2 py-1.5">Country</th>
            <th className="text-left px-2 py-1.5">Matched predicates</th>
            <th className="text-right px-2 py-1.5"></th>
          </tr>
        </thead>
        <tbody>
          {results.map(r => (
            <tr key={r.bank_key} className="border-t border-slate-100 hover:bg-slate-50">
              <td className="px-2 py-1.5 font-semibold text-slate-900">{r.bank_name}</td>
              <td className="px-2 py-1.5 text-slate-600">{r.country}</td>
              <td className="px-2 py-1.5">
                <div className="flex flex-wrap gap-1">
                  {r.matched_predicates.map((p, i) => (
                    <span key={i} className="inline-block px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-800 border border-emerald-200 text-[9px]">
                      {p.type}{p.topic ? `:${p.topic}` : ''}{p.trend ? `:${p.trend}` : ''}{p.severity ? `:${p.severity}` : ''}
                    </span>
                  ))}
                </div>
              </td>
              <td className="px-2 py-1.5 text-right">
                <Link to={`/bank/${encodeURIComponent(r.bank_key)}`}
                      className="inline-flex items-center gap-0.5 text-blue-700 hover:underline text-[10px]">
                  open <ChevronRight size={10} />
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function PortfolioQueryPage() {
  const [predicates, setPredicates] = useState([]);
  const [op] = useState('and');
  const [results, setResults] = useState(null);
  const [running, setRunning] = useState(false);
  const [examples, setExamples] = useState({});
  const [savedViews, setSavedViews] = useState([]);
  const [saveDialogOpen, setSaveDialogOpen] = useState(false);
  const [newViewName, setNewViewName] = useState('');
  // B3 — natural-language → predicate JSON state
  const [nlInput, setNlInput] = useState('');
  const [translating, setTranslating] = useState(false);
  const [nlResult, setNlResult] = useState(null); // { explanation, warnings, error? }

  useEffect(() => {
    getPortfolioQueryExamples().then(d => setExamples(d?.examples || {})).catch(() => {});
    refreshSavedViews();
  }, []);

  const refreshSavedViews = () => {
    listPortfolioSavedViews().then(d => setSavedViews(d?.views || [])).catch(() => setSavedViews([]));
  };

  const addPredicate = (type) => setPredicates(prev => [...prev, defaultPredicate(type)]);
  const updatePredicate = (i, p) => setPredicates(prev => prev.map((x, idx) => idx === i ? p : x));
  const removePredicate = (i) => setPredicates(prev => prev.filter((_, idx) => idx !== i));
  const clear = () => { setPredicates([]); setResults(null); };

  const loadExample = (key) => {
    const ex = examples[key];
    if (!ex) return;
    setPredicates(ex.filter.predicates || []);
    setResults(null);
  };

  const loadSavedView = (view) => {
    setPredicates(view.filter?.predicates || []);
    setResults(null);
  };

  // B3 — translate natural-language input → predicate JSON, then load into builder
  // The user always reviews/edits before clicking Run. Same query, same answer, always.
  const translate = async () => {
    if (!nlInput.trim()) return;
    setTranslating(true);
    setNlResult(null);
    try {
      const r = await translatePortfolioQuery(nlInput.trim());
      if (r.ok) {
        setPredicates(r.filter?.predicates || []);
        setResults(null);
        setNlResult({ explanation: r.explanation, warnings: r.warnings || [] });
      } else {
        setNlResult({ error: r.error, warnings: r.warnings || [] });
      }
    } catch (err) {
      setNlResult({ error: err.message || 'Translation failed' });
    } finally {
      setTranslating(false);
    }
  };

  const run = async () => {
    if (predicates.length === 0) return;
    setRunning(true);
    try {
      const d = await runPortfolioQuery({ op, predicates });
      setResults(d?.matched || []);
    } catch (err) {
      setResults([]);
    } finally {
      setRunning(false);
    }
  };

  const save = async () => {
    if (!newViewName.trim() || predicates.length === 0) return;
    await createPortfolioSavedView({ name: newViewName.trim(), filter: { op, predicates } });
    setNewViewName('');
    setSaveDialogOpen(false);
    refreshSavedViews();
  };

  const remove = async (id) => {
    await deletePortfolioSavedView(id);
    refreshSavedViews();
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-6">
      <div className="mb-4">
        <h1 className="text-2xl font-bold text-slate-900">Portfolio Query</h1>
        <p className="text-[12px] text-slate-600 mt-1">
          Compose structured filters across signals, meeting facts, patterns, drift, and pulse changes.
          Each result shows which predicates matched. Deterministic — same query, same answer, always.
        </p>
      </div>

      {/* B3 — Natural-language input. LLM maps phrasing → predicates. User reviews
           before running. The deterministic engine still runs the actual query. */}
      <div className="mb-4 p-3 border border-blue-200 bg-blue-50 rounded">
        <div className="flex items-center gap-1.5 mb-2">
          <Wand2 size={12} className="text-blue-700" />
          <span className="text-[11px] font-bold text-blue-900 uppercase tracking-wider">Ask in plain English</span>
          <span className="text-[10px] text-blue-700 font-normal">— translates to structured predicates you can review before running</span>
        </div>
        <div className="flex items-stretch gap-2">
          <input
            value={nlInput}
            onChange={e => setNlInput(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && !translating) translate(); }}
            placeholder='e.g. "Swedish banks where a CFO is deteriorating on budget" · "banks with a high-grade urgent signal in the last 30 days"'
            className="flex-1 text-[12px] border border-blue-300 rounded px-2.5 py-1.5 bg-white focus:outline-none focus:border-blue-500"
          />
          <button
            onClick={translate}
            disabled={translating || !nlInput.trim()}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white text-[11px] font-bold rounded"
          >
            {translating ? <Loader2 size={11} className="animate-spin" /> : <MessageSquare size={11} />}
            Translate
          </button>
        </div>
        {nlResult?.explanation && (
          <div className="mt-2 text-[11px] text-blue-900">
            <strong>Parsed as:</strong> {nlResult.explanation}
            {nlResult.warnings?.length > 0 && (
              <div className="mt-1 text-amber-800">
                <strong>Warnings:</strong> {nlResult.warnings.join(' · ')}
              </div>
            )}
            <div className="mt-1 text-blue-700 text-[10px] italic">
              Predicates loaded into the builder below. Review and edit, then click Run query.
            </div>
          </div>
        )}
        {nlResult?.error && (
          <div className="mt-2 text-[11px] text-rose-800 bg-rose-50 border border-rose-200 rounded px-2 py-1.5">
            <strong>Couldn't translate:</strong> {nlResult.error}
            {nlResult.warnings?.length > 0 && (
              <div className="mt-0.5 text-[10px]">{nlResult.warnings.join(' · ')}</div>
            )}
          </div>
        )}
      </div>

      {/* Quick-start: examples + saved views */}
      <div className="mb-4 grid grid-cols-1 md:grid-cols-2 gap-3">
        <div className="p-3 border border-slate-200 rounded bg-white">
          <div className="flex items-center gap-1.5 text-[10px] font-bold text-slate-700 uppercase tracking-wider mb-2">
            <Sparkles size={11} /> Examples
          </div>
          <div className="space-y-1">
            {Object.entries(examples).map(([key, ex]) => (
              <button key={key} onClick={() => loadExample(key)}
                className="block w-full text-left text-[11px] text-blue-700 hover:underline py-0.5">
                {ex.name}
              </button>
            ))}
            {Object.keys(examples).length === 0 && <div className="text-[10px] text-slate-500 italic">Loading…</div>}
          </div>
        </div>
        <div className="p-3 border border-slate-200 rounded bg-white">
          <div className="flex items-center gap-1.5 text-[10px] font-bold text-slate-700 uppercase tracking-wider mb-2">
            <Bookmark size={11} /> Saved views
          </div>
          {savedViews.length === 0 ? (
            <div className="text-[10px] text-slate-500 italic">None saved yet. Build a query and click "Save view."</div>
          ) : (
            <div className="space-y-1">
              {savedViews.map(v => (
                <div key={v.id} className="flex items-center justify-between gap-2">
                  <button onClick={() => loadSavedView(v)} className="text-[11px] text-blue-700 hover:underline">
                    {v.name}
                  </button>
                  <button onClick={() => remove(v.id)} className="p-0.5 text-slate-400 hover:text-rose-600">
                    <Trash2 size={10} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Filter builder */}
      <div className="mb-3 p-3 border border-slate-200 rounded bg-white">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[11px] font-bold text-slate-900 uppercase tracking-wider">
            Predicates ({predicates.length}) — combined with AND
          </span>
          <div className="flex items-center gap-1">
            <select onChange={e => { addPredicate(e.target.value); e.target.value = ''; }}
              className="text-[10px] border border-slate-200 rounded px-1.5 py-0.5 bg-white">
              <option value="">+ Add predicate…</option>
              {PREDICATE_DEFS.map(d => <option key={d.type} value={d.type}>{d.label}</option>)}
            </select>
            <button onClick={clear} disabled={predicates.length === 0}
              className="text-[10px] text-slate-500 hover:text-slate-800 px-1.5 py-0.5 disabled:opacity-40">
              Clear
            </button>
          </div>
        </div>
        {predicates.length === 0 ? (
          <div className="text-[11px] text-slate-500 italic py-3 text-center">
            No predicates. Add one to start, or click an example above.
          </div>
        ) : (
          <div className="space-y-1.5">
            {predicates.map((p, i) => (
              <PredicateRow key={i} predicate={p}
                onChange={(np) => updatePredicate(i, np)}
                onRemove={() => removePredicate(i)} />
            ))}
          </div>
        )}
      </div>

      <div className="flex items-center gap-2 mb-4">
        <button onClick={run} disabled={running || predicates.length === 0}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white text-[11px] font-bold rounded">
          {running ? <Loader2 size={11} className="animate-spin" /> : <Play size={11} />}
          Run query
        </button>
        <button onClick={() => setSaveDialogOpen(true)} disabled={predicates.length === 0}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 disabled:opacity-40 text-slate-700 text-[11px] font-bold rounded">
          <BookmarkPlus size={11} /> Save view
        </button>
        {results && (
          <span className="text-[11px] text-slate-600">
            {results.length} bank{results.length === 1 ? '' : 's'} matched
          </span>
        )}
      </div>

      {saveDialogOpen && (
        <div className="mb-4 p-3 border border-slate-300 bg-amber-50 rounded">
          <div className="flex items-center gap-2">
            <input value={newViewName} onChange={e => setNewViewName(e.target.value)}
              placeholder="Name this view (e.g. 'Deteriorating CFOs in Sweden')"
              className="flex-1 text-[11px] border border-slate-300 rounded px-2 py-1 bg-white" />
            <button onClick={save} disabled={!newViewName.trim()}
              className="inline-flex items-center gap-1 px-2 py-1 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-40 text-white text-[11px] font-bold rounded">
              <Save size={11} /> Save
            </button>
            <button onClick={() => setSaveDialogOpen(false)}
              className="px-2 py-1 text-slate-500 hover:text-slate-800 text-[11px]">
              Cancel
            </button>
          </div>
        </div>
      )}

      <ResultsTable results={results} />
    </div>
  );
}
