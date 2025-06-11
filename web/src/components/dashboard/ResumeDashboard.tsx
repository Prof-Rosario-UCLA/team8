'use client'
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { PlusIcon, FileTextIcon, CalendarIcon, EditIcon, Trash2Icon } from "lucide-react"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { useEffect, useState } from "react"
import { ResumeType } from "@/lib/types/Resume"
import LoadingPage from "@/components/loading/Loading"
import { useRouter } from "next/navigation"
import { parseDates } from "@/lib/utils/date"

export default function ResumeDashboard() {
  const router = useRouter()
  const [resumes, setResumes] = useState<ResumeType[]>([])
  const [isLoaded, setIsLoaded] = useState<boolean>(false)
  const [isCreating, setIsCreating] = useState<boolean>(false)
  const [resumeToDelete, setResumeToDelete] = useState<ResumeType | null>(null)
  
  useEffect(() => {
    const fetchResumes = async () => {
      try {
        const response = await fetch('/api/resume/all');
        if (!response.ok) {
          throw new Error('Failed to fetch resumes');
        }
        const data = await response.json();
        
        // Use the centralized utility to parse dates in the entire resumes array
        setResumes(parseDates(data.resumes) as ResumeType[]);
      } catch (error) {
        console.error("Error fetching resumes:", error);
      } finally {
        setIsLoaded(true);
      }
    };
    
    fetchResumes();
  }, []);
  
  const handleCreateResume = async () => {
    setIsCreating(true);
    try {
      const response = await fetch('/api/resume/create', { method: 'POST' });
      if (!response.ok) throw new Error('Failed to create resume');
      const newResume = await response.json();
      router.push(`/resume/editor/${newResume.id}`);
    } catch (error) {
      console.error("Error creating resume:", error);
    } finally {
      setIsCreating(false);
    }
  };

  const handleDeleteResume = async () => {
    if (!resumeToDelete) return;

    try {
      const response = await fetch(`/api/resume/delete/${resumeToDelete.id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete resume');
      }

      setResumes(prevResumes => prevResumes.filter(r => r.id !== resumeToDelete.id));
    } catch (error) {
      console.error("Error deleting resume:", error);
      // Optionally show an error toast to the user
    } finally {
      setResumeToDelete(null); // Close the dialog
    }
  };

  if (!isLoaded) {
    return <LoadingPage />
  }

  return (
    <>
      <section className="h-full bg-gray-50">
        {/* Header */}
        <header className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex justify-between items-center">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Resume Dashboard</h1>
                <p className="mt-2 text-gray-600">Manage and create your professional resumes</p>
              </div>
              <Button onClick={handleCreateResume} disabled={isCreating} className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700">
                <PlusIcon className="h-4 w-4" />
                {isCreating ? 'Creating...' : 'Create New Resume'}
              </Button>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {resumes.length === 0 ? (
            // Empty State
            <section className="text-center py-12">
              <FileTextIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-lg font-medium text-gray-900">No resumes yet</h3>
              <p className="mt-1 text-gray-500">Get started by creating your first resume.</p>
              <div className="mt-6">
                <Button onClick={handleCreateResume} disabled={isCreating} className="bg-blue-600 hover:bg-blue-700">
                  <PlusIcon className="h-4 w-4 mr-2" />
                  {isCreating ? 'Creating...' : 'Create Your First Resume'}
                </Button>
              </div>
            </section>
          ) : (
            // Resume Grid
            <section>
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold text-gray-900">Your Resumes</h2>
                <span className="text-sm text-gray-500">{resumes.length} resume{resumes.length !== 1 ? 's' : ''}</span>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {resumes.map((resume) => (
                  <article key={resume.id}>
                    <Card className="hover:shadow-md transition-shadow h-full flex flex-col">
                      <CardHeader className="pb-3">
                        <div className="flex justify-between items-start">
                          <div className="flex items-center space-x-2">
                            <FileTextIcon className="h-5 w-5 text-blue-600" />
                            <CardTitle className="text-lg">{resume.resume_name}</CardTitle>
                          </div>
                        </div>
                        <CardDescription className="flex items-center text-sm text-gray-500">
                          <CalendarIcon className="h-3 w-3 mr-1" />
                          Last modified {resume.updated_at ? resume.updated_at.toLocaleDateString() : "N/A"}
                        </CardDescription>
                      </CardHeader>
                      
                      <CardContent className="pt-0 mt-auto">
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Template {resume.template_id}</span>
                          <div className="flex items-center gap-2">
                            <Link href={`/resume/editor/${resume.id}`} passHref>
                              <Button size="sm" variant="outline" className="flex items-center gap-1">
                                <EditIcon className="h-3 w-3" />
                                Edit
                              </Button>
                            </Link>
                            <Button
                              size="sm"
                              variant="destructive"
                              className="flex items-center gap-1"
                              onClick={() => setResumeToDelete(resume)}
                            >
                              <Trash2Icon className="h-3 w-3" />
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </article>
                ))}
              </div>
            </section>
          )}
        </section>
      </section>

      {/* Deletion Confirmation Dialog */}
      <AlertDialog open={!!resumeToDelete} onOpenChange={(isOpen) => !isOpen && setResumeToDelete(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete the resume 
              <span className="font-semibold"> &quot;{resumeToDelete?.name}&quot; </span> 
              and all of its associated data from our servers.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDeleteResume}>Delete</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
} 