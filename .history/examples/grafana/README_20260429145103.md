# Grafana demo

The compose file boots Grafana with anonymous admin access at
<http://localhost:3000> and provisions an Infinity datasource pointed at
the gateway.

## Steps

```sh
# from apps/05-historian-bridge/
docker compose up --build
python examples/seed_demo.py    # POSTs synthetic points into /write
```

Then in Grafana → Explore, choose **HistorianBridge**, query type **JSON**,
URL: `/query`, method **POST**, body:

```json
{
  "tags": ["site.line1.station_a.temperature"],
  "from": "${__from:date}",
  "to":   "${__to:date}",
  "agg":  "avg",
  "interval": "1m"
}
```

Each row in the response has `tag`, `ts`, `value`. Map `ts` to time and
`value` to a number in the Infinity column config and you'll see a time
series.

## API surface

- `GET  /healthz`
- `GET  /tags?prefix=&limit=`
- `GET  /current?tag=a&tag=b`
- `POST /query`  (body: `TagQuery`)
- `POST /write`  (body: `HistorianPoint[]`, when `HISTORIAN_BRIDGE_WRITE=true`)
