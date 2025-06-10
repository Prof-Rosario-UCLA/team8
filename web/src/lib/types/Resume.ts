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
  id: number | string;
  title: string;
  organization: string;
  start_date: Date | null;
  end_date: Date | null;
  location: string;
  description: string;
}

export interface ResumeSectionType {
  id: number | string;
  name: string
  section_type: ResumeSectionItemType
  items: ResumeItemType[] // Array position = display order
}

export enum ResumeSectionItemType {
  Education = "education",
  Experience = "experience",
  Projects = "project",
  Skills = "skill",
}

export const ORDERED_SECTION_TYPES = [
  ResumeSectionItemType.Education,
  ResumeSectionItemType.Experience,
  ResumeSectionItemType.Projects,
  ResumeSectionItemType.Skills,
];

export const SECTION_TYPE_DISPLAY_NAME_MAP: Record<ResumeSectionItemType, string> = {
  [ResumeSectionItemType.Education]: "Education",
  [ResumeSectionItemType.Experience]: "Experience",
  [ResumeSectionItemType.Projects]: "Projects",
  [ResumeSectionItemType.Skills]: "Technical Skills",
};

export const ALL_SECTION_TYPES = [
  ResumeSectionItemType.Education,
  ResumeSectionItemType.Experience,
  ResumeSectionItemType.Projects,
  ResumeSectionItemType.Skills,
]

export interface ResumeType {
  id: number;
  template_id: number
  name: string // The title of the resume document, e.g. "Software Engineer Resume"
  resume_name: string  // The person's name on the resume, e.g. "John Doe"
  phone: string
  email: string
  linkedin: string
  github: string
  website: string
  sections: ResumeSectionType[] // Array position = display order
  updated_at: Date | null
}

// These types are for the payload sent to the backend when creating/updating a resume.
// Temporary string IDs are replaced with null.
export type ResumeItemPayload = Omit<ResumeItemType, 'id'> & { id: number | null };

export type ResumeSectionPayload = Omit<ResumeSectionType, 'id' | 'items'> & {
  id: number | null;
  items: ResumeItemPayload[];
};

export type ResumeUpdatePayload = Omit<ResumeType, 'sections'> & {
  sections: ResumeSectionPayload[];
};
