import { useEffect, useMemo, useState } from "react";
import {
  getCameras,
  getSnapshotArchive,
  snapshotDownloadUrl,
  snapshotImageUrl,
} from "../../services/api";

const PAGE_SIZE = 18;

export default function SnapshotsPage() {
  const [cameras, setCameras] = useState([]);
  const [archive, setArchive] = useState({
    items: [],
    total: 0,
    page: 1,
    page_size: PAGE_SIZE,
    pages: 0,
  });

  const [filters, setFilters] = useState({
    cameraId: "",
    startDate: "",
    endDate: "",
  });

  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [preview, setPreview] = useState(null);

  useEffect(() => {
    getCameras().then(setCameras).catch(() => setCameras([]));
  }, []);

  async function loadArchive(nextPage = page) {
    setLoading(true);
    setError("");

    try {
      const startAt = filters.startDate
        ? `${filters.startDate}T00:00:00`
        : null;

      const endAt = filters.endDate
        ? `${filters.endDate}T23:59:59`
        : null;

      const data = await getSnapshotArchive({
        cameraId: filters.cameraId || null,
        startAt,
        endAt,
        page: nextPage,
        pageSize: PAGE_SIZE,
      });

      setArchive(data);
      setPage(nextPage);
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "Could not load snapshot archive"
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadArchive(1);
    // Initial load only; filters are applied manually.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const rangeLabel = useMemo(() => {
    if (!archive.total) return "0 snapshots";

    const start = (archive.page - 1) * archive.page_size + 1;
    const end = Math.min(
      archive.page * archive.page_size,
      archive.total
    );

    return `${start}-${end} of ${archive.total}`;
  }, [archive]);

  function applyFilters(event) {
    event.preventDefault();
    loadArchive(1);
  }

  function resetFilters() {
    setFilters({
      cameraId: "",
      startDate: "",
      endDate: "",
    });

    window.setTimeout(() => {
      setPage(1);
      getSnapshotArchive({
        page: 1,
        pageSize: PAGE_SIZE,
      })
        .then(setArchive)
        .catch(() => {});
    }, 0);
  }

  return (
    <section>
      <div className="page-header">
        <div>
          <p className="eyebrow">Archive</p>
          <h1>Snapshots</h1>
          <p className="page-subtitle">
            Browse captured construction images by camera and date.
          </p>
        </div>

        <div className="archive-count">{rangeLabel}</div>
      </div>

      <form className="filter-bar" onSubmit={applyFilters}>
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
        <div className="empty-card">Loading snapshots...</div>
      ) : archive.items.length === 0 ? (
        <div className="empty-card">
          <h3>No snapshots found</h3>
          <p>Capture images or change the archive filters.</p>
        </div>
      ) : (
        <div className="snapshot-gallery">
          {archive.items.map((item) => (
            <article className="snapshot-card" key={item.id}>
              <button
                className="snapshot-image-button"
                onClick={() => setPreview(item)}
                type="button"
              >
                <img
                  src={snapshotImageUrl(item.id)}
                  alt={`Camera ${item.camera_id} snapshot`}
                  loading="lazy"
                />
              </button>

              <div className="snapshot-card-body">
                <div>
                  <strong>Camera {item.camera_id}</strong>
                  <span>
                    {new Date(item.captured_at).toLocaleString()}
                  </span>
                </div>

                <a
                  className="button small"
                  href={snapshotDownloadUrl(item.id)}
                >
                  Download
                </a>
              </div>
            </article>
          ))}
        </div>
      )}

      <div className="pagination">
        <button
          className="button secondary"
          disabled={page <= 1 || loading}
          onClick={() => loadArchive(page - 1)}
        >
          Previous
        </button>

        <span>
          Page {archive.page || 1} of {archive.pages || 1}
        </span>

        <button
          className="button secondary"
          disabled={
            loading ||
            archive.pages === 0 ||
            page >= archive.pages
          }
          onClick={() => loadArchive(page + 1)}
        >
          Next
        </button>
      </div>

      {preview ? (
        <div
          className="modal-backdrop"
          onClick={() => setPreview(null)}
          role="presentation"
        >
          <div
            className="snapshot-preview"
            onClick={(event) => event.stopPropagation()}
            role="presentation"
          >
            <div className="snapshot-preview-header">
              <div>
                <p className="eyebrow">Camera {preview.camera_id}</p>
                <h2>{new Date(preview.captured_at).toLocaleString()}</h2>
              </div>

              <button
                className="button secondary"
                onClick={() => setPreview(null)}
              >
                Close
              </button>
            </div>

            <img
              src={snapshotImageUrl(preview.id)}
              alt={`Snapshot ${preview.id}`}
            />

            <div className="snapshot-preview-footer">
              <span>{preview.filename}</span>
              <a
                className="button primary"
                href={snapshotDownloadUrl(preview.id)}
              >
                Download image
              </a>
            </div>
          </div>
        </div>
      ) : null}
    </section>
  );
}
