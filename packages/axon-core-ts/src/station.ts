/** Station specification & test step model. Drives StationLine and EOL. */

export type CarrierType = "tray" | "pallet" | "conveyor" | "agv" | "manual";

export interface StationIO {
  itemRef: string;
  carrier: CarrierType;
  fixtureId?: string;
}

export type TestKind =
  | "visual"
  | "dimensional"
  | "leak-helium"
  | "leak-pressure-decay"
  | "isolation"
  | "hipot"
  | "hvil"
  | "insulation-resistance"
  | "weld-pull"
  | "weld-resistance"
  | "torque"
  | "ocv"
  | "dcir"
  | "capacity"
  | "thermal-imaging"
  | "communication"
  | "firmware-flash"
  | "other";

export interface TestSpec {
  parameter: string;
  unit: string;
  min?: number;
  max?: number;
  rampMs?: number;
  holdMs?: number;
  /** Number of samples / readings to acquire. */
  samples?: number;
}

export interface TestStep {
  id: string;
  kind: TestKind;
  spec: TestSpec;
  required: boolean;
  /** If a previous step failed, may we still attempt this one? */
  runOnPriorFail?: boolean;
}

export interface StationSpec {
  id: string;
  /** Human-readable name, e.g., "Cell Terminal Welding". */
  name: string;
  /** Logical line, e.g., "module-line-1". */
  line: string;
  /** Position in the line; lower runs first. */
  position: number;
  inputs: StationIO[];
  outputs: StationIO[];
  tests: TestStep[];
  cycleTimeSec: number;
  takt?: number; // target seconds per cycle for OEE tracking
  /** OprNum that this station maps to in the ERP routing. */
  oprNum?: number;
  /** Site code (e.g., factory or building). */
  site?: string;
}

export interface TestResult {
  id: string;
  stepId: string;
  itemRef: string;
  pass: boolean;
  measurements: Record<string, number | string>;
  startedAt: string;
  finishedAt: string;
  operator?: string;
  /** Free-form notes from operator or test runner. */
  notes?: string;
}
