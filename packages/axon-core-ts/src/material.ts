/**
 * Material — anything tracked in PLM/ERP that can flow through production.
 * Categories follow the canonical battery BOM hierarchy used across the suite.
 */
export type MaterialCategory =
  | "cathode-active"
  | "anode-active"
  | "electrolyte"
  | "binder"
  | "conductive-additive"
  | "current-collector-foil"
  | "separator"
  | "tab"
  | "can"
  | "cap"
  | "busbar"
  | "thermal-interface"
  | "adhesive"
  | "fastener"
  | "harness"
  | "sensor"
  | "cell"
  | "module"
  | "pack"
  | "consumable"
  | "other";

export interface Quantity {
  value: number;
  unit: string; // e.g. "kg", "pcs", "L"
}

export interface SpecRange {
  min?: number;
  max?: number;
  /** strict less-than, e.g., "<1 ppm" appears in CoAs */
  lt?: number;
  gt?: number;
  unit: string;
}

export interface MaterialSpec {
  parameters: Record<string, SpecRange>;
}

export interface Material {
  /** Canonical PLM identifier (Teamcenter / D365 item id). */
  id: string;
  name: string;
  category: MaterialCategory;
  spec?: MaterialSpec;
  /** ISO-3166 alpha-2 country of origin. */
  countryOfOrigin?: string;
  /** SDS / safety classification (UN class for li-ion etc.). */
  hazardClass?: string;
}

export interface Supplier {
  id: string;
  name: string;
  approved: boolean;
  rating?: 1 | 2 | 3 | 4 | 5;
}
