import React from "react";
import { Alert, AlertTitle } from "@/components/ui/alert";
import { ExclamationTriangleIcon } from "@radix-ui/react-icons";

export const ErrorMessage: React.FC<{ error: string }> = ({ error }) => (
  <Alert variant="destructive">
    <ExclamationTriangleIcon className="h-4 w-4" />
    <AlertTitle>{error}</AlertTitle>
  </Alert>
);
