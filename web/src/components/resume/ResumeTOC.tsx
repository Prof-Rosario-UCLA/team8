import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
  DragOverlay,
  DragStartEvent,
} from "@dnd-kit/core";
import {
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { useState } from "react";

import { ResumeType } from "@/lib/types/Resume";
import { SortableItem } from "./SortableItem";

interface ResumeTOCProps {
  resume: ResumeType;
  handleDragEnd: (event: DragEndEvent) => void;
}

export default function ResumeTOC({ resume, handleDragEnd }: ResumeTOCProps) {
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const [activeId, setActiveId] = useState<string | null>(null);

  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(event.active.id as string);
  };

  const internalHandleDragEnd = (event: DragEndEvent) => {
    setActiveId(null);
    handleDragEnd(event); // Call parent handler
  };
  
  const activeItem = activeId
    ? resume.sections
        .flatMap((s) => s.items.map((i) => ({ ...i, sectionId: s.id })))
        .find((i) => `${i.sectionId}::${i.id}` === activeId)
    : null;


  return (
    <aside className="relative h-full w-64 bg-gray-50 border-r border-gray-200 p-4 overflow-y-auto z-20">
      <h2 className="text-lg font-semibold text-gray-800 mb-4 sticky top-0 bg-gray-50 pb-2 z-10">
        Table of Contents
      </h2>
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragStart={handleDragStart}
        onDragEnd={internalHandleDragEnd}
      >
        <nav className="space-y-4">
          {resume.sections.map((section) => (
            <div key={section.id}>
              <h3 className="text-sm font-medium text-gray-700">
                {section.name}
              </h3>
              <SortableContext
                items={section.items.map((item) => `${section.id}::${item.id}`)}
                strategy={verticalListSortingStrategy}
              >
                <ul className="mt-2 space-y-1">
                  {section.items.map((item) => (
                    <SortableItem
                      key={`${section.id}::${item.id}`}
                      id={`${section.id}::${item.id}`}
                      title={item.title}
                    />
                  ))}
                </ul>
              </SortableContext>
            </div>
          ))}
        </nav>
        <DragOverlay>
            {activeItem ? (
                <SortableItem id={`${activeItem.sectionId}::${activeItem.id}`} title={activeItem.title} />
            ) : null}
        </DragOverlay>
      </DndContext>
    </aside>
  );
}
