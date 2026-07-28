# Cloudflare-Blocked UN Career Sites (Confirmed 2026-05-11)

## Sites that block browser access via Cloudflare

| Site | Error | Workaround |
|------|-------|------------|
| UN Women (unwomen.org) | 403 Forbidden | Use Impactpool proxy |
| UN Careers (careers.un.org) | Cloudflare challenge | Use Impactpool proxy |
| UNDRR (undrr.org) | Cloudflare challenge | Use Impactpool proxy |
| UNHCR (unhcr.org) | Cloudflare challenge | Use Impactpool proxy |
| unjobs.org | Cloudflare challenge | Use Impactpool proxy |
| UN-Habitat (unhabitat.org/careers) | 404 or empty | Check unhabitat.org/join-us (usually only 1-2 non-ICT roles) |

## Impactpool curl fallback pattern

When browser is slow or blocked, use curl to fetch Impactpool pages:

```bash
# Search for jobs
curl -s "https://www.impactpool.org/search?q=ICT+OR+digital+OR+AI" \
  -H "User-Agent: Mozilla/5.0" | grep -o 'href="/jobs/[0-9]*"'

# Get job detail (title, org, deadline)
curl -s "https://www.impactpool.org/jobs/XXXXXX" \
  -H "User-Agent: Mozilla/5.0" | grep -o '<title>[^<]*</title>'

# Batch verify multiple job IDs
for id in ID1 ID2 ID3; do
  result=$(curl -s "https://www.impactpool.org/jobs/$id" \
    -H "User-Agent: Mozilla/5.0" | grep -o '<title>[^<]*</title>' | head -1)
  echo "$id: $result"
done
```

## Impactpool org filter is broken

The `&org=UNHCR` URL parameter does NOT filter by organization. All org values return the same 200-300 general results. To find org-specific jobs:
1. Use a broad search (e.g., `q=ICT+OR+digital+OR+AI`)
2. Fetch results via curl
3. Click through to individual job detail pages to confirm the organization
