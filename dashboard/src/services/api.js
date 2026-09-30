import axios from "axios";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

export async function getHealth() {
  const response = await api.get("/health/");
  return response.data;
}

export async function getCameras() {
  const response = await api.get("/cameras/");
  return response.data;
}

export async function createCamera(payload) {
  const response = await api.post("/cameras/", payload);
  return response.data;
}

export async function updateCamera(cameraId, payload) {
  const response = await api.patch(`/cameras/${cameraId}`, payload);
  return response.data;
}

export async function deleteCamera(cameraId) {
  const response = await api.delete(`/cameras/${cameraId}`);
  return response.data;
}

export async function enableCamera(cameraId) {
  const response = await api.post(`/cameras/${cameraId}/enable`);
  return response.data;
}

export async function disableCamera(cameraId) {
  const response = await api.post(`/cameras/${cameraId}/disable`);
  return response.data;
}

export async function testCameraConnection(cameraId) {
  const response = await api.post(`/cameras/${cameraId}/test-connection`);
  return response.data;
}

export async function captureSnapshot(cameraId) {
  const response = await api.post(`/snapshots/${cameraId}`);
  return response.data;
}

export async function getSnapshotPolicy(cameraId) {
  const response = await api.get(`/snapshot-engine/cameras/${cameraId}/policy`);
  return response.data;
}

export async function updateSnapshotPolicy(cameraId, payload) {
  const response = await api.patch(
    `/snapshot-engine/cameras/${cameraId}/policy`,
    payload
  );
  return response.data;
}

export async function getSnapshots(cameraId = null) {
  const response = await api.get("/snapshots/", {
    params: cameraId ? { camera_id: cameraId } : undefined,
  });
  return response.data;
}

export async function getTimelapses(cameraId = null) {
  const response = await api.get("/timelapses/", {
    params: cameraId ? { camera_id: cameraId } : undefined,
  });
  return response.data;
}

export async function getStorageStatus() {
  const response = await api.get("/storage/status");
  return response.data;
}

export async function getCloudStatus() {
  const response = await api.get("/cloud/status");
  return response.data;
}

export async function getSnapshotArchive({
  cameraId = null,
  startAt = null,
  endAt = null,
  page = 1,
  pageSize = 24,
} = {}) {
  const response = await api.get("/snapshots/archive", {
    params: {
      camera_id: cameraId || undefined,
      start_at: startAt || undefined,
      end_at: endAt || undefined,
      page,
      page_size: pageSize,
    },
  });
  return response.data;
}

export function snapshotImageUrl(snapshotId) {
  return `${API_BASE_URL}/snapshots/${snapshotId}/image${mediaTokenQuery()}`;
}

export function snapshotDownloadUrl(snapshotId) {
  return `${API_BASE_URL}/snapshots/${snapshotId}/download${mediaTokenQuery()}`;
}

export async function getTimelapseLibrary({
  cameraId = null,
  status = null,
  startAt = null,
  endAt = null,
  page = 1,
  pageSize = 12,
} = {}) {
  const response = await api.get("/timelapses/library", {
    params: {
      camera_id: cameraId || undefined,
      status: status || undefined,
      start_at: startAt || undefined,
      end_at: endAt || undefined,
      page,
      page_size: pageSize,
    },
  });
  return response.data;
}

export function timelapseVideoUrl(timelapseId) {
  return `${API_BASE_URL}/timelapses/${timelapseId}/video${mediaTokenQuery()}`;
}

export function timelapseDownloadUrl(timelapseId) {
  return `${API_BASE_URL}/timelapses/${timelapseId}/download${mediaTokenQuery()}`;
}


export async function previewTimelapse(payload) {
  const response = await api.post("/timelapses/preview", payload);
  return response.data;
}

export async function generateTimelapse(payload) {
  const response = await api.post("/timelapses/generate", payload, { timeout: 300000 });
  return response.data;
}

export function setAuthToken(token) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
    localStorage.setItem("access_token", token);
  } else {
    delete api.defaults.headers.common.Authorization;
    localStorage.removeItem("access_token");
  }
}

export function loadStoredAuthToken() {
  const token = localStorage.getItem("access_token");
  if (token) api.defaults.headers.common.Authorization = `Bearer ${token}`;
  return token;
}

export async function loginUser(email, password) {
  const response = await api.post("/auth/login", { email, password });
  return response.data;
}

export async function getCurrentUser() {
  const response = await api.get("/auth/me");
  return response.data;
}

export async function getUsers() {
  const response = await api.get("/users/");
  return response.data;
}

export async function createUser(payload) {
  const response = await api.post("/users/", payload);
  return response.data;
}

export async function updateUser(userId, payload) {
  const response = await api.patch(`/users/${userId}`, payload);
  return response.data;
}

export async function deleteUser(userId) {
  const response = await api.delete(`/users/${userId}`);
  return response.data;
}

export function mediaTokenQuery() {
  const token = localStorage.getItem("access_token");
  return token ? `?token=${encodeURIComponent(token)}` : "";
}


export async function getMonitoringHealth() {
  const response = await api.get("/monitoring/health");
  return response.data;
}

export async function getMonitoringLogs(limit = 100) {
  const response = await api.get("/monitoring/logs", {
    params: { limit },
  });
  return response.data;
}

export async function startHighSpeedCapture(payload) {
  const response = await api.post("/high-speed-capture/start", payload);
  return response.data;
}

export async function getHighSpeedCaptureStatus(cameraId) {
  const response = await api.get(`/high-speed-capture/${cameraId}/status`);
  return response.data;
}

export async function stopHighSpeedCapture(cameraId) {
  const response = await api.post(`/high-speed-capture/${cameraId}/stop`);
  return response.data;
}
