"use client";

import { useState, useEffect, useCallback } from "react";
import ResumeSection from "@/components/resume/ResumeSectionCard";
import { Button } from "@/components/ui/button";
import { EyeIcon, SaveIcon } from "lucide-react";
import { ResumeItemType, ResumeSectionType, ResumeType, ORDERED_SECTION_TYPES, SECTION_TYPE_DISPLAY_NAME_MAP, ResumeUpdatePayload } from "@/lib/types/Resume";
import LoadingPage from "@/components/loading/Loading";
import LabelledInput from "@/components/ui/LabelledInput";
import { Input } from "@/components/ui/input";
import { parseDates } from "@/lib/utils/date";
import { ChevronLeft, ChevronRight } from "lucide-react";
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
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [isCompiling, setIsCompiling] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  const startCompilation = useCallback(async () => {
    if (!resumeId) return;
    
    setIsCompiling(true);

    try {
      const compileResponse = await fetch(`/api/compile/${resumeId}`, { method: 'POST' });
      if (!compileResponse.ok) throw new Error("Failed to start compilation");
      
      const compileData = await compileResponse.json();
      console.log("Compile response:", compileData);

      const { task_id } = compileData;
      
      const poll = async () => {
        const statusResponse = await fetch(`/api/compile/status/${task_id}`);
        if (!statusResponse.ok) {
          // Stop polling on server error
          clearInterval(intervalId);
          setIsCompiling(false);
          return;
        }

        const result = await statusResponse.json();
        
        console.log("Poll result:", result);

        if (result.status === 'done') {
          setPdfUrl(result.url);
          setIsCompiling(false);
          clearInterval(intervalId);
        } else if (result.status === 'failure') {
          console.error("PDF Compilation failed:", result.error);
          setIsCompiling(false);
          clearInterval(intervalId);
        }
        // If 'pending', do nothing and let it poll again
      };

      const intervalId = setInterval(poll, 2000); // Poll every 2 seconds
    } catch (error) {
      console.error("Error during compilation process:", error);
      setIsCompiling(false);
    }
  }, [resumeId]);

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

        // Ensure all sections are present and add a default item if a section is new
        const existingSectionTypes = new Set(data.sections.map((s: ResumeSectionType) => s.section_type));
        console.log("Existing section types:", existingSectionTypes);
        console.log("Ordered section types:", ORDERED_SECTION_TYPES);
        for (const sectionType of ORDERED_SECTION_TYPES) {
          if (!existingSectionTypes.has(sectionType)) {
            const newSection: ResumeSectionType = {
              id: crypto.randomUUID(),
              name: SECTION_TYPE_DISPLAY_NAME_MAP[sectionType],
              section_type: sectionType,
              items: [{
                id: crypto.randomUUID(),
                title: "New Entry",
                organization: "",
                start_date: null,
                end_date: null,
                location: "",
                description: "",
              }],
            };
            data.sections.push(newSection);
          }
        }
        
        // Sort sections based on the predefined order
        data.sections.sort((a: ResumeSectionType, b: ResumeSectionType) => {
          return ORDERED_SECTION_TYPES.indexOf(a.section_type) - ORDERED_SECTION_TYPES.indexOf(b.section_type);
        });

        // Recursively parse date strings into Date objects
        const resumeDataWithDates = parseDates(data) as ResumeType;
        
        setResume(resumeDataWithDates);
        startCompilation(); // Initial compilation
      } catch (error) {
        console.error("Error loading resume:", error);
        // Handle error state in UI, e.g., show a notification
      } finally {
        setIsLoading(false);
      }
    };

    loadResume();
  }, [resumeId, startCompilation]);

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

  const deleteItemFromSection = (sectionId: string | number, itemId: string | number) => {
    if (!resume) return;

    setResume(prev => {
      if (!prev) return null;

      const section = prev.sections.find(s => s.id === sectionId);
      if (!section || section.items.length <= 1) {
        // Prevent deleting the last item
        return prev;
      }

      return {
        ...prev,
        sections: prev.sections.map(s =>
          s.id === sectionId
            ? { ...s, items: s.items.filter(item => item.id !== itemId) }
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
    setSaveError(null);

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
        if (response.status >= 400 && response.status < 500) {
          const errorData = await response.json();
          setSaveError(errorData.error || "An unknown validation error occurred.");
          setHasUnsavedChanges(true); // Keep unsaved state
          console.error("Client-side validation error:", errorData);
        } else {
          console.log("Save request failed but has been queued for background sync.");
          setSaveError("Server error, your changes will be saved in the background.");
        }
      } else {
        const data = await response.json();
        console.log('Resume saved, server response:', data);
        const resumeDataWithDates = parseDates(data) as ResumeType;
        setResume(resumeDataWithDates);
        setHasUnsavedChanges(false);
        setSaveError(null);
        startCompilation(); // Re-compile after a successful save
      }
    } catch (error) {
      console.error("Fetch failed. The service worker will handle retrying.", error);
      setSaveError("Network error. Your changes have been queued for saving.");
    }
  };

  return {
    resume,
    isLoading,
    hasUnsavedChanges,
    updateResumeItem,
    reorderItem,
    saveResume,
    addItemToSection,
    deleteItemFromSection,
    handleDragEnd,
    updateUserInfo,
    updateResumeName,
    syncMessage,
    pdfUrl,
    isCompiling,
    saveError,
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

  const { resume, hasUnsavedChanges, saveResume, reorderItem, addItemToSection, deleteItemFromSection, updateResumeItem, handleDragEnd, updateUserInfo, updateResumeName, syncMessage, pdfUrl, isCompiling, saveError } = resumeEditor;

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
        {saveError && (
          <div className="mt-2 text-sm text-red-600 bg-red-50 p-2 rounded">
            <strong>Error:</strong> {saveError}
          </div>
        )}
        {hasUnsavedChanges && !syncMessage && !saveError && (
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
        {resume.sections.map((section) => (
          <ResumeSection 
            key={section.id}
            title={section.name}
            resumeItems={section.items}
            compact={true}
            className="bg-white shadow-sm"
            onMoveItemUp={(itemId) => reorderItem(section.id, itemId, 'up')}
            onMoveItemDown={(itemId) => reorderItem(section.id, itemId, 'down')}
            onAddItem={() => addItemToSection(section.id)}
            onUpdateItem={(itemId, updates) => updateResumeItem(section.id, itemId, updates)}
            onDeleteItem={(itemId) => deleteItemFromSection(section.id, itemId)}
          />
        ))}
        
      </div>
    </section>
  );

  // Right panel WILL be an iframe of the latex resume pdf, currently just placeholder html elements
  const rightPanel = (
    <section className="w-1/2 bg-gray-100 overflow-auto hidden md:block">
      {/* Preview Header */}
      <header className="sticky top-0 bg-white border-b border-gray-200 p-4 z-10">
        <div className="flex items-center gap-2">
          <EyeIcon className="h-5 w-5 text-gray-600" />
          <h2 className="text-lg font-medium text-gray-900">Resume Preview</h2>
          {isCompiling && <span className="text-xs text-gray-500 ml-2">(Compiling...)</span>}
        </div>
      </header>
      
      <div className="p-2 h-full">
        {pdfUrl ? (
          <iframe src={pdfUrl + '#toolbar=0'} className="w-full h-full border-none" title="Resume Preview"></iframe>
        ) : (
          <div className="flex items-center justify-center h-full bg-white rounded-md">
            <div className="text-center">
              {isCompiling ? (
                <>
                  <LoadingPage message="Generating PDF preview..." />
                </>
              ) : (
                <p className="text-gray-500">Save your resume to see the preview.</p>
              )}
            </div>
          </div>
        )}
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