import { useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Check } from 'lucide-react';
import { useCountry, useCountryBanks } from '../hooks/useData';
import { calcScoreFromData, scoreColor, dataConfidenceFromData } from '../data/scoring';
import { getMarketForCountry } from '../data/utils';
import { LoadingState, ErrorState } from '../components/common/DataState';
import TabBar from '../components/common/TabBar';
import Section from '../components/common/Section';
import FilterPanel from '../components/common/FilterPanel';
import { ScoreBadge, ConfidenceBadge } from '../components/common/Badge';
import { useCompare } from '../context/CompareContext';
import BarChart from '../components/charts/BarChart';
import FintechLandscapeGrid from '../components/country/FintechLandscapeGrid';
import RegulatoryPanel from '../components/country/RegulatoryPanel';
import MarketTrends, { SectionSourcesFooter } from '../components/country/MarketTrends';
import CustomerNeedsPanel from '../components/country/CustomerNeedsPanel';
import CountryRefreshButton from '../components/country/CountryRefreshButton';
import { SearchFallbackLink } from '../components/common/SourceLink';
import RegionIntelDashboard from '../components/common/RegionIntelDashboard';
import CountryProfileTab from '../components/country/CountryProfileTab';

export default function CountryPage() {
  const { countryName } = useParams();
  const navigate = useNavigate();
  const country = decodeURIComponent(countryName);
  const { data: countryData, isLoading, error, refetch } = useCountry(country);
  const { data: countryBanks } = useCountryBanks(country);
  const marketKey = getMarketForCountry(country);
  const { toggle: toggleCompare, isSelected } = useCompare();
  const [filters, setFilters] = useState({ minScore: 0, maxScore: 10, confidence: 'all', hasPowerMap: false, dealSize: 'all', hasValueSelling: false, sortBy: 'score' });

  const handleRefreshed = useCallback(() => { refetch(); }, [refetch]);

  if (isLoading) return <LoadingState message="Loading country data..." />;
  if (error) return <ErrorState message={error.message} />;

  const data = countryData?.data;

  if (!data) {
    return (
      <div>
        <button onClick={() => navigate(marketKey ? `/market/${marketKey}` : '/')} className="flex items-center gap-2 text-sm text-fg-muted hover:text-primary mb-4"><ArrowLeft size={16} /> Back</button>
        <p className="text-primary-700">Data for {country} is being researched.</p>
      </div>
    );
  }

  // Build bank list with computed scores
  const allBanks = (countryBanks || []).map(b => ({
    key: b.key,
    name: b.bank_name,
    country: b.country,
    type: b.data?.backbase_qualification?.bank_type || '',
    total_assets: b.data?.operational_profile?.total_assets || '',
    score: calcScoreFromData(b.qualification),
    bankData: b.data,
    qualification: b.data?.backbase_qualification || null,
    _qualData: b.qualification,
    _valueSelling: b.value_selling,
  })).sort((a, b) => b.score - a.score);

  // Parse deal value helper
  const parseDealMin = (str) => {
    if (!str) return 0;
    const rangeM = str.match(/€([\d.]+)-([\d.]+)M/);
    if (rangeM) return parseFloat(rangeM[1]);
    const singleM = str.match(/€([\d.]+)M/);
    if (singleM) return parseFloat(singleM[1]);
    const kMatch = str.match(/€([\d.]+)K/);
    if (kMatch) return parseFloat(kMatch[1]) / 1000;
    return 0;
  };

  // Apply filters
  let filteredBanks = allBanks.filter(b => {
    if (b.score < filters.minScore) return false;
    if (b.score > filters.maxScore) return false;
    if (filters.confidence !== 'all') {
      const conf = dataConfidenceFromData(b.key, b.bankData);
      if (filters.confidence === 'deep' && conf.level !== 'deep') return false;
      if (filters.confidence === 'standard' && conf.level === 'preliminary') return false;
    }
    if (filters.hasPowerMap && !b._qualData?.power_map?.activated) return false;
    if (filters.hasValueSelling && !b._valueSelling) return false;
    if (filters.dealSize !== 'all') {
      const dealMin = parseDealMin(b.qualification?.deal_size);
      if (filters.dealSize === 'large' && dealMin < 10) return false;
      if (filters.dealSize === 'medium' && (dealMin < 3 || dealMin >= 10)) return false;
      if (filters.dealSize === 'small' && dealMin >= 3) return false;
    }
    return true;
  });

  // Apply sorting
  if (filters.sortBy === 'name') {
    filteredBanks.sort((a, b) => a.name.localeCompare(b.name));
  } else if (filters.sortBy === 'confidence') {
    const confOrder = { deep: 3, standard: 2, preliminary: 1 };
    filteredBanks.sort((a, b) => (confOrder[dataConfidenceFromData(b.key, b.bankData).level] || 0) - (confOrder[dataConfidenceFromData(a.key, a.bankData).level] || 0));
  }

  // Pipeline metrics
  const prospects = allBanks.filter(b => b.score >= 5);
  const hotBanks = allBanks.filter(b => b.score >= 8);
  const powerMaps = allBanks.filter(b => b._qualData?.power_map?.activated).length;
  const avgScore = prospects.length > 0
    ? (prospects.reduce((sum, b) => sum + b.score, 0) / prospects.length).toFixed(1)
    : '—';

  // Banks needing attention
  const needsAttention = allBanks.filter(b => {
    if (b.score < 6) return false;
    const conf = dataConfidenceFromData(b.key, b.bankData);
    return conf.level === 'preliminary' || (!b._qualData?.power_map?.activated && b.score >= 7);
  });

  const sw = data.strengths_weaknesses;
  const fintechCategories = data.fintech_landscape?.categories?.length || 0;
  const regulationCount = data.regulatory_environment?.key_regulations?.length || 0;
  const trendCount = (data.market_news?.trends?.length || 0) + (data.market_news?.recent_deals?.length || 0);

  /* ─── TARGET TAB ─── */
  const TargetTab = () => (
    <div className="space-y-4">
      {/* Pipeline hero metrics */}
      <div className="grid grid-cols-4 gap-2">
        <div className="bg-surface border border-border rounded-xl p-2.5 text-center">
          <div className="text-xl font-black text-primary">{prospects.length}</div>
          <div className="text-[8px] text-fg-muted uppercase tracking-wide">Prospects</div>
        </div>
        <div className="bg-surface border border-border rounded-xl p-2.5 text-center">
          <div className="text-xl font-black text-success">{hotBanks.length}</div>
          <div className="text-[8px] text-fg-muted uppercase tracking-wide">Hot (8+)</div>
        </div>
        <div className="bg-surface border border-border rounded-xl p-2.5 text-center">
          <div className="text-xl font-black text-primary-700">{powerMaps}</div>
          <div className="text-[8px] text-fg-muted uppercase tracking-wide">Power Maps</div>
        </div>
        <div className="bg-surface border border-border rounded-xl p-2.5 text-center">
          <div className="text-xl font-black text-fg">{avgScore}</div>
          <div className="text-[8px] text-fg-muted uppercase tracking-wide">Avg Score</div>
        </div>
      </div>

      {/* Needs attention callout */}
      {needsAttention.length > 0 && (
        <div className="p-3 bg-warning-subtle border border-warning/20 rounded-lg">
          <div className="text-[10px] font-bold text-warning uppercase tracking-wide mb-1">Needs Attention ({needsAttention.length})</div>
          <div className="flex flex-wrap gap-1.5">
            {needsAttention.map(b => (
              <span key={b.key}
                onClick={() => navigate(`/bank/${encodeURIComponent(b.key)}`)}
                className="text-[10px] bg-warning/10 text-fg-subtle px-2 py-0.5 rounded cursor-pointer hover:bg-warning/20 transition-colors">
                {b.name} ({b.score})
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Bank list with filters */}
      <FilterPanel onFilter={setFilters} initialFilters={filters} />

      <div className="flex flex-col lg:flex-row gap-5">
        {/* Pipeline sidebar */}
        {filteredBanks.filter(b => b.score >= 4).length > 0 && (
          <div className="lg:w-52 shrink-0">
            <div className="text-[10px] font-bold text-fg-muted uppercase tracking-wider mb-2">Pipeline Ranking</div>
            <div className="flex lg:flex-col gap-1 overflow-x-auto lg:overflow-x-visible pb-2 lg:pb-0 scrollbar-hide">
              {filteredBanks.filter(b => b.score >= 4).map(b => (
                <div key={b.key} onClick={() => navigate(`/bank/${encodeURIComponent(b.key)}`)}
                  className="flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer hover:translate-x-0.5 transition-all shrink-0 min-w-[170px] lg:min-w-0"
                  style={{ background: scoreColor(b.score) + '10' }}>
                  <span className="w-7 h-7 rounded-full flex items-center justify-center font-extrabold text-xs border-2 shrink-0"
                    style={{ color: scoreColor(b.score), borderColor: scoreColor(b.score), background: 'white' }}>{b.score}</span>
                  <div className="flex-1 min-w-0">
                    <div className="font-semibold text-xs text-fg truncate">{b.name}</div>
                    <div className="text-[10px] text-fg-muted">{b.qualification?.deal_size || ''}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        {/* Bank cards */}
        <div className="flex-1 min-w-0 flex flex-col gap-2">
          {filteredBanks.map(b => {
            const conf = dataConfidenceFromData(b.key, b.bankData);
            return (
              <div key={b.key} className="flex items-center gap-3 p-3 bg-surface border border-border rounded-lg hover:border-primary/30 transition-all cursor-pointer group"
                onClick={() => navigate(`/bank/${encodeURIComponent(b.key)}`)}>
                <button onClick={e => { e.stopPropagation(); toggleCompare(b.key); }}
                  className={`w-5 h-5 rounded border-2 flex items-center justify-center shrink-0 transition-colors ${isSelected(b.key) ? 'bg-primary border-primary' : 'border-border-strong hover:border-primary'}`}>
                  {isSelected(b.key) && <Check size={12} className="text-white" />}
                </button>
                <ScoreBadge score={b.score} />
                <div className="flex-1 min-w-0">
                  <div className="font-bold text-sm text-fg">{b.name}</div>
                  <div className="text-[10px] font-semibold" style={{ color: scoreColor(b.score) }}>{b.qualification?.label || ''}</div>
                  <div className="text-xs text-fg-muted">{b.type} {b.total_assets ? '• ' + b.total_assets : ''}</div>
                </div>
                <div className="flex items-center gap-1">
                  <ConfidenceBadge level={conf.level} />
                  {b._qualData?.power_map?.activated && <span className="w-5 h-5 rounded bg-primary text-white text-[10px] flex items-center justify-center" title="Power Map">✓</span>}
                </div>
                {b.bankData && <span className="text-[9px] font-bold text-primary bg-primary/8 px-2 py-0.5 rounded group-hover:bg-primary/15">DEEP DIVE</span>}
              </div>
            );
          })}
        </div>
      </div>

      {/* Score distribution — collapsible */}
      {allBanks.length > 0 && (
        <Section title="Score Distribution" defaultOpen={false}>
          <BarChart items={allBanks.slice(0, 10).map(b => ({ name: b.name, score: b.score }))} height={allBanks.slice(0, 10).length * 28 + 30} />
        </Section>
      )}
    </div>
  );

  /* ─── INTEL TAB (consolidated from old Pitch + Intel) ─── */
  const IntelTab = () => (
    <div className="space-y-1">
      {/* SWOT — moved from old Pitch tab */}
      {sw && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
          <div className="p-4 bg-primary-50 border border-primary/20 rounded-lg">
            <h4 className="text-[10px] font-bold text-primary uppercase tracking-wide mb-2">✓ Market Strengths</h4>
            <div className="flex flex-wrap gap-1">{sw.strengths.map((s, i) => <span key={i} className="text-[10px] bg-primary/8 text-fg-subtle px-2 py-0.5 rounded">{s}</span>)}</div>
          </div>
          <div className="p-4 bg-danger-subtle border border-danger/10 rounded-lg">
            <h4 className="text-[10px] font-bold text-danger uppercase tracking-wide mb-2">✗ Market Gaps (Our Opportunity)</h4>
            <div className="flex flex-wrap gap-1">{sw.weaknesses.map((w, i) => <span key={i} className="text-[10px] bg-danger/8 text-fg-subtle px-2 py-0.5 rounded">{w}</span>)}</div>
          </div>
        </div>
      )}
      {/* Backbase signals — moved from old Pitch tab */}
      {data.backbase_opportunities && (
        <div className="mb-3">
          <h3 className="text-xs font-bold text-fg-muted uppercase tracking-wide mb-2">Backbase Signals</h3>
          <div className="p-4 bg-primary-700/5 border border-primary-700/10 rounded-xl">
            <p className="text-xs text-fg-subtle leading-relaxed">{data.backbase_opportunities}</p>
            <div className="mt-2">
              <SearchFallbackLink
                query={`Backbase ${country} banking opportunity`}
                label="Verify Backbase signals online"
              />
            </div>
          </div>
        </div>
      )}
      {/* Country context sections — each with a "verify online" search fallback link */}
      {data.demographics && (
        <Section title="Demographics">
          <p className="text-sm text-fg-subtle leading-relaxed">{data.demographics}</p>
          <div className="mt-2"><SearchFallbackLink query={`${country} banking demographics population`} label="Search latest demographic data" /></div>
        </Section>
      )}
      {data.banking_sector && (
        <Section title="Banking Sector">
          <p className="text-sm text-fg-subtle leading-relaxed">{data.banking_sector}</p>
          <div className="mt-2"><SearchFallbackLink query={`${country} banking sector overview`} label="Search latest sector reports" /></div>
        </Section>
      )}
      {data.digital_banking && (
        <Section title="Digital Banking" defaultOpen={false}>
          <p className="text-sm text-fg-subtle leading-relaxed">{data.digital_banking}</p>
          <div className="mt-2"><SearchFallbackLink query={`${country} digital banking adoption`} label="Search digital banking news" /></div>
        </Section>
      )}
      {data.consumer_segments && (
        <Section title="Consumer Segments" defaultOpen={false}>
          <p className="text-sm text-fg-subtle leading-relaxed">{data.consumer_segments}</p>
          <div className="mt-2"><SearchFallbackLink query={`${country} consumer banking segments`} label="Search segment data" /></div>
        </Section>
      )}
      {data.spending_trends && (
        <Section title="Spending Trends" defaultOpen={false}>
          <p className="text-sm text-fg-subtle leading-relaxed">{data.spending_trends}</p>
          <div className="mt-2"><SearchFallbackLink query={`${country} consumer spending trends 2026`} label="Search spending data" /></div>
        </Section>
      )}

      {/* Aggregated sources for the whole country (top-level) */}
      <SectionSourcesFooter sources={data.sources || []} label={`All sources for ${country}`} />
    </div>
  );

  return (
    <div className="animate-fade-in-up">
      <button onClick={() => navigate(marketKey ? `/market/${marketKey}` : '/')} className="flex items-center gap-2 text-sm text-fg-muted hover:text-primary mb-3 transition-colors">
        <ArrowLeft size={16} /> Back
      </button>

      {/* Header with refresh button */}
      <div className="flex items-start justify-between mb-1">
        <h2 className="text-xl font-black text-fg">{country}</h2>
        <CountryRefreshButton countryName={country} data={data} onRefreshed={handleRefreshed} />
      </div>
      <p className="text-primary text-xs italic mb-2">{data.tagline}</p>

      {/* Inline KPI badges */}
      <div className="flex gap-1.5 flex-wrap mb-4">
        {(data.kpis || []).map((k, i) => (
          <span key={i} className="text-[9px] bg-surface border border-border rounded-full px-2.5 py-1 inline-flex items-center gap-1">
            <span className="text-fg-disabled">{k.label}:</span> <strong className="text-fg">{k.value}</strong>
          </span>
        ))}
      </div>

      {/* Three-tab layout: live intelligence (default), bank-filter UI,
          curated country profile (all reference content reorganized into
          6 thematic clusters with visual accents). */}
      <TabBar id="country-tabs" sticky tabs={[
        {
          label: '🧠 Intelligence',
          content: <RegionIntelDashboard kind="countries" identifier={country} label={country} />,
        },
        {
          label: '🎯 Target',
          badge: prospects.length || null,
          content: <TargetTab />,
        },
        {
          label: '📚 Country Profile',
          content: <CountryProfileTab country={country} data={data} sw={sw} />,
        },
      ]} />
    </div>
  );
}
