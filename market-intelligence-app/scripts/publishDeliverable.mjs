#!/usr/bin/env node
/**
 * /publish-deliverable CLI — register a VC artifact into Nova
 * ───────────────────────────────────────────────────────────
 * VC produces a deliverable file (HTML / Excel / Markdown / JSON / PDF) and
 * runs this command. The deliverable is inspected (type/title/summary
 * extracted), registered as engagement_artifacts row, and a Nova signal is
 * emitted so the change feed surfaces it for AEs.
 *
 * Usage:
 *   node scripts/publishDeliverable.mjs --engagement=<id> --file=path/to/roi.xlsx
 *   node scripts/publishDeliverable.mjs --engagement=<id> --url=https://... --type=presentation --title="Deck"
 */

import dotenv from 'dotenv';
dotenv.config({ override: true, quiet: true });

import { getDb } from './db.mjs';
import { ingestDeliverable } from './lib/deliverableIngest.mjs';

const args = process.argv.slice(2);
const get = (key) => args.find(a => a.startsWith(`--${key}=`))?.split('=')[1];

const engagementId = get('engagement');
const filePath = get('file') || get('url');
const overrideType = get('type');
const overrideTitle = get('title');
const overrideSummary = get('summary');
const publishedBy = get('by');

if (!engagementId || !filePath) {
  console.error('Usage: publishDeliverable.mjs --engagement=<id> --file=<path> | --url=<url>');
  console.error('  Optional: --type=roi|capability_assessment|roadmap|presentation|other');
  console.error('            --title="..." --summary="..." --by="VC Name"');
  process.exit(1);
}

const db = getDb();
const override = {};
if (overrideType) override.artifact_type = overrideType;
if (overrideTitle) override.title = overrideTitle;
if (overrideSummary) override.summary = overrideSummary;

try {
  const artifact = ingestDeliverable(db, {
    engagement_id: engagementId,
    file_path: filePath,
    published_by: publishedBy,
    override,
  });
  console.log('═'.repeat(60));
  console.log(`  ✓ Deliverable published: ${artifact.title}`);
  console.log('═'.repeat(60));
  console.log(`  Type: ${artifact.artifact_type}`);
  console.log(`  Format: ${artifact.content_format}`);
  console.log(`  URL: ${artifact.content_url}`);
  console.log(`  Engagement: ${artifact.engagement_id}`);
  console.log(`  Published by: ${artifact.published_by || '(unset)'}`);
  console.log();
  console.log(`  ✓ Nova signal emitted — change feed will surface this within seconds`);
  console.log(`  ✓ Bank profile artifact panel updated`);
} catch (err) {
  console.error(`✗ Failed: ${err.message}`);
  process.exit(1);
}
