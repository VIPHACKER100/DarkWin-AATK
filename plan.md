# DARKWIN — Analysis & Fix Plan

**Date:** 2026-08-09
**Scope:** Full analysis of every report/output file in `reports/` + the modules that
produce them, followed by code fixes. All issues below were confirmed against real
scan artifacts (logs, TXT/CSV/XML outputs) and the module source.

---

## 1. What was analyzed

- **114 files** in `reports/` (8 target folders, 11 sessions): log files, `asn.txt`,
  `whois.txt`, `subdomains_*.txt`, `dns_brute.{csv,xml}`, `reverse_ip.txt`,
  `social.txt`, `cloud_enum.log`, `email_harvester.log`, `metadata_scraper.log`.
- The modules that write them: `modules/recon/*`, `modules/osint/*`, `modules/cloud/*`,
  `modules/web/*`, plus `core` (config/engine/pipeline) and the dashboard backend.
- Installer state (`install_tools.log`, `scripts/install_tools.sh`) and tool PATH.

---

## 2. Issues found (with evidence)

### 2.1 Target URL not sanitized → broken output directories  [CRITICAL]
- Direct evidence:
  - `reports/https:/acropolis.in/2026-07-24_02-24-43/...`
  - `reports/http:/testaspnet.vulnweb.com/about.aspx/2026-07-20_12-33-39/...`
  - `reports/https:/https:/xprtcommunity.in/2026-07-20_13-44-39/...`
- Root cause: `core/config_loader.get_output_dir()` used the raw target string as a
  path component (`Path(base) / target / session_id`). A target like
  `https://xprtcommunity.in` was parsed by `pathlib` as `https:/xprtcommunity.in`,
  creating nested, unwritable-from-dashboard folders and a double-scheme folder
  (`https:/https:/...`).
- Downstream effect: external tools were fed the full URL — `theHarvester` ran against
   `https://https://xprtcommunity.in/` and returned nothing;
  ShodanInternetDB could not resolve them.

### 2.2 `asn.txt` contained raw junk instead of data  [HIGH
- Evidence: `asn.txt` files contain `% No entries found for the selected source(s).`
  followed by the full HTML of a bgp.he.net **404 page** (`<title>... - bgp.he.net</title>`).
- Root cause: `modules/recon/asn_lookup.py` ran `whois -h whois.radb.net` and
  `curl … https://bgp.he.net/dns/<target>` and dumped **both** streams into
  `asn.txt`, including error/404 HTML.

### 2.3 `metadata_scraper` (metagoofil) is Python 2 but runs under Python 3  [HIGH]
- Evidence: `metadata_scraper.log` shows
  `SyntaxError: Missing parentheses in call to 'print'. Did you mean print(...)?`
- Root cause: upstream `metagoofil` 2.2 is Python 2-only. The installer wrote a
  wrapper that `exec python3 /opt/metagoofil/metagoofil.py` and referenced a
  nonexistent `/opt/metagoofil/requirements.txt`.

### 2.4 `cloud_enum` not installed correctly  [HIGH]
- Evidence: every `cloud_enum.log` contains only
  `[!] Please pip install requirements.txt.`
- Root cause: `install_cloud_enum()` ran `pip3 install -r /opt/cloud_enum/requirements.txt`
  which doesn’t exist (the repo ships `pyproject.toml`), and installed the tool via a
  symlink that couldn’t resolve its bundled `enum_tools` package.

### 2.5 `sherlock`/`arjun` "not found" at runtime  [MEDIUM]
- Evidence: `social_media_enum.log` → `/bin/sh: 1: sherlock: not found`.
- Root cause: tools installed into the project venv (`venv/bin/sherlock`, `arjun`)
  are not reachable from shells that don’t have the venv on `PATH`. The installer
  never placed them in `/usr/local/bin`.

### 2.6 Empty `wordlists/` directory  [MEDIUM]
- Evidence: `wordlists/` contains only `.gitkeep`; `dns_brute`/fuzzers reference
  `wordlists/SecLists/...` and `wordlists/PayloadsAllTheThings/...`.
- Root cause: `scripts/install_wordlists.sh` was never run.

### 2.7 Missing API keys → noisy theHarvester runs  [OPERATIONAL]
- Evidence: dozens of `[!] Missing API key for …` lines in `email_harvester.log`
  (bevigil, bitbucket, github, brave, builtwith, etc.).
- Some of this is expected without keys; the tool should still degrade cleanly.

### 2.8 Stray artifact files at repo root  [LOW]
- Evidence: `emails.json` / `emails.xml` at the repository root (mtime 2026-08-09 00:03),
  an earlier theHarvester run that wrote to the CWD.

---

## 3. Fixes applied

### 3.1 New `core/target.py`
- `normalize_target()` — strips scheme (`://…`), path/query/fragment, port and
  trailing dot; lowercases; best-effort handles double-scheme inputs; keeps IPv4/IPv6.
- `validate_target()` — rejects anything that isn’t a sane hostname or IP
  (`../`, `/`, `:`, empty etc.).
- `safe_target()` — normalize + validate, and the result is guaranteed safe to embed
  in a filesystem path (matches dashboard `RE_ID`).

### 3.2 Target normalization wired in everywhere targets become paths/tool args
- `core/config_loader.get_output_dir()` — defensive `safe_target()` before MkDir
  (falls back to `_invalid_target` instead of creating nested dirs).
- `core/darkwin.py` CLI `run` — rejects invalid targets with a clear message.
- `dashboard/backend/app.py` `start_scan` — normalizes the target and returns 400
  for unusable ones.
- `dashboard/backend/app.py` `list_targets` — skips folders created from malformed
  targets (`http:`, `https:`) so they no longer surface as ghost targets that can’t
  be opened/deleted.

### 3.3 `modules/recon/asn_lookup.py` — rewritten
- Primary source: HackerTarget `aslookup` API → clean `IP,ASN,Owner` CSV.
- Fallback: parsed `origin:`/`descr:` lines from `whois -h whois.radb.net`.
- No more raw HTML / 404 pages in `asn.txt`.

### 3.4 `modules/osint/metadata_scraper.py` — Python 2 aware
- Prefers `python2 /opt/metagoofil/metagoofil.py`.
- Falls back to `metagoofil` on PATH.
- Creates a clean `metadata/` dir + writes an explanatory note if the tool is missing,
  instead of letting a py3 SyntaxError pollute the log.

### 3.5 `modules/osint/social_media_enum.py` & `modules/cloud/cloud_enum.py`
- Skip gracefully (with a log message / empty result file) when `sherlock` /
  `cloud_enum` are not installed, instead of `/bin/sh: … not found` noise.

### 3.6 `scripts/install_tools.sh`
- `install_pip()` now symlinks pip-installed binaries into `/usr/local/bin`.
- `install_metagoofil()` installs `python2` (best effort) and generates a
  python2-first wrapper; stops referencing a nonexistent `requirements.txt`.
- `install_cloud_enum()` installs the package from its `pyproject.toml`
  (`pip3 install /opt/cloud_enum`), which resolves the `enum_tools` import and
  the “Please pip install requirements.txt” failure.

### 3.7 Progress bar on every pipeline execution path
- New `core/console_progress.py` — shared `cli_progress()` context manager that
  shows a live 0–100% `rich` bar (phase label + bar + percent) on interactive
  terminals and falls back to one clean `[NN%] <phase>` line per update when
  stdout is piped (non-TTY), so output stays tidy with `| tee`/CI.
- `darkwin run` now wraps `run_pipeline` with it (replaces the earlier inline
  bar), so the CLI shows realtime progress.
- The **dashboard backend console** now also renders the same bar around scans
  triggered over HTTP (`/scan`), covering the last remaining execution path.

### 3.8 Tests
- Added `tests/unit/test_target.py` (8 cases, incl. the exact malformed-folder reproductions).
- Updated `tests/unit/test_recon_modules.py`, `test_osint_modules.py`,
  `test_cloud_modules.py` for the new behaviors (missing-binary skips, clean ASN output).
- `test_cli_run_recon_mode` now also exercises the CLI progress-bar path with a mocked pipeline.

---

## 4. Verification

- Full backend suite: **225 passed** (`PYTHONPATH=venv/... pytest -q`).
- Smoke checks:
  - `safe_target("http://testaspnet.vulnweb.com/about.aspx")` → `testaspnet.vulnweb.com`
  - `safe_target("https://https://xprtcommunity.in/")` → `xprtcommunity.in`
  - Dashboard: `POST /scan {target:"https://x.com/path"}` → normalized to `x.com`;
    `POST /scan {target:"https://"}` → 400.

---

## 5. Follow-up / operational steps (not code-changes)

Status as of last session:
- [x] Malformed folders `reports/http:` / `reports/https:` were already gone.
- [x] `bash scripts/install_wordlists.sh` — SecLists + PayloadsAllTheThings cloned into `wordlists/`.
- [x] Tool re-verify — `verify_all_tools` now reports **all tools found** (metagoofil,
      cloud_enum, msfconsole, linkfinder…). `sherlock`/`arjun` were already installed in the
      project `venv/` but invisible to `shutil.which` because `venv/bin` isn't on PATH; fixed
      with symlinks into `~/.local/bin`.
- [x] Stale root artifacts removed: `emails.json`, `emails.xml`.
- [ ] **Add API keys** to `core/config.yaml` (`api_keys.github_token`,
      `api_keys.hibp_api_key`, and any of theHarvester sources you use) for better OSINT results.

---

## 6. File change summary

| File | Change |
|------|--------|
| `core/target.py` | **new** — normalization/validation/safe-slug |
| `core/config_loader.py` | sanitize target in `get_output_dir` |
| `core/darkwin.py` | CLI validates + normalizes target |
| `dashboard/backend/app.py` | normalize on `/scan`, filter bad dirs in `/targets` |
| `modules/recon/asn_lookup.py` | rewritten (API + parsed radb fallback) |
| `modules/osint/metadata_scraper.py` | python2-aware + graceful |
| `modules/osint/social_media_enum.py` | missing-binary skip |
| `modules/cloud/cloud_enum.py` | missing-binary skip |
| `core/darkwin.py` | CLI `run` wraps pipeline in a live rich progress bar |
| `core/console_progress.py` | **new** — shared live-bar / piped progress renderer |
| `dashboard/backend/app.py` | server-console progress for HTTP-triggered scans |
| `scripts/install_tools.sh` | pip symlinks; metagoofil python2; cloud_enum pyproject |
| `tests/unit/test_target.py` | **new** |
| `tests/unit/test_recon_modules.py` | ASN tests updated |
| `tests/unit/test_osint_modules.py` | sherlock/metagoofil tests updated |
| `tests/unit/test_cloud_modules.py` | cloud_enum tests updated |