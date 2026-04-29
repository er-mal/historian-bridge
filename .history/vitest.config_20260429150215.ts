import { defineConfig } from "vitest/config";

export default defineConfig({
    test: {
        include: ["tests/**/*.test.ts"],
        environment: "node",
    },
    resolve: {
        // NodeNext-style ".js" imports resolve to TS sources during tests.
        alias: [{ find: /^(\.{1,2}\/.*)\.js$/, replacement: "$1" }],
    },
});
