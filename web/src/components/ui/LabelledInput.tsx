import { cn } from "@/lib/utils";

export default function LabelledInput({ label, input, className }: { label: string, input: React.ReactNode, className?: string }) {
  return (
    <div className={cn("flex flex-col gap-1", className)}>
      <label className="text-sm text-muted-foreground">{label}</label>
      {input}
    </div>
  )
}