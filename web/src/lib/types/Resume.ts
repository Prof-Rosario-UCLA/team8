
/**
Ex. 
{
    "id": 3,
    "item_type": "Experience",
    "title": "Software Engineer Intern",
    "organization": "Macrosoft",
    "start_date": 
    "end_date": 
    "location": "New York City, NY",
    "description": "Worked on the Macrodata Refinement Team.\nBuild data cleaning pipelines for data wrangling and cleaning used by data engineers within Macrosoft to serve cutting-edge healthcare technology customers.\nIncorperated Large-Language Models (LLMs) agents to help automate the data cleaning process using unsupervised machine learning."
},
  
 */
export interface ResumeItemType {
  id: number;
  item_type: string;
  title: string;
  organization: string;
  start_date: Date | null;
  end_date: Date | null;
  location: string;
  description: string;
}

export interface ResumeSectionType {
  id: string
  name: string
  type: 'education' | 'experience' | 'projects' | 'skills'
  items: ResumeItemType[] // Array position = display order
}

export interface ResumeType {
  id: string
  template: number
  name: string
  resume_name: string  // this is the name of the resume, not the user's name
  phone: string
  email: string
  linkedin: string
  github: string
  website: string
  sections: ResumeSectionType[] // Array position = display order
  updated_at: Date
}
