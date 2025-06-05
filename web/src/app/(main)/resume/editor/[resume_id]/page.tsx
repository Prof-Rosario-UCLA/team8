"use client"

import { useState, useEffect } from "react"
import ResumeSection from "@/components/resume/ResumeSectionCard"
import { Button } from "@/components/ui/button"
import { PlusIcon, EyeIcon, SaveIcon } from "lucide-react"
import { ResumeItemType, ResumeSectionType, ResumeType } from "@/lib/types/Resume"

// Hook for resume state management - future-proofed for backend sync
function useResumeEditor(resumeId: string) {
  const [resume, setResume] = useState<ResumeType | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)

  // Simulate loading resume data (replace with actual API call later)
  useEffect(() => {
    const loadResume = async () => {
      setIsLoading(true)
      
      // Mock data with proper DateTime objects
      const mockResume: ResumeType = {
        id: resumeId,
        template: 1,
        name: "Jake Doe",
        resume_name: "Jake's Resume",
        phone: "(123) 456-7890",
        email: "jake@example.com",
        linkedin: "linkedin.com/in/jake",
        github: "github.com/jake",
        website: "https://www.example.com",
        updated_at: new Date(),
        sections: [
          {
            id: "education",
            name: "Education",
            type: "education",
            items: [
              {
                id: 1,
                item_type: "Education",
                title: "Masters in Computer Science",
                organization: "University of California, Los Angeles (UCLA)",
                start_date: new Date("2024-09-01"),
                end_date: null, // Present
                location: "Los Angeles, CA",
                description: "",
              },
              {
                id: 2,
                item_type: "Education", 
                title: "Bachelor of Science in Computer Science",
                organization: "University of California, Los Angeles (UCLA)",
                start_date: new Date("2020-09-01"),
                end_date: new Date("2024-06-01"),
                location: "Los Angeles, CA",
                description: "",
              },
            ]
          },
          {
            id: "experience",
            name: "Experience",
            type: "experience",
            items: [
              {
                id: 3,
                item_type: "Experience",
                title: "Software Engineer Intern",
                organization: "Macrosoft",
                start_date: new Date("2023-06-01"),
                end_date: new Date("2023-09-01"),
                location: "New York City, NY",
                description: "Worked on the Macrodata Refinement Team.\nBuild data cleaning pipelines for data wrangling and cleaning used by data engineers within Macrosoft to serve cutting-edge healthcare technology customers.\nIncorporated Large-Language Models (LLMs) agents to help automate the data cleaning process using unsupervised machine learning.",
              },
              {
                id: 4,
                item_type: "Experience",
                title: "Software Engineer Intern", 
                organization: "Poogle",
                start_date: new Date("2022-06-01"),
                end_date: new Date("2022-09-01"),
                location: "Sunnyvale, CA",
                description: "Worked on the Poodle Petting Services Team.\nDeveloped a distributed poodle scheduling service able to store millions of data points on poodle petting for millions of customers at Poogle.\nImplemented distributed consensus in Go using the Paxos algorithm to maintain eventual consistency and availability.",
              },
              {
                id: 5,
                item_type: "Experience",
                title: "Software Engineer Intern",
                organization: "Bananazon", 
                start_date: new Date("2021-06-01"),
                end_date: new Date("2021-09-01"),
                location: "Seattle, WA",
                description: "Worked on the Cloud Banana Ingestion Team.\nDeveloped a full-stack web application for counting bananas.\nUsed big-data algorithms like MapReduce to scale banana counting 10x for thousands of Bananazon employees.",
              },
            ]
          },
          {
            id: "projects",
            name: "Projects", 
            type: "projects",
            items: [
              {
                id: 6,
                item_type: "Project",
                title: "Temporal Rollback Automation - Time Variance Authority (TVA)",
                organization: "Club Project",
                start_date: new Date("2023-01-01"),
                end_date: new Date("2023-03-01"),
                location: "Los Angeles, CA",
                description: "Developed CI/CD pipeline for multiverse branch pruning using Loki-as-Code and Nexus Fluctuation Monitoring (NFM); reduced unauthorized timeline deployments by 87%.\nContainerized temporal rollback tools using ChronoDocker; ensured reproducibility across divergent realities and local pocket dimensions.\nImplemented real-time anomaly alerts via Slack-to-Timeline PagerDuty integration—successfully caught two Lokis, one Kang, and an unpaid intern before universe destabilization.",
              },
              {
                id: 7,
                item_type: "Project",
                title: "The Matrix",
                organization: "Club Project",
                start_date: new Date("2022-01-01"),
                end_date: new Date("2022-03-01"),
                location: "Los Angeles, CA", 
                description: "Designed and maintained immersive neural-interactive simulation for 99.9% of humanity; received consistently high user engagement despite complete lack of consent.\nLed team of Agents in real-time anomaly detection and reality-bending bug resolution, including high-priority escalations (e.g. \"The One\")\nIntroduced bullet-time rendering engine and kung fu auto-installation via direct brain upload, reducing training time by 100%.",
              },
              {
                id: 8,
                item_type: "Project",
                title: "Death Star",
                organization: "Class Project",
                start_date: new Date("2021-01-01"),
                end_date: new Date("2021-03-01"),
                location: "Los Angeles, CA",
                description: "Spearheaded cross-functional collaboration with Sith Lords, bounty hunters, and disgruntled contractors to deliver a planetary-scale laser weapon ahead of Empire fiscal year-end.\nImplemented robust access control systems (e.g., trench run) with intentional single-point-of-failure for testing Rebel threat response protocols\nReduced planet removal time by 99.99%, achieving galactic-scale disruption with minimal QA oversight",
              },
            ]
          },
          {
            id: "skills",
            name: "Technical Skills",
            type: "skills",
            items: [
              {
                id: 9,
                item_type: "Skill",
                title: "Languages",
                organization: "",
                start_date: null,
                end_date: null,
                location: "",
                description: "Python, C++, JavaScript.",
              },
              {
                id: 10,
                item_type: "Skill",
                title: "Frameworks",
                organization: "",
                start_date: null,
                end_date: null,
                location: "",
                description: "Express.js, React.js, Flask.",
              },
              {
                id: 11,
                item_type: "Skill",
                title: "Tools",
                organization: "",
                start_date: null,
                end_date: null,
                location: "",
                description: "Git, Docker, VSCode.",
              },
            ]
          }
        ]
      }

      // No need to sort - array position IS the order
      setResume(mockResume)
      setIsLoading(false)
    }

    loadResume()
  }, [resumeId])

  // Future: Functions for CRUD operations and reordering
  const updateResumeItem = (sectionId: string, itemId: number, updates: Partial<ResumeItemType>) => {
    if (!resume) return

    setResume(prev => {
      if (!prev) return null
      
      return {
        ...prev,
        sections: prev.sections.map(section => 
          section.id === sectionId 
            ? {
                ...section,
                items: section.items.map(item =>
                  item.id === itemId ? { ...item, ...updates } : item
                )
              }
            : section
        ),
        updated_at: new Date()
      }
    })
    setHasUnsavedChanges(true)
  }

  const reorderSection = (sectionId: string, direction: 'up' | 'down') => {
    if (!resume) return

    setResume(prev => {
      if (!prev) return null
      
      // Find the section index
      const sectionIndex = prev.sections.findIndex(section => section.id === sectionId)
      if (sectionIndex === -1) return prev
      
      // Check boundaries
      if (direction === 'up' && sectionIndex === 0) return prev
      if (direction === 'down' && sectionIndex === prev.sections.length - 1) return prev
      
      // Create a copy of sections array
      const newSections = [...prev.sections]
      
      // Swap with adjacent section
      const targetIndex = direction === 'up' ? sectionIndex - 1 : sectionIndex + 1
      const temp = newSections[targetIndex]
      newSections[targetIndex] = newSections[sectionIndex]
      newSections[sectionIndex] = temp
      
      return {
        ...prev,
        sections: newSections,
        updated_at: new Date()
      }
    })
    
    setHasUnsavedChanges(true)
  }

  const reorderItem = (sectionId: string, itemId: number, direction: 'up' | 'down') => {
    if (!resume) return
    
    setResume(prev => {
      if (!prev) return null
      
      // Find the section
      const sectionIndex = prev.sections.findIndex(section => section.id === sectionId)
      if (sectionIndex === -1) return prev
      
      const section = prev.sections[sectionIndex]
      
      // Find the item index
      const itemIndex = section.items.findIndex(item => item.id === itemId)
      if (itemIndex === -1) return prev
      
      // Check boundaries
      if (direction === 'up' && itemIndex === 0) return prev
      if (direction === 'down' && itemIndex === section.items.length - 1) return prev
      
      // Create a copy of items array
      const newItems = [...section.items]
      
      // Swap with adjacent item
      const targetIndex = direction === 'up' ? itemIndex - 1 : itemIndex + 1
      const temp = newItems[targetIndex]
      newItems[targetIndex] = newItems[itemIndex]
      newItems[itemIndex] = temp
      
      // Update the section with new items order
      const newSections = [...prev.sections]
      newSections[sectionIndex] = {
        ...section,
        items: newItems
      }
      
      return {
        ...prev,
        sections: newSections,
        updated_at: new Date()
      }
    })
    
    setHasUnsavedChanges(true)
  }

  const saveResume = async () => {
    if (!resume) return
    
    // TODO 

    const response = await fetch(`/api/views/resume/update/${resume.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(resume),
    })
    if (!response.ok) {
      console.error('Failed to save resume:', response.statusText)
      return
    }
    const data = await response.json()
    console.log('Resume saved:', data)

    console.log('Saving resume:', resume)
    setHasUnsavedChanges(false)
  }

  return {
    resume,
    isLoading,
    hasUnsavedChanges,
    updateResumeItem,
    reorderSection,
    reorderItem,
    saveResume
  }
}

export default function ResumeEditorPage({ params }: { params: Promise<{ resume_id: string }> }) {
  const [resolvedParams, setResolvedParams] = useState<{ resume_id: string } | null>(null)

  useEffect(() => {
    params.then(setResolvedParams)
  }, [params])

  const resumeEditor = useResumeEditor(resolvedParams?.resume_id || '')

  if (!resolvedParams || resumeEditor.isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading resume editor...</p>
        </div>
      </div>
    )
  }

  if (!resumeEditor.resume) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-gray-600">Resume not found</p>
        </div>
      </div>
    )
  }

  const { resume, hasUnsavedChanges, saveResume, reorderSection, reorderItem } = resumeEditor

  // Split view: editor on left, preview on right
  const leftPanel = (
    <div className="w-1/2 border-r border-gray-200 bg-gray-50 overflow-auto">
      {/* Editor Header */}
      <div className="sticky top-0 bg-white border-b border-gray-200 p-4 z-10">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-gray-900">{resume.resume_name}</h1>
            <p className="text-sm text-gray-600">Resume Editor</p>
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
        {hasUnsavedChanges && (
          <div className="mt-2 text-xs text-amber-600 bg-amber-50 px-2 py-1 rounded">
            You have unsaved changes
          </div>
        )}
      </div>

      {/* Resume Sections */}
      <div className="p-4 space-y-4">
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
            onAddItem={() => console.log('Add item to section', section.id)}
          />
        ))}
        
        {/* Future: Add Section Button */}
        <Button variant="outline" className="w-full flex items-center gap-2 border-dashed">
          <PlusIcon className="h-4 w-4" />
          Add Section
        </Button>
      </div>
    </div>
  )

  // Right panel WILL be an iframe of the latex resume pdf, currently just placeholder html elements
  const rightPanel = (
    <div className="w-1/2 bg-white overflow-auto">
      {/* Preview Header */}
      <div className="sticky top-0 bg-white border-b border-gray-200 p-4 z-10">
        <div className="flex items-center gap-2">
          <EyeIcon className="h-5 w-5 text-gray-600" />
          <h2 className="text-lg font-medium text-gray-900">Resume Preview</h2>
        </div>
      </div>

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
    </div>
  )

  return (
    <div className="h-screen flex">
      {leftPanel}
      {rightPanel}
    </div>
  )
} 