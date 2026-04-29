/** Battery hierarchy: Cell → Module → Pack. */

export interface Cell {
  id: string;
  serial?: string;
  lotId: string;
  chemistry: string; // e.g., "NMC811", "LFP", "NCA"
  formatCode: string; // e.g., "21700", "4680", "PHEV2"
  capacityNominal_Ah: number;
  capacityMeasured_Ah?: number;
  ocv_V?: number;
  internalResistance_mOhm?: number;
  productionOrderId?: string;
}

export interface Module {
  id: string;
  serial: string;
  cellIds: string[];
  topology: string; // e.g., "12s2p"
  productionOrderId?: string;
}

export interface Pack {
  id: string;
  serial: string;
  moduleIds: string[];
  customer?: string;
  application: "EV" | "ESS" | "industrial" | "marine" | "aerospace" | "other";
  bmsHardwareRev?: string;
  bmsFirmwareRev?: string;
  productionOrderId?: string;
}
