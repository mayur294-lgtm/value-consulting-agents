/**
 * Pulse Export — B4 (post-Sprint-5)
 * ─────────────────────────────────
 * Converts a Pulse payload into shareable formats designed for leadership
 * consumption: clean HTML (the primary share format) and enriched markdown
 * (the AE-friendly archive format).
 *
 * Design principles:
 *   • Self-contained HTML — single file, inline CSS, no external assets
 *   • Every claim retains its provenance — tier + grade + date + publisher
 *     spelled out inline (since hover isn't available in print/PDF)
 *   • Drift + patterns rendered alongside the section synthesis they belong
 *     to, not buried in raw JSON
 *   • Lint warnings surfaced at the top of each section so reader knows
 *     where the synthesis is or isn't defensible
 *   • No prose drift — the export carries what the Pulse already contains,
 *     no LLM in this export loop
 */

const SECTION_LABELS = {
  strategic_posture:     'Strategic Posture',
  quarterly_execution:   'Quarterly Execution',
  market_signals:        'Market Signals',
  engagement_trend:      'Engagement Trend',
  dmu_changes:           'DMU Changes',
  budget_cycles:         'Budget Cycles',
  blockers_asks_actions: 'Blockers / Asks / Actions',
};

const TIER_LABEL = { 1: 'Verified', 2: 'Inferred', 3: 'Estimated' };
const FRESHNESS_LABEL = { green: '🟢 Green', yellow: '🟡 Yellow', stale: '🔴 Stale' };

function fmt(d) {
  if (!d) return '—';
  try {
    const dt = new Date(String(d).replace(' ', 'T') + (String(d).includes('T') ? '' : 'Z'));
    if (isNaN(dt)) return String(d).slice(0, 10);
    return dt.toLocaleDateString('en-US', { day: '2-digit', month: 'short', year: 'numeric' });
  } catch { return String(d).slice(0, 10); }
}

function escHtml(s) {
  if (s == null) return '';
  return String(s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

// ──────────────────────────────────────────────────────────────────────
// Markdown export — enriched with drift + patterns inline
// ──────────────────────────────────────────────────────────────────────

export function pulseToMarkdown(pulse) {
  const lines = [];
  const m = pulse.metrics || {};

  lines.push(`# ${pulse.bank_name} — Quarterly Pulse · ${pulse.period}`);
  lines.push('');
  lines.push(`**Period**: ${pulse.period_starts_at} → ${pulse.period_ends_at}  `);
  lines.push(`**Generated**: ${fmt(pulse.generated_at)}  `);
  lines.push(`**Overall freshness**: ${FRESHNESS_LABEL[pulse.freshness?.overall] || pulse.freshness?.overall}  `);
  if (pulse.confirmed_by_ae_at) {
    lines.push(`**Confirmed by**: ${pulse.confirmed_by_ae} on ${fmt(pulse.confirmed_by_ae_at)}  `);
  }
  lines.push(`**Source records**: ${m.total_source_records || 0} · **Lint warnings**: ${m.lint_warning_count || 0} · **Internal sections**: ${m.sections_with_internal_data || 0}`);
  lines.push('');
  lines.push('---');
  lines.push('');

  for (const [key, sec] of Object.entries(pulse.sections || {})) {
    lines.push(`## ${SECTION_LABELS[key] || key}`);
    lines.push(`*Freshness: ${FRESHNESS_LABEL[sec.freshness] || sec.freshness}*`);
    lines.push('');

    // Lint warnings — surface BEFORE synthesis so reader knows where to be careful
    if (Array.isArray(sec._lint) && sec._lint.length > 0) {
      lines.push(`> ⚠️ **Provenance lint** (${sec._lint.length} warning${sec._lint.length === 1 ? '' : 's'}):`);
      sec._lint.forEach(w => lines.push(`> - \`${w.code}\`: ${w.message}`));
      lines.push('');
    }

    lines.push(sec.synthesis || '_(no synthesis)_');
    lines.push('');

    if (sec.diff_vs_previous && !/no prior pulse/i.test(sec.diff_vs_previous)) {
      lines.push(`**Δ vs previous**: ${sec.diff_vs_previous}`);
      lines.push('');
    }

    // Section-specific structured payloads — surface inline, not hidden
    const drift = sec.data?.stakeholder_drift;
    if (drift && (drift.improving?.length || drift.deteriorating?.length || drift.mixed?.length || drift.new_positions?.length)) {
      lines.push(`### Stakeholder drift`);
      ['improving', 'deteriorating', 'mixed', 'new_positions'].forEach(bucket => {
        const items = drift[bucket] || [];
        if (items.length === 0) return;
        const label = bucket === 'new_positions' ? 'New positions' : bucket.charAt(0).toUpperCase() + bucket.slice(1);
        lines.push(`**${label}** (${items.length}):`);
        items.forEach(c => {
          const last = c.series?.[c.series.length - 1];
          lines.push(`- **${c.speaker_name}**${c.speaker_role ? ` · ${c.speaker_role}` : ''} on **${c.topic}** → ${c.trend}${c.n_facts > 1 ? ` (n=${c.n_facts})` : ''}`);
          if (last?.position) lines.push(`  - "${last.position}"`);
          if (last?.evidence_quote) lines.push(`  - *Verbatim: "${last.evidence_quote}"*`);
        });
        lines.push('');
      });
    }

    const patterns = sec.data?.corroborated_patterns;
    if (Array.isArray(patterns) && patterns.length > 0) {
      lines.push(`### Corroborated patterns (${patterns.length})`);
      patterns.forEach(p => {
        const gap = p.gap_days >= 0
          ? `signal ${p.gap_days}d after meeting`
          : `signal ${Math.abs(p.gap_days)}d before meeting (reactive)`;
        lines.push(`- **${p.type}** · *${p.topic}* · confidence: ${p.confidence}${p.signal_grade ? ` · signal grade: ${p.signal_grade}` : ''}${p.signal_publisher ? ` · ${p.signal_publisher}` : ''}`);
        lines.push(`  - ${p.summary}`);
        lines.push(`  - **Fact** (${fmt(p.meeting_date)}): ${p.speaker || '(unattributed)'}`);
        lines.push(`  - **Signal** (${gap}): [${p.signal_title || '(no title)'}](${p.signal_url || '#'})`);
      });
      lines.push('');
    }

    // Sources — every claim's provenance trail
    if (sec.source_records?.length) {
      lines.push('**Sources**:');
      sec.source_records.forEach(s => {
        const tier = TIER_LABEL[s.confidence_tier] || 'Estimated';
        const link = s.source_url ? `[${s.label || s.source_url}](${s.source_url})` : (s.label || '(no link)');
        const gradeChip = s.source_grade ? ` · grade ${s.source_grade}` : '';
        const pubChip = s.publisher_name ? ` · ${s.publisher_name}` : '';
        lines.push(`- [T${s.confidence_tier} · ${tier}${gradeChip}] ${link} — ${s.source_type}${pubChip}${s.source_date ? ' · ' + fmt(s.source_date) : ''}`);
      });
      lines.push('');
    }
    lines.push('---');
    lines.push('');
  }

  // Footer
  lines.push('');
  lines.push(`*Generated by Nova on ${fmt(pulse.generated_at)}. Every claim above traces to a source record.*`);
  lines.push(`*Confidence tiers: T1 Verified · T2 Inferred · T3 Estimated. Source grades: A Primary · B Tier-1 press · C Trade press · D Low-authority.*`);
  return lines.join('\n');
}

// ──────────────────────────────────────────────────────────────────────
// HTML export — designed for sharing with leadership (print-friendly)
// ──────────────────────────────────────────────────────────────────────

export function pulseToHtml(pulse) {
  const m = pulse.metrics || {};

  const styles = `
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 880px; margin: 32px auto; padding: 0 24px; color: #0f172a; line-height: 1.5; }
    h1 { font-size: 28px; margin: 0 0 8px; color: #0f172a; }
    h2 { font-size: 18px; margin: 24px 0 8px; padding-top: 16px; border-top: 1px solid #e2e8f0; color: #1e293b; }
    h3 { font-size: 14px; margin: 16px 0 6px; color: #475569; text-transform: uppercase; letter-spacing: 0.04em; }
    .meta { font-size: 11px; color: #64748b; margin-bottom: 12px; }
    .meta strong { color: #0f172a; }
    .freshness { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 10px; font-weight: 700; text-transform: uppercase; }
    .freshness.green { background: #d1fae5; color: #065f46; }
    .freshness.yellow { background: #fef3c7; color: #92400e; }
    .freshness.stale { background: #fee2e2; color: #991b1b; }
    .synthesis { font-size: 13px; margin: 8px 0 12px; }
    .diff { background: #eff6ff; border-left: 3px solid #3b82f6; padding: 6px 10px; font-size: 11px; color: #1e3a8a; margin: 6px 0; }
    .lint { background: #fffbeb; border-left: 3px solid #f59e0b; padding: 6px 10px; font-size: 11px; color: #78350f; margin: 6px 0; }
    .lint code { background: rgba(120, 53, 15, 0.1); padding: 1px 4px; border-radius: 3px; font-size: 10px; }
    table { width: 100%; border-collapse: collapse; font-size: 11px; margin: 6px 0; }
    th, td { padding: 4px 8px; text-align: left; border-bottom: 1px solid #e2e8f0; vertical-align: top; }
    th { background: #f8fafc; font-weight: 700; color: #475569; text-transform: uppercase; font-size: 9px; letter-spacing: 0.04em; }
    .chip { display: inline-block; padding: 1px 6px; border-radius: 4px; font-size: 9px; font-weight: 700; margin-right: 4px; }
    .chip.t1 { background: #059669; color: white; }
    .chip.t2 { background: #f59e0b; color: white; }
    .chip.t3 { background: #fb7185; color: white; }
    .chip.gA { background: #0f172a; color: white; }
    .chip.gB { background: #1d4ed8; color: white; }
    .chip.gC { background: #e2e8f0; color: #1e293b; }
    .chip.gD { background: #fee2e2; color: #991b1b; }
    .pattern { border: 1px solid #e2e8f0; border-radius: 6px; padding: 8px; margin: 6px 0; font-size: 11px; }
    .pattern .summary { font-size: 12px; margin: 4px 0; }
    .pattern-meta { color: #64748b; font-size: 10px; }
    .ladder { font-size: 10px; color: #475569; }
    .quote { font-style: italic; color: #475569; font-size: 11px; }
    .footer { margin-top: 32px; padding-top: 16px; border-top: 1px solid #e2e8f0; font-size: 10px; color: #94a3b8; }
    a { color: #1d4ed8; }
    @media print { body { margin: 0; max-width: none; } h2 { page-break-after: avoid; } table, .pattern { page-break-inside: avoid; } }
  `;

  const tierChip = (t) => t ? `<span class="chip t${t}">T${t} ${escHtml(TIER_LABEL[t] || '')}</span>` : '';
  const gradeChip = (g) => g ? `<span class="chip g${g}">${escHtml(g)}</span>` : '';

  const sourceRow = (s) => `
    <tr>
      <td>${tierChip(s.confidence_tier)}${gradeChip(s.source_grade)}</td>
      <td>${s.source_url ? `<a href="${escHtml(s.source_url)}" target="_blank">${escHtml(s.label || s.source_url)}</a>` : escHtml(s.label || '(no link)')}</td>
      <td>${escHtml(s.publisher_name || s.source_type || '')}</td>
      <td>${escHtml(fmt(s.source_date))}</td>
    </tr>
  `;

  const driftSection = (drift) => {
    if (!drift) return '';
    const buckets = [
      { key: 'improving', label: 'Improving' },
      { key: 'deteriorating', label: 'Deteriorating' },
      { key: 'mixed', label: 'Mixed' },
      { key: 'new_positions', label: 'New positions' },
    ];
    const total = buckets.reduce((sum, b) => sum + (drift[b.key]?.length || 0), 0);
    if (total === 0) return '';
    let html = `<h3>Stakeholder drift</h3>`;
    buckets.forEach(b => {
      const items = drift[b.key] || [];
      if (items.length === 0) return;
      html += `<p style="font-size:11px;color:#475569;"><strong>${b.label}</strong> (${items.length})</p><ul style="font-size:11px;margin:0 0 8px;padding-left:20px;">`;
      items.forEach(c => {
        const last = c.series?.[c.series.length - 1];
        const ladder = (c.series || []).map(s => `${s.sentiment} (${escHtml(s.meeting_date)})`).join(' → ');
        html += `<li><strong>${escHtml(c.speaker_name)}</strong>${c.speaker_role ? ` · ${escHtml(c.speaker_role)}` : ''} on <strong>${escHtml(c.topic)}</strong> → ${escHtml(c.trend)}${c.n_facts > 1 ? ` (n=${c.n_facts})` : ''}<br><span class="ladder">${ladder}</span>`;
        if (last?.position) html += `<br><span class="quote">"${escHtml(last.position)}"</span>`;
        if (last?.evidence_quote) html += `<br><span class="quote">Verbatim: "${escHtml(last.evidence_quote)}"</span>`;
        html += `</li>`;
      });
      html += `</ul>`;
    });
    return html;
  };

  const patternsSection = (patterns) => {
    if (!Array.isArray(patterns) || patterns.length === 0) return '';
    let html = `<h3>Corroborated patterns (${patterns.length})</h3>`;
    patterns.forEach(p => {
      const gap = p.gap_days >= 0 ? `signal ${p.gap_days}d after meeting` : `signal ${Math.abs(p.gap_days)}d before meeting (reactive)`;
      html += `
        <div class="pattern">
          <div>
            <span class="chip" style="background:${p.type === 'corroborates' ? '#d1fae5;color:#065f46' : p.type === 'contradicts' ? '#fee2e2;color:#991b1b' : '#dbeafe;color:#1e3a8a'}">${escHtml(p.type)}</span>
            <span class="chip" style="background:#e2e8f0;color:#1e293b">${escHtml(p.topic)}</span>
            <span class="chip" style="background:${p.confidence === 'high' ? '#0f172a;color:white' : p.confidence === 'medium' ? '#e2e8f0;color:#1e293b' : '#f1f5f9;color:#64748b'}">${escHtml(p.confidence)}</span>
            ${gradeChip(p.signal_grade)}
            <span class="pattern-meta">· ${escHtml(gap)}</span>
          </div>
          <div class="summary">${escHtml(p.summary)}</div>
          <div class="pattern-meta">
            <strong>Fact</strong> (${escHtml(fmt(p.meeting_date))}): ${escHtml(p.speaker || '(unattributed)')}
          </div>
          <div class="pattern-meta">
            <strong>Signal</strong>: ${p.signal_url ? `<a href="${escHtml(p.signal_url)}" target="_blank">${escHtml(p.signal_title || '(no title)')}</a>` : escHtml(p.signal_title || '(no signal)')}
          </div>
        </div>
      `;
    });
    return html;
  };

  const sectionsHtml = Object.entries(pulse.sections || {}).map(([key, sec]) => `
    <h2>${escHtml(SECTION_LABELS[key] || key)}
      <span class="freshness ${sec.freshness}">${escHtml(FRESHNESS_LABEL[sec.freshness] || sec.freshness)}</span>
    </h2>
    ${Array.isArray(sec._lint) && sec._lint.length > 0 ? `
      <div class="lint">
        <strong>⚠ Provenance lint</strong> (${sec._lint.length}):
        <ul style="margin:4px 0;padding-left:20px;">
          ${sec._lint.map(w => `<li><code>${escHtml(w.code)}</code>: ${escHtml(w.message)}</li>`).join('')}
        </ul>
      </div>
    ` : ''}
    <p class="synthesis">${escHtml(sec.synthesis || '(no synthesis)')}</p>
    ${sec.diff_vs_previous && !/no prior pulse/i.test(sec.diff_vs_previous) ? `<div class="diff"><strong>Δ vs previous:</strong> ${escHtml(sec.diff_vs_previous)}</div>` : ''}
    ${driftSection(sec.data?.stakeholder_drift)}
    ${patternsSection(sec.data?.corroborated_patterns)}
    ${sec.source_records?.length ? `
      <h3>Sources (${sec.source_records.length})</h3>
      <table><thead><tr><th>Provenance</th><th>Source</th><th>Publisher</th><th>Date</th></tr></thead>
        <tbody>${sec.source_records.map(sourceRow).join('')}</tbody></table>
    ` : ''}
  `).join('');

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>${escHtml(pulse.bank_name)} — Quarterly Pulse · ${escHtml(pulse.period)}</title>
<style>${styles}</style>
</head>
<body>
  <h1>${escHtml(pulse.bank_name)} — Quarterly Pulse · ${escHtml(pulse.period)}</h1>
  <div class="meta">
    <strong>Period</strong>: ${escHtml(pulse.period_starts_at)} → ${escHtml(pulse.period_ends_at)}<br>
    <strong>Generated</strong>: ${escHtml(fmt(pulse.generated_at))} ·
    <strong>Overall freshness</strong>: <span class="freshness ${pulse.freshness?.overall}">${escHtml(FRESHNESS_LABEL[pulse.freshness?.overall] || pulse.freshness?.overall)}</span><br>
    ${pulse.confirmed_by_ae_at ? `<strong>Confirmed by</strong>: ${escHtml(pulse.confirmed_by_ae)} on ${escHtml(fmt(pulse.confirmed_by_ae_at))}<br>` : ''}
    <strong>Source records</strong>: ${m.total_source_records || 0} ·
    <strong>Lint warnings</strong>: ${m.lint_warning_count || 0} ·
    <strong>Internal sections</strong>: ${m.sections_with_internal_data || 0}
  </div>
  ${sectionsHtml}
  <div class="footer">
    Generated by Nova on ${escHtml(fmt(pulse.generated_at))}. Every claim above traces to a source record.<br>
    <strong>Confidence tiers</strong>: T1 Verified · T2 Inferred · T3 Estimated.
    <strong>Source grades</strong>: A Primary · B Tier-1 press · C Trade press · D Low-authority.
  </div>
</body>
</html>`;
}
