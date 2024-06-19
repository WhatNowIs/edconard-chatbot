import { Loader2 } from "lucide-react";
import { Button } from "../button";

export function SubmitButton({ isSubmitting, text, className }: { isSubmitting: boolean, text: string; className: string; }) {
  return (
    <Button type="submit" disabled={isSubmitting} className={className}>
      {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : text}
    </Button>
  );
}
