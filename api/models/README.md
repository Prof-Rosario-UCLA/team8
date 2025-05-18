---

# Overview 🏗️

This project stores every user’s **master profile** (education, experience, projects, skills) and lets them build any number of **resume views** on top of that data with **zero duplication**.
Two core design ideas drive the schema:

1. **Reference + Overlay**

   * Global tables (`projects`, `experiences`, `bullet_points`, …) hold canonical data.
   * A résumé contains only lightweight “diff rows” (`resume_items`, `resume_bullets`) that override or reorder the global data **for that résumé alone**.

2. **Strict structure for LaTeX**
   Each field in the LaTeX template maps directly to a column, so PDF generation is deterministic and easy to test.

---

# Entity Groups

| Group                 | Key Tables                                                         | Purpose                                                                                       |
| --------------------- | ------------------------------------------------------------------ | --------------------------------------------------------------------------------------------- |
| **User profile**      | `users`, `websites`                                                | Authentication-agnostic account row plus outbound links.                                      |
| **Canonical content** | `educations`, `experiences`, `projects`, `skills`, `bullet_points` | One-time entry by user.  Drives AI retrieval and is the single source of truth.               |
| **Skills mapping**    | `experience_skills`, `project_skills`                              | Normalised many-to-many for faceted search (by tech stack, etc.).                             |
| **Template & résumé** | `templates`, `resumes`, `resume_sections`                          | Template = external LaTeX/GCS URI.  Résumé row tracks which template and holds section order. |
| **Overlay layer**     | `resume_items`, `resume_bullets`                                   | Per-résumé diff: item inclusion, local description overrides, reordered / rewritten bullets.  |

---

# Edit Paths

| UI action                                       | DB write target                                                       | Notes                                                      |
| ----------------------------------------------- | --------------------------------------------------------------------- | ---------------------------------------------------------- |
| **Update profile** (“edit everywhere”)          | `projects`, `experiences`, `bullet_points`, …                         | Changes propagate to all future résumés unless overridden. |
| **Edit inside one résumé**                      | `resume_items.custom_desc` or `resume_bullets`                        | Leaves global rows untouched.                              |
| **Re-order items** (drag card)                  | swap `order_index` in `resume_items`                                  |                                                            |
| **Re-order top sections** (drag section header) | swap `order_index` in `resume_sections`                               |                                                            |
| **Delete résumé**                               | `ON DELETE CASCADE` removes its overlay rows only; global data stays. |                                                            |

---

# Bullet-Point Integrity

`bullet_points` are polymorphic: `(parent_type, parent_id)` may point to `educations`, `experiences`, `projects`, `publications`, or `awards`.

### Option A (default in `base.py`)

*PostgreSQL constraint trigger* (`bullet_parent_check`) rejects rows whose `parent_id` does not exist.
Pros: hard guarantee ✧ Cons: requires raw SQL and is Postgres-only.

### Option B (all-Python)

Comment out the trigger DDL and enable the provided `before_flush` listener (see code sample in the README footer).
Pros: no SQL, portable ✧ Cons: relies on application code for correctness.

Pick one approach and document it in your migration guide.

---

# Quick Reference: Table Key Columns

| Table               | PK / composite PK                 | Main FKs                                     |
| ------------------- | --------------------------------- | -------------------------------------------- |
| `users`             | `id`                              | –                                            |
| `educations`        | `id`                              | `user_id → users`                            |
| `experiences`       | `id`                              | `user_id → users`                            |
| `projects`          | `id`                              | `user_id → users`                            |
| `bullet_points`     | `id`                              | polymorphic via trigger / listener           |
| `skills`            | `id`                              | –                                            |
| `experience_skills` | `(experience_id, skill_id)`       | → `experiences`, `skills`                    |
| `project_skills`    | `(project_id, skill_id)`          | → `projects`, `skills`                       |
| `templates`         | `id`                              | –                                            |
| `resumes`           | `id`                              | `user_id → users`, `template_id → templates` |
| `resume_sections`   | `(resume_id, section_type)`       | `resume_id → resumes`                        |
| `resume_items`      | `(resume_id, item_type, item_id)` | `resume_id → resumes`                        |
| `resume_bullets`    | composite FK to `resume_items`    | – (inherits cascade)                         |

---

# How to Add a New Content Type

1. Create a new global table (e.g., `certifications`).
2. Add the enum value to `ParentType` and `ResumeItemType`.
3. Add a bullet relationship helper in the new model.
4. Update the trigger / listener mapping for bullet validation.
5. Update the LaTeX template and front-end section registry.

---

# Before-Flush Listener (if you drop the trigger)

```python
from sqlalchemy.orm import Session
from sqlalchemy import event

PARENT_LOOKUP = {
    "education":   Education,
    "experience":  Experience,
    "project":     Project,
    "publication": Publication,  # when implemented
    "award":       Award         # when implemented
}

@event.listens_for(Session, "before_flush")
def validate_bulletpoints(session, *_):
    for obj in session.new.union(session.dirty):
        if isinstance(obj, BulletPoint):
            model = PARENT_LOOKUP[obj.parent_type.value]
            if session.get(model, obj.parent_id) is None:
                raise ValueError("Invalid bullet parent")
```

---

# Migration 

probably will do Alembic?