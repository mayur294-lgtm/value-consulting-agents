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
  Newspaper, Zap, ExternalLink, Search, AlertCircle, Sparkles, ShieldCheck,
} from 'lucide-react';
import FintechLandscapeGrid from './FintechLandscapeGrid';
import RegulatoryPanel from './RegulatoryPanel';
import MarketTrends from './MarketTrends';
import CustomerNeedsPanel from './CustomerNeedsPanel';
import CountryRefreshButton from './CountryRefreshButton';
import { SearchFallbackLink } from '../common/SourceLink';
import { normalizeProseField, uniqueSourceUrls } from '../../utils/proseField';

/**
 * Source coverage chip — surfaces the % of fact-claims in a section that
 * carry a source_url. Green ≥80%, amber 40-79%, red <40%, gray "no claims".
 * The agent populates `_source_coverage` post-parse (Sprint refresh).
 */
function SourceCoverageChip({ coverage }) {
  if (!coverage || coverage.total === 0) return null;
  const tone = coverage.pct >= 80 ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
             : coverage.pct >= 40 ? 'bg-amber-100 text-amber-800 border-amber-300'
             : 'bg-rose-100 text-rose-800 border-rose-300';
  const Icon = coverage.pct >= 80 ? ShieldCheck : AlertCircle;
  return (
    <span className={`inline-flex items-center gap-1 text-[9px] font-bold px-1.5 py-0.5 rounded border ${tone}`}
          title={`${coverage.sourced}/${coverage.total} fact-claims have a source URL`}>
      <Icon size={9} /> {coverage.sourced}/{coverage.total} sourced ({coverage.pct}%)
    </span>
  );
}

/**
 * Curated reference badge — for plain prose fields that don't carry sources.
 * Tells the AE this is curated content (not auto-validated) and links to a
 * verify-online search.
 */
function CuratedReferenceBadge() {
  return (
    <span className="inline-flex items-center gap-1 text-[9px] font-bold px-1.5 py-0.5 rounded border bg-slate-100 text-slate-700 border-slate-300"
          title="Curated reference content — not auto-validated. Use the verify-online link to confirm.">
      <Sparkles size={9} /> Curated reference
    </span>
  );
}

/**
 * One thematic cluster — colored accent header + collapsible body.
 * `tone` selects the accent palette.
 * Optional `coverage` shows a source-coverage chip; `lastRefreshed` shows freshness.
 */
function Cluster({ title, icon: Icon, tone = 'slate', defaultOpen = true, count = null, subtitle = null, coverage = null, curated = false, lastRefreshed = null, children }) {
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
        {coverage && <SourceCoverageChip coverage={coverage} />}
        {curated && <CuratedReferenceBadge />}
        {lastRefreshed && (
          <span className="text-[9px] text-slate-500 font-normal">
            refreshed {String(lastRefreshed).slice(0, 10)}
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
 * ProseSection — renders a normalized prose field with its sources inline.
 * If the field is the new {summary, sources, last_refreshed} shape:
 *   • Renders the summary paragraph
 *   • Shows a coverage chip (or "Curated reference" badge if no sources)
 *   • Lists the source URLs as clickable citations at the foot
 *   • Shows last_refreshed timestamp
 *
 * If the field is a legacy raw string:
 *   • Renders the string
 *   • Shows the "Curated reference" badge
 *   • Shows the search fallback link to verify online
 *
 * Either way the AE always has an action affordance.
 */
function ProseSection({ title, value, country, fallbackQuery, fallbackLabel }) {
  const norm = normalizeProseField(value);
  if (!norm.summary) return null;
  const sources = uniqueSourceUrls(norm.sources);

  return (
    <div className="mb-3 last:mb-0">
      <div className="flex items-center gap-2 mb-1.5">
        <h4 className="text-[11px] font-bold text-slate-700 uppercase tracking-wide">{title}</h4>
        {norm.isSourced ? (
          <SourceCoverageChip coverage={norm.coverage || { sourced: sources.length, total: sources.length, pct: 100 }} />
        ) : (
          <CuratedReferenceBadge />
        )}
        {norm.last_refreshed && (
          <span className="text-[9px] text-slate-500">refreshed {String(norm.last_refreshed).slice(0, 10)}</span>
        )}
      </div>
      <div className="text-[12px] text-slate-700 leading-relaxed">{norm.summary}</div>
      {sources.length > 0 && (
        <div className="mt-1.5 flex flex-wrap gap-1.5">
          <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wider self-center">Sources:</span>
          {sources.map((s, i) => (
            <a key={i} href={s.url} target="_blank" rel="noopener noreferrer"
               className="inline-flex items-center gap-0.5 text-[9px] text-blue-700 hover:underline px-1.5 py-0.5 bg-blue-50 rounded border border-blue-100"
               title={s.title || s.url}>
              <ExternalLink size={9} /> {s.source || 'source'} {s.date && `· ${String(s.date).slice(0, 7)}`}
            </a>
          ))}
        </div>
      )}
      {!norm.isSourced && fallbackQuery && (
        <div className="mt-1.5">
          <SearchFallbackLink query={fallbackQuery} label={fallbackLabel || 'Verify online'} />
        </div>
      )}
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

export default function CountryProfileTab({ country, data, sw, onRefreshed }) {
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
      {/* Refresh + freshness banner — surfaces source-traceability state */}
      <div className="mb-3 flex items-center justify-between gap-3 p-2.5 bg-slate-50 border border-slate-200 rounded-lg">
        <div className="text-[11px] text-slate-700">
          All country profile sections are now <strong>refreshable + source-traceable</strong>. Sourced sections
          show a <strong>shield chip</strong> with coverage % (X/Y fact-claims with source URLs). Sections still
          on legacy curated text show a <strong>"Curated reference" badge</strong> until refreshed. Click Refresh
          to pull latest news + sources for the structured sections; for full prose-field refresh use the CLI
          <code className="bg-white px-1 mx-1 rounded">npm run refresh-countries:prose</code>.
        </div>
        <div className="shrink-0">
          <CountryRefreshButton countryName={country} data={data} onRefreshed={onRefreshed} />
        </div>
      </div>

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

      {/* ───── Cluster 1: Macro Context (now refreshable prose) ───── */}
      <div id="cluster-macro">
        <Cluster title="Macro Context" icon={Globe} tone="slate" defaultOpen={true}>
          <TwoCol>
            <ProseSection title="Banking Sector" value={data.banking_sector} country={country}
              fallbackQuery={`${country} banking sector overview 2026`} fallbackLabel="Search latest sector reports" />
            <ProseSection title="Demographics" value={data.demographics} country={country}
              fallbackQuery={`${country} banking demographics population`} fallbackLabel="Search demographic data" />
          </TwoCol>
        </Cluster>
      </div>

      {/* ───── Cluster 2: Regulatory Landscape (auto-refreshed, sourced) ───── */}
      <div id="cluster-regulatory">
        <Cluster title="Regulatory Landscape" icon={Scale} tone="amber" defaultOpen={true}
          count={regCount || null}
          coverage={data.regulatory_environment?._source_coverage}
          lastRefreshed={data.regulatory_environment?.last_refreshed}>
          {data.regulatory_environment ? (
            <RegulatoryPanel data={data.regulatory_environment} countryName={country} />
          ) : (
            <p className="text-[11px] text-slate-500 italic">No regulatory data on file. <SearchFallbackLink query={`${country} banking regulator open banking AML`} label="Search regulators" /></p>
          )}
        </Cluster>
      </div>

      {/* ───── Cluster 3: Digital & Behavior — Customer Needs is sourced; Digital Banking is curated ───── */}
      <div id="cluster-digital">
        <Cluster title="Digital & Behavior" icon={Smartphone} tone="indigo" defaultOpen={true}
          count={cnCount + (data.digital_banking ? 1 : 0) || null}
          coverage={data.customer_needs?._source_coverage}
          lastRefreshed={data.customer_needs?.last_refreshed}>
          <ProseSection title="Digital Banking" value={data.digital_banking} country={country}
            fallbackQuery={`${country} digital banking adoption 2026`} fallbackLabel="Search digital banking news" />
          {data.customer_needs && (
            <Subsection title="Customer Needs · Adoption · Pain Points · Behavioral Shifts">
              <CustomerNeedsPanel data={data.customer_needs} countryName={country} />
            </Subsection>
          )}
        </Cluster>
      </div>

      {/* ───── Cluster 4: Competitive Landscape — Fintech is sourced; segments/spending are curated ───── */}
      <div id="cluster-competitive">
        <Cluster title="Competitive Landscape" icon={Building2} tone="purple" defaultOpen={false}
          count={fintechCount}
          coverage={data.fintech_landscape?._source_coverage}
          lastRefreshed={data.fintech_landscape?.last_refreshed}
          subtitle={data.fintech_landscape?.maturity_level ? `maturity: ${data.fintech_landscape.maturity_level}` : null}>
          {data.fintech_landscape && (
            <Subsection title="Fintech Landscape">
              <FintechLandscapeGrid data={data.fintech_landscape} countryName={country} />
            </Subsection>
          )}
          <TwoCol>
            <ProseSection title="Consumer Segments" value={data.consumer_segments} country={country}
              fallbackQuery={`${country} consumer banking segments`} fallbackLabel="Search segment data" />
            <ProseSection title="Spending Trends" value={data.spending_trends} country={country}
              fallbackQuery={`${country} consumer spending trends 2026`} fallbackLabel="Search spending data" />
          </TwoCol>
        </Cluster>
      </div>

      {/* ───── Cluster 5: Market Activity (auto-refreshed, sourced) ───── */}
      <div id="cluster-activity">
        <Cluster title="Market Activity · Trends + Recent Deals" icon={Newspaper} tone="blue" defaultOpen={false}
          count={trendCount || null}
          coverage={data.market_news?._source_coverage}
          lastRefreshed={data.market_news?.last_refreshed}>
          {data.market_news ? (
            <MarketTrends data={data.market_news} countryName={country} />
          ) : (
            <p className="text-[11px] text-slate-500 italic">No market news on file.</p>
          )}
        </Cluster>
      </div>

      {/* ───── Cluster 6: Backbase Angle (now refreshable) ───── */}
      <div id="cluster-backbase">
        <Cluster title="Backbase Angle · Signals + Market Strengths/Gaps" icon={Zap} tone="emerald" defaultOpen={true}
          count={(swotStrengths + swotWeaknesses) || null}>
          <ProseSection title="Backbase Signals & Opportunities" value={data.backbase_opportunities} country={country}
            fallbackQuery={`Backbase ${country} banking opportunity 2026`} fallbackLabel="Verify Backbase signals online" />

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
