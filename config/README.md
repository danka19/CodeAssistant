# Configuration Layout

Tracked configuration templates live in this directory.

- Start from `config.example.yaml`.
- Keep real secrets out of git.
- Load tokens and other credentials from environment variables or a systemd environment file.
- Treat files here as defaults and examples, not as a place for deployment state.
- For Phase 1 manual testing, set `TELEGRAM_BOT_TOKEN` in the environment and put your Telegram numeric user id into `telegram.allowed_user_ids`.
- You can also keep the allowlist next to the bot token by setting `TELEGRAM_ALLOWED_USER_IDS` as a comma-separated env variable, for example in `.env.local` or a systemd env file.
- For local repository testing, the app also reads `.env.local` at startup if that file exists.
