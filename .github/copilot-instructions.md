# Copilot instructions — 05-historian-bridge

This is one app in the Axon Suite monorepo. The shared kernel lives in
`packages/` at the repo root.

## Hard rules

1. **Kernel discipline.** Domain types come from `@axon/core` (TS) or
   `axon-core` (Py). Do not redefine `Material`, `MaterialLot`, `CoA`,
   `ProductionOrder`, `StationSpec`, `TestResult`, `HistorianTag`,
   `HistorianPoint` here. If a kernel type is wrong, change the kernel.
2. **No cross-app imports.** Apps must not import each other directly.
   Inter-app communication is HTTP over the typed contract in
   `@axon/mes-api`.
3. **Stack.** TypeScript: ES2022, NodeNext modules, strict, vitest.
   Python: 3.11+, Pydantic v2, async where it pays, pytest.
4. **Stay in scope.** `docs/validation.md` defines v1 surface and
   non-goals. Do not add features outside it without updating that file.
5. **No hand-edits to `pnpm-lock.yaml` / `uv.lock`.** Use the package
   managers.
