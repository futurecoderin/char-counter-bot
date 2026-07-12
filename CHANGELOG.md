# Changelog

All notable changes to Char Counter Bot are documented here.

This project follows [Semantic Versioning](https://semver.org/).

---

## [v1.0.0] — 2026-07-12  *(Current)*

### Added
- Initial public release as **Community Edition**
- Character count (total, including spaces)
- Character count (no spaces — tabs, newlines, spaces stripped)
- Word count (whitespace-delimited)
- Line count (newline-delimited)
- Forwarded message detection with distinct header
- Media caption analysis (photos, videos, documents, audio, voice)
- Google Sheets usage logging via Service Account (`sheets_logger.py`)
  - Non-blocking async writes (daemon thread — never slows the bot)
  - Lazy initialization with retry on transient errors
  - Auto-creates spreadsheet tab with headers on first run
- Webhook mode support (`WEBHOOK_URL` / `RENDER_EXTERNAL_URL`)
- Polling mode for local development (no server required)
- Flask + Gunicorn production WSGI setup
- `.env.example` with all configurable variables documented
- `GOOGLE_CREDENTIALS_PATH` environment variable for flexible key placement

### Changed
- `env_example.txt` → `.env.example` (standard naming)
- Bot description and welcome message updated to reference GitHub repo instead of personal domain
- `sheets_logger.py` scoped to Character Counter Bot only — removed dead code for unrelated bots
- Error startup message improved with clear setup instructions

### Removed
- Hardcoded `abhishekvigyan.com` references (3 occurrences)
- `log_video_downloader()` and `log_message_forwarder()` dead code from `sheets_logger.py`
- `VIDEO_DOWNLOADER_HEADERS` and `FORWARDER_HEADERS` unused constants
- Legacy `env.txt` fallback loading in `bot.py`

### Security
- `google_credentials.json` confirmed excluded from git via `.gitignore`
- `.env` confirmed excluded from git
- All secrets read exclusively from environment variables — zero hardcoded values

---

[v1.0.0]: https://github.com/futurecoderin/char-counter-bot/releases/tag/v1.0.0
