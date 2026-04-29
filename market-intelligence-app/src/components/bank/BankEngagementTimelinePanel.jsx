/**
 * BankEngagementTimelinePanel — forward-looking action plan
 * ─────────────────────────────────────────────────────────
 * Renders the 60/90-day execution timeline as a 4-lane × 2-horizon grid.
 * Each action carries provenance (evidence chips), status (planned →
 * in_progress → done), and owner/due-date metadata.
 *
 * The "Regenerate" button re-runs the deterministic action generator,
 * preserving any actions the AE has moved to in_progress / done /
 * dropped, plus any custom-added actions.
 */

import { useEffect, useState } from 'react';
import {
  Loader2, RefreshCw, Plus, Sparkles, CheckCircle2, Clock, XCircle,
  Briefcase, Users, Megaphone, Handshake, ChevronDown, ChevronRight, Trash2,
} from 'lucide-react';
import {
  fetchBankTimeline, regenerateBankTimeline, updateTimelineAction,
  addTimelineAction, deleteTimelineAction,
} from '../../data/api';

const CATEGORY_META = {
  workshop:             { label: 'Workshops',          Icon: Briefcase, tone: 'border-amber-300 bg-amber-50/40',  accent: 'text-amber-700' },
  stakeholder_outreach: { label: 'Stakeholder Reach',  Icon: Users,     tone: 'border-blue-300 bg-blue-50/40',    accent: 'text-blue-700' },
  marketing_event:      { label: 'Marketing & Events', Icon: Megaphone, tone: 'border-purple-300 bg-purple-50/40', accent: 'text-purple-700' },
  partner_led:          { label: 'Partner-Led',        Icon: Handshake, tone: 'border-emerald-300 bg-emerald-50/40', accent: 'text-emerald-700' },
};

const HORIZONS = [
  { id: '60d', label: 'Next 60 days', color: 'text-rose-700' },
  { id: '90d', label: 'Next 60-90 days', color: 'text-slate-700' },
];

const STATUS_META = {
  planned:     { Icon: Clock,        tone: 'text-slate-600 bg-slate-100',  label: 'Planned' },
  in_progress: { Icon: Loader2,      tone: 'text-blue-700 bg-blue-100',    label: 'In progress' },
  done:        { Icon: CheckCircle2, tone: 'text-emerald-700 bg-emerald-100', label: 'Done' },
  dropped:     { Icon: XCircle,      tone: 'text-slate-400 bg-slate-50',   label: 'Dropped' },
};

function ActionCard({ action, onUpdate, onDelete }) {
  const [expanded, setExpanded] = useState(false);
  const [busy, setBusy] = useState(false);
  const status = STATUS_META[action.status] || STATUS_META.planned;
  const StatusIcon = status.Icon;
  const evidence = action.evidence || {};
  const evidenceCounts = Object.entries(evidence)
    .filter(([_, v]) => Array.isArray(v) ? v.length > 0 : Boolean(v))
    .map(([k, v]) => ({ kind: k, count: Array.isArray(v) ? v.length : 1 }));

  const setStatus = async (newStatus) => {
    setBusy(true);
    try { await onUpdate(action.id, { status: newStatus }); } finally { setBusy(false); }
  };

  const setOwner = async (e) => {
    const owner = e.target.value;
    setBusy(true);
    try { await onUpdate(action.id, { owner }); } finally { setBusy(false); }
  };

  const setDueDate = async (e) => {
    const due_date = e.target.value;
    setBusy(true);
    try { await onUpdate(action.id, { due_date }); } finally { setBusy(false); }
  };

  const fade = action.status === 'done' || action.status === 'dropped';

  return (
    <div className={`p-2 border border-slate-200 rounded-md bg-white ${fade ? 'opacity-60' : ''} text-[11px] shadow-sm`}>
      <div className="flex items-start gap-1.5 mb-1">
        <button onClick={() => setExpanded(!expanded)} className="flex-shrink-0 mt-0.5 text-slate-400 hover:text-slate-700">
          {expanded ? <ChevronDown size={11} /> : <ChevronRight size={11} />}
        </button>
        <div className="flex-1 min-w-0">
          <div className="font-semibold text-slate-900 leading-tight">{action.title}</div>
          {!action.is_auto_generated && (
            <span className="inline-block text-[8px] font-bold px-1 py-0.5 rounded bg-slate-200 text-slate-600 mt-0.5">CUSTOM</span>
          )}
        </div>
        <span className="flex-shrink-0 text-[8px] font-bold px-1 py-0.5 rounded bg-slate-100 text-slate-600">P{action.priority}</span>
      </div>

      {/* Status pill row */}
      <div className="flex items-center gap-1.5 flex-wrap mb-1.5">
        <select value={action.status} onChange={(e) => setStatus(e.target.value)} disabled={busy}
          className={`text-[9px] font-bold px-1.5 py-0.5 rounded border-0 cursor-pointer ${status.tone}`}>
          <option value="planned">Planned</option>
          <option value="in_progress">In progress</option>
          <option value="done">Done</option>
          <option value="dropped">Dropped</option>
        </select>
        {evidenceCounts.length > 0 && (
          <span className="inline-flex items-center gap-1 text-[9px] text-slate-500">
            evidence:
            {evidenceCounts.map(e => (
              <span key={e.kind} className="px-1 py-0.5 bg-slate-100 rounded text-slate-700">
                {e.kind.replace(/_/g, ' ')} ×{e.count}
              </span>
            ))}
          </span>
        )}
        {busy && <Loader2 size={9} className="animate-spin text-slate-400" />}
      </div>

      {expanded && (
        <div className="space-y-1.5 pt-1 border-t border-slate-100">
          {action.rationale && (
            <div className="text-[10px] text-slate-700 leading-snug italic">{action.rationale}</div>
          )}
          <div className="flex items-center gap-2 text-[10px] flex-wrap">
            <label className="flex items-center gap-1">
              <span className="text-slate-500">Owner:</span>
              <input
                type="text" defaultValue={action.owner || ''} onBlur={setOwner}
                placeholder="—" className="w-24 border border-slate-200 rounded px-1 py-0.5 bg-white" />
            </label>
            <label className="flex items-center gap-1">
              <span className="text-slate-500">Due:</span>
              <input
                type="date" defaultValue={action.due_date || ''} onChange={setDueDate}
                className="border border-slate-200 rounded px-1 py-0.5 bg-white text-[9px]" />
            </label>
            <button
              onClick={() => { if (confirm('Delete this action?')) onDelete(action.id); }}
              className="inline-flex items-center gap-0.5 text-rose-600 hover:underline ml-auto"
            >
              <Trash2 size={9} /> remove
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function CategoryRow({ category, actions, onUpdate, onDelete }) {
  const meta = CATEGORY_META[category];
  const Icon = meta.Icon;
  const grouped60 = actions.filter(a => a.horizon === '60d');
  const grouped90 = actions.filter(a => a.horizon === '90d');

  return (
    <div className={`grid grid-cols-1 md:grid-cols-[180px_1fr_1fr] gap-2 border ${meta.tone} rounded-md p-2 mb-2`}>
      <div className={`flex items-center gap-1.5 ${meta.accent} px-1`}>
        <Icon size={14} />
        <span className="text-[12px] font-bold">{meta.label}</span>
        <span className="text-[10px] text-slate-500">({actions.length})</span>
      </div>
      <div className="space-y-1.5">
        {grouped60.length === 0 ? (
          <div className="text-[10px] text-slate-400 italic px-2 py-1">No 60d actions</div>
        ) : grouped60.map(a => (
          <ActionCard key={a.id} action={a} onUpdate={onUpdate} onDelete={onDelete} />
        ))}
      </div>
      <div className="space-y-1.5">
        {grouped90.length === 0 ? (
          <div className="text-[10px] text-slate-400 italic px-2 py-1">No 90d actions</div>
        ) : grouped90.map(a => (
          <ActionCard key={a.id} action={a} onUpdate={onUpdate} onDelete={onDelete} />
        ))}
      </div>
    </div>
  );
}

function AddActionForm({ bankKey, onAdded }) {
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ category: 'workshop', horizon: '60d', title: '', rationale: '', owner: '', due_date: '', priority: 5 });
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    if (!form.title.trim()) return;
    setBusy(true);
    try {
      await addTimelineAction(bankKey, form);
      setForm({ category: 'workshop', horizon: '60d', title: '', rationale: '', owner: '', due_date: '', priority: 5 });
      setOpen(false);
      onAdded();
    } finally { setBusy(false); }
  };

  if (!open) {
    return (
      <button onClick={() => setOpen(true)}
        className="inline-flex items-center gap-1 text-[10px] text-blue-700 hover:bg-blue-50 px-2 py-1 rounded">
        <Plus size={11} /> Add custom action
      </button>
    );
  }

  return (
    <form onSubmit={submit} className="border border-slate-200 rounded-md p-2 bg-slate-50/40 text-[11px] mb-2">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-1.5 mb-1.5">
        <select value={form.category} onChange={e => setForm({ ...form, category: e.target.value })}
          className="border border-slate-300 rounded px-1.5 py-1 bg-white text-[10px]">
          {Object.entries(CATEGORY_META).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
        </select>
        <select value={form.horizon} onChange={e => setForm({ ...form, horizon: e.target.value })}
          className="border border-slate-300 rounded px-1.5 py-1 bg-white text-[10px]">
          <option value="60d">60d</option>
          <option value="90d">90d</option>
        </select>
        <input type="text" value={form.owner} onChange={e => setForm({ ...form, owner: e.target.value })}
          placeholder="Owner" className="border border-slate-300 rounded px-1.5 py-1 bg-white" />
        <input type="date" value={form.due_date} onChange={e => setForm({ ...form, due_date: e.target.value })}
          className="border border-slate-300 rounded px-1.5 py-1 bg-white" />
      </div>
      <input type="text" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })}
        placeholder="Action title (e.g., Co-host MD-only roundtable on AML modernization)"
        className="w-full border border-slate-300 rounded px-1.5 py-1 bg-white mb-1.5" />
      <textarea value={form.rationale} onChange={e => setForm({ ...form, rationale: e.target.value })}
        placeholder="Why this matters (2-3 sentences)" rows={2}
        className="w-full border border-slate-300 rounded px-1.5 py-1 bg-white text-[10px] mb-1.5" />
      <div className="flex items-center justify-end gap-1.5">
        <button type="button" onClick={() => setOpen(false)} className="text-[10px] text-slate-500 hover:text-slate-800">Cancel</button>
        <button type="submit" disabled={busy || !form.title.trim()}
          className="inline-flex items-center gap-1 px-2 py-1 bg-slate-900 hover:bg-slate-800 disabled:opacity-40 text-white text-[10px] font-bold rounded">
          {busy && <Loader2 size={9} className="animate-spin" />} Add
        </button>
      </div>
    </form>
  );
}

export default function BankEngagementTimelinePanel({ bankKey, bankName }) {
  const [actions, setActions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [regenerating, setRegenerating] = useState(false);
  const [meta, setMeta] = useState(null); // { intent, summary }

  const refresh = async () => {
    setLoading(true);
    try {
      const r = await fetchBankTimeline(bankKey);
      setActions(r?.actions || []);
    } finally { setLoading(false); }
  };

  useEffect(() => { if (bankKey) refresh(); }, [bankKey]);

  const regenerate = async () => {
    if (!confirm('Regenerate timeline? This refreshes auto-generated actions still in "Planned" state. Custom actions and any in-progress / done / dropped actions are preserved.')) return;
    setRegenerating(true);
    try {
      const r = await regenerateBankTimeline(bankKey);
      setActions(r?.actions || []);
      setMeta({ intent: r?.intent, summary: r?.summary });
    } finally { setRegenerating(false); }
  };

  const onUpdate = async (id, updates) => { await updateTimelineAction(id, updates); refresh(); };
  const onDelete = async (id) => { await deleteTimelineAction(id); refresh(); };

  return (
    <div className="border border-slate-200 rounded-lg overflow-hidden bg-white mb-4">
      <div className="flex items-center justify-between px-3 py-2 bg-slate-100 border-b border-slate-200 flex-wrap gap-2">
        <div className="flex items-center gap-1.5">
          <Sparkles size={12} className="text-slate-700" />
          <span className="text-[11px] font-bold text-slate-900 uppercase tracking-wider">Engagement & Execution Timeline</span>
          <span className="text-[10px] text-slate-500">· next 60 / 90 days</span>
        </div>
        <div className="flex items-center gap-2">
          {meta?.intent && (
            <span className="text-[10px] text-slate-500">
              intent: <strong>{meta.intent.score}/100 ({meta.intent.tier})</strong>
            </span>
          )}
          {loading && <Loader2 size={11} className="animate-spin text-slate-500" />}
          <button onClick={regenerate} disabled={regenerating}
            className="inline-flex items-center gap-1 px-2 py-1 text-[10px] font-bold text-blue-700 hover:bg-blue-50 rounded">
            {regenerating ? <Loader2 size={11} className="animate-spin" /> : <RefreshCw size={11} />}
            {actions.length === 0 ? 'Generate' : 'Regenerate'}
          </button>
        </div>
      </div>

      <div className="p-3">
        {actions.length === 0 && !loading && (
          <div className="text-[11px] text-slate-600 italic py-4 text-center">
            No timeline yet. Click <strong>Generate</strong> to compose a 60/90-day plan from this bank's
            intelligence (power map, landing zones, account plan, signals, facts, patterns, drift,
            opportunity windows). Each action will trace back to its source evidence.
          </div>
        )}

        {actions.length > 0 && (
          <>
            {/* Header row labels */}
            <div className="hidden md:grid grid-cols-[180px_1fr_1fr] gap-2 mb-1 px-2">
              <div></div>
              <div className="text-[10px] font-bold text-rose-700 uppercase tracking-wider">Next 60 days</div>
              <div className="text-[10px] font-bold text-slate-700 uppercase tracking-wider">Next 60-90 days</div>
            </div>

            {Object.keys(CATEGORY_META).map(cat => (
              <CategoryRow
                key={cat}
                category={cat}
                actions={actions.filter(a => a.category === cat)}
                onUpdate={onUpdate}
                onDelete={onDelete}
              />
            ))}

            <AddActionForm bankKey={bankKey} onAdded={refresh} />

            {meta?.summary && (
              <div className="mt-3 text-[9px] text-slate-500 italic">
                Generated {meta.summary.total_actions} actions · workshops {meta.summary.by_category.workshop || 0} · stakeholder {meta.summary.by_category.stakeholder_outreach || 0} · marketing {meta.summary.by_category.marketing_event || 0} · partner {meta.summary.by_category.partner_led || 0}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
