/**
 * QuickIntelCard — bank-at-a-glance card replacing the old identity row + 9 buttons.
 *
 * Shows: score, KPIs, timing, value hypothesis, risk — all in one compact card.
 * Two primary actions only. Everything else in overflow menu.
 */
import { useState, useEffect } from 'react';
import { MoreHorizontal, FileText, Clock, Presentation, LayoutDashboard, Plus, FileSpreadsheet, ChevronDown, Loader } from 'lucide-react';
import { Link } from 'react-router-dom';
import { scoreColor } from '../../data/scoring';
import { getBankStatus, updateBankStatus } from '../../data/api';
import Button from '../common/Button';

const STAGE_LABELS = {
  prospect: { label: 'Prospect', color: '#6B7280' },
  discovery: { label: 'Discovery', color: '#3B82F6' },
  qualification: { label: 'Qualification', color: '#7C3AED' },
  proof_of_value: { label: 'Proof of Value', color: '#2563EB' },
  negotiation: { label: 'Negotiation', color: '#D97706' },
  won: { label: 'Won', color: '#10B981' },
  lost: { label: 'Lost', color: '#EF4444' },
  disqualified: { label: 'Disqualified', color: '#9CA3AF' },
  watching: { label: 'Watching', color: '#F59E0B' },
};

function OverflowMenu({ bankKey, bankName, onQuickPrep, onBriefing, onPresentation, onDashboard, onIntel }) {
  const [open, setOpen] = useState(false);

  // B2 — Soft-deprecated (Strategic Repositioning brief): "5-Min Prep",
  // "Executive Brief", and "Presentation" generate prose competing directly
  // with Claude-in-a-chat. Removed from the menu surface; underlying API
  // endpoints remain alive (with Sunset headers from earlier sessions) for
  // any in-flight workflow. Use the structured Pulse export (HTML) for
  // leadership shares instead — it carries source provenance the prose
  // surfaces could not.
  const items = [
    { label: 'Dashboard', icon: LayoutDashboard, action: onDashboard },
    { label: 'Add Intel', icon: Plus, action: onIntel },
  ];

  return (
    <div className="relative">
      <button onClick={() => setOpen(!open)}
        className="p-2 rounded-lg hover:bg-surface-2 text-fg-muted transition-colors">
        <MoreHorizontal size={16} />
      </button>
      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute right-0 top-full mt-1 z-50 bg-surface border border-border rounded-lg shadow-lg py-1 min-w-[180px]">
            {items.map(item => (
              <button key={item.label}
                onClick={() => { item.action?.(); setOpen(false); }}
                className="w-full flex items-center gap-2.5 px-3 py-2 text-xs text-fg hover:bg-surface-2 transition-colors">
                <item.icon size={14} className="text-fg-muted" />
                {item.label}
              </button>
            ))}
            <div className="border-t border-border my-1" />
            <Link to={`/account-plan/${encodeURIComponent(bankKey)}`}
              onClick={() => setOpen(false)}
              className="w-full flex items-center gap-2.5 px-3 py-2 text-xs text-fg hover:bg-surface-2 transition-colors">
              <FileSpreadsheet size={14} className="text-fg-muted" />
              Full Account Plan
            </Link>
          </div>
        </>
      )}
    </div>
  );
}

function DealStageBadge({ bankKey }) {
  const [stage, setStage] = useState('prospect');
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getBankStatus(bankKey).then(s => { if (s.status) setStage(s.status); }).catch(() => {});
  }, [bankKey]);

  const handleChange = async (newStage) => {
    setLoading(true);
    try {
      await updateBankStatus(bankKey, { status: newStage, excluded: newStage === 'disqualified' || newStage === 'lost' });
      setStage(newStage);
    } catch { /* silent */ }
    setLoading(false);
    setOpen(false);
  };

  const cfg = STAGE_LABELS[stage] || STAGE_LABELS.prospect;

  return (
    <div className="relative">
      <button onClick={() => setOpen(!open)}
        className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[9px] font-bold border transition-colors hover:shadow-sm"
        style={{ borderColor: cfg.color + '40', color: cfg.color, backgroundColor: cfg.color + '10' }}>
        <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: cfg.color }} />
        {loading ? <Loader size={8} className="animate-spin" /> : cfg.label}
        <ChevronDown size={8} />
      </button>
      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute left-0 top-full mt-1 z-50 bg-surface border border-border rounded-lg shadow-lg py-1 min-w-[140px]">
            {Object.entries(STAGE_LABELS).filter(([k]) => k !== stage).map(([key, cfg]) => (
              <button key={key} onClick={() => handleChange(key)}
                className="w-full flex items-center gap-2 px-3 py-1.5 text-[10px] text-fg hover:bg-surface-2 transition-colors">
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: cfg.color }} />
                {cfg.label}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default function QuickIntelCard({
  bankKey, bankName, country, score, data, qualification,
  onPrepMeeting, onQuickPrep, onBriefing, onPresentation, onDashboard, onIntel,
}) {
  const op = data?.operational_profile;
  const q = data?.backbase_qualification;

  // Compact KPI display
  const kpis = [
    op?.total_assets && { label: 'Assets', value: op.total_assets },
    op?.total_customers && { label: 'Customers', value: op.total_customers },
    op?.cost_income_ratio && { label: 'C/I', value: op.cost_income_ratio },
    op?.roe && { label: 'ROE', value: op.roe },
    op?.employees && { label: 'Staff', value: op.employees },
  ].filter(Boolean).slice(0, 4);

  return (
    <div className="bg-surface border border-border rounded-xl p-4 sm:p-5 mb-4">
      {/* Row 1: Name + Score + Country + Overflow */}
      <div className="flex items-center gap-3 mb-3">
        <h1 className="text-lg sm:text-xl font-black text-fg truncate">{bankName}</h1>
        <span className="px-2.5 py-0.5 rounded-full text-sm font-black text-white shrink-0"
              style={{ backgroundColor: scoreColor(score) }}>
          {score.toFixed(1)}
        </span>
        <span className="text-xs text-fg-muted">{country}</span>
        <DealStageBadge bankKey={bankKey} />
        <div className="flex-1" />
        <OverflowMenu bankKey={bankKey} bankName={bankName}
          onQuickPrep={onQuickPrep} onBriefing={onBriefing}
          onPresentation={onPresentation} onDashboard={onDashboard} onIntel={onIntel} />
      </div>

      {/* Row 2: KPIs strip */}
      {kpis.length > 0 && (
        <div className="flex flex-wrap gap-x-4 gap-y-1 mb-3">
          {kpis.map((kpi, i) => (
            <div key={i} className="text-[10px]">
              <span className="text-fg-muted">{kpi.label}: </span>
              <span className="font-bold text-fg">{kpi.value}</span>
            </div>
          ))}
        </div>
      )}

      {/* Row 3: Timing + Risk (from qualification) */}
      {q && (
        <div className="flex flex-wrap gap-x-4 gap-y-1 mb-3 text-[10px]">
          {q.timing && <div><span className="text-fg-muted">Timing: </span><span className="text-fg">{q.timing}</span></div>}
          {q.deal_size && <div><span className="text-fg-muted">Deal: </span><span className="font-bold text-primary">{q.deal_size}</span></div>}
          {q.risk && <div><span className="text-fg-muted">Risk: </span><span className="text-fg">{typeof q.risk === 'string' ? q.risk.substring(0, 60) : ''}</span></div>}
        </div>
      )}

      {/* Row 4: Primary actions */}
      <div className="flex items-center gap-2 pt-2 border-t border-border flex-wrap">
        <Button variant="primary" onClick={onPrepMeeting}>
          Prepare for Meeting
        </Button>
        <Link to={`/account-plan/${encodeURIComponent(bankKey)}`}>
          <Button variant="secondary">
            Account Plan
          </Button>
        </Link>
        <Link to={`/bank/${encodeURIComponent(bankKey)}/timeline`}>
          <Button variant="secondary">
            Execution Timeline
          </Button>
        </Link>
        <Link to={`/bank/${encodeURIComponent(bankKey)}/pulse`}>
          <Button variant="secondary">
            Quarterly Pulse
          </Button>
        </Link>
      </div>
    </div>
  );
}
