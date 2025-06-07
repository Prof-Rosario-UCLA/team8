import Link from "next/link";
import { Button } from "@/components/ui/button";
import { FileTextIcon, ArrowRightIcon, SparklesIcon, CheckIcon } from "lucide-react";

export default function Home() {
  const features = [
    "Professional resume templates",
    "Real-time preview as you edit", 
    "Export to PDF",
    "Multiple resume versions",
    "Clean, modern interface"
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16 text-center lg:pt-32">
          <div className="mx-auto max-w-4xl">
            <div className="mb-8 flex justify-center">
              <div className="flex items-center space-x-2 rounded-full bg-blue-100 px-4 py-2">
                <SparklesIcon className="h-5 w-5 text-blue-600" />
                <span className="text-sm font-medium text-blue-800">Professional Resume Builder</span>
              </div>
            </div>
            
            <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
              Create Your Perfect{" "}
              <span className="text-blue-600">Resume</span>
            </h1>
            
            <p className="mt-6 text-lg leading-8 text-gray-600 max-w-2xl mx-auto">
              Build professional resumes with our intuitive editor. Choose from modern templates, 
              get real-time previews, and export to PDF. Land your dream job with Prolio.
            </p>
            
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <Link href="/resume/dashboard">
                <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-white">
                  Get Started
                  <ArrowRightIcon className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link href="/resume/editor/demo">
                <Button variant="outline" size="lg">
                  View Demo
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="relative bg-white py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              Everything you need to build a standout resume
            </h2>
            <p className="mt-4 text-lg text-gray-600">
              Professional tools designed to help you create the perfect resume
            </p>
          </div>

          <div className="mt-16 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
            <div className="text-center">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100">
                <FileTextIcon className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="mt-4 text-lg font-medium text-gray-900">Professional Templates</h3>
              <p className="mt-2 text-sm text-gray-600">
                Choose from a variety of modern, ATS-friendly resume templates designed by professionals.
              </p>
            </div>

            <div className="text-center">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-lg bg-green-100">
                <SparklesIcon className="h-6 w-6 text-green-600" />
              </div>
              <h3 className="mt-4 text-lg font-medium text-gray-900">Real-time Preview</h3>
              <p className="mt-2 text-sm text-gray-600">
                See your resume come to life as you edit with our split-screen editor and live preview.
              </p>
            </div>

            <div className="text-center">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-lg bg-purple-100">
                <ArrowRightIcon className="h-6 w-6 text-purple-600" />
              </div>
              <h3 className="mt-4 text-lg font-medium text-gray-900">Easy Export</h3>
              <p className="mt-2 text-sm text-gray-600">
                Export your finished resume to PDF format, ready to send to employers.
              </p>
            </div>
          </div>

          {/* Feature List */}
          <div className="mt-16 bg-gray-50 rounded-2xl p-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
              <div>
                <h3 className="text-2xl font-bold text-gray-900 mb-6">Why choose Prolio?</h3>
                <ul className="space-y-4">
                  {features.map((feature, index) => (
                    <li key={index} className="flex items-center">
                      <CheckIcon className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="text-center">
                <div className="bg-white rounded-lg shadow-lg p-6 inline-block">
                  <FileTextIcon className="h-16 w-16 text-blue-600 mx-auto mb-4" />
                  <p className="text-sm text-gray-600">Start building your professional resume today</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-blue-600">
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:py-16 lg:px-8 lg:flex lg:items-center lg:justify-between">
          <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
            <span className="block">Ready to get started?</span>
            <span className="block text-blue-200">Create your resume today.</span>
          </h2>
          <div className="mt-8 flex lg:mt-0 lg:flex-shrink-0">
            <div className="inline-flex rounded-md shadow">
              <Link href="/resume/dashboard">
                <Button size="lg" variant="secondary" className="bg-white text-blue-600 hover:bg-gray-50">
                  Get started for free
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
