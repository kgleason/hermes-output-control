# hermes-output-control

Tiny Hermes plugin that suppresses noisy CLI progress lines while keeping useful terminal command summaries.

Suppresses:

- `┊ ⚡ preparing ...`
- `🔧 Auto-repaired tool name ...`

Keeps:

- `┊ 💻 $ gh ...`

## Install

```bash
git clone git@github.com:kgleason/hermes-output-control.git ~/.hermes/plugins/output-control
hermes plugins enable output-control
```

Restart Hermes sessions/gateways after enabling.
