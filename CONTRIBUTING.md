# Contributing to Char Counter Bot

Thank you for your interest in contributing! This is a community-driven project and all contributions are welcome.

---

## How to Contribute

### 🐛 Bug Reports

Before opening an issue:
- Check the [Troubleshooting section](README.md#troubleshooting) in the README
- Search [existing issues](https://github.com/futurecoderin/char-counter-bot/issues)

When reporting a bug, include:
- Python version (`python3 --version`)
- pyTelegramBotAPI version (`pip show pyTelegramBotAPI`)
- The full error traceback
- Steps to reproduce

### 💡 Feature Requests

Open a GitHub Issue describing:
- What you want the bot to do
- Why it would be useful
- Any implementation ideas you have

### 🔀 Pull Requests

1. Fork the repository
2. Create a branch: `git checkout -b feat/your-feature-name`
3. Make your changes following the coding standards below
4. Verify no secrets are present: `grep -rn "TOKEN\|token\|key\|password" bot.py`
5. Commit: `git commit -m "feat: describe your change"`
6. Push and open a PR against `main`

---

## Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/)
- Use f-strings for string formatting
- Type hints on new functions
- Docstrings on all public functions

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add sentence count to analysis output
fix: handle empty caption on voice messages
docs: add webhook deployment guide for Railway
refactor: extract text metrics into helper function
chore: bump pyTelegramBotAPI to 4.27.0
```

### Security

- **Never** commit `.env`, tokens, or credential files
- All secrets must be read from environment variables
- Run the secret check before every PR:

```bash
grep -rn "TOKEN\|BOT_TOKEN\|SPREADSHEET_ID" --include="*.py" .
# Expected output: only references to os.getenv(...), never literal values
```

---

## Development Setup

```bash
git clone https://github.com/futurecoderin/char-counter-bot.git
cd char-counter-bot
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Fill in TELEGRAM_BOT_TOKEN
python bot.py
```

---

## Questions?

Open a [GitHub Discussion](https://github.com/futurecoderin/char-counter-bot/discussions) for general questions.

Thank you for contributing! 🙏
