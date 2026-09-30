import { useEffect, useState } from "react";

export default function SnapshotPolicyForm({
  policy,
  onSave,
  onCancel,
  saving = false,
}) {
  const [form, setForm] = useState({
    enabled: true,
    interval_seconds: 21600,
    start_time: "00:00:00",
    end_time: "23:59:59",
    retry_count: 3,
    retry_delay_seconds: 2,
  });

  useEffect(() => {
    if (policy) {
      setForm({
        enabled: policy.enabled,
        interval_seconds: policy.interval_seconds,
        start_time: policy.start_time,
        end_time: policy.end_time,
        retry_count: policy.retry_count,
        retry_delay_seconds: policy.retry_delay_seconds,
      });
    }
  }, [policy]);

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function submit(event) {
    event.preventDefault();
    onSave({
      enabled: Boolean(form.enabled),
      interval_seconds: Number(form.interval_seconds),
      start_time: form.start_time,
      end_time: form.end_time,
      retry_count: Number(form.retry_count),
      retry_delay_seconds: Number(form.retry_delay_seconds),
    });
  }

  return (
    <form className="camera-form" onSubmit={submit}>
      <div className="form-grid">
        <label>
          <span>Interval (hours)</span>
          <input
            type="number"
            min="0.01"
            max="24"
            step="0.25"
            value={Number(form.interval_seconds) / 3600}
            onChange={(e) => update("interval_seconds", Number(e.target.value) * 3600)}
          />
          <small>6 hours = 4 captures per camera every 24 hours.</small>
        </label>

        <label>
          <span>Start time</span>
          <input
            type="time"
            step="1"
            value={form.start_time}
            onChange={(e) => update("start_time", e.target.value)}
          />
        </label>

        <label>
          <span>End time</span>
          <input
            type="time"
            step="1"
            value={form.end_time}
            onChange={(e) => update("end_time", e.target.value)}
          />
        </label>

        <label>
          <span>Retry count</span>
          <input
            type="number"
            min="0"
            max="10"
            value={form.retry_count}
            onChange={(e) => update("retry_count", e.target.value)}
          />
        </label>

        <label>
          <span>Retry delay</span>
          <input
            type="number"
            min="0"
            max="300"
            value={form.retry_delay_seconds}
            onChange={(e) => update("retry_delay_seconds", e.target.value)}
          />
        </label>

        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={form.enabled}
            onChange={(e) => update("enabled", e.target.checked)}
          />
          <span>Automatic capture enabled</span>
        </label>
      </div>

      <div className="form-actions">
        <button className="button secondary" type="button" onClick={onCancel}>
          Cancel
        </button>
        <button className="button primary" type="submit" disabled={saving}>
          {saving ? "Saving..." : "Save policy"}
        </button>
      </div>
    </form>
  );
}
