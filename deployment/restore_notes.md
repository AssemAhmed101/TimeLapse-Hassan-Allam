# Restore Notes

Stop the stack before restoring production data.

```bash
docker compose down
```

Restore the SQLite database into the `backend_db` Docker volume and restore
`storage.tar.gz` into the `timelapse_storage` volume.

Always keep an additional copy of the current volumes before restoring.
After restoration:

```bash
docker compose up -d
docker compose ps
docker compose logs -f backend
```
