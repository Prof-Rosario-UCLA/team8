# prolio
CS 144: Web Applications. Repository for Prolio, an interactive resume content management system!

## About

Resume creator app that is CV focused.

That is the user flow is that they first enter ALL of their work experience, projects, etc (mostly tailored to CS majors but not strictly) and then can use this to assmeble a resume that points to these data.

Then a resume is kind of like a particular "view"/subset of the user's entire experience.

I say view, because the resume can "override" something to custom tailor to a JD whilst not tampering with the original data if it's an edit only for this particular resume.

When creating a resume, a user can select a set of preset (for now at least) LaTex resume templates to bake out their resume.

Thus a "resume" is currently a data structure that carries information of what CV content is included, and how it is ordered but the rendering of the resume visually is determined by the Latex template. A "resume" is then part data from the user cv, and a visual format decided by the associated template.

Within the resume editor, the user should be able to drag and drop broader sections on the resume (Skills, Projects, Experiences)
they can also reorder content within those fields.

They can also select a section and pull up their collection of entries (e.g. their projects for Project section) in a sidebar and drag and drop it into the resume form.

The resume editor view is a side by side layout with a editable form on the left, and the latex render preview on the right. Whenever a side menu is needed (e.g. to show existing projects to drag in) it can popover the latex render when appropriate to the context.

The specific details on the entries can also be editted, by default these will edit the "view" specific to the resume but can also optionally be written back to the underlying global entry for the user across resumes with a button press to commit it to all. 

Editor mode additional features:
Filtering down projects by tags and categories
Pinecone semantic search if we eventually have a pinecone db that stores vector embeddings of the entire entry (project, experience) and maps to the uuid in the SQL db to semantically search for appropriate content to a db or a user's wishes

Future stretch goals.

LLM assistant integration:
- a side chat panel 
- natural language resume building, can parse a JD into relevant queries into the vector db and fetch and even automatically assemble a start resume for the JD
- offer overall feedback on the entire resume document with context of the user's entire CV 
- probably need to add "formatters" to serialize the JSON structured data into natural language for LLM context
- can offer rewording in an inline chat for bullet points, fields etc 

## Monorepo organization

This is a monorepo for a resume content management system.

Next.js for server-side rendering under `web`, api is proxied to `/api`, the Flask backend.

## Setup Flask API
```
conda create -n prolio python=3.10
cd api
pip install -r requirements.txt
```

Create `.flaskenv` under `api/`
```
FLASK_APP=app
FLASK_DEBUG=1  
DATABASE_URL=<DB_URL_HERE>
```

