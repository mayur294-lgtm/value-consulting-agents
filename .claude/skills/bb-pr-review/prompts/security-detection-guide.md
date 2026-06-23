# Security Detection Guide

Reference for the security-reviewer agent. Adapted from the openai/privacy-filter model's PII taxonomy and detection approach (Apache 2.0, 1.5B params, 96% F1 on PII-Masking-300k).

---

## Cortex context — what actually ships here

Cortex is a consulting-deliverable system, not a deployed web app. The two highest-value risks are:

1. **Committed client PII.** Real client/member names, emails, phone numbers, account numbers, or unanonymized transcripts must never land in git, MCP, or the knowledge graph. They must be scrubbed first with `scripts/anonymize_transcript.py` (the `anonymize-guard.py` hook also blocks unscrubbed reads). Engagement inputs, knowledge files, and `ontology-test/` JSON are the usual offenders.
2. **Committed secrets.** API keys, tokens, and connector URLs (e.g. the Minimi connector secret token, MCP auth) must stay out of git-tracked files like `.mcp.json`. Use env vars.

The classic web-app vulnerabilities below (XSS, SQLi, injection) are kept for general awareness, but cortex has no served endpoints — **de-emphasise them and focus on committed-PII and committed-secret detection.** The TypeScript snippets are illustrative of the *patterns*; in cortex the same patterns appear in Python pipeline code, agent/skill prompts, YAML, JSON, and Markdown engagement files.

---

## Source taxonomy mapping

The openai/privacy-filter model detects 8 PII types via token classification. We collapsed these into 4 code-relevant categories for source code review:

| Original category | Our category | Rationale |
|---|---|---|
| Private person names | PII | Real names in fixtures, comments, error messages |
| Private addresses | PII | Rare in code — collapsed into PII |
| Private emails | PII | Common in test data and configs |
| Private phone numbers | PII | Occasional in test data |
| Private URLs | INTERNAL_URL | Staging, internal, webhook endpoints |
| Private dates | (dropped) | Dates in code are almost never PII — birth dates would be, but those appear in data stores, not source files |
| Account numbers | SECRET | Bank accounts, but more commonly: API key IDs, connection strings |
| Secrets | SECRET | Passwords, API keys, tokens, private keys |

LOG_LEAK has no direct equivalent in the model. It is our addition for the code review context, where the risk is not that PII exists in source but that it flows into observability systems at runtime.

---

## Detection heuristics

### SECRET — hardcoded credentials

Secrets are the highest-risk category. A leaked API key can be exploited within minutes of appearing in a public repository.

**High-confidence patterns (flag immediately):**

- **AWS access keys** — strings starting with `AKIA` or `ASIA` followed by 16 alphanumeric characters:
  ```typescript
  const accessKey = "AKIAIOSFODNN7EXAMPLE";
  ```

- **Generic API keys** — prefixes `sk_live_`, `sk_test_`, or `sk-` followed by 20+ characters:
  ```typescript
  const stripe = new Stripe("sk_live_EXAMPLE_KEY_REDACTED...");
  const openai = new OpenAI({ apiKey: "sk-proj-abc123def456ghi789..." });
  ```

- **GitHub tokens** — prefixes `ghp_`, `gho_`, `ghu_`, `ghs_`, `ghr_` followed by 36+ characters:
  ```typescript
  const token = "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghij";
  ```

- **Private keys** — PEM-encoded key blocks:
  ```typescript
  const key = `-----BEGIN RSA PRIVATE KEY-----
  MIIEowIBAAKCAQEA2a2rwplBQLFbH...
  -----END RSA PRIVATE KEY-----`;
  ```

- **Connection strings with embedded credentials**:
  ```typescript
  const db = "postgresql://admin:s3cretP@ss@db.example.com:5432/myapp";
  const cache = "redis://default:hunter2@redis-12345.us-east-1.ec2.cloud:6379";
  ```

- **JWT tokens** — `eyJ` followed by base64 (header.payload.signature):
  ```typescript
  const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U";
  ```

- **Password assignments** — `password`, `passwd`, or `pwd` assigned to a string literal:
  ```typescript
  const password = "hunter2";
  const dbConfig = { user: "admin", passwd: "correcthorsebatterystaple" };
  ```

**What is NOT a secret (do not flag):**

- **Environment variable references** — the value is loaded at runtime, not hardcoded:
  ```typescript
  const apiKey = process.env.STRIPE_SECRET_KEY;
  const token = import.meta.env.VITE_API_TOKEN;
  const secret = Deno.env.get("JWT_SECRET");
  ```

- **`.env.example` placeholders** — values are obviously not real:
  ```bash
  STRIPE_SECRET_KEY=your-key-here
  DATABASE_URL=postgresql://user:password@localhost:5432/mydb
  API_TOKEN=xxx
  JWT_SECRET=changeme
  ```

- **Type definitions and interfaces** — describing shape, not holding a value:
  ```typescript
  interface Config {
    apiKey: string;
    secretToken: string;
  }
  type DbCredentials = { password: string; connectionString: string };
  ```

- **Well-known test keys** — keys from vendor documentation meant for testing:
  ```typescript
  // Stripe's published test key
  const stripe = new Stripe("sk_test_EXAMPLE_KEY_REDACTED");
  ```

- **Mock variable names** — the name signals it is not real:
  ```typescript
  const mockApiKey = "fake-key-for-tests";
  const fakeToken = "test-token-12345";
  const testSecret = "not-a-real-secret";
  const dummyPassword = "placeholder";
  ```

---

### PII — real personal data in source

Real personal data in source code is a privacy risk and may violate data protection regulations. The challenge is distinguishing real data from deliberate test placeholders.

**High-confidence patterns:**

- **Email addresses with real-looking domains** — consumer or corporate email providers:
  ```typescript
  const adminEmail = "sarah.mitchell@gmail.com";
  const support = "tim@likeahuman.ai";
  const contacts = ["j.doe@outlook.com", "maria.garcia@company.co.uk"];
  ```

- **Phone numbers matching real formats** — international or domestic patterns with non-fictional exchanges:
  ```typescript
  const phone = "+1-312-555-7890";
  const mobile = "(020) 7946 0958";
  const emergency = "+44 7911 123456";
  ```

- **Full names with possessive or identifying context** — signals a real person, not a placeholder:
  ```typescript
  // Tim's staging credentials
  const owner = "Sarah Mitchell";
  const approver = { name: "Jan de Vries", email: "jan@company.nl" };
  ```

- **Physical addresses** — real street names, postcodes, cities:
  ```typescript
  const office = "123 Keizersgracht, 1015 CJ Amsterdam";
  const shipping = "42 Wallaby Way, Sydney NSW 2000";
  ```

**What is NOT PII (do not flag):**

- **RFC 2606 reserved domains and conventional test addresses**:
  ```typescript
  const email = "test@example.com";
  const user = "admin@example.org";
  const demo = "user@test.com";
  const placeholder = "foo@bar.baz";
  ```

- **Fictional phone range** — `555-0100` through `555-0199` are reserved for fiction:
  ```typescript
  const phone = "555-0123";
  const fax = "+1-555-0199";
  ```

- **Conventional placeholder names** — universally recognised as test data:
  ```typescript
  const user = { name: "John Doe", email: "john@example.com" };
  const participants = ["Alice", "Bob", "Charlie", "Eve"];
  const testUser = "Jane Smith";
  ```

- **Generic role-based identifiers**:
  ```typescript
  const admin = "admin@example.com";
  const testUser = "user_123";
  ```

**The key heuristic:** Does this look like it was copied from real data, or was it deliberately chosen as a placeholder? Real data tends to be specific and varied (different names, real domains, full addresses). Placeholders tend to be generic and repetitive (example.com, John Doe, 555-0100).

---

### LOG_LEAK — client data flowing to observability

The risk here is not PII in source code but client PII flowing into less-secured surfaces at runtime. In cortex that means the **engagement journal, telemetry blocks, Langfuse traces, MCP/KG syncs, and pipeline stdout/error output** — not just classic log aggregators. The TypeScript examples below are pattern illustrations; the equivalent in cortex is Python `print()`/`logging` of transcript or member data, or interpolating client names into telemetry/journal text.

**Patterns to flag:**

- **Logging entire user objects** — these typically contain email, name, and other PII fields:
  ```typescript
  console.log(user);
  console.log("Request body:", req.body);
  console.log("Session:", session);
  ```

- **Interpolating PII into error messages**:
  ```typescript
  console.error(`Failed to send email to ${user.email}`);
  console.warn(`Payment failed for ${customer.name}`);
  logger.error(`Auth failed: ${email} not found`);
  ```

- **Structured logging with full user objects**:
  ```typescript
  logger.info({ user, action: "login" });
  logger.debug({ customer, order });
  winston.log("info", { userData: req.user });
  ```

- **PII in exception messages** — these propagate to error tracking (Sentry, Bugsnag):
  ```typescript
  throw new Error(`Authentication failed for ${email}`);
  throw new AuthError(`User ${user.name} not authorized`);
  ```

- **PII in error responses to clients**:
  ```typescript
  res.status(500).json({ error: `Failed for user ${user.email}` });
  return NextResponse.json({ message: `Account ${email} suspended` }, { status: 403 });
  ```

**What is acceptable (do not flag):**

- **Logging opaque identifiers** — user IDs are not PII:
  ```typescript
  console.log(`Processing user ${userId}`);
  logger.info({ userId, action: "checkout" });
  ```

- **Development-only logging** — gated behind environment checks:
  ```typescript
  if (process.env.NODE_ENV === "development") {
    console.log("Debug user:", user);
  }
  ```

- **Logging counts and aggregates** — no individual data exposed:
  ```typescript
  console.log(`Processed ${users.length} users`);
  logger.info({ batchSize: orders.length, duration: elapsed });
  ```

- **Error messages without interpolated user data**:
  ```typescript
  throw new Error("Authentication failed");
  console.error("Payment processing error", error.code);
  logger.error("Database connection failed", { retryCount });
  ```

---

### INTERNAL_URL — exposed infrastructure

Internal URLs reveal infrastructure topology. Staging hostnames, admin panels, and database endpoints give attackers a map of the system before they start probing.

**Patterns to flag:**

- **Hostnames with internal/staging indicators** — subdomains or path segments containing `staging`, `internal`, `dev`, `preprod`, or `sandbox`:
  ```typescript
  const api = "https://api-staging.company.com/v2";
  const admin = "https://internal-admin.company.com/dashboard";
  const preview = "https://dev.myapp.io/api";
  const preprod = "https://preprod-api.example.com";
  ```

- **Hardcoded private IP addresses** — RFC 1918 ranges:
  ```typescript
  const dbHost = "10.0.3.42";
  const cache = "http://172.16.0.5:6379";
  const service = "http://192.168.1.100:8080/api";
  ```

- **Connector / webhook URLs with embedded tokens or secrets** (in cortex: the Minimi connector URL and MCP endpoints carry secret tokens — these must never be committed, especially not in git-tracked `.mcp.json`):
  ```
  https://hooks.slack.com/services/T01234567/B01234567/xyzSecretTokenHere
  https://minimi-connector.local/ctx?token=SECRET_TOKEN_HERE
  ```

- **Admin / dashboard URLs**:
  ```
  https://admin.company.com/users
  https://cloud.langfuse.com/project/abc123
  ```

- **Database hostnames**:
  ```typescript
  const host = "prod-db-cluster.c9abc123.eu-west-1.rds.amazonaws.com";
  const mongo = "mongodb+srv://cluster0.abc12.mongodb.net";
  ```

**What is acceptable (do not flag):**

- **Environment-gated URLs** — the correct pattern for environment-specific configuration:
  ```typescript
  const apiUrl = process.env.NODE_ENV === "production"
    ? process.env.API_URL
    : "http://localhost:3000";
  ```

- **Architecture comments** — describing topology, not connecting to it:
  ```typescript
  // In production, this calls the API gateway at api.company.com
  // which routes to the user-service behind the VPC.
  ```

- **Localhost references** — expected in development:
  ```typescript
  const devServer = "http://localhost:3000";
  const dbLocal = "postgresql://localhost:5432/myapp_dev";
  ```

- **`.env.example` placeholder hostnames**:
  ```bash
  API_URL=https://your-api-url.example.com
  DATABASE_HOST=your-db-host.example.com
  ```

---

## Confidence calibration

The security-reviewer applies asymmetric confidence thresholds. The cost of a false positive (developer spends 10 seconds confirming a test key is safe) is vastly lower than the cost of a false negative (a real secret ships to production). But the asymmetry differs by category.

### SECRET — be aggressive

Flag anything that looks like a real credential. The cost equation:

- **False positive:** Developer checks, confirms it is a test key or mock, dismisses. Cost: 10 seconds.
- **False negative:** Real API key or password ships to a repository. Cost: credential rotation, potential data breach, service compromise.

**When in doubt: flag it.** A brief interruption is always cheaper than a leaked credential.

### PII — be conservative

Only flag when there is supporting context that the data is real. A name alone is not enough — names are used as test data constantly.

- **False positive:** Developer checks, confirms "John Doe" is a placeholder, dismisses. Cost: 10 seconds, but repeated false positives on placeholder data erode trust in the reviewer.
- **False negative:** A real person's email or phone number in source code. Cost: privacy concern, potential regulatory issue, but lower blast radius than a leaked secret.

**When in doubt about a name:** only flag if there is possessive context ("Tim's key"), the name appears alongside other real-looking data (real email domain, real phone number), or the name is unusual enough that it is unlikely to be a placeholder.

**When in doubt about an email:** flag if the domain is a real consumer or corporate provider (gmail.com, outlook.com, company.co.uk). Do not flag reserved domains (example.com, example.org, test.com).

### LOG_LEAK — be moderate

Flag when PII fields are clearly being passed to logging or error output. Do not flag logging of opaque identifiers or development-gated debug blocks.

- **False positive:** Developer checks, confirms the logged field is an ID not PII, dismisses. Cost: 10 seconds.
- **False negative:** User emails or names flowing into log aggregators accessible to the entire engineering team, or into error tracking services with broad access. Cost: ongoing privacy leak, harder to remediate than a one-time secret exposure.

**When in doubt:** check whether the logged value could contain PII fields. `console.log(user)` is almost always a finding because user objects typically contain name and email. `console.log(userId)` is almost never a finding.

### INTERNAL_URL — be moderate

Flag hardcoded infrastructure URLs that reveal topology. Do not flag localhost, environment-gated patterns, or documentation comments.

- **False positive:** Developer checks, confirms the URL is gated or in a comment. Cost: 10 seconds.
- **False negative:** Internal hostname in source code gives attackers a target. Cost: information disclosure, reduced defence-in-depth.

**When in doubt:** check whether the URL is used in runtime code or is in a comment/documentation context. Runtime usage of hardcoded internal URLs is a finding. Descriptive comments about architecture are not.
