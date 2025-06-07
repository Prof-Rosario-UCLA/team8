import ResumeItemType from "@/lib/types/Resume";
import ResumeItemCard from "@/components/resume/ResumeItemCard";
import ResumeSection from "@/components/resume/ResumeSectionCard";

export default function DummyPage() {

  const dummyResumeItem: ResumeItemType = {
    id: 1,
    item_type: "experience",
    title: "Senior Software Engineer",
    organization: "Google",
    location: "Mountain View, CA",
    description: "Led development of scalable web applications using React, TypeScript, and Node.js. Mentored junior developers and implemented CI/CD pipelines that reduced deployment time by 60%.",
    start_date: new Date("2022-01-01"),
    end_date: new Date("2023-12-01"),
  }

  const dummyResumeItems: ResumeItemType[] = [
    {
      ...dummyResumeItem,
      id: 1,
      title: "Senior Software Engineer",
      organization: "Google",
      start_date: new Date("2022-01-01"),
      end_date: new Date("2023-12-01"),
    },
    {
      ...dummyResumeItem,
      id: 2,
      title: "Software Engineer II",
      organization: "Microsoft",
      location: "Seattle, WA",
      start_date: new Date("2020-06-01"),
      end_date: new Date("2021-12-01"),
      description: "Developed Azure cloud services and microservices architecture. Optimized database queries resulting in 40% performance improvement.",
    },
    {
      ...dummyResumeItem,
      id: 3,
      title: "Frontend Developer",
      organization: "Startup Inc",
      location: "San Francisco, CA",
      start_date: new Date("2019-01-01"),
      end_date: new Date("2020-05-01"),
      description: "Built responsive web applications with React and Redux. Collaborated with designers to implement pixel-perfect UIs.",
    },
  ]
  
  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-gray-900">Resume Component Demo</h1>
        
        {/* Key Improvements Section */}
        <div className="mb-8 p-6 bg-blue-50 rounded-lg border border-blue-200">
          <h2 className="text-xl font-semibold mb-4 text-blue-900">✨ Key Improvements</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <h3 className="font-medium text-blue-800 mb-2">🎯 Smart Space Utilization</h3>
              <ul className="text-blue-700 space-y-1 text-xs">
                <li>• Reduced card padding and margins</li>
                <li>• Smarter responsive breakpoints</li>
                <li>• Better text sizing hierarchy</li>
                <li>• Optimized for split-screen layouts</li>
              </ul>
            </div>
            <div>
              <h3 className="font-medium text-blue-800 mb-2">📅 Resume-Optimized Dates</h3>
              <ul className="text-blue-700 space-y-1 text-xs">
                <li>• Month/Year format (Jan 2023)</li>
                <li>• No text overflow issues</li>
                <li>• Compact date picker buttons</li>
                <li>• Professional resume format</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Split Screen Layout Example */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Split Screen Editor Layout</h2>
          <div className="bg-white rounded-lg shadow-lg overflow-hidden">
            <div className="flex min-h-[700px]">
              {/* Left Panel - Editor */}
              <div className="w-1/2 border-r border-gray-200 p-4 overflow-auto bg-gray-50">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-700">📝 Editor Panel</h3>
                  <span className="text-xs text-gray-500 bg-white px-2 py-1 rounded">Compact Mode</span>
                </div>
                <ResumeSection 
                  title="Experience" 
                  resumeItems={dummyResumeItems} 
                  compact={true}
                  className="max-w-full"
                />
              </div>
              
              {/* Right Panel - Preview */}
              <div className="w-1/2 p-6 overflow-auto bg-white">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-700">👁️ Resume Preview</h3>
                  <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">Live Preview</span>
                </div>
                <div className="space-y-4">
                  <div>
                    <h4 className="text-lg font-bold text-gray-900 mb-3">Experience</h4>
                    <div className="space-y-4">
                      {dummyResumeItems.map(item => (
                        <div key={item.id} className="border-l-2 border-blue-200 pl-4">
                          <div className="flex justify-between items-start mb-1">
                            <h5 className="font-semibold text-gray-800">{item.title}</h5>
                            <span className="text-sm text-gray-600">
                              {item.start_date ? new Date(item.start_date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' }) : 'N/A'} - 
                              {item.end_date ? new Date(item.end_date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' }) : 'Present'}
                            </span>
                          </div>
                          <div className="text-sm text-gray-600 mb-2">
                            {item.organization} • {item.location}
                          </div>
                          <p className="text-sm text-gray-700 leading-relaxed">{item.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Responsive Containers Demo */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Responsive Container Examples</h2>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Small Container */}
            <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
              <h3 className="text-sm font-medium mb-3 text-gray-700 flex items-center">
                📱 Small Container (320px)
                <span className="ml-2 text-xs bg-orange-100 text-orange-800 px-2 py-1 rounded">Compact</span>
              </h3>
              <div className="max-w-[320px]">
                <ResumeSection 
                  title="Experience" 
                  resumeItems={dummyResumeItems.slice(0, 1)} 
                  compact={true}
                />
              </div>
            </div>
            
            {/* Medium Container */}
            <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
              <h3 className="text-sm font-medium mb-3 text-gray-700 flex items-center">
                💻 Medium Container (480px)
                <span className="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">Standard</span>
              </h3>
              <div className="max-w-[480px]">
                <ResumeSection 
                  title="Experience" 
                  resumeItems={dummyResumeItems.slice(0, 1)} 
                  compact={false}
                />
              </div>
            </div>
            
            {/* Large Container */}
            <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
              <h3 className="text-sm font-medium mb-3 text-gray-700 flex items-center">
                🖥️ Large Container (640px)
                <span className="ml-2 text-xs bg-green-100 text-green-800 px-2 py-1 rounded">Full</span>
              </h3>
              <div className="max-w-[640px]">
                <ResumeSection 
                  title="Experience" 
                  resumeItems={dummyResumeItems.slice(0, 1)} 
                  compact={false}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Full Width Example */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Full Width Layout</h2>
          <ResumeSection 
            title="Experience" 
            resumeItems={dummyResumeItems} 
            className="max-w-4xl mx-auto"
          />
        </div>

        {/* Technical Details */}
        <div className="mt-12 p-6 bg-gray-100 rounded-lg">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">🛠️ Technical Implementation</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
            <div>
              <h3 className="font-medium text-gray-700 mb-2">Date Picker Improvements</h3>
              <ul className="text-gray-600 space-y-1">
                <li>• <code className="bg-white px-1 rounded">ResumeMonthYearField</code> for month/year only</li>
                <li>• Automatic date formatting (Jan 2023 vs January 2023)</li>
                <li>• Smart truncation to prevent overflow</li>
                <li>• Compact mode with smaller buttons</li>
              </ul>
            </div>
            <div>
              <h3 className="font-medium text-gray-700 mb-2">Layout Optimizations</h3>
              <ul className="text-gray-600 space-y-1">
                <li>• Reduced card padding from 24px to 16px</li>
                <li>• Smart responsive breakpoints (md: instead of lg:)</li>
                <li>• Flexible spacing based on container size</li>
                <li>• Better text hierarchy and sizing</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 