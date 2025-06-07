import { format } from "date-fns"
import { CalendarIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { cn } from "@/lib/utils"

interface DateFieldProps {
  value?: Date | null
  onChange: (date: Date | null) => void
  compact?: boolean
  monthYearOnly?: boolean
  className?: string
}

export const DateField = ({ 
  value, 
  onChange, 
  compact = false, 
  monthYearOnly = false,
  className 
}: DateFieldProps) => {
  
  const getDisplayFormat = () => {
    if (monthYearOnly) {
      return compact ? "MMM yyyy" : "MMMM yyyy" // "Jan 2023" or "January 2023"
    }
    return compact ? "MMM dd, yy" : "MMM dd, yyyy"
  }

  const getButtonText = () => {
    if (!value) return monthYearOnly ? "Month/Year" : "Select date"
    return format(value, getDisplayFormat())
  }

  const buttonHeight = compact ? "h-8" : "h-9"
  const textSize = compact ? "text-xs" : "text-sm"
  const iconSize = compact ? "h-3 w-3" : "h-4 w-4"
  const padding = compact ? "px-2" : "px-3"

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button 
          variant="outline" 
          className={cn(
            "justify-start text-left font-normal w-full min-w-0",
            buttonHeight,
            textSize,
            padding,
            !value && "text-muted-foreground",
            className
          )}
        >
          <CalendarIcon className={cn("shrink-0 mr-2", iconSize)} />
          <span className="truncate">
            {getButtonText()}
          </span>
        </Button>
      </PopoverTrigger>
      <PopoverContent 
        className="w-auto p-0" 
        align="start"
        side="bottom"
      >
        <Calendar
          mode="single"
          selected={value === null ? undefined : value}
          onSelect={(day) => onChange(day === undefined ? null : day)}
          initialFocus
          defaultMonth={value || undefined}
          // For resume dates, we typically want past dates enabled
          disabled={monthYearOnly ? (date) => date > new Date() : undefined}
          className={compact ? "text-sm" : undefined}
        />
      </PopoverContent>
    </Popover>
  )
}

// Dedicated component for resume dates (month/year only)
export const ResumeMonthYearField = ({ 
  value, 
  onChange, 
  compact = false,
  className 
}: DateFieldProps) => {
  return (
    <DateField 
      value={value} 
      onChange={onChange} 
      compact={compact}
      monthYearOnly={true}
      className={className}
    />
  )
}
