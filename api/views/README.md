# API Routes

This directory contains the Flask Blueprints that define the API routes for the application. Each file typically corresponds to a specific resource or a group of related resources, mapping URL endpoints to controller functions.

- `__init__.py`: Initializes and aggregates all route blueprints.
- `user_routes.py`: Routes for user management (including associated websites).
- `education_routes.py`: Routes for education entries.
- `experience_routes.py`: Routes for experience entries.
- `project_routes.py`: Routes for project entries.
- `skill_routes.py`: Routes for skills.
- `template_routes.py`: Routes for resume templates.
- `resume_routes.py`: Routes for managing resumes, their sections, and the items (education, experience, projects) within them, including customization and overrides.

These routes handle incoming HTTP requests, extract necessary data (from JSON bodies, URL parameters, query strings), call the appropriate controller functions from `api/controllers/`, and then format the controller's response (usually as JSON) with the correct HTTP status code. 

## Detailed Endpoint Documentation: `resume_routes.py`

The `resume_routes.py` blueprint manages all operations related to resumes. This includes CRUD for resumes themselves, management of sections within a resume, and the complex logic of adding, customizing, and removing items (like education, experience, projects) within a resume.

### Core Concepts for Resume Items

A key feature is the **override system** (detailed in `api/controllers/README.md`). When a global item (e.g., a project from your main profile) is added to a resume:
1. It's initially a direct link, showing the global data.
2. You can then customize it *for that resume only*.
3. The backend intelligently stores only the *differences* (overrides) from the global item. This includes:
    - `field_overrides`: For simple text fields (title, dates, description).
    - `ResumeBullet`s: For custom bullet points.
    - `resume_item_skills`: For a custom set of skills.

When an item is updated, the frontend sends the **full desired state** of the item for that resume. The backend then diffs this against the global item to update the overrides.

## API Endpoints for Resume Management

### 1. Overall Resume Structure (`GET /resumes/<uuid:resume_id>`)

*   **Action:** Fetches the complete structure of a specific resume, including its ordered sections and the items within those sections (with overrides applied).
*   **Success Response (200 OK):**
    ```json
    {
      "id": "<resume_uuid>",
      "user_id": "<user_uuid>",
      "title": "My Software Engineering Resume",
      "template_id": "<template_uuid>",
      "created_at": "YYYY-MM-DDTHH:MM:SSZ",
      "updated_at": "YYYY-MM-DDTHH:MM:SSZ",
      "sections": [
        {
          "resume_id": "<resume_uuid>",
          "section_type": "experience", // e.g., "experience", "project", "education"
          "title": "Work Experience",     // User-defined title for this section
          "order_index": 0,
          "items": [
            {
              "resume_id": "<resume_uuid>",
              "item_type": "experience", // Matches the section_type
              "item_id": "<global_experience_id_1>", // ID of the global Experience record
              "order_index": 0, // Order of this item within the "experience" section
              "data": {
                "id": "<global_experience_id_1>",
                "user_id": "<user_uuid>",
                "role": "Senior Developer (Resume Specific Title)",
                "company": "Tech Solutions Inc.",
                // ... all other fields for experience, resolved with overrides ...
              },
              "bullets": [
                "Custom bullet for this resume.",
                "Another tailored bullet point."
              ],
              "skills": [
                {"id": "<skill_uuid_A>", "name": "Custom Skill A", "category": "framework"}
              ]
            }
            // ... more items in this section ...
          ]
        },
        {
          "resume_id": "<resume_uuid>",
          "section_type": "project",
          "title": "Personal Projects",
          "order_index": 1,
          "items": [
            // ... project items ...
          ]
        }
        // ... more sections ...
      ]
    }
    ```

### 2. CRUD for Resumes

*   **`GET /resumes`**: List all resumes (can be filtered by `user_id` query param).
*   **`POST /resumes`**: Create a new resume.
    *   Payload: `{"user_id": "<user_uuid>", "title": "New Resume", "template_id": "<template_uuid_optional>"}`
    *   Response: Serialized new resume.
*   **`PUT /resumes/<uuid:resume_id>`**: Update resume metadata (e.g., title, template).
    *   Payload: `{"title": "Updated Resume Title", "template_id": "<new_template_uuid>"}`
    *   Response: Serialized updated resume.
*   **`DELETE /resumes/<uuid:resume_id>`**: Delete a resume.
    *   Response: `{"message": "Resume deleted successfully"}`

### 3. Managing Resume Sections

Sections are distinct parts of a resume like "Experience," "Education," "Projects." Each section has a `section_type` (which must be one of the `ResumeItemType` enum values like "experience", "project", etc.) and a user-defined `title`. A resume can only have one section of a given `section_type`. The order of these sections is managed separately.

#### a. Create or Update a Section
*   **Endpoint:** `POST /resumes/<uuid:resume_id>/sections`
*   **Action:** Creates a new section in the resume or updates the title of an existing section if one with the given `section_type` already exists.
*   **Payload:**
    ```json
    {
      "section_type": "experience", // e.g., "project", "education". Must be a valid ResumeItemType.
      "title": "Professional Experience",  // User-defined title for this section
      "order_index": 0 // Optional: if not provided, appends to the end. If provided for existing, updates order.
    }
    ```
*   **Success Response (201 Created or 200 OK):** The serialized resume section.
    ```json
    {
      "resume_id": "<resume_uuid>",
      "section_type": "experience",
      "title": "Professional Experience",
      "order_index": 0,
      "items": [] // New sections are initially empty
    }
    ```

#### b. Delete a Section
*   **Endpoint:** `DELETE /resumes/<uuid:resume_id>/sections/<string:section_type_str>`
    *   `section_type_str`: The type of the section to delete (e.g., "experience", "project").
*   **Action:** Removes the specified section and all its `ResumeItem` entries from the resume.
*   **Success Response (200 OK):**
    ```json
    {
      "message": "Resume section 'experience' deleted successfully"
    }
    ```

#### c. Reorder Sections
*   **Endpoint:** `PUT /resumes/<uuid:resume_id>/sections/order`
*   **Action:** Updates the display order of sections within the resume.
*   **Payload:** A list of section type strings in the desired order.
    ```json
    [
      "experience", // This section_type will now have order_index 0
      "project",    // This section_type will now have order_index 1
      "education"   // This section_type will now have order_index 2
      // ... other section types ...
    ]
    ```
*   **Success Response (200 OK):** The full serialized resume with sections in the new order.

### 4. Managing Items within a Resume Section

`ResumeItem` entries link global items (like a specific `Project` or `Experience` record) to a resume, allowing for overrides.

#### a. Add a Global Item to a Resume Section
*   **Endpoint:** `POST /resumes/<uuid:resume_id>/sections/<string:target_section_type_str>/items`
    *   `target_section_type_str`: The type of the section where the item should be added (e.g., "project", "experience"). This also defines the `item_type` of the `ResumeItem` created.
*   **Action:** Adds a reference to a global item into the specified section of the resume. If the section doesn't exist, it's created with a default title.
*   **Payload:**
    ```json
    {
      "global_item_id": "<uuid_of_global_project_or_experience_etc>",
      // Optional:
      // "order_index": 1, // Specific order within the section. Appends if omitted.
      // "section_title": "Custom Title for Auto-Created Section" // Used if section is auto-created
      // "field_overrides": { "title": "Override title for this resume" } // Initial field overrides
    }
    ```
*   **Success Response (201 Created):** The serialized `ResumeItem` detail as it appears in the resume.
    ```json
    {
      "resume_id": "<resume_uuid>",
      "item_type": "project", // Matches target_section_type_str
      "item_id": "<global_project_id>",
      "order_index": 0,
      "data": { /* ... resolved data of the global project, potentially with initial overrides ... */ },
      "bullets": [ /* ... list of bullet strings (initially from global or empty if overridden) ... */ ],
      "skills": [ /* ... list of skill objects (initially from global or empty if overridden) ... */ ]
    }
    ```

#### b. Update/Customize an Item in a Resume
*   **Endpoint:** `PUT /resumes/<uuid:resume_id>/items/<string:item_type_str>/<uuid:global_item_id>`
    *   `item_type_str`: The type of the item/section (e.g., "education", "experience", "project").
    *   `global_item_id`: UUID of the *global* item being customized.
*   **Payload:** The full desired state of the item's content *for this resume*.
    *   The `bullets` field should be a list of strings. Order is determined by the list sequence.
    ```json
    {
      "content": { // The key "content" wraps the data, bullets, and skills
        "data": {
          "title": "Updated Project Title for Resume",
          "desc_long": "A resume-specific description."
          /* ... other overridable fields for this item_type ... */
        },
        "bullets": [
          "Custom bullet point 1 for this resume",
          "Custom bullet point 2, rephrased for impact"
        ],
        "skills": [ // List of skill objects (only 'id' is strictly needed for association)
          { "id": "<skill_uuid_1>" },
          { "id": "<skill_uuid_2>" }
        ]
      }
    }
    ```
*   **Action:** The backend compares the submitted `content` (data fields, bullets, skills) with the global item.
    *   Differences in fields are stored/updated in `ResumeItem.field_overrides`.
    *   If submitted bullets differ from global bullets, existing `ResumeBullet`s for this item are replaced with the new list.
    *   If submitted skills differ from global skills, `resume_item_skills` associations are updated.
    *   If any part (fields, bullets, or skills) is submitted identically to the global version, corresponding overrides are removed.
*   **Success Response (200 OK):** The fully resolved (global data + overrides) and updated resume item.
    ```json
    {
      "resume_id": "<resume_uuid>",
      "item_type": "project",
      "item_id": "<global_item_id>",
      "order_index": 0, // Its current order_index
      "data": { /* ... fully resolved content fields after updates ... */ },
      "bullets": [ /* ... list of bullet strings after updates ... */ ],
      "skills": [ /* ... list of skill objects after updates ... */ ]
    }
    ```

#### c. Remove an Item from a Resume Section
*   **Endpoint:** `DELETE /resumes/<uuid:resume_id>/items/<string:item_type_str>/<uuid:global_item_id>`
    *   `item_type_str`: The type of the item/section (e.g., "experience", "project").
    *   `global_item_id`: UUID of the global item to remove from this resume.
*   **Action:** Removes the `ResumeItem` (and its associated `ResumeBullet`s and skill overrides) from the resume. The global item itself is not deleted.
*   **Success Response (200 OK):**
    ```json
    {
      "message": "Item removed from resume successfully"
    }
    ```

#### d. Reorder Items within a Section
*   **Endpoint:** `PUT /resumes/<uuid:resume_id>/items/order`
*   **Action:** Updates the order of items *within their respective sections*. The payload specifies the new order for items of a particular type.
*   **Payload:**
    ```json
    {
      "item_type": "project", // The type of items being reordered
      "ordered_ids": [ // List of global_item_ids in their new desired order for this section type
        "<global_project_id_3>",
        "<global_project_id_1>",
        "<global_project_id_2>"
      ]
    }
    ```
*   **Success Response (200 OK):** The full serialized resume with items in the new order.

### Error Handling

Common error responses include:
*   **400 Bad Request:** For invalid payload format, missing required fields, or validation errors (e.g., invalid UUID, invalid `item_type`).
     ```json
     { "error": "Request body must be JSON" }
     ```
     ```json
     { "error": "Missing 'user_id' in request body" }
     ```
     ```json
     { "error": "Invalid item_type: unknown_type" }
     ```
*   **404 Not Found:** When a specified resource (resume, section, global item) doesn't exist.
     ```json
     { "error": "Resume with ID <uuid> not found." }
     ```
*   **500 Internal Server Error:** For unexpected errors or database issues.
     ```json
     { "error": "An unexpected error occurred" }
     ```
     ```json
     { "error": "Database error: <specific_sqlalchemy_error_details>" }
     ``` 