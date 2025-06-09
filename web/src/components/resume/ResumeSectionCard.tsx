import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ResumeItemType } from "@/lib/types/Resume";
import ResumeItemCard from "./ResumeItemCard";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { ChevronUpIcon, ChevronDownIcon, PlusIcon } from "lucide-react";

interface ResumeSectionProps {
  title: string;
  resumeItems: ResumeItemType[];
  className?: string;
  compact?: boolean; // For smaller containers
  
  // Reordering callbacks
  onMoveUp?: () => void;
  onMoveDown?: () => void;
  isFirst?: boolean;
  isLast?: boolean;
  
  // Item reordering callbacks
  onMoveItemUp?: (itemId: number | string) => void;
  onMoveItemDown?: (itemId: number | string) => void;
  
  // Add item callback
  onAddItem?: () => void;

  // Update item callback
  onUpdateItem?: (itemId: number | string, updates: Partial<ResumeItemType>) => void;
}

export default function ResumeSection({ 
  title, 
  resumeItems, 
  className,
  compact = false,
  onMoveUp,
  onMoveDown,
  isFirst,
  isLast,
  onMoveItemUp,
  onMoveItemDown,
  onAddItem,
  onUpdateItem
}: ResumeSectionProps) {
  
  // Professional spacing and padding
  const getLayoutClasses = () => {
    if (compact) {
      return {
        header: "pb-2 px-3 pt-3",
        title: "text-base font-semibold text-gray-800",
        content: "px-3 pb-3 space-y-2",
      }
    }
    
    return {
      header: "pb-3 px-4 pt-4",
      title: "text-lg font-semibold text-gray-900",
      content: "px-4 pb-4 space-y-3",
    }
  }

  const layout = getLayoutClasses()

  const isSkill = title.toLowerCase() === "skill"

  return (
    <Card className={cn("w-full shadow-sm border-gray-200", className)}>
      <CardHeader className={layout.header}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {/* Section Elevator Buttons */}
            {(onMoveUp || onMoveDown) && (
              <div className="flex space-x-1">
                <Button
                  size="icon"
                  variant="ghost"
                  className={cn(
                    "h-6 w-6 rounded-full p-0",
                    isFirst ? "text-gray-300 cursor-not-allowed" : "text-gray-500 hover:text-blue-600 hover:bg-blue-50"
                  )}
                  disabled={isFirst}
                  onClick={onMoveUp}
                  aria-label="Move section up"
                >
                  <ChevronUpIcon className="h-4 w-4" />
                </Button>
                <Button
                  size="icon"
                  variant="ghost"
                  className={cn(
                    "h-6 w-6 rounded-full p-0",
                    isLast ? "text-gray-300 cursor-not-allowed" : "text-gray-500 hover:text-blue-600 hover:bg-blue-50"
                  )}
                  disabled={isLast}
                  onClick={onMoveDown}
                  aria-label="Move section down"
                >
                  <ChevronDownIcon className="h-4 w-4" />
                </Button>
              </div>
            )}
            <CardTitle className={layout.title}>
              {title}
            </CardTitle>
          </div>
          
          {/* Add Item Button */}
          {onAddItem && (
            <Button 
              size="sm" 
              variant="ghost" 
              className="h-7 px-2 text-xs text-gray-600 hover:text-blue-600 hover:bg-blue-50"
              onClick={onAddItem}
            >
              <PlusIcon className="h-3.5 w-3.5 mr-1" />
              Add Item
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className={layout.content}>
        {resumeItems.map((item, index) => (
          <ResumeItemCard 
            key={item.id} 
            resumeItem={item} 
            compact={compact}
            onMoveUp={onMoveItemUp ? () => onMoveItemUp(item.id) : undefined}
            onMoveDown={onMoveItemDown ? () => onMoveItemDown(item.id) : undefined}
            isFirst={index === 0}
            isLast={index === resumeItems.length - 1}
            onUpdate={(updates) => onUpdateItem && onUpdateItem(item.id, updates)}
            isSkill={isSkill}
          />
        ))}
      </CardContent>
    </Card>
  )
}