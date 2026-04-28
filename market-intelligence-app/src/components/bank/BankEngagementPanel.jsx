/**
 * BankEngagementPanel — AE↔VC bridge surface on bank profile
 * ──────────────────────────────────────────────────────────
 * Shows VC engagement state + artifacts on a bank's profile so AEs see
 * "VC engagement active" / "Capability assessment delivered" without
 * leaving Nova. Includes a Handoff button that creates an engagement +
 * persists snapshot.
 */

import { useEffect, useState } from 'react';
import {
  Briefcase, FileText, ExternalLink, Loader2, Plus, ArrowRight, CheckCircle, Clock,
} from 'lucide-react';
import { getBankEngagementSummary, handoffBank, transitionEngagement } from '../../data/api';

const STATE_TONE = {
  scoping: 'bg-slate-100 text-slate-700 border-slate-300',
  discovery: 'bg-blue-100 text-blue-800 border-blue-300',
  assessment: 'bg-amber-100 text-amber-800 border-amber-300',
  delivered: 'bg-emerald-100 text-emerald-800 border-emerald-300',
  closed: 'bg-slate-200 text-slate-600 border-slate-300',
};

const ARTIFACT_TYPE_ICON = {
  roi: '💰',
  capability_assessment: '📊',
  roadmap: '🗺️',
  presentation: '🎯',
  other: '📄',
};

const NEXT_STATE = {
  scoping: 'discovery',
  discovery: 'assessment',
  assessment: 'delivered',
  delivered: 'closed',
};

export default function BankEngagementPanel({ bankKey, bankName }) {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showHandoff, setShowHandoff] = useState(false);
  const [handoffForm, setHandoffForm] = useState({
    engagement_type: 'value_assessment',
    title: '',
    vc_lead: '',
    ae_lead: '',
  });
  const [submitting, setSubmitting] = useState(false);

  const refresh = () => {
    setLoading(true);
    getBankEngagementSummary(bankKey)
      .then(setSummary)
      .catch(() => setSummary(null))
      .finally(() => setLoading(false));
  };

  useEffect(refresh, [bankKey]);

  const handleHandoff = async () => {
    setSubmitting(true);
    try {
      await handoffBank(bankKey, {
        ...handoffForm,
        title: handoffForm.title || `${bankName} — ${handoffForm.engagement_type}`,
      });
      setShowHandoff(false);
      setHandoffForm({ engagement_type: 'value_assessment', title: '', vc_lead: '', ae_lead: '' });
      refresh();
    } catch (err) {
      alert(`Handoff failed: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  const advance = async (engagementId, currentState) => {
    const next = NEXT_STATE[currentState];
    if (!next) return;
    if (!confirm(`Advance engagement to "${next}"?`)) return;
    try {
      await transitionEngagement(engagementId, next);
      refresh();
    } catch (err) {
      alert(`Could not transition: ${err.message}`);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-[11px] text-slate-500 my-3">
        <Loader2 size={12} className="animate-spin" /> Loading engagement state…
      </div>
    );
  }

  return (
    <div className="border border-slate-200 rounded-lg overflow-hidden bg-white mb-4">
      <div className="flex items-center justify-between px-3 py-2 bg-slate-50 border-b border-slate-200">
        <div className="flex items-center gap-1.5">
          <Briefcase size={12} className="text-slate-700" />
          <span className="text-[11px] font-bold text-slate-900 uppercase tracking-wider">VC Engagement</span>
          {summary?.has_active_engagement && (
            <span className="text-[10px] font-bold text-emerald-700 px-1.5 py-0.5 bg-emerald-50 border border-emerald-300 rounded">
              ACTIVE
            </span>
          )}
        </div>
        <button onClick={() => setShowHandoff(!showHandoff)}
          className="inline-flex items-center gap-1 px-2 py-0.5 text-[10px] font-bold text-blue-700 hover:bg-blue-50 rounded">
          <Plus size={10} /> {showHandoff ? 'Cancel' : 'Hand off to VC'}
        </button>
      </div>

      {showHandoff && (
        <div className="p-3 bg-blue-50/50 border-b border-slate-200 text-[11px]">
          <div className="font-semibold text-slate-900 mb-2">New AE→VC Handoff</div>
          <div className="grid grid-cols-2 gap-2 mb-2">
            <label className="flex flex-col gap-1">
              <span className="text-[9px] font-bold text-slate-600 uppercase">Type</span>
              <select value={handoffForm.engagement_type}
                onChange={e => setHandoffForm({ ...handoffForm, engagement_type: e.target.value })}
                className="text-[11px] border border-slate-300 rounded px-2 py-1 bg-white">
                <option value="value_assessment">Value Assessment</option>
                <option value="ignite_inspire">Ignite Inspire</option>
                <option value="upgrade">Upgrade</option>
                <option value="roi_only">ROI only</option>
                <option value="capability_assessment">Capability assessment</option>
                <option value="other">Other</option>
              </select>
            </label>
            <label className="flex flex-col gap-1">
              <span className="text-[9px] font-bold text-slate-600 uppercase">Title</span>
              <input type="text" value={handoffForm.title}
                onChange={e => setHandoffForm({ ...handoffForm, title: e.target.value })}
                placeholder={`${bankName} — value assessment`}
                className="text-[11px] border border-slate-300 rounded px-2 py-1 bg-white" />
            </label>
            <label className="flex flex-col gap-1">
              <span className="text-[9px] font-bold text-slate-600 uppercase">VC Lead</span>
              <input type="text" value={handoffForm.vc_lead}
                onChange={e => setHandoffForm({ ...handoffForm, vc_lead: e.target.value })}
                placeholder="VC consultant name"
                className="text-[11px] border border-slate-300 rounded px-2 py-1 bg-white" />
            </label>
            <label className="flex flex-col gap-1">
              <span className="text-[9px] font-bold text-slate-600 uppercase">AE Lead</span>
              <input type="text" value={handoffForm.ae_lead}
                onChange={e => setHandoffForm({ ...handoffForm, ae_lead: e.target.value })}
                placeholder="Your name"
                className="text-[11px] border border-slate-300 rounded px-2 py-1 bg-white" />
            </label>
          </div>
          <button onClick={handleHandoff} disabled={submitting}
            className="inline-flex items-center gap-1 px-3 py-1 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white text-[11px] font-bold rounded">
            {submitting && <Loader2 size={10} className="animate-spin" />} Capture snapshot + create engagement
          </button>
          <div className="text-[9px] text-slate-500 mt-1.5">
            Snapshot captures: bank profile · stakeholders · meeting facts · drift · patterns · A/B-grade signals · latest Pulse.
          </div>
        </div>
      )}

      {!summary?.has_active_engagement && summary?.closed_count === 0 && (
        <div className="p-3 text-[11px] text-slate-500 italic">
          No VC engagements yet. Click "Hand off to VC" when ready to involve a value consultant.
        </div>
      )}

      {summary?.active_engagements?.map(eng => (
        <div key={eng.id} className="p-3 border-b border-slate-100 last:border-b-0">
          <div className="flex items-center gap-2 mb-1.5 flex-wrap">
            <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded border ${STATE_TONE[eng.state] || ''}`}>
              {eng.state}
            </span>
            <span className="text-[10px] text-slate-500">{eng.engagement_type}</span>
            <span className="text-[11px] font-semibold text-slate-900">{eng.title}</span>
            <div className="flex-1" />
            {NEXT_STATE[eng.state] && (
              <button onClick={() => advance(eng.id, eng.state)}
                className="inline-flex items-center gap-0.5 text-[10px] text-blue-700 hover:underline">
                advance to {NEXT_STATE[eng.state]} <ArrowRight size={9} />
              </button>
            )}
          </div>
          <div className="text-[10px] text-slate-500 flex items-center gap-2 flex-wrap">
            {eng.vc_lead && <span><strong>VC:</strong> {eng.vc_lead}</span>}
            {eng.ae_lead && <span><strong>AE:</strong> {eng.ae_lead}</span>}
            {eng.kickoff_date && <span><Clock size={9} className="inline" /> kickoff {eng.kickoff_date}</span>}
            {eng.target_close_date && <span>· target close {eng.target_close_date}</span>}
          </div>
        </div>
      ))}

      {summary?.artifact_count > 0 && (
        <div className="p-3 bg-emerald-50/30 border-t border-slate-200">
          <div className="text-[9px] font-bold text-slate-600 uppercase tracking-wider mb-1.5 flex items-center gap-1">
            <FileText size={10} /> Deliverables ({summary.artifact_count})
          </div>
          {summary.latest_artifact && (
            <div className="text-[11px] flex items-center gap-1.5">
              <span>{ARTIFACT_TYPE_ICON[summary.latest_artifact.artifact_type] || '📄'}</span>
              <span className="font-semibold text-slate-900">{summary.latest_artifact.title}</span>
              <span className="text-[10px] text-slate-500">· {summary.latest_artifact.artifact_type}</span>
              {summary.latest_artifact.content_url && (
                <a href={summary.latest_artifact.content_url} target="_blank" rel="noopener noreferrer"
                   className="ml-1 inline-flex items-center gap-0.5 text-blue-700 hover:underline text-[10px]">
                  <ExternalLink size={9} /> open
                </a>
              )}
            </div>
          )}
        </div>
      )}

      {summary?.closed_count > 0 && (
        <div className="px-3 py-1.5 text-[10px] text-slate-500 bg-slate-50 border-t border-slate-200">
          <CheckCircle size={9} className="inline mr-1" /> {summary.closed_count} closed engagement{summary.closed_count === 1 ? '' : 's'} on file
        </div>
      )}
    </div>
  );
}
