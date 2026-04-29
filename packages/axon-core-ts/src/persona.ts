/** Persona model used by FieldOps for ESS commissioning workflows. */

export type InteractionLevel = "intentional" | "incidental" | "none";

export interface Persona {
  id: string;
  name: string;
  role: string;
  interactionLevel: InteractionLevel;
  goals: string[];
  pains: string[];
  tools: string[];
  motivationalDrivers?: string[];
  knowledge?: string[];
  workhours?: string;
}
