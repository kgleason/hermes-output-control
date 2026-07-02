(function () {
  "use strict";

  const SDK = window.__HERMES_PLUGIN_SDK__;
  if (!SDK) return;
  const { React } = SDK;
  const h = React.createElement;
  const { useEffect, useState } = SDK.hooks;
  const { Card, CardHeader, CardTitle, CardContent, Badge, Button } = SDK.components;
  const Checkbox = SDK.components.Checkbox || function (props) {
    return h("input", {
      type: "checkbox",
      checked: !!props.checked,
      onChange: function (e) { props.onCheckedChange && props.onCheckedChange(e.target.checked); },
    });
  };

  function api(path, options) {
    return SDK.fetchJSON("/api/plugins/output-control" + path, options || {});
  }

  function OutputControlPage() {
    const [rules, setRules] = useState([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState("");

    function load() {
      setLoading(true);
      setError("");
      api("/rules")
        .then(function (data) { setRules(data.rules || []); })
        .catch(function (err) { setError(String(err && err.message || err)); })
        .finally(function () { setLoading(false); });
    }

    function save(next) {
      setRules(next);
      setSaving(true);
      setError("");
      api("/rules", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ rules: next.map(function (r) { return { id: r.id, enabled: !!r.enabled }; }) }),
      })
        .then(function (data) { setRules(data.rules || next); })
        .catch(function (err) { setError(String(err && err.message || err)); })
        .finally(function () { setSaving(false); });
    }

    function setRule(id, enabled) {
      save(rules.map(function (r) {
        return r.id === id ? Object.assign({}, r, { enabled: enabled }) : r;
      }));
    }

    function reset() {
      setSaving(true);
      api("/reset", { method: "POST" })
        .then(function (data) { setRules(data.rules || []); })
        .catch(function (err) { setError(String(err && err.message || err)); })
        .finally(function () { setSaving(false); });
    }

    useEffect(load, []);

    return h("div", { className: "space-y-4" },
      h(Card, null,
        h(CardHeader, { className: "flex flex-row items-center justify-between gap-4" },
          h("div", null,
            h(CardTitle, null, "Output Control"),
            h("p", { className: "text-sm text-muted-foreground mt-1" },
              "Toggle known Hermes CLI noise. Enabled means display it; disabled means suppress it. Restart Hermes sessions after changing rules."
            )
          ),
          h(Button, { variant: "outline", onClick: reset, disabled: saving }, "Reset")
        ),
        h(CardContent, { className: "space-y-3" },
          loading ? h("p", { className: "text-sm text-muted-foreground" }, "Loading…") : null,
          error ? h("p", { className: "text-sm text-destructive" }, error) : null,
          rules.map(function (rule) {
            return h("div", { key: rule.id, className: "flex items-start justify-between gap-4 rounded-lg border p-3" },
              h("div", { className: "space-y-1" },
                h("div", { className: "flex items-center gap-2" },
                  h("span", { className: "font-medium" }, rule.label),
                  h(Badge, { variant: "secondary" }, rule.id)
                ),
                h("p", { className: "text-sm text-muted-foreground" }, rule.description),
                h("code", { className: "text-xs" }, rule.match + ": " + rule.pattern)
              ),
              h("label", { className: "flex items-center gap-2 text-sm whitespace-nowrap" },
                h(Checkbox, {
                  checked: !!rule.enabled,
                  disabled: saving,
                  onCheckedChange: function (checked) { setRule(rule.id, !!checked); },
                }),
                "Display"
              )
            );
          })
        )
      )
    );
  }

  window.__HERMES_PLUGINS__.register("output-control", OutputControlPage);
})();
