/**
 * CountryProfileTab — restored + restructured country reference content
 * ────────────────────────────────────────────────────────────────────
 * Replaces the previous "Reference (deprecated)" tab with a proper,
 * well-organized country profile. All 14 reference categories the user
 * cares about are surfaced here, grouped into 6 thematic clusters with
 * distinct visual accents so the eye can scan without reading.
 *
 * Clusters (top → bottom in natural reading order for AE prep):
 *   1. 🌍 Macro Context        — banking sector + demographics
 *   2. 📜 Regulatory Landscape — central bank, key regs, open banking, AML
 *   3. 📱 Digital & Behavior   — digital banking + customer needs (adoption,
 *                                unmet needs, pain points, behavioral shifts)
 *   4. 🏗️ Competitive Landscape — fintech ecosystem + consumer segments + spending
 *   5. 📰 Market Activity       — trends + recent deals & transactions
 *   6. ⚡ Backbase Angle        — Backbase signals + market strengths/opportunities
 *
 * Each cluster:
 *   • Colored header bar with icon
 *   • Default-open status appropriate to AE workflow (macro/reg/digital/Backbase
 *     open by default; longer reading material collapsed)
 *   • Subsections grouped naturally inside
 *   • "Verify online" search-fallback links where useful
 *
 * Reuses existing structured renderers (FintechLandscapeGrid,
 * RegulatoryPanel, MarketTrends, CustomerNeedsPanel) — they already do good
 * work on the data. This component is the layout/framing layer.
 */

import { useState } from 'react';
import {
  ChevronDown, ChevronRight, Globe, Scale, Smartphone, Building2,
  Newspaper, Zap, ExternalLink, Search,
} from 'lucide-react';
import FintechLandscapeGrid from './FintechLandscapeGrid';
import RegulatoryPanel from './RegulatoryPanel';
import MarketTrends from './MarketTrends';
import CustomerNeedsPanel from './CustomerNeedsPanel';
import { SearchFallbackLink } from '../common/SourceLink';

/**
 * One thematic cluster — colored accent header + collapsible body.
 * `tone` selects the accent palette.
 */
function Cluster({ title, icon: Icon, tone = 'slate', defaultOpen = true, count = null, subtitle = null, children }) {
  const [open, setOpen] = useState(defaultOpen);

  // Tailwind palette per cluster — distinct enough to scan, restrained enough
  // to coexist on the page. Borders and headers; bodies stay neutral white.
  const TONE = {
    slate:   { border: 'border-slate-300',   bg: 'bg-slate-50',    accent: 'text-slate-700' },
    indigo:  { border: 'border-indigo-300',  bg: 'bg-indigo-50',   accent: 'text-indigo-700' },
    emerald: { border: 'border-emerald-300', bg: 'bg-emerald-50',  accent: 'text-emerald-700' },
    amber:   { border: 'border-amber-300',   bg: 'bg-amber-50',    accent: 'text-amber-700' },
    purple:  { border: 'border-purple-300',  bg: 'bg-purple-50',   accent: 'text-purple-700' },
    blue:    { border: 'border-blue-300',    bg: 'bg-blue-50',     accent: 'text-blue-700' },
  }[tone] || { border: 'border-slate-300', bg: 'bg-slate-50', accent: 'text-slate-700' };

  return (
    <div className={`mb-3 border ${TONE.border} rounded-lg overflow-hidden bg-white`}>
      <button
        onClick={() => setOpen(!open)}
        className={`w-full flex items-center gap-2 px-3 py-2.5 ${TONE.bg} hover:brightness-95 transition-all text-left`}
      >
        {open ? <ChevronDown size={14} className={TONE.accent} /> : <ChevronRight size={14} className={TONE.accent} />}
        <Icon size={14} className={TONE.accent} />
        <span className={`flex-1 text-[13px] font-bold ${TONE.accent}`}>{title}</span>
        {count != null && (
          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full bg-white ${TONE.accent} border ${TONE.border}`}>
            {count}
          </span>
        )}
        {subtitle && <span className="text-[10px] text-slate-500 font-normal">{subtitle}</span>}
      </button>
      {open && (
        <div className="p-3 bg-white">
          {children}
        </div>
      )}
    </div>
  );
}

/**
 * Subsection inside a cluster — neutral, lighter visual weight than Cluster.
 * Used when a cluster has 2+ logical subdivisions.
 */
function Subsection({ title, children, footer = null }) {
  return (
    <div className="mb-3 last:mb-0">
      <h4 className="text-[11px] font-bold text-slate-700 uppercase tracking-wide mb-1.5">{title}</h4>
      <div className="text-[12px] text-slate-700 leading-relaxed">{children}</div>
      {footer && <div className="mt-1.5">{footer}</div>}
    </div>
  );
}

/**
 * Two-column grid for short paragraphs. Falls back to single column on narrow.
 */
function TwoCol({ children }) {
  return <div className="grid grid-cols-1 md:grid-cols-2 gap-4">{children}</div>;
}

// ──────────────────────────────────────────────────────────────────────
// Top-level component
// ──────────────────────────────────────────────────────────────────────

export default function CountryProfileTab({ country, data, sw }) {
  const fintechCount = data.fintech_landscape?.categories?.length || null;
  const regCount = (data.regulatory_environment?.key_regulations?.length || 0) +
                   (data.regulatory_environment?.aml_kyc ? 1 : 0);
  const trendCount = (data.market_news?.trends?.length || 0) +
                     (data.market_news?.recent_deals?.length || 0);
  const cnCount = ['digital_adoption', 'unmet_needs', 'customer_pain_points', 'behavioral_shifts']
    .filter(k => data.customer_needs?.[k]).length;
  const swotStrengths = sw?.strengths?.length || 0;
  const swotWeaknesses = sw?.weaknesses?.length || 0;

  return (
    <div>
      {/* Quick anchor strip — lets AE jump to a cluster without scrolling */}
      <div className="mb-3 flex flex-wrap gap-1.5 text-[10px]">
        <span className="text-slate-500 mr-1 self-center">Jump to:</span>
        {[
          { id: 'cluster-macro',       label: '🌍 Macro' },
          { id: 'cluster-regulatory',  label: '📜 Regulatory' },
          { id: 'cluster-digital',     label: '📱 Digital & Behavior' },
          { id: 'cluster-competitive', label: '🏗️ Competitive' },
          { id: 'cluster-activity',    label: '📰 Market Activity' },
          { id: 'cluster-backbase',    label: '⚡ Backbase Angle' },
        ].map(s => (
          <a key={s.id} href={`#${s.id}`}
            className="inline-block px-2 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded transition-colors">
            {s.label}
          </a>
        ))}
      </div>

      {/* ───── Cluster 1: Macro Context ───── */}
      <div id="cluster-macro">
        <Cluster title="Macro Context" icon={Globe} tone="slate" defaultOpen={true}>
          <TwoCol>
            {data.banking_sector && (
              <Subsection title="Banking Sector"
                footer={<SearchFallbackLink query={`${country} banking sector overview 2026`} label="Search latest sector reports" />}>
                <p>{data.banking_sector}</p>
              </Subsection>
            )}
            {data.demographics && (
              <Subsection title="Demographics"
                footer={<SearchFallbackLink query={`${country} banking demographics population`} label="Search demographic data" />}>
                <p>{data.demographics}</p>
              </Subsection>
            )}
          </TwoCol>
        </Cluster>
      </div>

      {/* ───── Cluster 2: Regulatory Landscape ───── */}
      <div id="cluster-regulatory">
        <Cluster title="Regulatory Landscape" icon={Scale} tone="amber" defaultOpen={true}
          count={regCount || null}
          subtitle={data.regulatory_environment?.last_refreshed ? `refreshed ${String(data.regulatory_environment.last_refreshed).slice(0, 10)}` : null}>
          {data.regulatory_environment ? (
            <RegulatoryPanel data={data.regulatory_environment} countryName={country} />
          ) : (
            <p className="text-[11px] text-slate-500 italic">No regulatory data on file. <SearchFallbackLink query={`${country} banking regulator open banking AML`} label="Search regulators" /></p>
          )}
        </Cluster>
      </div>

      {/* ───── Cluster 3: Digital & Behavior ───── */}
      <div id="cluster-digital">
        <Cluster title="Digital & Behavior" icon={Smartphone} tone="indigo" defaultOpen={true}
          count={cnCount + (data.digital_banking ? 1 : 0) || null}>
          {data.digital_banking && (
            <Subsection title="Digital Banking"
              footer={<SearchFallbackLink query={`${country} digital banking adoption 2026`} label="Search digital banking news" />}>
              <p>{data.digital_banking}</p>
            </Subsection>
          )}
          {data.customer_needs && (
            <Subsection title="Customer Needs · Adoption · Pain Points · Behavioral Shifts">
              <CustomerNeedsPanel data={data.customer_needs} countryName={country} />
            </Subsection>
          )}
        </Cluster>
      </div>

      {/* ───── Cluster 4: Competitive Landscape ───── */}
      <div id="cluster-competitive">
        <Cluster title="Competitive Landscape" icon={Building2} tone="purple" defaultOpen={false}
          count={fintechCount}
          subtitle={data.fintech_landscape?.maturity_level ? `maturity: ${data.fintech_landscape.maturity_level}` : null}>
          {data.fintech_landscape && (
            <Subsection title="Fintech Landscape">
              <FintechLandscapeGrid data={data.fintech_landscape} countryName={country} />
            </Subsection>
          )}
          <TwoCol>
            {data.consumer_segments && (
              <Subsection title="Consumer Segments"
                footer={<SearchFallbackLink query={`${country} consumer banking segments`} label="Search segment data" />}>
                <p>{data.consumer_segments}</p>
              </Subsection>
            )}
            {data.spending_trends && (
              <Subsection title="Spending Trends"
                footer={<SearchFallbackLink query={`${country} consumer spending trends 2026`} label="Search spending data" />}>
                <p>{data.spending_trends}</p>
              </Subsection>
            )}
          </TwoCol>
        </Cluster>
      </div>

      {/* ───── Cluster 5: Market Activity ───── */}
      <div id="cluster-activity">
        <Cluster title="Market Activity · Trends + Recent Deals" icon={Newspaper} tone="blue" defaultOpen={false}
          count={trendCount || null}
          subtitle={data.market_news?.last_refreshed ? `refreshed ${String(data.market_news.last_refreshed).slice(0, 10)}` : null}>
          {data.market_news ? (
            <MarketTrends data={data.market_news} countryName={country} />
          ) : (
            <p className="text-[11px] text-slate-500 italic">No market news on file.</p>
          )}
        </Cluster>
      </div>

      {/* ───── Cluster 6: Backbase Angle ───── */}
      <div id="cluster-backbase">
        <Cluster title="Backbase Angle · Signals + Market Strengths/Gaps" icon={Zap} tone="emerald" defaultOpen={true}
          count={(swotStrengths + swotWeaknesses) || null}>
          {data.backbase_opportunities && (
            <Subsection title="Backbase Signals & Opportunities"
              footer={<SearchFallbackLink query={`Backbase ${country} banking opportunity 2026`} label="Verify Backbase signals online" />}>
              <p>{data.backbase_opportunities}</p>
            </Subsection>
          )}
          {sw && (
            <Subsection title="Market SWOT — Strengths & Gaps">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-1">
                <div className="p-3 bg-emerald-50/50 border border-emerald-200 rounded-lg">
                  <h5 className="text-[10px] font-bold text-emerald-700 uppercase tracking-wide mb-1.5">✓ Market Strengths</h5>
                  <div className="flex flex-wrap gap-1">
                    {sw.strengths.map((s, i) => (
                      <span key={i} className="text-[10px] bg-emerald-100 text-emerald-900 px-2 py-0.5 rounded">{s}</span>
                    ))}
                  </div>
                </div>
                <div className="p-3 bg-rose-50/50 border border-rose-200 rounded-lg">
                  <h5 className="text-[10px] font-bold text-rose-700 uppercase tracking-wide mb-1.5">✗ Market Gaps (our opportunity)</h5>
                  <div className="flex flex-wrap gap-1">
                    {sw.weaknesses.map((w, i) => (
                      <span key={i} className="text-[10px] bg-rose-100 text-rose-900 px-2 py-0.5 rounded">{w}</span>
                    ))}
                  </div>
                </div>
              </div>
            </Subsection>
          )}
        </Cluster>
      </div>

      <div className="mt-4 text-[10px] text-slate-400 text-center">
        Country profile content is a curated reference layer. For real-time, source-traceable intelligence, see the
        <strong className="mx-1">🧠 Intelligence</strong> tab.
      </div>
    </div>
  );
}
