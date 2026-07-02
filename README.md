# hermes-output-control

Configurable Hermes plugin that suppresses selected CLI progress/context messages while keeping useful terminal command summaries.

Defaults to suppress:

- `┊ ⚡ preparing ...`
- `🔧 Auto-repaired tool name ...`
- accidental `PONYTAIL MODE ACTIVE ...` context dumps

Keeps:

- `┊ 💻 $ gh ...`

## Install

```bash
git clone git@github.com:kgleason/hermes-output-control.git ~/.hermes/plugins/output-control
hermes plugins enable output-control
```

Restart Hermes sessions/gateways after enabling.

## Dashboard

Open `hermes dashboard` and use the `Output Control` tab to toggle known rules.

Enabled = display the message. Disabled = suppress it.

Changes are saved to `~/.hermes/plugins/output-control/rules.local.json`.
