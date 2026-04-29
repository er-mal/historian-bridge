/**
 * Production order + operation step model. Field names mirror Microsoft D365
 * F&O Production module so that the ShopFloor API integration can
 * round-trip without translation. These are public Microsoft schema names.
 */
export type ProdStatus =
  | "created"
  | "estimated"
  | "scheduled"
  | "released"
  | "started"
  | "reportedFinished"
  | "ended"
  | "cancelled";

export interface OperationStep {
  oprNum: number;
  oprId: string;
  oprPriority: number;
  jobIdentification?: string;
  capacityCheck?: boolean;
  resourceId?: string;
  oprDateTime?: string; // ISO-8601
  setupTimeSec?: number;
  runTimePerPieceSec?: number;
}

export interface ProductionOrder {
  id: string;
  prodId: string;
  itemId: string;
  qtyPlanned: number;
  qtyReported: number;
  status: ProdStatus;
  operations: OperationStep[];
  batchNumber?: string;
  inventBatchId?: string;
  createdAt?: string;
  scheduledStart?: string;
  scheduledEnd?: string;
}

export interface KanbanCard {
  id: string;
  itemId: string;
  qty: number;
  status: "empty" | "in-transit" | "filled" | "consumed";
  fromLocation: string;
  toLocation: string;
  productionOrderId?: string;
}
