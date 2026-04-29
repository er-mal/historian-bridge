/** Errors returned by the HistorianBridgeClient. */

export interface ProblemDetails {
    type?: string;
    title?: string;
    status?: number;
    detail?: string;
}

export class HistorianBridgeError extends Error {
    readonly status: number;
    readonly problem: ProblemDetails;
    constructor(status: number, problem: ProblemDetails) {
        super(problem.detail ?? problem.title ?? `HTTP ${status}`);
        this.name = "HistorianBridgeError";
        this.status = status;
        this.problem = problem;
    }
}
