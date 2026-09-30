import { useEffect, useState } from "react";
import CameraForm from "../../components/CameraForm";
import SnapshotPolicyForm from "../../components/SnapshotPolicyForm";
import StatusBadge from "../../components/StatusBadge";
import {
  captureSnapshot,
  createCamera,
  deleteCamera,
  disableCamera,
  enableCamera,
  getCameras,
  getSnapshotPolicy,
  testCameraConnection,
  updateCamera,
  updateSnapshotPolicy,
} from "../../services/api";

export default function CamerasPage() {
  const [cameras, setCameras] = useState([]);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [editing, setEditing] = useState(null);
  const [showCreate, setShowCreate] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [busyId, setBusyId] = useState(null);

  const [policyCamera, setPolicyCamera] = useState(null);
  const [policy, setPolicy] = useState(null);
  const [policySaving, setPolicySaving] = useState(false);

  async function load() {
    try {
      setError("");
      const data = await getCameras();
      setCameras(data);
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || "Failed to load cameras");
    }
  }

  useEffect(() => {
    load();
  }, []);

  function notify(text) {
    setMessage(text);
    window.setTimeout(() => setMessage(""), 2500);
  }

  async function handleCreate(payload) {
    setSubmitting(true);
    setError("");
    try {
      await createCamera(payload);
      setShowCreate(false);
      notify("Camera added successfully.");
      await load();
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || "Failed to add camera");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleEdit(payload) {
    if (!editing) return;

    setSubmitting(true);
    setError("");
    try {
      await updateCamera(editing.id, payload);
      setEditing(null);
      notify("Camera updated.");
      await load();
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || "Failed to update camera");
    } finally {
      setSubmitting(false);
    }
  }

  async function toggleCamera(camera) {
    setBusyId(camera.id);
    try {
      if (camera.is_enabled) {
        await disableCamera(camera.id);
        notify("Camera disabled.");
      } else {
        await enableCamera(camera.id);
        notify("Camera enabled.");
      }
      await load();
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || "Failed to change camera state");
    } finally {
      setBusyId(null);
    }
  }

  async function handleConnection(camera) {
    setBusyId(camera.id);
    try {
      const result = await testCameraConnection(camera.id);
      notify(`${camera.name}: ${result.status} — ${result.message}`);
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || "Connection test failed");
    } finally {
      setBusyId(null);
    }
  }

  async function handleSnapshot(camera) {
    setBusyId(camera.id);
    try {
      await captureSnapshot(camera.id);
      notify(`Snapshot captured from ${camera.name}.`);
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || "Snapshot failed");
    } finally {
      setBusyId(null);
    }
  }

  async function handleDelete(camera) {
    const confirmed = window.confirm(
      `Delete "${camera.name}"? This may also remove related database records.`
    );

    if (!confirmed) return;

    setBusyId(camera.id);
    try {
      await deleteCamera(camera.id);
      notify("Camera deleted.");
      await load();
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || "Failed to delete camera");
    } finally {
      setBusyId(null);
    }
  }

  async function openPolicy(camera) {
    setBusyId(camera.id);
    try {
      const data = await getSnapshotPolicy(camera.id);
      setPolicy(data);
      setPolicyCamera(camera);
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || "Failed to load policy");
    } finally {
      setBusyId(null);
    }
  }

  async function savePolicy(payload) {
    if (!policyCamera) return;

    setPolicySaving(true);
    try {
      const updated = await updateSnapshotPolicy(policyCamera.id, payload);
      setPolicy(updated);
      notify("Snapshot policy updated.");
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || "Failed to save policy");
    } finally {
      setPolicySaving(false);
    }
  }

  return (
    <section>
      <div className="page-header">
        <div>
          <p className="eyebrow">Devices</p>
          <h1>Camera Control</h1>
          <p className="page-subtitle">
            Add, configure and operate simulator, Hikvision and NVR camera sources.
          </p>
        </div>

        <button className="button primary" onClick={() => setShowCreate(true)}>
          Add camera
        </button>
      </div>

      {error ? <div className="alert">{String(error)}</div> : null}
      {message ? <div className="success-banner">{message}</div> : null}

      {showCreate ? (
        <div className="modal-backdrop">
          <div className="modal-card">
            <div className="modal-header">
              <div>
                <p className="eyebrow">New device</p>
                <h2>Add camera</h2>
              </div>
            </div>
            <CameraForm
              onSubmit={handleCreate}
              onCancel={() => setShowCreate(false)}
              submitting={submitting}
            />
          </div>
        </div>
      ) : null}

      {editing ? (
        <div className="modal-backdrop">
          <div className="modal-card">
            <div className="modal-header">
              <div>
                <p className="eyebrow">Camera {editing.id}</p>
                <h2>Edit camera</h2>
              </div>
            </div>
            <CameraForm
              initialValue={editing}
              onSubmit={handleEdit}
              onCancel={() => setEditing(null)}
              submitting={submitting}
            />
          </div>
        </div>
      ) : null}

      {policyCamera ? (
        <div className="modal-backdrop">
          <div className="modal-card">
            <div className="modal-header">
              <div>
                <p className="eyebrow">{policyCamera.name}</p>
                <h2>Snapshot policy</h2>
              </div>
            </div>
            <SnapshotPolicyForm
              policy={policy}
              onSave={savePolicy}
              onCancel={() => {
                setPolicyCamera(null);
                setPolicy(null);
              }}
              saving={policySaving}
            />
          </div>
        </div>
      ) : null}

      <div className="camera-grid">
        {cameras.map((camera) => (
          <article className="camera-card" key={camera.id}>
            <div className="camera-card-top">
              <div>
                <span className="camera-id">Camera #{camera.id}</span>
                <h3>{camera.name}</h3>
                <p>
                  {camera.provider}
                  {camera.host ? ` · ${camera.host}` : ""}
                </p>
              </div>

              <StatusBadge
                status={camera.is_enabled ? "enabled" : "disabled"}
              />
            </div>

            <div className="camera-meta">
              <div>
                <span>Channel</span>
                <strong>{camera.channel}</strong>
              </div>
              <div>
                <span>Scheme</span>
                <strong>{camera.scheme?.toUpperCase()}</strong>
              </div>
              <div>
                <span>Port</span>
                <strong>{camera.port || "Default"}</strong>
              </div>
            </div>

            <div className="camera-actions">
              <button
                className="button small"
                onClick={() => handleConnection(camera)}
                disabled={busyId === camera.id}
              >
                Test connection
              </button>

              <button
                className="button small"
                onClick={() => handleSnapshot(camera)}
                disabled={busyId === camera.id || !camera.is_enabled}
              >
                Capture
              </button>

              <button
                className="button small"
                onClick={() => openPolicy(camera)}
                disabled={busyId === camera.id}
              >
                Policy
              </button>

              <button
                className="button small"
                onClick={() => toggleCamera(camera)}
                disabled={busyId === camera.id}
              >
                {camera.is_enabled ? "Disable" : "Enable"}
              </button>

              <button
                className="button small"
                onClick={() => setEditing(camera)}
              >
                Edit
              </button>

              <button
                className="button small danger"
                onClick={() => handleDelete(camera)}
                disabled={busyId === camera.id}
              >
                Delete
              </button>
            </div>
          </article>
        ))}

        {cameras.length === 0 ? (
          <div className="empty-card">
            <h3>No cameras yet</h3>
            <p>Add a simulator or Hikvision source to start capturing.</p>
          </div>
        ) : null}
      </div>
    </section>
  );
}
