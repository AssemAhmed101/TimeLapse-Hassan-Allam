import { useEffect, useMemo, useState } from "react";
import StatCard from "../../components/StatCard";
import StatusBadge from "../../components/StatusBadge";
import {
  getCameras,
  getCloudStatus,
  getSnapshots,
  getStorageStatus,
  getTimelapses,
} from "../../services/api";

export default function DashboardPage() {
  const [state, setState] = useState({
    loading: true,
    error: "",
    cameras: [],
    snapshots: [],
    timelapses: [],
    storage: null,
    cloud: null,
  });

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const [cameras, snapshots, timelapses, storage, cloud] =
          await Promise.all([
            getCameras(),
            getSnapshots(),
            getTimelapses(),
            getStorageStatus(),
            getCloudStatus(),
          ]);

        if (!cancelled) {
          setState({
            loading: false,
            error: "",
            cameras,
            snapshots,
            timelapses,
            storage,
            cloud,
          });
        }
      } catch (error) {
        if (!cancelled) {
          setState((current) => ({
            ...current,
            loading: false,
            error:
              error?.response?.data?.detail ||
              error?.message ||
              "Could not reach backend",
          }));
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const onlineCount = useMemo(
    () => state.cameras.filter((camera) => camera.is_enabled).length,
    [state.cameras]
  );

  return (
    <section>
      <div className="page-header">
        <div>
          <p className="eyebrow">System Overview</p>
          <h1>Dashboard</h1>
          <p className="page-subtitle">
            Cameras, captures, generated time-lapses, storage and cloud status.
          </p>
        </div>

        <div className="connection-card">
          <span>Backend</span>
          <StatusBadge status={state.error ? "offline" : state.loading ? "checking" : "online"} />
        </div>
      </div>

      {state.error ? (
        <div className="alert">
          Backend connection error: {state.error}
        </div>
      ) : null}

      <div className="stats-grid">
        <StatCard
          label="Cameras"
          value={state.loading ? "—" : state.cameras.length}
          hint={`${onlineCount} enabled`}
        />
        <StatCard
          label="Snapshots"
          value={state.loading ? "—" : state.snapshots.length}
          hint="Stored captures"
        />
        <StatCard
          label="Time-Lapses"
          value={state.loading ? "—" : state.timelapses.length}
          hint="Generated videos"
        />
        <StatCard
          label="Cloud"
          value={state.loading ? "—" : state.cloud?.provider || "Unknown"}
          hint={state.cloud?.configured ? "Configured" : "Needs setup"}
        />
      </div>

      <div className="content-grid">
        <article className="panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">Cameras</p>
              <h2>Camera status</h2>
            </div>
          </div>

          <div className="camera-list">
            {state.cameras.length === 0 && !state.loading ? (
              <p className="empty-state">No cameras added yet.</p>
            ) : (
              state.cameras.slice(0, 6).map((camera) => (
                <div className="camera-row" key={camera.id}>
                  <div>
                    <strong>{camera.name}</strong>
                    <small>
                      {camera.provider} · channel {camera.channel}
                    </small>
                  </div>
                  <StatusBadge
                    status={camera.is_enabled ? "enabled" : "disabled"}
                  />
                </div>
              ))
            )}
          </div>
        </article>

        <article className="panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">Storage</p>
              <h2>Disk overview</h2>
            </div>
          </div>

          {state.storage ? (
            <div className="storage-summary">
              <div>
                <span>Free space</span>
                <strong>{state.storage.disk.free_gb} GB</strong>
              </div>
              <div>
                <span>Usage</span>
                <strong>{state.storage.disk.usage_percent}%</strong>
              </div>
              <div>
                <span>Snapshots</span>
                <strong>{state.storage.snapshots.total_mb} MB</strong>
              </div>
              <div>
                <span>Videos</span>
                <strong>{state.storage.timelapses.total_mb} MB</strong>
              </div>
            </div>
          ) : (
            <p className="empty-state">Storage data unavailable.</p>
          )}
        </article>
      </div>
    </section>
  );
}
