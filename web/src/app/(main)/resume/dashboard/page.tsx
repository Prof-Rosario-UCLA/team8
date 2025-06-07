import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { PlusIcon, FileTextIcon, CalendarIcon, EditIcon } from "lucide-react"

export default function DashboardPage() {
  // Mock data - eventually this will come from the backend
  const mockResumes = [
    {
      id: "1",
      name: "Jake's Resume",
      template: "Professional",
      lastModified: new Date("2024-01-15"),
      status: "draft"
    },
    {
      id: "2", 
      name: "Software Engineer Resume",
      template: "Modern",
      lastModified: new Date("2024-01-10"),
      status: "published"
    }
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Resume Dashboard</h1>
              <p className="mt-2 text-gray-600">Manage and create your professional resumes</p>
            </div>
            <Button className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700">
              <PlusIcon className="h-4 w-4" />
              Create New Resume
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {mockResumes.length === 0 ? (
          // Empty State
          <div className="text-center py-12">
            <FileTextIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-lg font-medium text-gray-900">No resumes yet</h3>
            <p className="mt-1 text-gray-500">Get started by creating your first resume.</p>
            <div className="mt-6">
              <Button className="bg-blue-600 hover:bg-blue-700">
                <PlusIcon className="h-4 w-4 mr-2" />
                Create Your First Resume
              </Button>
            </div>
          </div>
        ) : (
          // Resume Grid
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Your Resumes</h2>
              <span className="text-sm text-gray-500">{mockResumes.length} resume{mockResumes.length !== 1 ? 's' : ''}</span>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {mockResumes.map((resume) => (
                <Card key={resume.id} className="hover:shadow-md transition-shadow cursor-pointer">
                  <CardHeader className="pb-3">
                    <div className="flex justify-between items-start">
                      <div className="flex items-center space-x-2">
                        <FileTextIcon className="h-5 w-5 text-blue-600" />
                        <CardTitle className="text-lg">{resume.name}</CardTitle>
                      </div>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        resume.status === 'published' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {resume.status}
                      </span>
                    </div>
                    <CardDescription className="flex items-center text-sm text-gray-500">
                      <CalendarIcon className="h-3 w-3 mr-1" />
                      Last modified {resume.lastModified.toLocaleDateString()}
                    </CardDescription>
                  </CardHeader>
                  
                  <CardContent className="pt-0">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">{resume.template} template</span>
                      <Link href={`/resume/editor/${resume.id}`}>
                        <Button size="sm" variant="outline" className="flex items-center gap-1">
                          <EditIcon className="h-3 w-3" />
                          Edit
                        </Button>
                      </Link>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
