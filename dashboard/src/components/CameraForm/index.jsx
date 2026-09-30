import { useEffect, useState } from "react";

const emptyForm = {
  name: "",
  provider: "simulator",
  host: "",
  username: "",
  password: "",
  scheme: "http",
  port: "",
  channel: 1,
  ptz_preset_id: "",
  ptz_settle_seconds: 15,
  is_enabled: true,
};

export default function CameraForm({
  initialValue = null,
  onSubmit,
  onCancel,
  submitting = false,
}) {
  const [form, setForm] = useState(emptyForm);

  useEffect(() => {
    if (initialValue) {
      setForm({
        name: initialValue.name || "",
        provider: initialValue.provider || "simulator",
        host: initialValue.host || "",
        username: initialValue.username || "",
        password: "",
        scheme: initialValue.scheme || "http",
        port: initialValue.port ?? "",
        channel: initialValue.channel ?? 1,
        ptz_preset_id: initialValue.ptz_preset_id ?? "",
        ptz_settle_seconds: initialValue.ptz_settle_seconds ?? 15,
        is_enabled: initialValue.is_enabled ?? true,
      });
    } else {
      setForm(emptyForm);
    }
  }, [initialValue]);

  const isHikvision =
    form.provider === "hikvision" || form.provider === "hikvision_nvr";

  function update(field, value) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  function handleSubmit(event) {
    event.preventDefault();

    const payload = {
      name: form.name.trim(),
      provider: form.provider,
      host: isHikvision ? form.host.trim() || null : null,
      username: isHikvision ? form.username.trim() || null : null,
      scheme: form.scheme,
      port: form.port === "" ? null : Number(form.port),
      channel: Number(form.channel),
      ptz_preset_id:
        isHikvision && form.ptz_preset_id !== ""
          ? Number(form.ptz_preset_id)
          : null,
      ptz_settle_seconds: Number(form.ptz_settle_seconds),
      is_enabled: Boolean(form.is_enabled),
    };

    if (form.password) {
      payload.password = form.password;
    } else if (!initialValue && isHikvision) {
      payload.password = "";
    }

    onSubmit(payload);
  }

  return (
    <form className="camera-form" onSubmit={handleSubmit}>
      <div className="form-grid">
        <label>
          <span>Name</span>
          <input
            value={form.name}
            onChange={(e) => update("name", e.target.value)}
            placeholder="Tower Camera 01"
            required
          />
        </label>

        <label>
          <span>Provider</span>
          <select
            value={form.provider}
            onChange={(e) => update("provider", e.target.value)}
          >
            <option value="simulator">Simulator</option>
            <option value="hikvision">Hikvision Camera</option>
            <option value="hikvision_nvr">Hikvision NVR</option>
          </select>
        </label>

        {isHikvision ? (
          <>
            <label>
              <span>Host / IP</span>
              <input
                value={form.host}
                onChange={(e) => update("host", e.target.value)}
                placeholder="192.168.1.50"
                required
              />
            </label>

            <label>
              <span>Username</span>
              <input
                value={form.username}
                onChange={(e) => update("username", e.target.value)}
                placeholder="admin"
                required
              />
            </label>

            <label>
              <span>Password</span>
              <input
                type="password"
                value={form.password}
                onChange={(e) => update("password", e.target.value)}
                placeholder={initialValue ? "Leave blank to keep existing" : "Password"}
                required={!initialValue}
              />
            </label>

            <label>
              <span>Scheme</span>
              <select
                value={form.scheme}
                onChange={(e) => update("scheme", e.target.value)}
              >
                <option value="http">HTTP</option>
                <option value="https">HTTPS</option>
              </select>
            </label>

            <label>
              <span>Port</span>
              <input
                type="number"
                min="1"
                max="65535"
                value={form.port}
                onChange={(e) => update("port", e.target.value)}
                placeholder="80"
              />
            </label>

            <label>
              <span>Channel</span>
              <input
                type="number"
                min="1"
                max="256"
                value={form.channel}
                onChange={(e) => update("channel", e.target.value)}
              />
            </label>

            <label>
              <span>Fixed PTZ preset</span>
              <input
                type="number"
                min="1"
                max="300"
                value={form.ptz_preset_id}
                onChange={(e) => update("ptz_preset_id", e.target.value)}
                placeholder="1"
              />
            </label>

            <label>
              <span>PTZ settle time (seconds)</span>
              <input
                type="number"
                min="0"
                max="120"
                value={form.ptz_settle_seconds}
                onChange={(e) => update("ptz_settle_seconds", e.target.value)}
              />
            </label>
          </>
        ) : null}

        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={form.is_enabled}
            onChange={(e) => update("is_enabled", e.target.checked)}
          />
          <span>Camera enabled</span>
        </label>
      </div>

      <div className="form-actions">
        <button className="button secondary" type="button" onClick={onCancel}>
          Cancel
        </button>
        <button className="button primary" type="submit" disabled={submitting}>
          {submitting ? "Saving..." : initialValue ? "Save changes" : "Add camera"}
        </button>
      </div>
    </form>
  );
}
