/**
 * TimelinePage — dedicated full-screen Engagement & Execution Timeline view
 * ─────────────────────────────────────────────────────────────────────────
 * Reached from the "Execution Timeline" button on the bank profile (mirroring
 * the Pulse / Account Plan navigation pattern). Hosts the 4-lane × 2-horizon
 * action grid with more breathing room than the inline panel.
 */

import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, ExternalLink } from 'lucide-react';
import BankEngagementTimelinePanel from '../components/bank/BankEngagementTimelinePanel';
import { useBank } from '../hooks/useData';
import { LoadingState, ErrorState } from '../components/common/DataState';
import { parseBankKey } from '../data/scoring';

export default function TimelinePage() {
  const { bankKey } = useParams();
  const decoded = decodeURIComponent(bankKey);
  const { data: profile, isLoading, error } = useBank(decoded);

  if (isLoading) return <LoadingState message="Loading bank…" />;
  if (error) return <ErrorState message={error.message} />;

  const bankName = profile?.data?.bank_name || profile?.bank_name || parseBankKey(decoded).bankName;

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <div className="mb-3 flex items-center justify-between flex-wrap gap-2">
        <Link to={`/bank/${encodeURIComponent(decoded)}`}
          className="inline-flex items-center gap-1.5 text-[12px] text-slate-600 hover:text-slate-900">
          <ArrowLeft size={14} /> Back to {bankName}
        </Link>
        <Link to={`/account-plan/${encodeURIComponent(decoded)}`}
          className="inline-flex items-center gap-1 text-[11px] text-blue-700 hover:underline">
          Open Account Plan <ExternalLink size={11} />
        </Link>
      </div>

      <div className="mb-4">
        <h1 className="text-2xl font-bold text-slate-900">{bankName} — Execution Timeline</h1>
        <p className="text-[12px] text-slate-600 mt-1 max-w-3xl">
          Forward-looking <strong>60-day</strong> and <strong>90-day</strong> action plan composed from this bank's
          intelligence — power map, landing zones, account plan, signals, meeting facts, patterns,
          drift, intent score, opportunity windows, country regulatory pressure, and active VC engagement state.
          Every action traces to its source evidence. Re-generation preserves your customizations.
        </p>
      </div>

      <BankEngagementTimelinePanel bankKey={decoded} bankName={bankName} />
    </div>
  );
}
