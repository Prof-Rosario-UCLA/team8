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

### Resume Management

#### 1. Get All Resumes
*   **Endpoint:** `GET /resumes`
*   **Query Parameters:**
    *   `user_id` (optional, UUID): Filters resumes by the specified user.
*   **Action:** Retrieves a list of all resumes, or resumes filtered by `user_id`.
*   **Success Response (200 OK):**
    ```json
    [
      {
        "id": "<resume_uuid>",
        "user_id": "<user_uuid>",
        "title": "Software Engineer Resume",
        "template_id": "<template_uuid>",
        "created_at": "iso_timestamp",
        "updated_at": "iso_timestamp"
        // ... other resume fields ...
      }
      // ... more resumes ...
    ]
    ```

#### 2. Create a New Resume
*   **Endpoint:** `POST /resumes`
*   **Payload:**
    ```json
    {
      "user_id": "<user_uuid>",
      "title": "My New Resume",
      "template_id": "<template_uuid>" // Optional
    }
    ```
*   **Action:** Creates a new resume record.
*   **Success Response (201 Created):** The newly created resume object.
    ```json
    {
      "id": "<new_resume_uuid>",
      "user_id": "<user_uuid>",
      "title": "My New Resume",
      "template_id": "<template_uuid>",
      // ... other fields ...
    }
    ```

#### 3. Get a Specific Resume
*   **Endpoint:** `GET /resumes/<uuid:resume_id>`
*   **Action:** Retrieves a specific resume by its ID, including its sections and fully resolved items (global data + overrides).
*   **Success Response (200 OK):** Detailed resume object.
    ```json
    {
      "id": "<resume_uuid>",
      "title": "Data Scientist Resume",
      "user_id": "<user_uuid>",
      "template_id": "<template_uuid>",
      // ... other resume fields ...
      "sections": [
        {
          "id": "<section_uuid>",
          "title": "Experience",
          "order_index": 0,
          "items": [
            {
              "resume_item_id": "<resume_item_uuid>", // ID of the ResumeItem link
              "item_id": "<global_experience_id>",    // ID of the global Experience record
              "item_type": "experience",
              "order_index": 0,
              "content": { // Fully resolved content
                "title": "Senior Developer (Resume Specific Title)",
                "company": "Tech Solutions Inc.",
                "date_start": "2020-01-01",
                // ... all other fields for experience, resolved with overrides ...
                "bullets": [
                  {"content": "Custom bullet for this resume.", "order_index": 0}
                ],
                "skills": [
                  {"id": "<skill_uuid>", "name": "Custom Skill Set"}
                ]
              }
            }
            // ... more items in section ...
          ]
        }
        // ... more sections ...
      ]
    }
    ```

#### 4. Update Resume Metadata
*   **Endpoint:** `PUT /resumes/<uuid:resume_id>`
*   **Payload:** (Fields are optional; only provided fields will be updated)
    ```json
    {
      "title": "Updated Resume Title",
      "template_id": "<new_template_uuid>"
    }
    ```
*   **Action:** Updates the metadata (e.g., title, template) of a specific resume.
*   **Success Response (200 OK):** The updated resume object.

#### 5. Delete a Resume
*   **Endpoint:** `DELETE /resumes/<uuid:resume_id>`
*   **Action:** Deletes a specific resume and all its associated data (sections, resume items, overrides) due to cascading deletes in the database.
*   **Success Response (200 OK):**
    ```json
    {
      "message": "Resume deleted successfully"
    }
    ```

### Resume Section Management

#### 1. Add a New Section to a Resume
*   **Endpoint:** `POST /resumes/<uuid:resume_id>/sections`
*   **Payload:**
    ```json
    {
      "title": "New Section Title"
      // "layout_type": "optional_layout_identifier" // If supported
    }
    ```
*   **Action:** Creates a new section within the specified resume. The `order_index` is typically assigned automatically.
*   **Success Response (201 Created):** The newly created section object.
    ```json
    {
      "id": "<new_section_uuid>",
      "resume_id": "<resume_uuid>",
      "title": "New Section Title",
      "order_index": 2 // Example
    }
    ```

#### 2. Remove a Section from a Resume
*   **Endpoint:** `DELETE /resumes/<uuid:resume_id>/sections/<uuid:section_id>`
*   **Action:** Removes a section from a resume.
    *   **Internal Note:** The controller logic needs to define how `ResumeItem`s within this section are handled (e.g., cascade delete, disassociate, prevent deletion if items exist). Currently, it assumes cascade or that items are handled/disallowed at a higher level.
*   **Success Response (200 OK):**
    ```json
    {
      "message": "Section removed successfully"
    }
    ```

#### 3. Update the Order of Sections within a Resume
*   **Endpoint:** `PUT /resumes/<uuid:resume_id>/sections/order`
*   **Payload:** A list defining the new order of sections.
    ```json
    [
      { "id": "<section_id_1>", "order_index": 0 },
      { "id": "<section_id_2>", "order_index": 1 }
      // ... more sections with their new order_index ...
    ]
    ```
*   **Action:** Updates the `order_index` for each `ResumeSection` record associated with the resume.
*   **Success Response (200 OK):** The updated resume object with reordered sections.

### Resume Item Management

These endpoints manage individual items (Education, Experience, Project, etc.) within a resume.

#### 1. Add a Global Item to a Resume
*   **Endpoint:** `POST /resumes/<uuid:resume_id>/items`
*   **Payload:**
    ```json
    {
      "item_type": "project", // e.g., "education", "experience", "project"
      "item_id": "<global_project_id>", // UUID of the global item
      "section_id": "<section_uuid>" // UUID of the resume section to add this item to
      // "order_index": 0 // Optional: if not provided, item is added to the end
    }
    ```
*   **Action:** Creates a `ResumeItem` record, linking the specified global item to the resume and placing it in the given section. Initially, this item has no overrides.
*   **Success Response (201 Created):** Details of the newly created `ResumeItem` link, often including the resolved content of the item.
    ```json
    {
      "resume_item_id": "<new_resume_item_uuid>",
      "item_id": "<global_project_id>",
      "item_type": "project",
      "section_id": "<section_uuid>",
      "order_index": 0,
      "content": { /* ... resolved content of the global project ... */ }
    }
    ```

#### 2. Update a Specific Item in a Resume (Override System)
*   **Endpoint:** `PUT /resumes/<uuid:resume_id>/items/<item_type_str>/<uuid:item_id>`
    *   `item_type_str`: e.g., "education", "experience", "project"
    *   `item_id`: UUID of the *global* item being customized.
*   **Payload:** The **full desired state** of the item's content *for this resume*. The structure must be `{"content": {"data": {...}}}`.
    ```json
    {
      "content": {
        "data": {
          // --- Common fields ---
          "title": "Resume-Specific Title for Project X", // Overridden
          "organization": "Global Org Name", // Not overridden, matches global
          "location": "New Location for Resume", // Overridden
          "date_start": "2022-01-01",
          "date_end": "2022-12-31",
          "desc_short": "Short description for resume.", // Overridden
          "desc_long": "A very detailed long description tailored for this specific resume application, highlighting different aspects than the global version.", // Overridden
          
          // --- Bullets (Full list for this resume) ---
          "bullets": [
            { "content": "Custom bullet point 1 for this resume.", "order_index": 0 },
            { "content": "Custom bullet point 2, different from global.", "order_index": 1 }
          ],
          
          // --- Skills (Full list of skill UUIDs for this resume) ---
          "skills": [
            "<skill_uuid_A>", // Skill A is relevant for this resume
            "<skill_uuid_C>"  // Skill C is also relevant
            // Global item might have had Skill A and Skill B. Skill B is omitted here.
          ]
          // ... any other fields relevant to the item_type ...
        }
      }
    }
    ```
*   **Action (Internal):**
    1.  Retrieves the `ResumeItem` linking `resume_id` and `item_id` (global item ID).
    2.  Retrieves the corresponding global item (e.g., `Project` with `item_id`).
    3.  **Diffs Field Overrides:** Compares each field in the payload's `data` (e.g., `title`, `desc_long`) with the global item's fields.
        *   If a submitted field differs, it's added/updated in `ResumeItem.field_overrides` (JSONB).
        *   If a submitted field matches the global item's value (and was previously overridden), it's removed from `field_overrides`.
    4.  **Diffs Bullet Points:** Compares the submitted `bullets` list (content and order) with the global item's bullets.
        *   If different, existing `ResumeBullet`s for this `ResumeItem` are deleted, and new ones are created from the payload.
        *   If identical to global, `ResumeBullet`s are deleted (reverting to global).
    5.  **Diffs Skills:** Compares the submitted `skills` list (of UUIDs) with the global item's skills.
        *   If different, existing `resume_item_skills` associations for this `ResumeItem` are cleared, and new ones are created from the payload.
        *   If identical to global, `resume_item_skills` associations are cleared (reverting to global).
*   **Success Response (200 OK):** The updated `ResumeItem` details, reflecting the newly applied overrides and resolved content.
    ```json
    {
      "resume_item_id": "<resume_item_uuid>",
      "item_id": "<global_item_id>",
      "item_type": "project",
      // ... other fields ...
      "content": { /* ... fully resolved content after updates ... */ }
    }
    ```

#### 3. Remove an Item from a Resume
*   **Endpoint:** `DELETE /resumes/<uuid:resume_id>/items/<item_type_str>/<uuid:item_id>`
     *   `item_type_str`: e.g., "education", "experience", "project"
     *   `item_id`: UUID of the *global* item.
*   **Action:** Deletes the `ResumeItem` record. This also removes associated `ResumeBullet`s and `resume_item_skills` entries due to cascading deletes. The global item itself is unaffected.
*   **Success Response (200 OK):**
     ```json
     {
       "message": "Item removed from resume successfully"
     }
     ```

#### 4. Reorder Items within a Resume
*   **Endpoint:** `PUT /resumes/<uuid:resume_id>/items/order`
*   **Payload:** A list defining the new order of items. Each object in the list identifies an item and its new `order_index` and potentially new `section_id`.
     ```json
     {
       "items": [
         {
           "item_type": "project", // Type of the global item
           "item_id": "<global_project_id_1>", // UUID of the global item
           "order_index": 0,
           "section_id": "<section_uuid_A>" // Item moved to or within this section
         },
         {
           "item_type": "experience",
           "item_id": "<global_experience_id_1>",
           "order_index": 1,
           "section_id": "<section_uuid_A>"
         },
         {
           "item_type": "education",
           "item_id": "<global_education_id_1>",
           "order_index": 0, // Order index is per section
           "section_id": "<section_uuid_B>"
         }
         // ... more items ...
       ]
     }
     ```
*   **Action:** Updates the `order_index` and `section_id` on the `ResumeItem` records. The backend needs to find the correct `ResumeItem` based on `resume_id`, `item_type`, and `item_id`.
*   **Success Response (200 OK):** The updated resume object or a success message.
     ```json
     {
       "id": "<resume_uuid>",
       "title": "My Reordered Resume",
       // ... full resume structure with reordered items ...
     }
     ```

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