/**
 * Benchmark Bridge — surface industry benchmarks per bank
 * ───────────────────────────────────────────────────────
 * VCs need benchmarks for ROI/capability work. Today they manually fetch
 * them. This lib pulls relevant benchmarks for a bank from the parent
 * Cortex /benchmarks/ folder (CSV files) and returns them with full
 * provenance (source, year, region match).
 *
 * The benchmark library structure follows Cortex's existing
 * "benchmarks-csv" endpoint — see /api/knowledge/benchmarks-csv.
 * This bridge re-exposes that data scoped to a specific bank's
 * country/region so AE+VC see "your bank's CTI ratio vs Nordic median."
 */

import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

// Where the parent Cortex monorepo keeps benchmark CSVs.
// Resolves relative to market-intelligence-app/ → ../benchmarks/
const BENCHMARK_DIRS = [
  join(process.cwd(), '..', 'benchmarks'),
  join(process.cwd(), 'benchmarks'),
];

function findBenchmarkDir() {
  for (const d of BENCHMARK_DIRS) {
    if (existsSync(d)) return d;
  }
  return null;
}

/**
 * Parse a CSV file (lightweight — assumes simple comma-delimited values
 * with header row, no embedded commas in values).
 */
function parseCsv(content) {
  const lines = content.split(/\r?\n/).filter(l => l.trim());
  if (lines.length < 2) return [];
  const headers = lines[0].split(',').map(h => h.trim());
  return lines.slice(1).map(line => {
    const values = line.split(',').map(v => v.trim());
    const obj = {};
    headers.forEach((h, i) => { obj[h] = values[i] || ''; });
    return obj;
  });
}

/**
 * List benchmark CSV files available in the benchmarks folder.
 */
export function listBenchmarkFiles() {
  const dir = findBenchmarkDir();
  if (!dir) return [];
  try {
    return readdirSync(dir).filter(f => f.endsWith('.csv'));
  } catch { return []; }
}

/**
 * Get benchmarks relevant to a specific bank.
 * Scopes by country / region match where possible.
 */
export function getBenchmarksForBank(db, bankKey, options = {}) {
  const { region = 'global' } = options;
  const bank = db.prepare('SELECT * FROM banks WHERE key = ?').get(bankKey);
  if (!bank) return { error: 'bank not found' };

  const dir = findBenchmarkDir();
  if (!dir) {
    return {
      bank: { key: bankKey, name: bank.bank_name, country: bank.country },
      benchmarks: [],
      note: 'Benchmark library not found at expected paths. Configure BENCHMARK_DIR or ensure ../benchmarks/ exists.',
    };
  }

  const files = listBenchmarkFiles();
  const benchmarks = [];

  for (const file of files) {
    try {
      const content = readFileSync(join(dir, file), 'utf8');
      const rows = parseCsv(content);
      // Filter: prefer rows matching the bank's region/country, fallback to global
      const relevantRows = rows.filter(r => {
        const r_region = (r.region || r.geography || '').toLowerCase();
        const bank_country = (bank.country || '').toLowerCase();
        return !r_region ||
               r_region === 'global' ||
               r_region.includes(bank_country) ||
               bank_country.includes(r_region) ||
               (region && r_region.includes(region.toLowerCase()));
      });
      if (relevantRows.length > 0) {
        benchmarks.push({
          source_file: file,
          benchmark_name: file.replace(/\.csv$/, '').replace(/[_-]+/g, ' '),
          rows: relevantRows.slice(0, 6),
          total_rows_in_file: rows.length,
          relevant_rows: relevantRows.length,
        });
      }
    } catch (err) {
      console.warn(`[benchmarkBridge] Failed to read ${file}: ${err.message}`);
    }
  }

  return {
    bank: { key: bankKey, name: bank.bank_name, country: bank.country },
    benchmarks,
    note: benchmarks.length === 0 ? 'No region-specific benchmarks; consider adding to /benchmarks/.' : null,
  };
}
