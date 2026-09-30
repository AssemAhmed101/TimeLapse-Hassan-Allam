import { useEffect, useState } from "react";
import {
  API_BASE_URL,
  getMonitoringHealth,
  getMonitoringLogs,
} from "../../services/api";
import { useAuth } from "../../auth/AuthContext";

export default function SettingsPage() {
  const { user } = useAuth();
  const [health, setHealth] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function refresh() {
    setLoading(true);
    setError("");

    try {
      const data = await getMonitoringHealth();
      setHealth(data);

      if (user?.role === "admin" || user?.role === "operator") {
        const logData = await getMonitoringLogs(80);
        setLogs(logData.lines || []);
      }
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "Could not load monitoring data"
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  return (
    <section>
      <div className="page-header">
        <div>
          <p className="eyebrow">System Operations</p>
          <h1>Monitoring & Reliability</h1>
          <p className="page-subtitle">
            Live system health, scheduler state, storage, cloud and recent logs.
          </p>
        </div>

        <button className="button secondary" onClick={refresh} disabled={loading}>
          {loading ? "Checking..." : "Refresh"}
        </button>
      </div>

      {error ? <div className="alert">{String(error)}</div> : null}

      {health ? (
        <>
          <div className={`system-health-banner ${health.status}`}>
            <div>
              <span>Overall System Status</span>
              <strong>{health.status.toUpperCase()}</strong>
            </div>
            <small>
              Uptime: {Math.floor(health.uptime_seconds / 60)} minutes
            </small>
          </div>

          <div className="monitor-grid">
            <article className="monitor-card">
              <span>Database</span>
              <strong>{health.database.ok ? "Online" : "Offline"}</strong>
              <small>{health.database.error || "Database connection healthy"}</small>
            </article>

            <article className="monitor-card">
              <span>Scheduler</span>
              <strong>{health.scheduler.running ? "Running" : "Stopped"}</strong>
              <small>
                {health.scheduler.cycle_count} cycles / {health.scheduler.failed_cycle_count} failed
              </small>
            </article>

            <article className="monitor-card">
              <span>Storage</span>
              <strong>{health.storage.disk.free_gb} GB free</strong>
              <small>{health.storage.disk.usage_percent}% used</small>
            </article>

            <article className="monitor-card">
              <span>Cloud</span>
              <strong>{health.cloud.configured ? "Configured" : "Not configured"}</strong>
              <small>{health.cloud.provider}</small>
            </article>

            <article className="monitor-card">
              <span>Cameras</span>
              <strong>{health.cameras.enabled} / {health.cameras.total} enabled</strong>
              <small>
                Last snapshot: {health.cameras.latest_snapshot_at
                  ? new Date(health.cameras.latest_snapshot_at).toLocaleString()
                  : "No snapshots yet"}
              </small>
            </article>

            <article className="monitor-card">
              <span>Version</span>
              <strong>{health.application.version}</strong>
              <small>{health.application.environment}</small>
            </article>
          </div>

          {health.warnings?.length ? (
            <div className="monitor-warning-list">
              <strong>Warnings</strong>
              {health.warnings.map((warning) => (
                <span key={warning}>{warning}</span>
              ))}
            </div>
          ) : null}
        </>
      ) : null}

      <div className="panel settings-panel">
        <div>
          <span>API Base URL</span>
          <strong>{API_BASE_URL}</strong>
        </div>
        <div>
          <span>Current Phase</span>
          <strong>Phase 16 — Monitoring & Reliability</strong>
        </div>
      </div>

      {(user?.role === "admin" || user?.role === "operator") ? (
        <div className="log-panel">
          <div className="log-panel-header">
            <div>
              <p className="eyebrow">Diagnostics</p>
              <h2>Recent Logs</h2>
            </div>
            <span>{logs.length} lines</span>
          </div>

          <pre>
            {logs.length ? logs.join("\n") : "No log entries yet."}
          </pre>
        </div>
      ) : null}
    </section>
  );
}
