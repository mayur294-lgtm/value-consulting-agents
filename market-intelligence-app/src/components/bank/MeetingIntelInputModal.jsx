/**
 * MeetingIntelInputModal — paste transcript or email thread, get facts
 * ─────────────────────────────────────────────────────────────────────
 * The /log-meeting and /log-email skills, surfaced as a single modal with
 * two tabs. AE pastes raw input, modal sends to ingest-transcript /
 * ingest-email API, displays the structured result.
 */

import { useState } from 'react';
import { X, Loader2, FileText, Mail, CheckCircle, AlertCircle } from 'lucide-react';
import { ingestTranscript, ingestEmailThread } from '../../data/api';

export default function MeetingIntelInputModal({ bankKey, onClose, onSaved }) {
  const [mode, setMode] = useState('transcript');  // 'transcript' | 'email'
  const [text, setText] = useState('');
  const [date, setDate] = useState('');
  const [meetingType, setMeetingType] = useState('client');
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const submit = async () => {
    if (!text.trim() || text.length < 50) {
      setError('Paste at least 50 characters of content.');
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      let r;
      if (mode === 'transcript') {
        r = await ingestTranscript(bankKey, {
          transcript: text,
          ...(date ? { meeting_date: date } : {}),
          meeting_type: meetingType,
        });
      } else {
        r = await ingestEmailThread(bankKey, {
          thread: text,
          ...(date ? { thread_date: date } : {}),
        });
      }
      setResult(r);
      if (onSaved) onSaved(r);
    } catch (err) {
      setError(err.message || 'Ingest failed');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto"
           onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200 sticky top-0 bg-white">
          <div className="flex items-center gap-2">
            <span className="text-[14px] font-bold text-slate-900">Log meeting intel</span>
            <span className="text-[10px] text-slate-500">Anti-hallucination guardrails active — speakers must match persons table, quotes verbatim</span>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-700">
            <X size={16} />
          </button>
        </div>

        {/* Mode tabs */}
        <div className="flex border-b border-slate-200">
          <button onClick={() => setMode('transcript')}
            className={`flex-1 flex items-center justify-center gap-1.5 py-2 text-[11px] font-bold ${
              mode === 'transcript' ? 'text-blue-700 border-b-2 border-blue-600 bg-blue-50/40' : 'text-slate-600 hover:bg-slate-50'
            }`}>
            <FileText size={12} /> Meeting Transcript
          </button>
          <button onClick={() => setMode('email')}
            className={`flex-1 flex items-center justify-center gap-1.5 py-2 text-[11px] font-bold ${
              mode === 'email' ? 'text-blue-700 border-b-2 border-blue-600 bg-blue-50/40' : 'text-slate-600 hover:bg-slate-50'
            }`}>
            <Mail size={12} /> Email Thread
          </button>
        </div>

        <div className="p-4 space-y-3">
          {/* Date + type */}
          <div className="flex items-center gap-2 text-[11px]">
            <label className="flex items-center gap-1">
              <span className="text-slate-600">Date:</span>
              <input type="date" value={date} onChange={e => setDate(e.target.value)}
                className="border border-slate-300 rounded px-2 py-1 bg-white" />
              <span className="text-slate-400 text-[10px]">(optional)</span>
            </label>
            {mode === 'transcript' && (
              <label className="flex items-center gap-1 ml-3">
                <span className="text-slate-600">Type:</span>
                <select value={meetingType} onChange={e => setMeetingType(e.target.value)}
                  className="border border-slate-300 rounded px-2 py-1 bg-white">
                  <option value="client">Client</option>
                  <option value="discovery">Discovery</option>
                  <option value="demo">Demo</option>
                  <option value="negotiation">Negotiation</option>
                  <option value="kickoff">Kickoff</option>
                  <option value="internal">Internal</option>
                </select>
              </label>
            )}
          </div>

          {/* Paste area */}
          <div>
            <label className="text-[11px] font-bold text-slate-700 uppercase tracking-wider">
              Paste {mode === 'transcript' ? 'transcript' : 'email thread'}
            </label>
            <textarea value={text} onChange={e => setText(e.target.value)} rows={14}
              placeholder={mode === 'transcript'
                ? 'Paste the Zoom/Teams/Otter transcript here. Speaker labels + plain prose both work.\n\nExample:\nFrank Vang-Jensen (CEO): We need to accelerate our platform consolidation...\nIan Smith (CFO): Agreed, but multi-country compliance is a structural concern...'
                : 'Paste the email thread (replies + headers). Standard "On X wrote:" markers work fine.\n\nExample:\nFrom: Bo Lykkegaard <bo@danskebank.dk>\nTo: oumaima@backbase.com\nSubject: Re: Replatforming follow-up\n\nThanks for the deck. We have some concerns about...'}
              className="w-full mt-1 text-[11px] font-mono border border-slate-300 rounded px-2 py-1.5 bg-white resize-y" />
            <div className="text-[10px] text-slate-500 mt-0.5">
              {text.length} characters · paste at least 50
            </div>
          </div>

          {error && (
            <div className="p-2 bg-rose-50 border border-rose-200 rounded text-[11px] text-rose-800 flex items-start gap-1.5">
              <AlertCircle size={11} className="mt-0.5 flex-shrink-0" /> {error}
            </div>
          )}

          {result && (
            <div className="p-3 bg-emerald-50 border border-emerald-200 rounded text-[11px] space-y-1.5">
              <div className="flex items-center gap-1.5 font-bold text-emerald-800">
                <CheckCircle size={12} /> Ingested · meeting id {result.meeting_id?.slice(0, 8)}…
              </div>
              <div className="text-emerald-900">
                <strong>{result.facts_extracted}</strong> facts extracted ·
                <strong> {result.facts_attributed}</strong> attributed (T1) ·
                <strong> {result.facts_extracted - result.facts_attributed}</strong> unattributed (T2)
              </div>
              <div className="text-emerald-900">
                <strong>Date:</strong> {result.metadata?.meeting_date} ·
                <strong> Outcome:</strong> {result.metadata?.outcome}
              </div>
              {result.metadata?.attendees && (
                <div className="text-emerald-900"><strong>Attendees:</strong> {result.metadata.attendees}</div>
              )}
              {result.metadata?.notes && (
                <div className="text-emerald-900 italic mt-1">"{result.metadata.notes}"</div>
              )}
              {result.facts_extracted === 0 && (
                <div className="text-amber-700 mt-1">
                  <AlertCircle size={11} className="inline mr-1" />
                  No facts extracted — likely no clear stakeholder claims OR speakers didn't match the persons table. Add stakeholders first, then re-paste.
                </div>
              )}
            </div>
          )}
        </div>

        <div className="flex items-center justify-end gap-2 px-4 py-3 border-t border-slate-200 sticky bottom-0 bg-white">
          <button onClick={onClose} className="px-3 py-1 text-[11px] text-slate-600 hover:text-slate-900">
            Close
          </button>
          {!result && (
            <button onClick={submit} disabled={submitting || text.length < 50}
              className="inline-flex items-center gap-1 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white text-[11px] font-bold rounded">
              {submitting && <Loader2 size={11} className="animate-spin" />}
              Ingest with Claude
            </button>
          )}
          {result && (
            <button onClick={() => { setResult(null); setText(''); setError(null); }}
              className="inline-flex items-center gap-1 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-800 text-[11px] font-bold rounded">
              Ingest another
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
