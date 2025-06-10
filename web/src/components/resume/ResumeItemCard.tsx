"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { ResumeItemType } from "@/lib/types/Resume"
import { ResumeMonthYearField } from "../ui/datepicker"
import LabelledInput from "../ui/LabelledInput"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { ChevronUpIcon, ChevronDownIcon } from "lucide-react"
interface ResumeItemCardProps {
  resumeItem: ResumeItemType;
  compact?: boolean;
  className?: string;
  onMoveUp?: () => void;
  onMoveDown?: () => void;
  isFirst?: boolean;
  isLast?: boolean;
  onUpdate: (updates: Partial<ResumeItemType>) => void;
  isSkill?: boolean;
}

export default function ResumeItemCard({ 
  resumeItem, 
  compact = false,
  className,
  onMoveUp,
  onMoveDown,
  isFirst,
  isLast,
  onUpdate,
  isSkill = false,
}: ResumeItemCardProps) {

  const handleFieldChange = (field: keyof ResumeItemType, value: string | Date | null) => {
    onUpdate({ [field]: value });
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
                htmlFor={`title-${resumeItem.id}`}
                className="w-full"
                input={
                  <Input
                    id={`title-${resumeItem.id}`}
                    value={resumeItem.title}
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
                      value={resumeItem.start_date}
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
                      value={resumeItem.end_date}
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


        {!isSkill && <>
        {/* Dates for compact mode */}
        {compact && (
          <div className={layout.dateRow}>
            <LabelledInput 
              label="Start Date" 
              className="flex-1"
              input={
                <ResumeMonthYearField
                  value={resumeItem.start_date}
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
                  value={resumeItem.end_date}
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
            htmlFor={`organization-${resumeItem.id}`}
            className="flex-1 min-w-0"
            input={
              <Input
                id={`organization-${resumeItem.id}`}
                value={resumeItem.organization}
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
            htmlFor={`location-${resumeItem.id}`}
            className="flex-1 min-w-0"
            input={
              <Input
                id={`location-${resumeItem.id}`}
                value={resumeItem.location}
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
        </>}

        {/* Description - Full Width */}
        <div className="w-full">
          <LabelledInput 
            label="Description" 
            htmlFor={`description-${resumeItem.id}`}
            input={
              <Textarea
                id={`description-${resumeItem.id}`}
                value={resumeItem.description}
                onChange={(e) => handleFieldChange("description", e.target.value)}
                placeholder={isSkill ? "Describe your skills... (Comma separated)" : "Describe your role and achievements..."}
                className={cn("w-full resize-y", layout.textarea)}
              />
            }
          />
        </div>
      </CardContent>
    </Card>
  )
}
