import { useEffect, useMemo, useState } from "react";
import StatusBadge from "../../components/StatusBadge";
import TimelapseBuilder from "../../components/TimelapseBuilder";
import {
  getCameras,
  getTimelapseLibrary,
  timelapseDownloadUrl,
  timelapseVideoUrl,
} from "../../services/api";

const PAGE_SIZE = 9;

export default function TimelapsesPage() {
  const [cameras, setCameras] = useState([]);
  const [library, setLibrary] = useState({
    items: [],
    total: 0,
    page: 1,
    page_size: PAGE_SIZE,
    pages: 0,
  });

  const [filters, setFilters] = useState({
    cameraId: "",
    status: "",
    startDate: "",
    endDate: "",
  });

  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [playing, setPlaying] = useState(null);

  useEffect(() => {
    getCameras().then(setCameras).catch(() => setCameras([]));
  }, []);

  async function loadLibrary(nextPage = page, nextFilters = filters) {
    setLoading(true);
    setError("");

    try {
      const data = await getTimelapseLibrary({
        cameraId: nextFilters.cameraId || null,
        status: nextFilters.status || null,
        startAt: nextFilters.startDate
          ? `${nextFilters.startDate}T00:00:00`
          : null,
        endAt: nextFilters.endDate
          ? `${nextFilters.endDate}T23:59:59`
          : null,
        page: nextPage,
        pageSize: PAGE_SIZE,
      });

      setLibrary(data);
      setPage(nextPage);
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "Could not load time-lapse library"
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadLibrary(1);
    // Initial load only.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const rangeLabel = useMemo(() => {
    if (!library.total) return "0 videos";

    const start = (library.page - 1) * library.page_size + 1;
    const end = Math.min(
      library.page * library.page_size,
      library.total
    );

    return `${start}-${end} of ${library.total}`;
  }, [library]);

  function applyFilters(event) {
    event.preventDefault();
    loadLibrary(1);
  }

  function resetFilters() {
    const cleared = {
      cameraId: "",
      status: "",
      startDate: "",
      endDate: "",
    };

    setFilters(cleared);
    loadLibrary(1, cleared);
  }

  return (
    <section>
      <div className="page-header">
        <div>
          <p className="eyebrow">Video Library</p>
          <h1>Time-Lapses</h1>
          <p className="page-subtitle">
            Browse, play and download generated construction time-lapse videos.
          </p>
        </div>

        <div className="archive-count">{rangeLabel}</div>
      </div>

<TimelapseBuilder
  cameras={cameras}
  onGenerated={() => loadLibrary(1)}
/>

      <form className="filter-bar timelapse-filter-bar" onSubmit={applyFilters}>
        <label>
          <span>Camera</span>
          <select
            value={filters.cameraId}
            onChange={(event) =>
              setFilters((current) => ({
                ...current,
                cameraId: event.target.value,
              }))
            }
          >
            <option value="">All cameras</option>
            {cameras.map((camera) => (
              <option key={camera.id} value={camera.id}>
                {camera.name}
              </option>
            ))}
          </select>
        </label>

        <label>
          <span>Status</span>
          <select
            value={filters.status}
            onChange={(event) =>
              setFilters((current) => ({
                ...current,
                status: event.target.value,
              }))
            }
          >
            <option value="">All statuses</option>
            <option value="completed">Completed</option>
            <option value="processing">Processing</option>
            <option value="failed">Failed</option>
          </select>
        </label>

        <label>
          <span>From</span>
          <input
            type="date"
            value={filters.startDate}
            onChange={(event) =>
              setFilters((current) => ({
                ...current,
                startDate: event.target.value,
              }))
            }
          />
        </label>

        <label>
          <span>To</span>
          <input
            type="date"
            value={filters.endDate}
            onChange={(event) =>
              setFilters((current) => ({
                ...current,
                endDate: event.target.value,
              }))
            }
          />
        </label>

        <div className="filter-actions">
          <button className="button secondary" type="button" onClick={resetFilters}>
            Reset
          </button>
          <button className="button primary" type="submit">
            Apply filters
          </button>
        </div>
      </form>

      {error ? <div className="alert">{String(error)}</div> : null}

      {loading ? (
        <div className="empty-card">Loading time-lapses...</div>
      ) : library.items.length === 0 ? (
        <div className="empty-card">
          <h3>No time-lapses found</h3>
          <p>Generate a video or change the filters.</p>
        </div>
      ) : (
        <div className="timelapse-library">
          {library.items.map((item) => (
            <article className="timelapse-card" key={item.id}>
              <div className="video-placeholder">
                {item.status === "completed" && item.video_url ? (
                  <button
                    className="video-open-button"
                    onClick={() => setPlaying(item)}
                    type="button"
                  >
                    <span className="play-icon">▶</span>
                    <span>Play video</span>
                  </button>
                ) : (
                  <div className="video-unavailable">
                    <StatusBadge status={item.status} />
                    <span>Video not available for playback</span>
                  </div>
                )}
              </div>

              <div className="timelapse-card-body">
                <div className="timelapse-card-heading">
                  <div>
                    <span className="camera-id">Time-Lapse #{item.id}</span>
                    <h3>Camera {item.camera_id}</h3>
                  </div>
                  <StatusBadge status={item.status} />
                </div>

                <div className="timelapse-meta">
                  <div>
                    <span>From</span>
                    <strong>
                      {item.period_start
                        ? new Date(item.period_start).toLocaleString()
                        : "—"}
                    </strong>
                  </div>
                  <div>
                    <span>To</span>
                    <strong>
                      {item.period_end
                        ? new Date(item.period_end).toLocaleString()
                        : "—"}
                    </strong>
                  </div>
                </div>

                <div className="timelapse-card-footer">
                  <span className="truncate">{item.filename}</span>

                  {item.status === "completed" && item.download_url ? (
                    <a
                      className="button small"
                      href={timelapseDownloadUrl(item.id)}
                    >
                      Download
                    </a>
                  ) : null}
                </div>
              </div>
            </article>
          ))}
        </div>
      )}

      <div className="pagination">
        <button
          className="button secondary"
          disabled={page <= 1 || loading}
          onClick={() => loadLibrary(page - 1)}
        >
          Previous
        </button>

        <span>
          Page {library.page || 1} of {library.pages || 1}
        </span>

        <button
          className="button secondary"
          disabled={
            loading ||
            library.pages === 0 ||
            page >= library.pages
          }
          onClick={() => loadLibrary(page + 1)}
        >
          Next
        </button>
      </div>

      {playing ? (
        <div
          className="modal-backdrop"
          onClick={() => setPlaying(null)}
          role="presentation"
        >
          <div
            className="video-modal"
            onClick={(event) => event.stopPropagation()}
            role="presentation"
          >
            <div className="snapshot-preview-header">
              <div>
                <p className="eyebrow">Camera {playing.camera_id}</p>
                <h2>Time-Lapse #{playing.id}</h2>
              </div>

              <button
                className="button secondary"
                onClick={() => setPlaying(null)}
              >
                Close
              </button>
            </div>

            <video
              src={timelapseVideoUrl(playing.id)}
              controls
              autoPlay
              playsInline
            />

            <div className="snapshot-preview-footer">
              <span>{playing.filename}</span>
              <a
                className="button primary"
                href={timelapseDownloadUrl(playing.id)}
              >
                Download video
              </a>
            </div>
          </div>
        </div>
      ) : null}
    </section>
  );
}
