/** Historian (process data) model. Used by HistorianBridge and labbench clients. */

export interface HistorianTag {
  name: string;
  description?: string;
  unit?: string;
  /** Canonical asset path, e.g., "Site/Line/Station/Sensor". */
  assetPath?: string;
}

export type Quality = "good" | "bad" | "questionable" | "uncertain";

export interface HistorianPoint {
  tag: string;
  ts: string; // ISO-8601 UTC
  value: number;
  quality?: Quality;
}

export interface TagQuery {
  tags: string[];
  from: string;
  to: string;
  /** Aggregation (default: raw). */
  agg?: "raw" | "avg" | "min" | "max" | "stddev" | "count" | "first" | "last";
  /** Sample interval for aggregations, e.g., "1m", "10s". */
  interval?: string;
}
