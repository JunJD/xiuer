import { client } from "@/app/openapi-client/sdk.gen";
import qs from "qs";

const configureClient = () => {
  const baseURL = process.env.API_BASE_URL || "http://localhost:8000";

  client.setConfig({
    baseURL: baseURL,
    querySerializer: (params) => qs.stringify(params),
  });
};

configureClient();
