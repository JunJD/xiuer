import { useFormStatus } from "react-dom";
import { Button } from "@/components/ui/button";

export function SubmitButton({ text }: { text: string }) {
  const { pending } = useFormStatus();

  return (
    <Button className="w-full" type="submit" disabled={pending}>
      {pending ? "Loading..." : text}
    </Button>
  );
}
