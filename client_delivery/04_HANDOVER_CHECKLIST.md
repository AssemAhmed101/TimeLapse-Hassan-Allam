# Client Handover Checklist

## Infrastructure

- [ ] Production server prepared
- [ ] Docker installed
- [ ] Docker Compose installed
- [ ] Stable camera network route available
- [ ] Server storage capacity approved
- [ ] Server backup destination approved

## Application

- [ ] `.env.production` created
- [ ] Strong JWT secret configured
- [ ] Trusted hosts configured
- [ ] CORS origin configured
- [ ] HTTPS configured if remote access is required
- [ ] Backend container healthy
- [ ] Dashboard container healthy

## Accounts

- [ ] First admin created
- [ ] Operator accounts created
- [ ] Viewer accounts created if required
- [ ] Default/test accounts removed

## Cameras

For every Hikvision camera/NVR:

- [ ] IP verified
- [ ] Username verified
- [ ] Password verified
- [ ] Port verified
- [ ] Channel verified
- [ ] Test Connection passed
- [ ] Manual snapshot passed
- [ ] Snapshot policy configured

## Time-Lapse

- [ ] Snapshot archive checked
- [ ] Preview test passed
- [ ] MP4 generation passed
- [ ] Video playback passed
- [ ] Video download passed

## Storage & Cloud

- [ ] Local storage checked
- [ ] Retention policy approved
- [ ] Cloud provider configured if required
- [ ] Cloud upload test passed
- [ ] Backup executed
- [ ] Restore procedure reviewed

## Monitoring

- [ ] Database shows Online
- [ ] Scheduler shows Running
- [ ] Storage status healthy
- [ ] Camera status reviewed
- [ ] Recent logs checked

## Documentation

- [ ] Setup Guide delivered
- [ ] Admin Guide delivered
- [ ] Operator Guide delivered
- [ ] Deployment Guide delivered
- [ ] Backup/Restore notes delivered

## Client acceptance

- [ ] Client representative reviewed dashboard
- [ ] Client representative can log in
- [ ] Client representative can view snapshots
- [ ] Client representative can play time-lapses
- [ ] Operator training completed
- [ ] Admin training completed
- [ ] Final acceptance signed
