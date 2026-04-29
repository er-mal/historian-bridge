import { defineConfig } from "vitest/config";

export default defineConfig({
    resolve: {
        extensions: [".ts", ".tsx", ".js", ".mjs", ".json"],
    },
    test: {
        include: ["tests/**/*.test.ts"],
        environment: "node",
    },
});
