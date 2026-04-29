import type { AttachmentRef } from "./lot.js";

export type MeasurementResult = "pass" | "fail" | "review" | "informational";

/**
 * One row from a Certificate of Analysis. Values can be numeric or string
 * (e.g. "<1 ppm" appears verbatim in supplier CoAs and must round-trip).
 */
export interface CoAMeasurement {
  parameter: string;
  value: number | string;
  unit: string;
  spec?: { min?: number; max?: number; lt?: number; gt?: number };
  result: MeasurementResult;
  notes?: string;
}

export interface CoA {
  id: string;
  lotId: string;
  supplierId: string;
  issuedAt: string; // ISO-8601
  validatedBy?: string;
  measurements: CoAMeasurement[];
  attachments?: AttachmentRef[];
  /** Overall pass/fail rolled up from measurements. */
  overall: MeasurementResult;
}

export function rollUp(measurements: CoAMeasurement[]): MeasurementResult {
  if (measurements.some((m) => m.result === "fail")) return "fail";
  if (measurements.some((m) => m.result === "review")) return "review";
  return "pass";
}

/** Apply a spec to a numeric value and return the verdict. */
export function evaluate(value: number, spec: NonNullable<CoAMeasurement["spec"]>): MeasurementResult {
  if (spec.min !== undefined && value < spec.min) return "fail";
  if (spec.max !== undefined && value > spec.max) return "fail";
  if (spec.lt !== undefined && !(value < spec.lt)) return "fail";
  if (spec.gt !== undefined && !(value > spec.gt)) return "fail";
  return "pass";
}
