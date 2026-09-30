import { useEffect, useMemo, useState } from "react";
import {
  generateTimelapse,
  previewTimelapse,
  startHighSpeedCapture,
  getHighSpeedCaptureStatus,
  stopHighSpeedCapture,
} from "../../services/api";

const resolutionOptions = [
  { label: "Original", width: "", height: "" },
  { label: "720p", width: 1280, height: 720 },
  { label: "1080p", width: 1920, height: 1080 },
  { label: "1440p", width: 2560, height: 1440 },
  { label: "4K", width: 3840, height: 2160 },
];

function toApiDateTime(value) {
  return value ? new Date(value).toISOString() : null;
}

function toLocalDateTimeInput(value) {
  if (!value) return "";
  const date = new Date(value);
  const pad = (part) => String(part).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

export default function TimelapseBuilder({
  cameras,
  onGenerated,
}) {
  const [form, setForm] = useState({
    cameraId: cameras[0]?.id ? String(cameras[0].id) : "",
    startAt: "",
    endAt: "",
    fps: 25,
    resolution: "1080p",
  });

  const [preview, setPreview] = useState(null);
  const [previewing, setPreviewing] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [testConfig, setTestConfig] = useState({ intervalSeconds: "1", durationMinutes: "15" });
  const [testStatus, setTestStatus] = useState(null);
  const [testLoading, setTestLoading] = useState(false);
  const [testError, setTestError] = useState("");

  useEffect(() => {
    if (!form.cameraId) {
      setTestStatus(null);
      return undefined;
    }

    let cancelled = false;
    let timer = null;

    async function poll() {
      try {
        const data = await getHighSpeedCaptureStatus(Number(form.cameraId));
        if (cancelled) return;
        setTestStatus(data);

        if (data.running) {
          timer = window.setTimeout(poll, 1000);
        }
      } catch {
        if (!cancelled) setTestStatus(null);
      }
    }

    poll();
    return () => {
      cancelled = true;
      if (timer) window.clearTimeout(timer);
    };
  }, [form.cameraId, testStatus?.running]);

  async function handleStartTest() {
    if (!form.cameraId) return;
    setTestError("");
    setTestLoading(true);
    try {
      const data = await startHighSpeedCapture({
        camera_id: Number(form.cameraId),
        interval_seconds: Number(testConfig.intervalSeconds),
        duration_seconds: Number(testConfig.durationMinutes) * 60,
      });
      setTestStatus(data);
    } catch (err) {
      setTestError(err?.response?.data?.detail || err?.message || "Could not start capture test");
    } finally {
      setTestLoading(false);
    }
  }

  async function handleStopTest() {
    if (!form.cameraId) return;
    setTestError("");
    try {
      const data = await stopHighSpeedCapture(Number(form.cameraId));
      setTestStatus(data);
    } catch (err) {
      setTestError(err?.response?.data?.detail || err?.message || "Could not stop capture test");
    }
  }

  function useTestRange() {
    const rangeStart = testStatus?.started_at || testStatus?.first_snapshot_at;
    const rangeEnd = testStatus?.finished_at || testStatus?.last_snapshot_at;
    if (!rangeStart || !rangeEnd) return;
    const paddedEnd = new Date(new Date(rangeEnd).getTime() + 2000).toISOString();
    setForm((current) => ({
      ...current,
      startAt: toLocalDateTimeInput(rangeStart),
      endAt: toLocalDateTimeInput(paddedEnd),
      fps: 25,
    }));
    setPreview(null);
    setSuccess("");
  }

  const selectedResolution = useMemo(
    () =>
      resolutionOptions.find(
        (item) => item.label === form.resolution
      ) || resolutionOptions[0],
    [form.resolution]
  );

  function update(field, value) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));

    setPreview(null);
    setSuccess("");
  }

  function payload() {
    return {
      camera_id: Number(form.cameraId),
      start_at: toApiDateTime(form.startAt),
      end_at: toApiDateTime(form.endAt),
      fps: Number(form.fps),
    };
  }

  async function handlePreview() {
    setError("");
    setSuccess("");
    setPreviewing(true);

    try {
      const data = await previewTimelapse(payload());
      setPreview(data);
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "Preview failed"
      );
    } finally {
      setPreviewing(false);
    }
  }

  async function handleGenerate() {
    setError("");
    setSuccess("");
    setGenerating(true);

    try {
      const base = payload();

      const data = await generateTimelapse({
        ...base,
        output_width: selectedResolution.width || null,
        output_height: selectedResolution.height || null,
      });

      setSuccess(
        `Time-lapse #${data.timelapse.id} generated from ${data.snapshot_count} snapshots.`
      );

      if (onGenerated) {
        onGenerated(data);
      }
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "Generation failed"
      );
    } finally {
      setGenerating(false);
    }
  }

  const validForm =
    form.cameraId &&
    form.startAt &&
    form.endAt &&
    Number(form.fps) > 0;

  return (
    <div className="builder-panel">
      <div className="builder-header">
        <div>
          <p className="eyebrow">Create video</p>
          <h2>Custom Time-Lapse Builder</h2>
          <p>
            Choose the camera, time range, frame rate and output resolution.
          </p>
        </div>
      </div>

      <div className="high-speed-test">
        <div className="high-speed-test-head">
          <div>
            <p className="eyebrow">Short performance test</p>
            <h3>High-Speed Capture Test</h3>
            <p>Capture fast snapshots for a short test, then use the exact range to generate a smooth time-lapse.</p>
          </div>
          <span className={`capture-state ${testStatus?.state || "idle"}`}>
            {testStatus?.state || "idle"}
          </span>
        </div>

        <div className="high-speed-controls">
          <label>
            <span>Snapshot interval</span>
            <select
              value={testConfig.intervalSeconds}
              disabled={testStatus?.running}
              onChange={(event) => setTestConfig((current) => ({ ...current, intervalSeconds: event.target.value }))}
            >
              <option value="1">Every 1 second</option>
              <option value="0.5">Every 0.5 second</option>
              <option value="2">Every 2 seconds</option>
            </select>
          </label>

          <label>
            <span>Test duration</span>
            <select
              value={testConfig.durationMinutes}
              disabled={testStatus?.running}
              onChange={(event) => setTestConfig((current) => ({ ...current, durationMinutes: event.target.value }))}
            >
              <option value="5">5 minutes</option>
              <option value="10">10 minutes</option>
              <option value="15">15 minutes</option>
            </select>
          </label>

          <div className="high-speed-actions">
            {!testStatus?.running ? (
              <button className="button primary" type="button" disabled={!form.cameraId || testLoading} onClick={handleStartTest}>
                {testLoading ? "Starting..." : "Start Capture Test"}
              </button>
            ) : (
              <button className="button danger" type="button" onClick={handleStopTest}>Stop Test</button>
            )}
          </div>
        </div>

        {testStatus && testStatus.state !== "idle" ? (
          <>
            <div className="capture-progress"><div style={{ width: `${testStatus.progress_percent || 0}%` }} /></div>
            <div className="capture-stats">
              <div><span>Captured</span><strong>{testStatus.captured_snapshots}</strong></div>
              <div><span>Expected</span><strong>{testStatus.expected_snapshots}</strong></div>
              <div><span>Failed</span><strong>{testStatus.failed_snapshots}</strong></div>
              <div><span>Remaining</span><strong>{Math.ceil((testStatus.remaining_seconds || 0) / 60)} min</strong></div>
            </div>
            {testStatus.last_error ? <div className="alert builder-alert">Last capture error: {testStatus.last_error}</div> : null}
            {!testStatus.running && testStatus.captured_snapshots >= 2 ? (
              <div className="builder-actions">
                <button className="button secondary" type="button" onClick={useTestRange}>Use Test Range Below</button>
              </div>
            ) : null}
          </>
        ) : null}

        {testError ? <div className="alert builder-alert">{String(testError)}</div> : null}
        <p className="high-speed-note">0.5s is best-effort; actual speed depends on the NVR, network and snapshot response time. Cloud upload is skipped during this short test.</p>
      </div>

      <div className="builder-grid">
        <label>
          <span>Camera</span>
          <select
            value={form.cameraId}
            onChange={(event) =>
              update("cameraId", event.target.value)
            }
          >
            <option value="">Select camera</option>
            {cameras.map((camera) => (
              <option key={camera.id} value={camera.id}>
                {camera.name}
              </option>
            ))}
          </select>
        </label>

        <label>
          <span>Start date & time</span>
          <input
            type="datetime-local"
            value={form.startAt}
            onChange={(event) =>
              update("startAt", event.target.value)
            }
          />
        </label>

        <label>
          <span>End date & time</span>
          <input
            type="datetime-local"
            value={form.endAt}
            onChange={(event) =>
              update("endAt", event.target.value)
            }
          />
        </label>

        <label>
          <span>FPS</span>
          <input
            type="number"
            min="1"
            max="60"
            value={form.fps}
            onChange={(event) =>
              update("fps", event.target.value)
            }
          />
        </label>

        <label>
          <span>Resolution</span>
          <select
            value={form.resolution}
            onChange={(event) =>
              update("resolution", event.target.value)
            }
          >
            {resolutionOptions.map((option) => (
              <option key={option.label} value={option.label}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
      </div>

      {error ? <div className="alert builder-alert">{String(error)}</div> : null}
      {success ? <div className="success-banner builder-alert">{success}</div> : null}

      {preview ? (
        <div className="builder-preview">
          <div>
            <span>Snapshots found</span>
            <strong>{preview.snapshot_count}</strong>
          </div>
          <div>
            <span>Estimated video length</span>
            <strong>{preview.estimated_duration_seconds}s</strong>
          </div>
          <div>
            <span>FPS</span>
            <strong>{preview.fps}</strong>
          </div>
          <div>
            <span>Ready</span>
            <strong>{preview.can_generate ? "Yes" : "No"}</strong>
          </div>
        </div>
      ) : null}

      <div className="builder-actions">
        <button
          className="button secondary"
          type="button"
          onClick={handlePreview}
          disabled={!validForm || previewing || generating}
        >
          {previewing ? "Checking..." : "Preview"}
        </button>

        <button
          className="button primary"
          type="button"
          onClick={handleGenerate}
          disabled={
            !validForm ||
            generating ||
            !preview ||
            !preview.can_generate
          }
        >
          {generating ? "Generating MP4..." : "Generate Time-Lapse"}
        </button>
      </div>
    </div>
  );
}
