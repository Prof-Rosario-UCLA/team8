"use client";

import { useState, useEffect } from "react";
import ResumeSection from "@/components/resume/ResumeSectionCard";
import { Button } from "@/components/ui/button";
import { PlusIcon, EyeIcon, SaveIcon } from "lucide-react";
import { ResumeItemType, ResumeSectionType, ResumeType, ResumeSectionItemType, ALL_SECTION_TYPES, ResumeUpdatePayload } from "@/lib/types/Resume";
import LoadingPage from "@/components/loading/Loading";
import LabelledInput from "@/components/ui/LabelledInput";
import { Input } from "@/components/ui/input";
import { parseDates } from "@/lib/utils/date";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ChevronDown, ChevronLeft, ChevronRight } from "lucide-react";
import ResumeTOC from "@/components/resume/ResumeTOC";
import { DragEndEvent } from "@dnd-kit/core";
import { arrayMove } from "@dnd-kit/sortable";
import UserInfoCard from "@/components/resume/UserInfoCard";
import { cn } from "@/lib/utils";

// Hook for resume state management - future-proofed for backend sync
function useResumeEditor(resumeId: string) {
  const [resume, setResume] = useState<ResumeType | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [syncMessage, setSyncMessage] = useState<string | null>(null);

  useEffect(() => {
    const handleServiceWorkerMessage = (event: MessageEvent) => {
      if (event.data.type === "RESUME_SYNC_SUCCESS") {
        setSyncMessage(event.data.message);
        setHasUnsavedChanges(false);
        setTimeout(() => setSyncMessage(null), 5000); // Clear message after 5s
      }
    };
    navigator.serviceWorker.addEventListener("message", handleServiceWorkerMessage);
    return () => {
      navigator.serviceWorker.removeEventListener("message", handleServiceWorkerMessage);
    };
  }, [resumeId]);

  useEffect(() => {
    if (!resumeId) {
        setIsLoading(false);
        return;
    }

    const loadResume = async () => {
      setIsLoading(true);
      try {
        const response = await fetch(`/api/resume/${resumeId}`); // Adjusted API endpoint
        if (!response.ok) {
            throw new Error(`Failed to fetch resume: ${response.statusText}`);
        }
        const data = await response.json();
        console.log('Resume data received:', data);

        // Recursively parse date strings into Date objects
        const resumeDataWithDates = parseDates(data) as ResumeType;
        
        setResume(resumeDataWithDates);
      } catch (error) {
        console.error("Error loading resume:", error);
        // Handle error state in UI, e.g., show a notification
      } finally {
        setIsLoading(false);
      }
    };

    loadResume();
  }, [resumeId]);

  const addSection = (sectionType: ResumeSectionItemType) => {
    if (!resume) return;

    // Capitalize first letter for display name
    const name = sectionType.charAt(0).toUpperCase() + sectionType.slice(1);

    const newSection: ResumeSectionType = {
        id: crypto.randomUUID(), // Temporary client-side ID
        name: name,
        type: sectionType,
        items: [],
    };

    setResume(prev => {
        if (!prev) return null;
        return {
            ...prev,
            sections: [...prev.sections, newSection],
            updated_at: new Date(),
        };
    });
    setHasUnsavedChanges(true);
  };

  const addItemToSection = (sectionId: string | number) => {
    if (!resume) return;

    const section = resume.sections.find(s => s.id === sectionId);
    if (!section) {
      console.error("Section not found for adding item");
      return;
    }

    const newId = crypto.randomUUID();
    const newItem: ResumeItemType = {
        id: newId,
        title: "New Role",
        organization: "New Company",
        start_date: new Date(),
        end_date: null,
        location: "City, State",
        description: "",
    };

    setResume(prev => {
        if (!prev) return null;
        return {
            ...prev,
            sections: prev.sections.map(s =>
                s.id === sectionId
                    ? { ...s, items: [...s.items, newItem] }
                    : s
            ),
            updated_at: new Date(),
        };
    });
    setHasUnsavedChanges(true);
  };

  const updateResumeItem = (sectionId: string | number, itemId: string | number, updates: Partial<ResumeItemType>) => {
    if (!resume) return;

    setResume(prev => {
      if (!prev) return null;

      return {
        ...prev,
        sections: prev.sections.map(section =>
          section.id === sectionId
            ? {
                ...section,
                items: section.items.map(item =>
                  item.id === itemId ? { ...item, ...updates } : item
                ),
              }
            : section
        ),
        updated_at: new Date(),
      };
    });
    setHasUnsavedChanges(true);
  };

  const reorderSection = (sectionId: string | number, direction: 'up' | 'down') => {
    if (!resume) return;

    setResume(prev => {
      if (!prev) return null;
      
      const sectionIndex = prev.sections.findIndex(section => section.id === sectionId);
      if (sectionIndex === -1) return prev;
      
      if (direction === 'up' && sectionIndex === 0) return prev;
      if (direction === 'down' && sectionIndex === prev.sections.length - 1) return prev;
      
      const newSections = [...prev.sections];
      
      const targetIndex = direction === 'up' ? sectionIndex - 1 : sectionIndex + 1;
      const temp = newSections[targetIndex];
      newSections[targetIndex] = newSections[sectionIndex];
      newSections[sectionIndex] = temp;
      
      return {
        ...prev,
        sections: newSections,
        updated_at: new Date()
      };
    });
    
    setHasUnsavedChanges(true);
  };

  const reorderItem = (sectionId: string | number, itemId: string | number, direction: 'up' | 'down') => {
    if (!resume) return;
    
    setResume(prev => {
      if (!prev) return null;
      
      const sectionIndex = prev.sections.findIndex(section => section.id === sectionId);
      if (sectionIndex === -1) return prev;
      
      const section = prev.sections[sectionIndex];
      
      const itemIndex = section.items.findIndex(item => item.id === itemId);
      if (itemIndex === -1) return prev;
      
      if (direction === 'up' && itemIndex === 0) return prev;
      if (direction === 'down' && itemIndex === section.items.length - 1) return prev;
      
      const newItems = [...section.items];
      
      const targetIndex = direction === 'up' ? itemIndex - 1 : itemIndex + 1;
      const temp = newItems[targetIndex];
      newItems[targetIndex] = newItems[itemIndex];
      newItems[itemIndex] = temp;
      
      const newSections = [...prev.sections];
      newSections[sectionIndex] = {
        ...section,
        items: newItems
      };
      
      return {
        ...prev,
        sections: newSections,
        updated_at: new Date()
      };
    });
    
    setHasUnsavedChanges(true);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (active.id !== over?.id && over) {
        setResume((prev) => {
            if (!prev) return null;

            const activeId = active.id as string;
            const overId = over.id as string;

            const [activeSectionId, activeItemId] = activeId.split('::');
            const [overSectionId, overItemId] = overId.split('::');

            if (activeSectionId !== overSectionId) {
                return prev;
            }

            const sectionIndex = prev.sections.findIndex(s => s.id.toString() === activeSectionId);
            if (sectionIndex === -1) return prev;
            
            const section = prev.sections[sectionIndex];
            const oldIndex = section.items.findIndex(i => i.id.toString() === activeItemId);
            const newIndex = section.items.findIndex(i => i.id.toString() === overItemId);

            if (oldIndex === -1 || newIndex === -1) return prev;

            const newItems = arrayMove(section.items, oldIndex, newIndex);

            const newSections = [...prev.sections];
            newSections[sectionIndex] = {
                ...section,
                items: newItems,
            };

            return {
                ...prev,
                sections: newSections,
                updated_at: new Date(),
            };
        });
        setHasUnsavedChanges(true);
    }
  };

  const updateUserInfo = (updates: Partial<ResumeType>) => {
    setResume(prev => {
      if (!prev) return null;
      return {
        ...prev,
        ...updates,
        updated_at: new Date(),
      };
    });
    setHasUnsavedChanges(true);
  };

  const updateResumeName = (name: string) => {
    setResume(prev => {
      if (!prev) return null;
      return { ...prev, resume_name: name, updated_at: new Date() };
    });
    setHasUnsavedChanges(true);
  };

  const saveResume = async () => {
    if (!resume || !hasUnsavedChanges) return;

    setHasUnsavedChanges(true); // UI shows "saving..." until sync is confirmed.

    try {
      const payload: ResumeUpdatePayload = {
        ...resume,
        sections: resume.sections.map(section => ({
          ...section,
          id: typeof section.id === 'string' ? null : section.id,
          items: section.items.map(item => ({
            ...item,
            id: typeof item.id === 'string' ? null : item.id,
          })),
        })),
      };
      
      const response = await fetch(`/api/resume/update/${resume.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        console.log("Save request failed but has been queued for background sync.");
      } else {
        const data = await response.json();
        console.log('Resume saved, server response:', data);
        const resumeDataWithDates = parseDates(data) as ResumeType;
        setResume(resumeDataWithDates);
        setHasUnsavedChanges(false);
      }
    } catch (error) {
      console.error("Fetch failed. The service worker will handle retrying.", error);
    }
  };

  const availableSectionTypes = resume 
    ? ALL_SECTION_TYPES.filter(type => !resume.sections.some(s => s.type === type))
    : [];

  return {
    resume,
    isLoading,
    hasUnsavedChanges,
    updateResumeItem,
    reorderSection,
    reorderItem,
    saveResume,
    addSection,
    addItemToSection,
    availableSectionTypes,
    handleDragEnd,
    updateUserInfo,
    updateResumeName,
    syncMessage,
  };
}

export default function ResumeEditorPage({ params }: { params: Promise<{ resume_id: string }> }) {
  const [resolvedParams, setResolvedParams] = useState<{ resume_id: string } | null>(null);
  const [isTocOpen, setIsTocOpen] = useState(true);

  useEffect(() => {
    params.then(setResolvedParams);
  }, [params]);

  const resumeEditor = useResumeEditor(resolvedParams?.resume_id || '');

  if (!resolvedParams || resumeEditor.isLoading) {
    return (
      <LoadingPage message="Loading resume editor..." />  
    );
  }

  if (!resumeEditor.resume) {
    return (
      <div className="flex items-center justify-center flex-1 h-full">
        <section className="text-center">
          <p className="text-gray-600">Resume not found</p>
        </section>
      </div>
    );
  }

  const { resume, hasUnsavedChanges, saveResume, reorderSection, reorderItem, addSection, addItemToSection, availableSectionTypes, updateResumeItem, handleDragEnd, updateUserInfo, updateResumeName, syncMessage } = resumeEditor;

  // Split view: editor on left, preview on right
  const leftPanel = (
    <section className="w-full md:w-1/2 border-r border-gray-200 bg-gray-50 overflow-auto">
      {/* Editor Header */}
      <header className="sticky top-0 bg-white border-b border-gray-200 p-4 z-10">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-gray-900 pb-4">Resume Editor</h1>
            <LabelledInput
              label="Resume Name"
              htmlFor="resume_name"
              input={<Input id="resume_name" value={resume.resume_name} onChange={(e) => updateResumeName(e.target.value)} />}
            />
          </div>
          <div className="flex gap-2">
            <Button 
              variant="outline" 
              size="sm"
              onClick={saveResume}
              disabled={!hasUnsavedChanges}
              className="flex items-center gap-2"
            >
              <SaveIcon className="h-4 w-4" />
              {hasUnsavedChanges ? 'Save Changes' : 'Saved'}
            </Button>
          </div>
        </div>
        {syncMessage && (
          <div className="mt-2 text-xs text-green-600 bg-green-50 px-2 py-1 rounded">
            {syncMessage}
          </div>
        )}
        {hasUnsavedChanges && !syncMessage && (
          <div className="mt-2 text-xs text-amber-600 bg-amber-50 px-2 py-1 rounded">
            You have unsaved changes
          </div>
        )}
      </header>

      {/* User Info and Resume Sections */}
      <div className="p-4 space-y-4">
        <UserInfoCard 
            userInfo={resume}
            onUpdate={updateUserInfo}
            className="bg-white shadow-sm"
        />
        {resume.sections.map((section, sectionIndex) => (
          <ResumeSection 
            key={section.id}
            title={section.name}
            resumeItems={section.items}
            compact={true}
            className="bg-white shadow-sm"
            onMoveUp={sectionIndex > 0 ? () => reorderSection(section.id, 'up') : undefined}
            onMoveDown={sectionIndex < resume.sections.length - 1 ? () => reorderSection(section.id, 'down') : undefined}
            isFirst={sectionIndex === 0}
            isLast={sectionIndex === resume.sections.length - 1}
            onMoveItemUp={(itemId) => reorderItem(section.id, itemId, 'up')}
            onMoveItemDown={(itemId) => reorderItem(section.id, itemId, 'down')}
            onAddItem={() => addItemToSection(section.id)}
            onUpdateItem={(itemId, updates) => updateResumeItem(section.id, itemId, updates)}
          />
        ))}
        
        {/* Add Section Dropdown Button */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button 
              variant="outline" 
              className="w-full flex items-center gap-2 border-dashed"
              disabled={availableSectionTypes.length === 0}
            >
              <PlusIcon className="h-4 w-4" />
              Add Section
              <ChevronDown className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-full">
            {availableSectionTypes.map(type => (
              <DropdownMenuItem key={type} onClick={() => addSection(type)}>
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
        {availableSectionTypes.length === 0 && (
          <p className="text-xs text-center text-gray-500 mt-2">
            All section types have been added.
          </p>
        )}
      </div>
    </section>
  );

  // Right panel WILL be an iframe of the latex resume pdf, currently just placeholder html elements
  const rightPanel = (
    <section className="w-1/2 bg-white overflow-auto hidden md:block">
      {/* Preview Header */}
      <header className="sticky top-0 bg-white border-b border-gray-200 p-4 z-10">
        <div className="flex items-center gap-2">
          <EyeIcon className="h-5 w-5 text-gray-600" />
          <h2 className="text-lg font-medium text-gray-900">Resume Preview</h2>
        </div>
      </header>

      {/* Preview Content - Future: Replace with actual resume template */}
      <div className="p-6">
        <div className="max-w-2xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-gray-900">{resume.name.replace("'s Resume", "")}</h1>
            <div className="text-sm text-gray-600 mt-2 space-y-1">
              <p>{resume.email} • {resume.phone}</p>
              <p>{resume.linkedin} • {resume.github}</p>
              {resume.website && <p>{resume.website}</p>}
            </div>
          </div>

          {resume.sections.map((section) => (
            <div key={section.id} className="mb-6">
              <h2 className="text-lg font-semibold text-gray-900 border-b border-gray-300 pb-1 mb-3">
                {section.name}
              </h2>
              <div className="space-y-3">
                {section.items.map((item) => (
                  <div key={item.id} className="text-sm">
                    <div className="flex justify-between items-start mb-1">
                      <h3 className="font-medium text-gray-800">{item.title}</h3>
                      {item.start_date && (
                        <span className="text-gray-600 text-xs">
                          {item.start_date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                          {item.end_date ? ` - ${item.end_date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}` : ' - Present'}
                        </span>
                      )}
                    </div>
                    {item.organization && (
                      <div className="text-gray-600 text-xs mb-1">
                        {item.organization}{item.location && ` • ${item.location}`}
                      </div>
                    )}
                    {item.description && (
                      <p className="text-gray-700 text-xs leading-relaxed whitespace-pre-line">
                        {item.description}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );

  return (
    <section className="flex h-full">
      <div className={cn(
          "relative h-full transition-all duration-300 ease-in-out w-0 border-r border-gray-200",
          isTocOpen ? "md:w-64" : "md:w-10"
      )}>
        {isTocOpen && <ResumeTOC resume={resume} handleDragEnd={handleDragEnd} />}
        <Button
            onClick={() => setIsTocOpen(!isTocOpen)}
            variant="outline"
            size="icon"
            className="absolute top-1/2 z-30 bg-white rounded-full shadow-md h-8 w-8 hidden md:flex"
            style={{
              right: isTocOpen ? '-16px' : undefined,
              left: isTocOpen ? undefined : '50%',
              transform: isTocOpen ? 'translateY(-50%)' : 'translate(-50%, -50%)',
            }}
          >
            {isTocOpen ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
          </Button>
      </div>
      <div className="flex-1 flex">
        {leftPanel}
        {rightPanel}
      </div>
    </section>
  );
}