import type { Quantity } from "./material.js";

export type LotStatus =
  | "pending-iqc"
  | "iqc-in-progress"
  | "released"
  | "quarantined"
  | "rejected"
  | "expired";

/** A receipt of material from a supplier, tracked through IQC and inventory. */
export interface MaterialLot {
  id: string;
  materialId: string;
  supplierId: string;
  supplierLotRef?: string;
  quantity: Quantity;
  receivedAt: string; // ISO-8601
  status: LotStatus;
  expiresAt?: string;
  storageLocation?: string;
  /** ID of the latest CoA attached to this lot. */
  coaId?: string;
}

export interface AttachmentRef {
  id: string;
  fileName: string;
  mediaType: string;
  size?: number;
  uri?: string;
}
