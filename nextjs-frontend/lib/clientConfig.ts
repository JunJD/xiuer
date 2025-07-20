import { client } from "@/app/openapi-client/sdk.gen";
import qs from "qs";

const configureClient = () => {
  let baseURL: string;

  if (typeof window !== 'undefined') {
    baseURL = `${window.location.protocol}//${window.location.host}`;
  } else {
    baseURL = process.env.API_BASE_URL || "http://backend:8000";
  }

  client.setConfig({
    baseURL: baseURL,
    querySerializer: (params) => qs.stringify(params),
  });
};

configureClient();
