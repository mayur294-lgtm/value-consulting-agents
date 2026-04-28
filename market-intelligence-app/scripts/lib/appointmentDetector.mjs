/**
 * Appointment Detector — structured DMU change extraction from signals
 * ────────────────────────────────────────────────────────────────────
 * Replaces regex-based detection in pulseGenerator. For each stakeholder
 * signal, attempts to extract structured appointment metadata:
 *   { type, person_name, role, predecessor, effective_date, source_url }
 *
 * Why dedicated agent: the regex in pulseGenerator catches the FACT of an
 * appointment but doesn't structure WHO/WHAT/WHEN. This lib produces
 * structured extractions per signal so DMU change tables can render
 * proper "Person X joins as Role Y replacing Person Z effective Date"
 * cells.
 *
 * Implementation: deterministic regex + heuristic for V0; LLM-bounded
 * fallback only when regex confidence is low (saves API spend).
 */

// Patterns for appointment / departure detection. Each captures the parts.
const APPOINTMENT_PATTERNS = [
  // "X is appointed CEO" / "X named as CTO" / "X joins as Head of"
  /^(.+?)\s+(?:is\s+)?(?:appointed|named|joins\s+as|hires?\s+as)\s+(?:the\s+)?(?:new\s+|incoming\s+)?(.+?)(?:\s+at\s+(.+?))?$/i,
  // "X becomes new CEO"
  /^(.+?)\s+becomes?\s+(?:the\s+)?(?:new\s+|incoming\s+)?(.+)$/i,
  // "X to become CEO"
  /^(.+?)\s+to\s+become\s+(?:the\s+)?(.+)$/i,
];

const DEPARTURE_PATTERNS = [
  /^(.+?)\s+(?:resigns?|resigned|departs?|departed|steps?\s+down|leaves|to\s+leave|out\s+as|retir(?:es|ed|ing))/i,
];

const ROLE_KEYWORDS = [
  'CEO', 'CTO', 'CIO', 'CFO', 'CDO', 'COO', 'CHRO', 'CMO', 'CCO',
  'Chief', 'Head of', 'Group', 'President', 'Chair', 'Chairman', 'Chairwoman',
  'Director', 'Executive', 'Lead', 'VP', 'SVP', 'EVP',
];

function looksLikePersonName(s) {
  if (!s) return false;
  const trimmed = s.trim();
  const words = trimmed.split(/\s+/);
  if (words.length < 2 || words.length > 4) return false;
  return words.every(w => /^[A-ZÅÄÖÆØ][a-zåäöæø]+$/.test(w) || /^(van|von|de|du|le|la|al|el)$/i.test(w));
}

function containsRole(s) {
  if (!s) return false;
  return ROLE_KEYWORDS.some(k => new RegExp(`\\b${k}\\b`, 'i').test(s));
}

/**
 * Extract structured appointment info from a single signal title.
 * Returns null if no appointment detected.
 */
export function detectAppointment(signalTitle) {
  if (!signalTitle) return null;
  // Strip publisher tail (everything after final " - ")
  const cleanTitle = signalTitle.replace(/\s+[\-–—]\s+[^-–—]+$/, '');

  // Try each pattern
  for (const pattern of APPOINTMENT_PATTERNS) {
    const m = cleanTitle.match(pattern);
    if (!m) continue;
    const candidatePerson = m[1].trim();
    const candidateRole = m[2].trim();
    if (!looksLikePersonName(candidatePerson)) continue;
    if (!containsRole(candidateRole) && candidateRole.length > 60) continue;
    return {
      type: 'appointment',
      person_name: candidatePerson,
      role: candidateRole.slice(0, 100),
      predecessor: null,
      effective_date: null,
      confidence: 'medium',
    };
  }

  for (const pattern of DEPARTURE_PATTERNS) {
    const m = cleanTitle.match(pattern);
    if (!m) continue;
    const candidatePerson = m[1].trim();
    if (!looksLikePersonName(candidatePerson)) continue;
    return {
      type: 'departure',
      person_name: candidatePerson,
      role: null,
      predecessor: null,
      effective_date: null,
      confidence: 'medium',
    };
  }

  return null;
}

/**
 * Detect appointments/departures across a bank's stakeholder signals.
 * Returns structured event list.
 */
export function detectBankAppointments(db, bankKey, options = {}) {
  const { withinDays = 90 } = options;
  const cutoff = new Date(); cutoff.setDate(cutoff.getDate() - withinDays);
  const cutoffISO = cutoff.toISOString();

  const signals = db.prepare(`
    SELECT id, title, source_url, source_grade, publisher_name, detected_at, mentioned_stakeholders
    FROM deal_signals
    WHERE deal_id = ? AND signal_category = 'stakeholder'
      AND COALESCE(is_demo, 0) = 0
      AND detected_at >= ?
  `).all(bankKey, cutoffISO);

  const events = [];
  for (const s of signals) {
    const detection = detectAppointment(s.title);
    if (!detection) continue;
    events.push({
      ...detection,
      signal_id: s.id,
      signal_title: s.title,
      source_url: s.source_url,
      source_grade: s.source_grade,
      publisher_name: s.publisher_name,
      detected_at: s.detected_at,
    });
  }

  return events;
}
