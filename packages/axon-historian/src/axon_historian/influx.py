"""InfluxDB 2.x historian driver — fast modern default for greenfield plants."""
from __future__ import annotations
from typing import AsyncIterator, Iterable, Optional
from axon_core import HistorianPoint, HistorianTag, TagQuery
from .base import ConnectionInfo, HistorianClient


class InfluxHistorian(HistorianClient):
    def __init__(self, info: ConnectionInfo, bucket: str, org: str) -> None:
        self.info = info
        self.bucket = bucket
        self.org = org
        self._client = None
        self._write = None
        self._query = None

    async def connect(self) -> None:
        try:
            from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
        except ImportError as e:
            raise ImportError("InfluxHistorian requires `influxdb-client`. Install axon-historian[influx].") from e
        self._client = InfluxDBClientAsync(url=self.info.url or "", token=self.info.token or "", org=self.org)
        self._write = self._client.write_api()
        self._query = self._client.query_api()

    async def close(self) -> None:
        if self._client is not None:
            await self._client.close()
            self._client = None

    async def list_tags(self, prefix: Optional[str] = None, limit: int = 1000) -> list[HistorianTag]:
        flux = f'import "influxdata/influxdb/schema" schema.measurements(bucket: "{self.bucket}")'
        tables = await self._query.query(flux)
        names: list[str] = []
        for tb in tables:
            for rec in tb.records:
                v = rec.get_value()
                if not prefix or str(v).startswith(prefix):
                    names.append(str(v))
        return [HistorianTag(name=n) for n in names[:limit]]

    async def get_current(self, tags: Iterable[str]) -> list[HistorianPoint]:
        out: list[HistorianPoint] = []
        for tag in tags:
            flux = (
                f'from(bucket:"{self.bucket}") |> range(start:-1h) '
                f'|> filter(fn:(r)=> r._measurement=="{tag}") |> last()'
            )
            tables = await self._query.query(flux)
            for tb in tables:
                for rec in tb.records:
                    out.append(HistorianPoint(tag=tag, ts=rec.get_time().isoformat(), value=float(rec.get_value())))
        return out

    async def query(self, q: TagQuery) -> AsyncIterator[HistorianPoint]:
        tags_filter = " or ".join(f'r._measurement=="{t}"' for t in q.tags)
        flux = (
            f'from(bucket:"{self.bucket}") |> range(start: {q.from_}, stop: {q.to}) '
            f'|> filter(fn:(r)=> {tags_filter})'
        )
        tables = await self._query.query(flux)
        for tb in tables:
            for rec in tb.records:
                yield HistorianPoint(
                    tag=str(rec.get_measurement()),
                    ts=rec.get_time().isoformat(),
                    value=float(rec.get_value()),
                )

    async def write(self, points: Iterable[HistorianPoint]) -> None:
        from influxdb_client import Point
        records = [Point(p.tag).field("value", p.value).time(p.ts) for p in points]
        await self._write.write(bucket=self.bucket, org=self.org, record=records)
