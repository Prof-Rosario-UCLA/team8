import { cn } from "@/lib/utils";
import { Label } from "@/components/ui/label";

export default function LabelledInput({ label, input, className, htmlFor }: { label: string, input: React.ReactNode, className?: string, htmlFor?: string }) {
  return (
    <div className={cn("flex flex-col gap-1", className)}>
      <Label htmlFor={htmlFor}>{label}</Label>
      {input}
    </div>
  )
}