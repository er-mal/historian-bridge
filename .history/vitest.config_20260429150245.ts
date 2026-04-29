import path from "node:path";
import { defineConfig } from "vitest/config";

// Strip ".js" suffix from relative imports so NodeNext-style sources resolve
// to .ts files during tests.
const stripJsExt = {
    name: "strip-js-ext",
    enforce: "pre" as const,
    async resolveId(source: string, importer: string | undefined) {
        if (!importer) return null;
        if (!/^\.{1,2}\//.test(source)) return null;
        if (!source.endsWith(".js")) return null;
        const base = path.resolve(path.dirname(importer), source.slice(0, -3));
        for (const ext of [".ts", ".tsx", ".js"]) {
            return base + ext;
        }
        return null;
    },
};

export default defineConfig({
    plugins: [stripJsExt],
    test: {
        include: ["tests/**/*.test.ts"],
        environment: "node",
    },
});
