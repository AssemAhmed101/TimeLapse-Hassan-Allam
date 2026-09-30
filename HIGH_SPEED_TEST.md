# High-Speed 15-Minute Test

Recommended first real NVR test:

- Camera: the working Hikvision/NVR camera
- Snapshot interval: **1 second**
- Test duration: **15 minutes**
- Expected snapshots: about **900**
- Time-lapse FPS: **25**
- Expected video duration: about **36 seconds**

## From the dashboard

1. Open **Time-Lapses**.
2. Select the camera.
3. In **High-Speed Capture Test**, choose **Every 1 second** and **15 minutes**.
4. Click **Start Capture Test**.
5. Keep the backend running. The panel shows captured, failed and remaining counts.
6. When the state becomes **completed**, click **Use Test Range Below**.
7. Click **Preview**.
8. Confirm roughly 900 snapshots were found.
9. Keep FPS at 25 and choose 720p for the first test.
10. Click **Generate Time-Lapse** and play the generated MP4.

The 0.5-second mode is best-effort and should be tested only after the 1-second test succeeds. Real speed depends on NVR response time and the LAN.
