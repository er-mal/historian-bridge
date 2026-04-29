/** Quality / non-conformity / quarantine model. */

export type Severity = 1 | 2 | 3 | 4;
export type QualityState = "open" | "investigation" | "containment" | "resolved" | "closed";

export interface NonConformity {
  id: string;
  productionOrderId?: string;
  lotId?: string;
  itemRef?: string;
  reportedAt: string;
  reportedBy: string;
  severity: Severity;
  state: QualityState;
  description: string;
  rootCause?: string;
  capa?: string; // corrective and preventive action
  closedAt?: string;
}

export interface QuarantineOrder {
  id: string;
  lotId: string;
  reason: string;
  createdAt: string;
  releasedAt?: string;
  rejectedAt?: string;
  releasedBy?: string;
}

export interface QualityOrder {
  id: string;
  productionOrderId?: string;
  lotId?: string;
  type: "incoming" | "in-process" | "outgoing";
  testPlanId?: string;
  state: QualityState;
}
