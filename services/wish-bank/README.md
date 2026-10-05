# CareerHub Wish Bank service

Vercel root: `services/wish-bank`

Required environment:

- `WISH_BANK_SHARED_SECRET` — server-to-server secret used by personalised CareerHub sites.
- `BLOB_READ_WRITE_TOKEN` — supplied by the connected Vercel Blob store.

Optional environment:

- `WISH_BANK_GITHUB_TOKEN` — enables projection of accepted wishes to structured GitHub issues in CareerHubZero.
- `WISH_BANK_REPOSITORY` — defaults to `Motherpher/CareerHubZero`.

Blob is the operational system of record. GitHub projection is a development convenience, not a runtime dependency.
