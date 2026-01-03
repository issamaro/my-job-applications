# UX Design: My Job Applications (Unified View)

**Date:** 2026-01-03
**Status:** Draft

---

## 1. Before & After

### Before (Current - Broken)

```
+-----------------------------------------------------------+
|                    Resume Generator Page                   |
+-----------------------------------------------------------+
|                                                           |
|  [Job Description Input Area]                             |
|  [Generate Button]                                        |
|                                                           |
+-- Saved Job Descriptions --------------------------- [-] -+
|   +-- Job Item ------------------------------------+      |
|   | Untitled Job                           Edit Del|      |
|   | We are looking for a software developer...     |      |
|   | Jan 3, 2026 · 1 resume  <-- NOT CLICKABLE      |      |
|   +------------------------------------------------+      |
+-----------------------------------------------------------+
                          ^
                          | User: "Where's my resume?"
                          v
+-- History ------------------------------------------ [-] -+
|   Software Developer · Odoo · Match: 72%          Delete  |
|   Jan 3, 2026                                             |
+-----------------------------------------------------------+
    ^
    | User: "Is this the same job? Different name..."
```

### After (Fixed)

```
+-----------------------------------------------------------+
|                    Resume Generator Page                   |
+-----------------------------------------------------------+
|                                                           |
|  [Job Description Input Area]                             |
|  [Generate Button]                                        |
|                                                           |
+-- My Job Applications ------------------------------ [-] -+
|                                                           |
|   +-- Software Developer at Odoo --------- [^] ---+       |
|   | We are looking for a software developer...    |       |
|   | Jan 3, 2026 · 1 resume                        |       |
|   +-----------------------------------------------+       |
|   |   -> Resume · Jan 3, 2026 · 72%       Delete  |       |
|   +-----------------------------------------------+       |
|                                                           |
|   +-- Product Manager at StartupXYZ ------ [v] ---+       |
|   | Seeking a product manager to lead...          |       |
|   | Jan 2, 2026 · 2 resumes                       |       |
|   +-----------------------------------------------+       |
|                                                           |
+-----------------------------------------------------------+

User: "One section. Job -> Resumes. Makes sense."
```

---

## 2. User Journeys

### Journey A: View Recent Work

| Step | Location | User Sees | User Does | Feedback |
|------|----------|-----------|-----------|----------|
| 1 | Resume Generator | "My Job Applications" section | Scrolls down | Jobs listed, most recent first |
| 2 | Job list | First job EXPANDED with resumes | Sees resumes immediately | Match scores visible |
| 3 | Resume item | Resume with date + score | Clicks resume | Resume loads in preview panel |

### Journey B: Find Older Job's Resume

| Step | Location | User Sees | User Does | Feedback |
|------|----------|-----------|-----------|----------|
| 1 | Job list | Collapsed job showing "2 resumes" | Clicks [v] toggle | Loading spinner briefly |
| 2 | Expanded job | List of 2 resumes | Compares dates + scores | Newest first |
| 3 | Resume item | Resume they want | Clicks it | Resume loads in preview |

### Journey C: Generate from Existing Job

| Step | Location | User Sees | User Does | Feedback |
|------|----------|-----------|-----------|----------|
| 1 | Job item | "Software Developer at Odoo" title | Clicks job content | JD loads in editor |
| 2 | Editor | JD text populated, editing indicator | Edits text if needed | "Editing: Software Developer at Odoo" |
| 3 | Editor | Generate button | Clicks "Generate Resume" | Loading state |
| 4 | Preview | Generated resume | Views result | Match score shown |
| 5 | Job list | Same job now shows "2 resumes" | Expands to verify | New resume at top |

### Journey D: Delete a Resume

| Step | Location | User Sees | User Does | Feedback |
|------|----------|-----------|-----------|----------|
| 1 | Expanded job | Resume with Delete link | Clicks Delete | Confirm dialog appears |
| 2 | Dialog | "Delete Resume?" message | Clicks Confirm | Dialog closes |
| 3 | Job list | Resume removed, count updated | Continues | "2 resumes" -> "1 resume" |

---

## 3. UI States

### 3.1 Section States

| State | Condition | Visual |
|-------|-----------|--------|
| **Empty** | No saved job descriptions | "No job applications yet. Paste a job description above to get started." |
| **Loading** | Initial fetch in progress | 3 skeleton loaders |
| **Loaded** | Jobs available | Job list, first expanded |
| **Error** | Fetch failed | "Could not load job applications. Please refresh the page." |

### 3.2 Job Item States

| State | Condition | Visual |
|-------|-----------|--------|
| **Collapsed (has resumes)** | resume_count > 0, not expanded | [v] toggle visible |
| **Collapsed (no resumes)** | resume_count = 0 | No toggle, "0 resumes" as text |
| **Expanding** | Fetching resumes | Spinner in toggle area |
| **Expanded** | Resumes loaded and visible | [^] toggle, resume list below |
| **Selected** | Loaded in editor | Blue left border highlight |

### 3.3 Auto-expand Rule

```
On page load:
  jobs[0] (most recent): EXPANDED by default
  jobs[1..n]: COLLAPSED

On user toggle:
  - Click [v]: Expand that job, fetch resumes
  - Click [^]: Collapse that job
  - Multiple jobs CAN be expanded simultaneously
```

---

## 4. Component Specifications

### 4.1 My Job Applications Section

```
+-- My Job Applications ------------------------------ [-] -+
|                                                           |
|   [JobApplicationItem - expanded]                         |
|   [JobApplicationItem - collapsed]                        |
|   [JobApplicationItem - collapsed]                        |
|                                                           |
+-----------------------------------------------------------+
```

### 4.2 Job Item - Expanded (Has Resumes)

```
+---------------------------------------------------------------+
|# Software Developer at Odoo                       Edit  Delete |
|  We are looking for a software developer to join our team...   |
|  Jan 3, 2026   1 resume  [^]                                   |
+----------------------------------------------------------------+
|    -> Resume · Jan 3, 2026 · Match: 72%                Delete  |
+----------------------------------------------------------------+
 ^                                                          ^
 | Blue border if currently loaded in editor                |
                                                        Delete link
```

### 4.3 Job Item - Collapsed (Has Resumes)

```
+---------------------------------------------------------------+
|  Product Manager at StartupXYZ                    Edit  Delete |
|  Seeking a product manager to lead our mobile product team...  |
|  Jan 2, 2026   2 resumes  [v]                                  |
+---------------------------------------------------------------+
                            ^
                            | Click to expand
```

### 4.4 Job Item - No Resumes (No Toggle)

```
+---------------------------------------------------------------+
|  Untitled Job                                     Edit  Delete |
|  Looking for a creative designer to help rebrand our...        |
|  Jan 1, 2026   0 resumes                                       |
+---------------------------------------------------------------+
                        ^
                        | No toggle - nothing to expand
```

### 4.5 Resume Item (Inside Expanded Job)

```
+---------------------------------------------------------------+
|    -> Resume · Jan 3, 2026 · Match: 72%                Delete  |
+---------------------------------------------------------------+
     ^                                                      ^
     | Click entire row to load resume                      |
                                                        Delete link
```

---

## 5. Wireframes

### Mobile (< 768px)

```
+---------------------------+
|    Resume Generator       |
+---------------------------+
| [JD Input Textarea]       |
| [Generate]                |
+---------------------------+
| My Job Applications  [-]  |
+---------------------------+
| # Software Dev @ Odoo [^] |
| We are looking for a...   |
| Jan 3 · 1 resume          |
+---------------------------+
|  -> Resume · Jan 3 · 72%  |
|                   [Delete]|
+---------------------------+
| Product Mgr @ XYZ    [v]  |
| Seeking a product...      |
| Jan 2 · 2 resumes         |
+---------------------------+
```

### Desktop (>= 768px)

```
+---------------------------------------------------------------+
|                      Resume Generator                          |
+---------------------------+-----------------------------------+
|                           |                                   |
| [JD Input Textarea]       |   [Resume Preview Panel]          |
|                           |                                   |
| [Save] [Generate]         |   (Shows selected resume          |
|                           |    or empty state)                |
+---------------------------+-----------------------------------+
| My Job Applications                                      [-]  |
+---------------------------------------------------------------+
| # Software Developer at Odoo                    Edit Del  [^] |
| We are looking for a software developer to join our team...   |
| Jan 3, 2026   1 resume                                        |
+---------------------------------------------------------------+
|    -> Resume · Jan 3, 2026 · Match: 72%               Delete  |
+---------------------------------------------------------------+
| Product Manager at StartupXYZ                   Edit Del  [v] |
| Seeking a product manager to lead our mobile product team...  |
| Jan 2, 2026   2 resumes                                       |
+---------------------------------------------------------------+
```

---

## 6. Sort Order

| Level | Sort By | Direction | Example |
|-------|---------|-----------|---------|
| Jobs | `updated_at` | DESC | Most recently modified first |
| Resumes (within job) | `created_at` | DESC | Newest resume first |

**Note:** Job's `updated_at` updates when:
- JD text is edited
- Title is changed
- New resume is generated (backend updates it)

---

## 7. Error Messages

| Error | Message | Recovery |
|-------|---------|----------|
| Fetch jobs failed | "Could not load job applications" | Refresh page |
| Fetch resumes failed | "Could not load resumes" | Retry button in expand area |
| Delete resume failed | "Could not delete resume. Please try again." | Retry |
| Delete job failed | "Could not delete job application. Please try again." | Retry |

---

## 8. Confirmation Dialogs

### Delete Job Application

```
+----------------------------------------------+
|                                              |
|   Delete Job Application?                    |
|                                              |
|   This will delete the job description and   |
|   2 generated resumes. This cannot be undone.|
|                                              |
|           [Cancel]    [Delete]               |
|                                              |
+----------------------------------------------+
```

### Delete Resume

```
+----------------------------------------------+
|                                              |
|   Delete Resume?                             |
|                                              |
|   This generated resume will be permanently  |
|   deleted. This cannot be undone.            |
|                                              |
|           [Cancel]    [Delete]               |
|                                              |
+----------------------------------------------+
```

---

## 9. Accessibility

### Keyboard Navigation

| Key | Action |
|-----|--------|
| Tab | Navigate between jobs, resumes, buttons |
| Enter/Space | Toggle expand/collapse, select resume, activate button |
| Escape | Close confirmation dialog |

### ARIA Attributes

| Element | Attribute | Purpose |
|---------|-----------|---------|
| Section collapse button | `aria-expanded="true/false"` | Announce collapse state |
| Job expand toggle | `aria-expanded="true/false"` | Announce expand state |
| Resume list | `role="list"` | Semantic list |
| Resume item | `role="listitem"` | Semantic list item |
| Delete buttons | `aria-label="Delete resume for [job title]"` | Context for screen readers |
| Loading state | `aria-busy="true"` | Announce loading |

### Focus Management

- When job expands: Focus moves to first resume item
- When dialog opens: Focus moves to Cancel button
- When dialog closes: Focus returns to triggering button
- When resume deleted: Focus moves to next resume or job toggle

### Checklist

- [x] All interactive elements keyboard accessible
- [x] Focus states visible (existing styles)
- [x] Form fields have labels
- [x] Color contrast meets WCAG 2.1 AA
- [x] Error states announced to screen readers
- [x] Loading states communicated via aria-busy

---

## 10. Files to Change

| File | Change |
|------|--------|
| `ResumeGenerator.svelte` | Remove ResumeHistory import, track loadedJobId |
| `SavedJobsList.svelte` | Rename header, pass autoExpandFirst prop, add onSelectResume |
| `SavedJobItem.svelte` | Add expand/collapse, fetch/display resumes, delete resume |
| `ResumeHistory.svelte` | **DELETE** |
| `_saved-jobs.scss` | Add `.resume-list` and `.resume-item` styles |
| `_history.scss` | **DELETE** (styles moved to _saved-jobs.scss) |

---

*Next: /v3-verify-analysis*
