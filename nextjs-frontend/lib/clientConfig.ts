import { client } from "@/app/openapi-client/sdk.gen";
import qs from "qs";

const configureClient = () => {
  const baseURL = process.env.API_BASE_URL;

  client.setConfig({
    baseURL: baseURL,
    querySerializer: (params) => qs.stringify(params),
  });
};

configureClient();
