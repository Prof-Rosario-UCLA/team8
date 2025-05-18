All the business logic for actually working with the models.

- `user_controller.py`
- `website_controller.py` (Manages website data, often called by `user_controller.py`)
- `education_controller.py`
- `experience_controller.py`
- `project_controller.py`
- `skill_controller.py`
- `template_controller.py`
- `resume_controller.py`

# Resume Customization: The Override System

This document outlines the architecture and business logic behind customizing resume items (Education, Experience, Projects) within a specific resume. The core principle is that users can pull "global" items into a resume and then tailor them for that resume's specific context without altering the original global item.

## Core Concepts

1.  **Global Items vs. Resume Items:**
    *   **Global Items** (e.g., `Education`, `Experience`, `Project` models): These are the canonical records of a user's experiences, projects, etc. They serve as the single source of truth for these entities.
    *   **Resume Items** (`ResumeItem` model): This model links a global item to a specific resume. It's the cornerstone of customization, holding references to the global item and storing any overrides.

2.  **Frontend Responsibility:**
    *   When a user edits a resume item, the frontend works with a serialized JSON representation of that item. This representation already reflects the current state (global data + any active overrides).
    *   Upon saving changes to a resume item, the frontend sends the **entire, current JSON state** of that item (including its `item_id` which links to the global item, and `resume_item_id` which is the ID of the `ResumeItem` record itself) to the backend.
    *   The frontend **does not** track or send diffs. It sends the complete desired state.

3.  **Backend Responsibility (The `update_resume_item` Endpoint):**
    *   The primary endpoint for handling edits to a specific item within a resume is `PUT /resumes/<resume_id>/items/<item_type_str>/<item_id>`.
    *   When this endpoint receives the full JSON for a resume item, the backend performs the following:
        *   **Diffing:** It compares the received data against the corresponding global item (e.g., the `Project` record linked by `item_id`).
        *   **Field Overrides (`ResumeItem.field_overrides` - JSONB):**
            *   For simple fields (e.g., title, dates, company, role, `desc_long`), the backend identifies which submitted fields *differ* from their counterparts in the global item.
            *   Only these differing fields are stored as key-value pairs in the `field_overrides` JSONB column of the `ResumeItem`.
            *   If a user changes an overridden field *back to its original global value*, the backend removes that specific key from the `field_overrides` JSONB. This ensures `field_overrides` only contains active deviations.
        *   **Bullet Point Overrides (`ResumeBullet` Table):**
            *   The submitted list of bullet strings (where order is determined by the list index) is compared to the global item's bullets.
            *   If they differ, any existing `ResumeBullet` records for this `ResumeItem` are deleted, and new `ResumeBullet` records are created to store the *entire submitted list of bullet strings*, with their order preserved.
            *   If the submitted bullet list becomes identical to the global item's bullets, all `ResumeBullet` records for this `ResumeItem` are deleted, effectively reverting to the global bullets.
        *   **Skill Overrides (`resume_item_skills` Association Table):**
            *   The submitted list of skill IDs is compared to the skills associated with the global item.
            *   If they differ, existing entries in the `resume_item_skills` table for this `ResumeItem` are removed, and new entries are created to link the `ResumeItem` to the *entire submitted list of skills*.
            *   If the submitted skill list becomes identical to the global item's skills, all `resume_item_skills` entries for this `ResumeItem` are removed, reverting to the global skills.

4.  **Serialization (Fetching Resume Data):**
    *   When a resume is fetched (e.g., via `GET /resumes/<resume_id>`), the backend serializes each `ResumeItem`.
    *   For each item, it starts with the data from the corresponding global item.
    *   It then applies any values found in `ResumeItem.field_overrides`.
    *   If `ResumeBullet` records exist for the `ResumeItem`, their content strings are used (ordered by `order_index`); otherwise, the global item's bullet content strings are used (ordered by `order_index`). The `bullets` field in the serialized output will be a list of these strings.
    *   If skill associations exist in `resume_item_skills` for the `ResumeItem`, those are used; otherwise, the global item's skills are used.
    *   The `desc_long` field is the primary description field. The frontend can implement fallback logic (e.g., using `title` for projects if `desc_long` is empty) if needed for display.

## Key API Endpoints & Operations

*   **Adding an Item to a Resume:**
    *   `POST /resumes/<resume_id>/items`
    *   Payload: `{ "item_type": "project", "item_id": "<global_project_id>", "section_id": "<section_id>" }`
    *   Action: Creates a new `ResumeItem` record linking the global item to the resume. Initially, this `ResumeItem` has no overrides (`field_overrides` is empty/null, no `ResumeBullet`s, no `resume_item_skills`).

*   **Updating a Specific Item in a Resume:**
    *   `PUT /resumes/<resume_id>/items/<item_type_str>/<global_item_id>`
    *   Payload: The full JSON representation of the `ResumeItem` as the user currently sees it.
        *   The `content.bullets` field should be a list of strings, e.g., `["Bullet point 1", "Bullet point 2"]`.
        *   Example: `{"content": {"data": {"title": "Updated Title"}, "bullets": ["New bullet 1", "New bullet 2"], "skills": [{"id": "skill_uuid"}]}}`
    *   Action: Backend performs diffing and updates `field_overrides`, `ResumeBullet`s, and `resume_item_skills` as described above.

*   **Removing an Item from a Resume:**
    *   `DELETE /resumes/<resume_id>/items/<item_type_str>/<global_item_id>`
    *   Action: Deletes the `ResumeItem` record and, due to cascading deletes, its associated `ResumeBullet`s and `resume_item_skills` entries.

*   **Reordering Items within a Resume:**
    *   `PUT /resumes/<resume_id>/items/order`
    *   Payload: A list defining the new order of items, e.g., `[{ "item_type": "project", "item_id": "<global_id_1>", "order_index": 0, "section_id": "<new_section_id_if_moved>" }, ...]`
    *   Action: Updates the `order_index` and `section_id` on the `ResumeItem` records.

*   **Reordering Sections within a Resume:**
    *   `PUT /resumes/<resume_id>/sections/order`
    *   Payload: A list defining the new order of sections, e.g., `[{ "id": "<section_id_1>", "order_index": 0 }, ...]` or simply `["<section_id_1>", "<section_id_2>", ...]`
    *   Action: Updates the `order_index` on the `ResumeSection` records.

## Data Flow Example: Editing a Project's Title in a Resume

1.  User loads a resume. Frontend fetches and displays a project item. Its title is "Global Project Title" (from the global `Project` record).
2.  User edits the title within the resume context to "Resume-Specific Project Title".
3.  User saves. Frontend sends the entire project item JSON, including `{"title": "Resume-Specific Project Title", ...}` to `PUT /resumes/.../items/.../<project_id>`.
4.  Backend receives this. It fetches the global `Project` record, which has `title: "Global Project Title"`.
5.  Backend compares: `"Resume-Specific Project Title"` (submitted) != `"Global Project Title"` (global).
6.  Backend updates the `ResumeItem.field_overrides` to include/update `{"title": "Resume-Specific Project Title"}`.
7.  Later, user edits the title again, changing it back to "Global Project Title".
8.  Frontend sends `{"title": "Global Project Title", ...}`.
9.  Backend compares: `"Global Project Title"` (submitted) == `"Global Project Title"` (global).
10. Backend *removes* the `"title"` key from `ResumeItem.field_overrides`. The item now effectively uses the global title again.

This system provides flexibility for resume customization while maintaining a clear separation between global data and resume-specific overrides.