export default function StatusBadge({ status = "unknown" }) {
  const normalized = String(status).toLowerCase();
  return (
    <span className={`status-badge status-${normalized}`}>
      {status}
    </span>
  );
}
