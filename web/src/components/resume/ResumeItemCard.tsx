"use client"

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import ResumeItemType from "@/lib/types/Resume"
import { useState } from "react"
import { useResumeItemSync } from "@/lib/hooks/resume/useResumeItemSync"
import { ResumeMonthYearField } from "../ui/datepicker"
import LabelledInput from "../ui/LabelledInput"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { ChevronUpIcon, ChevronDownIcon } from "lucide-react"

const capitalize = (s: string) => {
  if (typeof s !== 'string' || !s) return ''
  return s.charAt(0).toUpperCase() + s.slice(1)
}

interface ResumeItemCardProps {
  resumeItem: ResumeItemType;
  compact?: boolean;
  className?: string;
  onMoveUp?: () => void;
  onMoveDown?: () => void;
  isFirst?: boolean;
  isLast?: boolean;
}

export default function ResumeItemCard({ 
  resumeItem, 
  compact = false,
  className,
  onMoveUp,
  onMoveDown,
  isFirst,
  isLast
}: ResumeItemCardProps) {
  const [localItem, setLocalItem] = useState(resumeItem)
  const { updateField } = useResumeItemSync(resumeItem.id)

  const handleFieldChange = (field: keyof ResumeItemType, value: string | Date | null) => {
    // Convert Date to ISO string for start_date and end_date
    let processedValue = value;
    if ((field === "start_date" || field === "end_date") && value instanceof Date) {
      processedValue = value.toISOString();
    } else if (value === null && (field === "start_date" || field === "end_date")) {
      processedValue = null; // Allow null to be passed if date is cleared
    }

    setLocalItem((prev) => ({ ...prev, [field]: processedValue }))

    // TODO: Remove this, we don't need to update the field all the time, since we can just bulk update the resume on save
    // if (field === "start_date" || field === "end_date") {
    //   updateField(field, processedValue === null ? "" : String(processedValue))
    // } else {
    //   updateField(field, String(processedValue ?? ""))
    // }
  }

  // Smart responsive breakpoints - use available space efficiently
  const getLayoutClasses = () => {
    if (compact) {
      return {
        container: "space-y-3",
        header: "pb-1",
        title: "text-sm font-medium",
        content: "space-y-3 px-4 pb-3",
        titleRow: "flex flex-col space-y-2",
        dateRow: "flex flex-col space-y-2",
        orgRow: "flex flex-col space-y-2",
        textarea: "min-h-[50px] text-xs",
      }
    }
    
    return {
      container: "space-y-0",
      header: "pb-3 px-4 pt-3",
      title: "text-base font-semibold",
      content: "space-y-3 px-4 pb-4", 
      titleRow: "flex flex-col md:flex-row md:items-start gap-3",
      dateRow: "flex flex-col sm:flex-row gap-2",
      orgRow: "flex flex-col sm:flex-row gap-2",
      textarea: "min-h-[70px] text-sm",
    }
  }

  const layout = getLayoutClasses()

  return (
    <Card className={cn(layout.container, "w-full border border-gray-200", className)}>
      <CardContent className={layout.content}>
        {/* Title Row - Always takes priority, full width on small screens */}
        <div className={layout.titleRow}>
          <div className={compact ? "w-full" : "flex-1 min-w-0"}>
            <div className="flex items-start gap-2">
              {/* Elevator Buttons - Only shown if callbacks are provided */}
              {(onMoveUp || onMoveDown) && (
                <div className="flex flex-col space-y-1 mt-6">
                  <Button
                    size="icon"
                    variant="ghost"
                    className={cn(
                      "h-6 w-6 rounded-full p-0",
                      compact ? "h-5 w-5" : "h-6 w-6",
                      isFirst ? "text-gray-300 cursor-not-allowed" : "text-gray-500 hover:text-blue-600 hover:bg-blue-50"
                    )}
                    disabled={isFirst}
                    onClick={onMoveUp}
                    aria-label="Move item up"
                  >
                    <ChevronUpIcon className="h-3.5 w-3.5" />
                  </Button>
                  <Button
                    size="icon"
                    variant="ghost"
                    className={cn(
                      "h-6 w-6 rounded-full p-0",
                      compact ? "h-5 w-5" : "h-6 w-6",
                      isLast ? "text-gray-300 cursor-not-allowed" : "text-gray-500 hover:text-blue-600 hover:bg-blue-50"
                    )}
                    disabled={isLast}
                    onClick={onMoveDown}
                    aria-label="Move item down"
                  >
                    <ChevronDownIcon className="h-3.5 w-3.5" />
                  </Button>
                </div>
              )}
              
              <LabelledInput 
                label="Title" 
                className="w-full"
                input={
                  <Input
                    value={localItem.title}
                    onChange={(e) => handleFieldChange("title", e.target.value)}
                    placeholder="Job Title"
                    className={cn(
                      "w-full font-medium truncate",
                      compact ? "h-8 text-xs" : "h-9 text-sm"
                    )}
                  />
                }
              />
            </div>
          </div>
          
          {/* Date Range - Smart responsive behavior */}
          {!compact && (
            <div className="flex-1 min-w-0 max-w-md">
              <div className={layout.dateRow}>
                <LabelledInput 
                  label="Start" 
                  className="flex-1 min-w-0"
                  input={
                    <ResumeMonthYearField
                      value={localItem.start_date ? new Date(localItem.start_date) : null}
                      onChange={(date) => handleFieldChange("start_date", date)}
                      compact={compact}
                      className="w-full"
                    />
                  }
                />
                <LabelledInput 
                  label="End" 
                  className="flex-1 min-w-0"
                  input={
                    <ResumeMonthYearField
                      value={localItem.end_date ? new Date(localItem.end_date) : null}
                      onChange={(date) => handleFieldChange("end_date", date)}
                      compact={compact}
                      className="w-full"
                    />
                  }
                />
              </div>
            </div>
          )}
        </div>

        {/* Dates for compact mode */}
        {compact && (
          <div className={layout.dateRow}>
            <LabelledInput 
              label="Start Date" 
              className="flex-1"
              input={
                <ResumeMonthYearField
                  value={localItem.start_date ? new Date(localItem.start_date) : null}
                  onChange={(date) => handleFieldChange("start_date", date)}
                  compact={true}
                  className="w-full"
                />
              }
            />
            <LabelledInput 
              label="End Date" 
              className="flex-1"
              input={
                <ResumeMonthYearField
                  value={localItem.end_date ? new Date(localItem.end_date) : null}
                  onChange={(date) => handleFieldChange("end_date", date)}
                  compact={true}
                  className="w-full"
                />
              }
            />
          </div>
        )}
        
        {/* Organization and Location Row */}
        <div className={layout.orgRow}>
          <LabelledInput 
            label="Organization" 
            className="flex-1 min-w-0"
            input={
              <Input
                value={localItem.organization}
                onChange={(e) => handleFieldChange("organization", e.target.value)}
                placeholder="Company/Organization"
                className={cn(
                  "w-full truncate",
                  compact ? "h-8 text-xs" : "h-9 text-sm"
                )}
              />
            }
          />
          <LabelledInput 
            label="Location" 
            className="flex-1 min-w-0"
            input={
              <Input
                value={localItem.location}
                onChange={(e) => handleFieldChange("location", e.target.value)}
                placeholder="City, State"
                className={cn(
                  "w-full truncate",
                  compact ? "h-8 text-xs" : "h-9 text-sm"
                )}
              />
            }
          />
        </div>
        
        {/* Description - Full Width */}
        <div className="w-full">
          <LabelledInput 
            label="Description" 
            input={
              <Textarea
                value={localItem.description}
                onChange={(e) => handleFieldChange("description", e.target.value)}
                placeholder="Describe your role and achievements..."
                className={cn("w-full resize-y", layout.textarea)}
              />
            }
          />
        </div>
      </CardContent>
    </Card>
  )
}
