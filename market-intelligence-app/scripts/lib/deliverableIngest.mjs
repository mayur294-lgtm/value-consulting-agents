/**
 * Deliverable Ingest — VC artifact → Nova publication
 * ───────────────────────────────────────────────────
 * When VC produces a deliverable (ROI model, capability assessment,
 * roadmap, presentation), this library:
 *   1. Reads the deliverable file (HTML / Excel / PDF / Markdown / JSON)
 *   2. Extracts a structured summary of key findings (best-effort, no LLM
 *      required for V0 — extracts from filename + first paragraph + any
 *      JSON sidecar)
 *   3. Registers the artifact via engagementTracker.registerArtifact()
 *      which auto-emits a Nova signal so the change feed surfaces it
 *
 * The contract: VC drops a file in the engagement folder + calls this lib,
 * Nova learns about the deliverable. AEs see "VC published ROI for Bank X"
 * in their change feed within seconds.
 */

import { readFileSync, existsSync, statSync } from 'node:fs';
import { extname, basename } from 'node:path';
import { registerArtifact } from './engagementTracker.mjs';

const ARTIFACT_TYPE_HINTS = {
  // Type hints based on filename patterns — best-effort detection
  roi: /\b(roi|business[_-]?case|value[_-]?case|financial[_-]?model)\b/i,
  capability_assessment: /\b(capability|maturity|assessment|gap[_-]?analysis)\b/i,
  roadmap: /\b(roadmap|plan|prioriti[sz]ed)\b/i,
  presentation: /\b(presentation|slides|deck|prezi)\b/i,
};

const FORMAT_BY_EXT = {
  '.html': 'html', '.htm': 'html',
  '.xlsx': 'xlsx', '.xlsm': 'xlsx',
  '.pdf': 'pdf',
  '.md': 'md', '.markdown': 'md',
  '.json': 'json',
};

/**
 * Inspect a deliverable file and extract metadata.
 * @returns {{ artifact_type, content_format, title, summary, key_findings }}
 */
export function inspectDeliverable(filePath) {
  if (!existsSync(filePath)) throw new Error(`File not found: ${filePath}`);
  const fileName = basename(filePath);
  const ext = extname(fileName).toLowerCase();
  const format = FORMAT_BY_EXT[ext] || 'other';

  // Type detection from filename
  let artifactType = 'other';
  for (const [type, pattern] of Object.entries(ARTIFACT_TYPE_HINTS)) {
    if (pattern.test(fileName)) { artifactType = type; break; }
  }

  // Title — strip extension, replace separators
  const title = fileName
    .replace(/\.[^.]+$/, '')
    .replace(/[_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  // Summary — try to extract from file content (best-effort, format-aware)
  let summary = null;
  let keyFindings = null;

  try {
    if (format === 'json') {
      const json = JSON.parse(readFileSync(filePath, 'utf8'));
      summary = json.summary || json.executive_summary || json.title || null;
      keyFindings = json.key_findings || json.scenarios || json.recommendations || null;
    } else if (format === 'md') {
      const md = readFileSync(filePath, 'utf8');
      // First non-heading paragraph as summary
      const firstPara = md.split(/\n\s*\n/).find(p => p.trim() && !p.startsWith('#') && !p.startsWith('```'));
      if (firstPara) summary = firstPara.slice(0, 300).trim();
    } else if (format === 'html') {
      const html = readFileSync(filePath, 'utf8');
      // Extract <title> and first <h1> or <p>
      const titleMatch = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i);
      const h1Match = html.match(/<h1[^>]*>([\s\S]*?)<\/h1>/i);
      const pMatch = html.match(/<p[^>]*>([\s\S]*?)<\/p>/i);
      summary = (titleMatch?.[1] || h1Match?.[1] || pMatch?.[1] || '').replace(/<[^>]+>/g, '').trim().slice(0, 300);
    }
    // For xlsx/pdf — V0 doesn't parse; V1 could use SheetJS/pdf-parse
  } catch (err) {
    console.warn(`[deliverableIngest] Could not inspect ${fileName}: ${err.message}`);
  }

  return {
    artifact_type: artifactType,
    content_format: format,
    title,
    summary,
    key_findings: keyFindings,
    file_size: statSync(filePath).size,
  };
}

/**
 * Ingest a deliverable file into Nova: inspect + register + emit signal.
 *
 * @param {Database} db
 * @param {object} input
 *   engagement_id: string (required)
 *   file_path: string (required) — local path or URL
 *   published_by: string (optional VC consultant name)
 *   override: { artifact_type, title, summary, key_findings } (optional)
 * @returns the registered artifact record
 */
export function ingestDeliverable(db, input) {
  const { engagement_id, file_path, published_by = null, override = {} } = input;
  if (!engagement_id) throw new Error('engagement_id required');
  if (!file_path) throw new Error('file_path required');

  // For local files, inspect; for URLs, just take metadata from override
  let metadata;
  if (file_path.startsWith('http://') || file_path.startsWith('https://')) {
    metadata = {
      artifact_type: override.artifact_type || 'other',
      content_format: 'url',
      title: override.title || file_path,
      summary: override.summary || null,
      key_findings: override.key_findings || null,
    };
  } else {
    metadata = inspectDeliverable(file_path);
  }

  return registerArtifact(db, {
    engagement_id,
    artifact_type: override.artifact_type || metadata.artifact_type,
    title: override.title || metadata.title,
    summary: override.summary || metadata.summary,
    content_url: file_path,
    content_format: metadata.content_format,
    key_findings: override.key_findings || metadata.key_findings,
    published_by,
  });
}
