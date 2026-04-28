/**
 * RegionProfileTab — restored + restructured region reference content
 * ───────────────────────────────────────────────────────────────────
 * Replaces the previous deprecated reference notice on MarketPage's
 * Context tab. Surfaces all 5 region-level reference fields (banking
 * landscape, regulations, digital maturity, consumer behavior, vendor
 * competitive landscape) plus market overview + key opportunities, all
 * grouped into thematic clusters mirroring the country-level layout.
 *
 * Visual treatment matches CountryProfileTab so AEs experience consistent
 * presentation across region and country pages.
 */

import { useState } from 'react';
import {
  ChevronDown, ChevronRight, Globe, Scale, Smartphone, Building2,
  Newspaper, Zap, Target, Search,
} from 'lucide-react';
import { SearchFallbackLink } from './SourceLink';

function Cluster({ title, icon: Icon, tone = 'slate', defaultOpen = true, count = null, subtitle = null, children }) {
  const [open, setOpen] = useState(defaultOpen);
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
      <button onClick={() => setOpen(!open)}
        className={`w-full flex items-center gap-2 px-3 py-2.5 ${TONE.bg} hover:brightness-95 transition-all text-left`}>
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
      {open && <div className="p-3 bg-white">{children}</div>}
    </div>
  );
}

function Subsection({ title, children, footer = null }) {
  return (
    <div className="mb-3 last:mb-0">
      <h4 className="text-[11px] font-bold text-slate-700 uppercase tracking-wide mb-1.5">{title}</h4>
      <div className="text-[12px] text-slate-700 leading-relaxed">{children}</div>
      {footer && <div className="mt-1.5">{footer}</div>}
    </div>
  );
}

export default function RegionProfileTab({ regionName, data }) {
  const oppCount = data.key_opportunities?.length || 0;

  return (
    <div>
      {/* Quick anchor strip */}
      <div className="mb-3 flex flex-wrap gap-1.5 text-[10px]">
        <span className="text-slate-500 mr-1 self-center">Jump to:</span>
        {[
          { id: 'rcluster-overview',     label: '🌐 Overview' },
          { id: 'rcluster-opportunity',  label: '🎯 Opportunities' },
          { id: 'rcluster-banking',      label: '🏛️ Banking' },
          { id: 'rcluster-regulatory',   label: '📜 Regulatory' },
          { id: 'rcluster-digital',      label: '📱 Digital' },
          { id: 'rcluster-consumer',     label: '👥 Consumer' },
          { id: 'rcluster-competitive',  label: '🏗️ Vendor Landscape' },
        ].map(s => (
          <a key={s.id} href={`#${s.id}`}
            className="inline-block px-2 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded transition-colors">
            {s.label}
          </a>
        ))}
      </div>

      {/* ───── Cluster 1: Overview narrative ───── */}
      <div id="rcluster-overview">
        <Cluster title={`${regionName} Market Overview`} icon={Globe} tone="slate" defaultOpen={true}>
          {data.market_overview ? (
            <div className="text-[12px] text-slate-700 leading-relaxed">
              {String(data.market_overview).split('\n').filter(p => p.trim()).map((p, i) => (
                <p key={i} className="mb-2 last:mb-0">{p}</p>
              ))}
            </div>
          ) : (
            <p className="text-[11px] text-slate-500 italic">No market overview narrative on file.</p>
          )}
        </Cluster>
      </div>

      {/* ───── Cluster 2: Key Opportunities ───── */}
      <div id="rcluster-opportunity">
        <Cluster title="Key Market Opportunities" icon={Target} tone="emerald" defaultOpen={true} count={oppCount || null}>
          {data.key_opportunities?.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {data.key_opportunities.map((o, i) => (
                <div key={i} className="p-3 bg-emerald-50/40 border border-emerald-200 rounded-lg">
                  <div className="text-[11px] font-bold text-emerald-700 mb-1">{o.title}</div>
                  <div className="text-[11px] text-slate-700 leading-relaxed">{o.detail}</div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-[11px] text-slate-500 italic">No opportunities cataloged for this region.</p>
          )}
        </Cluster>
      </div>

      {/* ───── Cluster 3: Banking landscape ───── */}
      <div id="rcluster-banking">
        <Cluster title="Banking Landscape" icon={Building2} tone="indigo" defaultOpen={true}>
          {data.banking_landscape ? (
            <Subsection
              title={`${regionName} Banking Sector`}
              footer={<SearchFallbackLink query={`${regionName} banking sector overview 2026`} label="Search latest sector reports" />}
            >
              <p>{data.banking_landscape}</p>
            </Subsection>
          ) : (
            <p className="text-[11px] text-slate-500 italic">No banking landscape data on file.</p>
          )}
        </Cluster>
      </div>

      {/* ───── Cluster 4: Regulatory ───── */}
      <div id="rcluster-regulatory">
        <Cluster title="Regulatory Environment" icon={Scale} tone="amber" defaultOpen={true}>
          {data.regulations ? (
            <Subsection
              title="Region-wide regulatory context"
              footer={<SearchFallbackLink query={`${regionName} banking regulations EU 2026`} label="Search regulatory updates" />}
            >
              <p>{data.regulations}</p>
            </Subsection>
          ) : (
            <p className="text-[11px] text-slate-500 italic">No regulatory data on file.</p>
          )}
        </Cluster>
      </div>

      {/* ───── Cluster 5: Digital maturity ───── */}
      <div id="rcluster-digital">
        <Cluster title="Digital Maturity" icon={Smartphone} tone="blue" defaultOpen={false}>
          {data.digital_maturity ? (
            <Subsection
              title="Digital banking maturity & adoption"
              footer={<SearchFallbackLink query={`${regionName} digital banking maturity 2026`} label="Search digital adoption data" />}
            >
              <p>{data.digital_maturity}</p>
            </Subsection>
          ) : (
            <p className="text-[11px] text-slate-500 italic">No digital maturity data on file.</p>
          )}
        </Cluster>
      </div>

      {/* ───── Cluster 6: Consumer behavior ───── */}
      <div id="rcluster-consumer">
        <Cluster title="Consumer Behavior" icon={Newspaper} tone="purple" defaultOpen={false}>
          {data.consumer_behavior ? (
            <Subsection
              title="Regional consumer banking behavior"
              footer={<SearchFallbackLink query={`${regionName} consumer banking behavior 2026`} label="Search consumer trends" />}
            >
              <p>{data.consumer_behavior}</p>
            </Subsection>
          ) : (
            <p className="text-[11px] text-slate-500 italic">No consumer behavior data on file.</p>
          )}
        </Cluster>
      </div>

      {/* ───── Cluster 7: Vendor competitive ───── */}
      <div id="rcluster-competitive">
        <Cluster title="Vendor Competitive Landscape" icon={Zap} tone="emerald" defaultOpen={false}>
          {data.competitive_landscape ? (
            <Subsection
              title="Backbase competitive context"
              footer={<SearchFallbackLink query={`Backbase ${regionName} competitive landscape`} label="Verify vendor positioning" />}
            >
              <p>{data.competitive_landscape}</p>
            </Subsection>
          ) : (
            <p className="text-[11px] text-slate-500 italic">No competitive landscape data on file.</p>
          )}
        </Cluster>
      </div>

      <div className="mt-4 text-[10px] text-slate-400 text-center">
        Region profile content is a curated reference layer. For real-time, source-traceable intelligence,
        see the <strong className="mx-1">🧠 Intelligence</strong> tab.
      </div>
    </div>
  );
}
