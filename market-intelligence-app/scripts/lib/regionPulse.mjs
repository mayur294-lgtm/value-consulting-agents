/**
 * Region Pulse Aggregator — Tier 2 (region/country page improvements)
 * ───────────────────────────────────────────────────────────────────
 * Aggregates bank-level pulses (Sprint 1) into a region/country-level
 * "Pulse" that answers "how is this region's quarter going?" without
 * forcing the AE to open every bank.
 *
 * Same structural-composition principle as bank Pulse:
 *   - Reads existing bank-level pulse payloads from `pulses` table
 *   - Composes deterministic rollups per section
 *   - No LLM in the synthesis loop
 *   - Source provenance preserved (every aggregate cites which banks
 *     contributed)
 *
 * The output mirrors the bank Pulse shape so UI components can be
 * partially reused.
 */

const TIER_GRADE_RANK = { A: 4, B: 3, C: 2, D: 1 };

function safeParse(json) {
  try { return JSON.parse(json); } catch { return null; }
}

function avg(arr) {
  if (!arr.length) return null;
  return +(arr.reduce((s, x) => s + x, 0) / arr.length).toFixed(2);
}

/**
 * Generate a region-level pulse from the bank-level pulses.
 *
 * @param {Database} db
 * @param {object} options
 *   bankKeys: string[]   — banks in this region/country
 *   periodId: string     — e.g. "2026-Q2"
 *   regionLabel: string  — display name (e.g. "Nordics" or "Sweden")
 *   priorPeriodId?: string — for delta computation; defaults to inferring Q-1
 * @returns {object} aggregated pulse payload
 */
export function generateRegionPulse(db, options) {
  const { bankKeys, periodId, regionLabel, priorPeriodId = inferPriorPeriod(periodId) } = options;
  if (!bankKeys || bankKeys.length === 0) {
    return null;
  }

  const placeholders = bankKeys.map(() => '?').join(',');
  const rows = db.prepare(`
    SELECT account_id AS bank_key, period_id, payload_json, generated_at
    FROM pulses
    WHERE account_id IN (${placeholders}) AND period_id IN (?, ?)
  `).all(...bankKeys, periodId, priorPeriodId);

  const currentByBank = new Map();
  const priorByBank = new Map();
  for (const row of rows) {
    const payload = safeParse(row.payload_json);
    if (!payload) continue;
    if (row.period_id === periodId) currentByBank.set(row.bank_key, payload);
    else if (row.period_id === priorPeriodId) priorByBank.set(row.bank_key, payload);
  }

  const pulses = Array.from(currentByBank.values());
  if (pulses.length === 0) {
    return {
      region: regionLabel,
      period: periodId,
      banks_in_scope: bankKeys.length,
      banks_with_pulse: 0,
      sections: {},
      coverage_warning: 'No bank-level pulses generated for this region in this period. Run npm run generate-pulses first.',
    };
  }

  // Engagement trend rollup — average score across pulses
  const engagementScores = pulses
    .map(p => p.sections?.engagement_trend?.data?.score)
    .filter(s => typeof s === 'number');
  const priorEngagementScores = Array.from(priorByBank.values())
    .map(p => p.sections?.engagement_trend?.data?.score)
    .filter(s => typeof s === 'number');
  const avgEngagement = avg(engagementScores);
  const avgPriorEngagement = avg(priorEngagementScores);
  const engagementDelta = (avgEngagement != null && avgPriorEngagement != null)
    ? +(avgEngagement - avgPriorEngagement).toFixed(2) : null;

  // Market signals rollup — total + by category + by grade
  const allMarketSources = pulses.flatMap(p => p.sections?.market_signals?.source_records || []);
  const gradeDist = { A: 0, B: 0, C: 0, D: 0 };
  for (const s of allMarketSources) {
    if (s.source_grade && gradeDist[s.source_grade] != null) gradeDist[s.source_grade] += 1;
  }
  const totalMarketSignals = allMarketSources.length;

  // Quarterly execution rollup — combine action lists
  const quarterlyActions = pulses.flatMap(p => p.sections?.quarterly_execution?.data?.actions_taken || []);

  // DMU changes rollup — sum appointments/departures/registrations + collect patterns
  let appointments = 0, departures = 0, registrations = 0;
  let allPatterns = [];
  for (const p of pulses) {
    const dmu = p.sections?.dmu_changes?.data || {};
    appointments += (dmu.appointments?.length || 0);
    departures += (dmu.departures?.length || 0);
    registrations += (dmu.registrations?.length || 0);
    for (const pat of (dmu.corroborated_patterns || [])) {
      allPatterns.push({ ...pat, bank: p.bank_name });
    }
  }
  // Top patterns sorted by signal_grade then confidence
  allPatterns.sort((a, b) => {
    const ag = TIER_GRADE_RANK[a.signal_grade] || 0;
    const bg = TIER_GRADE_RANK[b.signal_grade] || 0;
    if (ag !== bg) return bg - ag;
    const ac = a.confidence === 'high' ? 3 : a.confidence === 'medium' ? 2 : 1;
    const bc = b.confidence === 'high' ? 3 : b.confidence === 'medium' ? 2 : 1;
    return bc - ac;
  });
  const topPatterns = allPatterns.slice(0, 8);

  // Drift rollup
  let driftImproving = 0, driftDeteriorating = 0, driftMixed = 0, driftNew = 0;
  for (const p of pulses) {
    const drift = p.sections?.engagement_trend?.data?.stakeholder_drift || {};
    driftImproving += (drift.improving?.length || 0);
    driftDeteriorating += (drift.deteriorating?.length || 0);
    driftMixed += (drift.mixed?.length || 0);
    driftNew += (drift.new_positions?.length || 0);
  }

  // Lint warnings rollup
  let totalLintWarnings = 0;
  for (const p of pulses) {
    totalLintWarnings += (p.metrics?.lint_warning_count || 0);
  }

  // Total source records
  const totalSourceRecords = pulses.reduce((s, p) => s + (p.metrics?.total_source_records || 0), 0);

  // Banks with no pulse — surface as coverage gap
  const banksWithoutPulse = bankKeys.filter(bk => !currentByBank.has(bk));

  return {
    region: regionLabel,
    period: periodId,
    prior_period: priorPeriodId,
    banks_in_scope: bankKeys.length,
    banks_with_pulse: pulses.length,
    banks_without_pulse: banksWithoutPulse,
    metrics: {
      total_source_records: totalSourceRecords,
      total_market_signals: totalMarketSignals,
      lint_warning_count: totalLintWarnings,
      grade_distribution: gradeDist,
    },
    sections: {
      engagement_trend: {
        synthesis: avgEngagement != null
          ? `Average engagement score: ${avgEngagement}/10${engagementDelta != null ? ` (Δ ${engagementDelta >= 0 ? '+' : ''}${engagementDelta} vs ${priorPeriodId})` : ''}. ${pulses.length}/${bankKeys.length} banks with pulse data.`
          : 'No engagement scores available.',
        data: {
          avg_score: avgEngagement,
          avg_prior_score: avgPriorEngagement,
          delta: engagementDelta,
          n_pulses: pulses.length,
          drift_summary: {
            improving: driftImproving,
            deteriorating: driftDeteriorating,
            mixed: driftMixed,
            new_positions: driftNew,
          },
        },
      },
      market_signals: {
        synthesis: `${totalMarketSignals} signal source-records across ${pulses.length} banks. Grade mix: A:${gradeDist.A} / B:${gradeDist.B} / C:${gradeDist.C} / D:${gradeDist.D}.`,
        data: { total: totalMarketSignals, grade_distribution: gradeDist },
      },
      dmu_changes: {
        synthesis: `${appointments} appointments · ${departures} departures · ${registrations} new contacts across the region. ${topPatterns.length} corroborated patterns surfaced.`,
        data: {
          appointments,
          departures,
          registrations,
          top_patterns: topPatterns,
        },
      },
      quarterly_execution: {
        synthesis: `${quarterlyActions.length} actions logged across ${pulses.length} banks this period.`,
        data: { actions_taken_count: quarterlyActions.length, sample_actions: quarterlyActions.slice(0, 6) },
      },
    },
  };
}

function inferPriorPeriod(periodId) {
  // 2026-Q2 → 2026-Q1; 2026-Q1 → 2025-Q4
  const m = String(periodId).match(/^(\d{4})-Q([1-4])$/);
  if (!m) return null;
  const year = parseInt(m[1], 10);
  const q = parseInt(m[2], 10);
  if (q === 1) return `${year - 1}-Q4`;
  return `${year}-Q${q - 1}`;
}
