/**
 * BankNotesPanel — shared AE+VC comment thread
 * ─────────────────────────────────────────────
 * Lightweight collaboration layer. Per-bank notes visible to both AE and
 * VC. Supports pinning + role tagging so AE-vs-VC perspective is clear.
 */

import { useEffect, useState } from 'react';
import { MessageCircle, Loader2, Trash2, Pin } from 'lucide-react';
import { fetchBankNotes, createBankNote, deleteBankNote } from '../../data/api';

const ROLE_TONE = {
  ae: 'bg-blue-100 text-blue-800 border-blue-300',
  vc: 'bg-purple-100 text-purple-800 border-purple-300',
  other: 'bg-slate-100 text-slate-700 border-slate-300',
};

function timeAgo(iso) {
  if (!iso) return '';
  const t = new Date(String(iso).replace(' ', 'T') + (String(iso).includes('T') ? '' : 'Z'));
  const diff = Date.now() - t.getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return days === 1 ? 'yesterday' : `${days}d ago`;
}

export default function BankNotesPanel({ bankKey }) {
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [draft, setDraft] = useState('');
  const [author, setAuthor] = useState('You');
  const [role, setRole] = useState('ae');
  const [submitting, setSubmitting] = useState(false);

  const refresh = () => {
    setLoading(true);
    fetchBankNotes(bankKey)
      .then(d => setNotes(d?.notes || []))
      .catch(() => setNotes([]))
      .finally(() => setLoading(false));
  };

  useEffect(refresh, [bankKey]);

  const submit = async (e) => {
    e?.preventDefault?.();
    if (!draft.trim()) return;
    setSubmitting(true);
    try {
      await createBankNote(bankKey, { author, author_role: role, body: draft.trim() });
      setDraft('');
      refresh();
    } finally {
      setSubmitting(false);
    }
  };

  const remove = async (id) => {
    if (!confirm('Delete this note?')) return;
    await deleteBankNote(id);
    refresh();
  };

  return (
    <div className="border border-slate-200 rounded-lg overflow-hidden bg-white mb-4">
      <div className="flex items-center justify-between px-3 py-2 bg-slate-50 border-b border-slate-200">
        <div className="flex items-center gap-1.5">
          <MessageCircle size={12} className="text-slate-700" />
          <span className="text-[11px] font-bold text-slate-900 uppercase tracking-wider">Bank Notes</span>
          <span className="text-[10px] text-slate-500">{notes.length} note{notes.length === 1 ? '' : 's'}</span>
        </div>
        {loading && <Loader2 size={11} className="animate-spin text-slate-500" />}
      </div>

      <form onSubmit={submit} className="p-3 border-b border-slate-100 bg-slate-50/50">
        <div className="flex items-center gap-2 mb-1.5 text-[10px]">
          <input value={author} onChange={e => setAuthor(e.target.value)}
            placeholder="Your name" className="flex-1 max-w-[160px] border border-slate-300 rounded px-2 py-1 bg-white" />
          <select value={role} onChange={e => setRole(e.target.value)}
            className="border border-slate-300 rounded px-2 py-1 bg-white">
            <option value="ae">AE</option>
            <option value="vc">VC</option>
            <option value="other">Other</option>
          </select>
        </div>
        <textarea value={draft} onChange={e => setDraft(e.target.value)} rows={2}
          placeholder="Add a note for the team — context, request, action…"
          className="w-full text-[11px] border border-slate-300 rounded px-2 py-1.5 bg-white resize-y" />
        <div className="flex justify-end mt-1.5">
          <button type="submit" disabled={submitting || !draft.trim()}
            className="inline-flex items-center gap-1 px-3 py-1 bg-slate-900 hover:bg-slate-800 disabled:opacity-40 text-white text-[10px] font-bold rounded">
            {submitting && <Loader2 size={10} className="animate-spin" />} Post note
          </button>
        </div>
      </form>

      {notes.length === 0 && !loading && (
        <div className="p-3 text-[11px] text-slate-500 italic">
          No notes yet. Use this thread for AE↔VC context, asks, and follow-ups visible to both sides.
        </div>
      )}

      {notes.map(n => (
        <div key={n.id} className={`p-3 border-b border-slate-100 last:border-b-0 ${n.pinned ? 'bg-amber-50/50' : ''}`}>
          <div className="flex items-center gap-1.5 mb-1 flex-wrap">
            <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded border ${ROLE_TONE[n.author_role] || ROLE_TONE.other}`}>
              {(n.author_role || 'OTHER').toUpperCase()}
            </span>
            <span className="text-[11px] font-semibold text-slate-900">{n.author}</span>
            <span className="text-[10px] text-slate-500">{timeAgo(n.created_at)}</span>
            {n.pinned ? <Pin size={9} className="text-amber-600" /> : null}
            <div className="flex-1" />
            <button onClick={() => remove(n.id)}
              className="text-slate-400 hover:text-rose-600">
              <Trash2 size={10} />
            </button>
          </div>
          <div className="text-[12px] text-slate-800 leading-snug whitespace-pre-wrap">{n.body}</div>
        </div>
      ))}
    </div>
  );
}
