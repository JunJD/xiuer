import { defineConfig } from "@hey-api/openapi-ts";

export default defineConfig({
  client: "@hey-api/client-axios",
  input: "./shared-data/openapi.json",
  output: {
    format: "prettier",
    lint: "eslint",
    path: "app/openapi-client",
  },
});
