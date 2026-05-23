# Configuration Layout

Tracked configuration templates live in this directory.

- Start from `config.example.yaml`.
- Keep real secrets out of git.
- Load tokens and other credentials from environment variables or a systemd environment file.
- Treat files here as defaults and examples, not as a place for deployment state.
