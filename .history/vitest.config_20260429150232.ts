import { defineConfig } from "vitest/config";

// Strip ".js" suffix from relative imports so NodeNext-style sources resolve
// to .ts files during tests. Implemented as a vite plugin (relative aliases
// are not supported in vitest/vite).
const stripJsExt = {
    name: "strip-js-ext",
    enforce: "pre" as const,
    resolveId(source: string, importer: string | undefined) {
        if (!importer) return null;
        if (!/^\.{1,2}\//.test(source)) return null;
        if (!source.endsWith(".js")) return null;
        return this.resolve(source.slice(0, -3), importer, { skipSelf: true });
    },
};

export default defineConfig({
    plugins: [stripJsExt],
    test: {
        include: ["tests/**/*.test.ts"],
        environment: "node",
    },
});
