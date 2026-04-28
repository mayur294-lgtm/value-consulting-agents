import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, TrendingUp, Target, Building2, Globe } from 'lucide-react';
import { useMarket, useMarketBanks } from '../hooks/useData';
import { calcScoreFromData, scoreColor } from '../data/scoring';
import { LoadingState, ErrorState } from '../components/common/DataState';
import TabBar from '../components/common/TabBar';
import Section from '../components/common/Section';
import BarChart from '../components/charts/BarChart';
import RegionIntelDashboard from '../components/common/RegionIntelDashboard';

export default function MarketPage() {
  const { marketKey } = useParams();
  const navigate = useNavigate();
  const { data: marketData, isLoading, error } = useMarket(marketKey);
  const { data: marketBanks } = useMarketBanks(marketKey);

  if (isLoading) return <LoadingState message="Loading market..." />;
  if (error) return <ErrorState message={error.message} />;

  const meta = marketData;
  const data = marketData?.data;

  if (!meta || !data) {
    return (
      <div>
        <button onClick={() => navigate('/')} className="flex items-center gap-2 text-sm text-fg-muted hover:text-primary mb-4"><ArrowLeft size={16} /> Back</button>
        <p className="text-primary-700">Data for this market is being researched.</p>
      </div>
    );
  }

  // Compute scores and filter banks
  const banks = (marketBanks || []).map(b => ({
    ...b,
    name: b.bank_name,
    score: calcScoreFromData(b.qualification),
    qualification: b.data?.backbase_qualification || null,
  })).sort((a, b) => b.score - a.score);

  const qualifiedBanks = banks.filter(b => b.score >= 5).slice(0, 10);

  // Pipeline metrics
  const totalProspects = banks.filter(b => b.score >= 5).length;
  const avgScore = totalProspects > 0
    ? (banks.filter(b => b.score >= 5).reduce((sum, b) => sum + b.score, 0) / totalProspects).toFixed(1)
    : '—';
  const hotOpps = banks.filter(b => b.score >= 8).length;

  // Country pipeline aggregation
  const countryPipeline = data.countries.map(co => {
    const countryBanks = banks.filter(b => b.country === co.name);
    const prospects = countryBanks.filter(b => b.score >= 5);
    return {
      ...co,
      prospectCount: prospects.length,
      topScore: prospects.length > 0 ? Math.max(...prospects.map(b => b.score)) : 0,
      totalBanks: countryBanks.length,
    };
  }).sort((a, b) => b.prospectCount - a.prospectCount || b.topScore - a.topScore);

  /* ─── PRIORITIZE TAB ─── */
  const PrioritizeTab = () => (
    <div className="space-y-5">
      {/* Hero pipeline metrics */}
      <div className="grid grid-cols-3 gap-2">
        <div className="bg-surface border border-border rounded-xl p-3 text-center">
          <div className="text-2xl font-black text-primary">{totalProspects}</div>
          <div className="text-[9px] text-fg-muted uppercase tracking-wide">Prospects</div>
        </div>
        <div className="bg-surface border border-border rounded-xl p-3 text-center">
          <div className="text-2xl font-black text-success">{hotOpps}</div>
          <div className="text-[9px] text-fg-muted uppercase tracking-wide">Hot (8+)</div>
        </div>
        <div className="bg-surface border border-border rounded-xl p-3 text-center">
          <div className="text-2xl font-black text-primary-700">{avgScore}</div>
          <div className="text-[9px] text-fg-muted uppercase tracking-wide">Avg Score</div>
        </div>
      </div>

      {/* Countries ranked by pipeline value */}
      <div>
        <h3 className="text-xs font-bold text-fg-muted uppercase tracking-wide mb-2">Countries by Pipeline Strength</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
          {countryPipeline.map(co => (
            <div key={co.name}
              onClick={() => navigate(`/country/${encodeURIComponent(co.name)}`)}
              className="flex items-center gap-3 p-3 bg-surface border border-border rounded-lg cursor-pointer hover:border-primary/40 transition-all group">
              <div className="w-9 h-9 rounded-lg bg-primary/8 flex items-center justify-center shrink-0">
                <Building2 size={16} className="text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-bold text-sm text-fg">{co.name}</div>
                <div className="text-[10px] text-fg-muted">{co.prospectCount} prospects · {co.totalBanks} banks</div>
              </div>
              {co.topScore > 0 && (
                <span className="text-xs font-black px-2 py-0.5 rounded-full"
                  style={{ color: scoreColor(co.topScore), background: scoreColor(co.topScore) + '12' }}>
                  Top {co.topScore}
                </span>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Top opportunities across all countries */}
      {qualifiedBanks.length > 0 && (
        <div>
          <h3 className="text-xs font-bold text-fg-muted uppercase tracking-wide mb-2">Top Opportunities</h3>
          <div className="flex flex-col gap-1.5">
            {qualifiedBanks.map(b => (
              <div key={b.key}
                onClick={() => navigate(`/bank/${encodeURIComponent(b.key)}`)}
                className="flex items-center gap-3 p-3 bg-surface border border-border rounded-lg cursor-pointer hover:border-primary/40 transition-all">
                <span className="w-9 h-9 rounded-lg flex items-center justify-center font-extrabold text-sm shrink-0"
                  style={{ color: scoreColor(b.score), background: scoreColor(b.score) + '12' }}>{b.score}</span>
                <div className="flex-1 min-w-0">
                  <div className="font-bold text-xs text-fg truncate">{b.name}</div>
                  <div className="text-[10px] font-semibold truncate" style={{ color: scoreColor(b.score) }}>
                    {b.qualification?.label || ''}
                  </div>
                </div>
                <div className="text-right shrink-0">
                  <div className="text-[10px] font-semibold text-primary-700">{b.qualification?.deal_size || ''}</div>
                  <div className="text-[9px] text-fg-disabled">{b.country}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Score distribution */}
      {qualifiedBanks.length > 0 && (
        <Section title="Score Distribution" defaultOpen={false}>
          <BarChart items={qualifiedBanks.map(b => ({ name: b.name, score: b.score }))} height={qualifiedBanks.length * 32 + 40} />
        </Section>
      )}
    </div>
  );

  /* ─── CONTEXT TAB ─── */
  const ContextTab = () => (
    <div className="space-y-4">
      {/* Market narrative — condensed */}
      <div className="p-4 bg-surface border border-border rounded-xl">
        <p className="text-sm text-fg-subtle leading-relaxed">
          {data.market_overview.split('\n').map((p, i) => <span key={i}>{p}<br /><br /></span>)}
        </p>
      </div>

      {/* Market opportunity themes */}
      <div>
        <h3 className="text-xs font-bold text-fg-muted uppercase tracking-wide mb-2">Key Market Opportunities</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {data.key_opportunities.map((o, i) => (
            <div key={i} className="p-3 bg-primary-700/5 border border-primary-700/10 rounded-lg">
              <div className="font-bold text-xs text-primary-700 mb-1">{o.title}</div>
              <div className="text-[11px] text-fg-muted leading-relaxed">{o.detail}</div>
            </div>
          ))}
        </div>
      </div>

      {/* B2-style soft-deprecation: the 5 static reference sections (Banking
          Landscape, Regulations, Digital Maturity, Consumer Behavior, Vendor
          Competitive Landscape) were dense prose nobody read. Removed in
          favor of the data-driven Intelligence tab. */}
      <div className="p-3 bg-amber-50 border border-amber-200 rounded text-[11px] text-amber-900">
        <strong>Reference sections deprecated.</strong> The static prose blocks (Banking Landscape, Regulations,
        Digital Maturity, Consumer Behavior, Vendor Competitive Landscape) have been retired.
        For market intelligence with source provenance, use the <strong>🧠 Intelligence</strong> tab.
      </div>
    </div>
  );

  return (
    <div className="animate-fade-in-up">
      <button onClick={() => navigate('/')} className="flex items-center gap-2 text-sm text-fg-muted hover:text-primary mb-3 transition-colors">
        <ArrowLeft size={16} /> Back to Markets
      </button>

      {/* Compact header with inline KPIs */}
      <div className="flex items-start justify-between mb-1">
        <div>
          <div className="text-2xl mb-0.5">{meta.emoji}</div>
          <h2 className="text-xl font-black text-fg">{meta.name} Banking Market</h2>
        </div>
      </div>

      {/* Inline KPI badges */}
      <div className="flex gap-1.5 flex-wrap mb-4">
        {data.kpis.map((k, i) => (
          <span key={i} className="text-[9px] bg-surface border border-border rounded-full px-2.5 py-1 inline-flex items-center gap-1">
            <span className="text-fg-disabled">{k.label}:</span> <strong className="text-fg">{k.value}</strong>
          </span>
        ))}
      </div>

      {/* Task-based tabs — Intelligence is the default landing, replacing the
          static reference Context as the page's primary surface. */}
      <TabBar id="market-tabs" sticky tabs={[
        {
          label: '🧠 Intelligence',
          content: <RegionIntelDashboard kind="regions" identifier={marketKey} label={meta.name} />,
        },
        {
          label: '🎯 Prioritize',
          badge: totalProspects || null,
          content: <PrioritizeTab />,
        },
        {
          label: '🧭 Context',
          badge: data.key_opportunities?.length || null,
          content: <ContextTab />,
        },
      ]} />
    </div>
  );
}
