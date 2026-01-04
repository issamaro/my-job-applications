# Feature Spec: Photo Management System

**Date:** 2026-01-04
**Source:** backlog/refined/photo-management.md
**Status:** Draft

---

## 1. Problem Statement

### User Request
> Add a complete photo management system for CV profile photos. Users can upload photos via drag-and-drop or file picker, then edit them using a dedicated modal with crop, rotate, and zoom controls. Photos are stored in the backend and displayed on the user's profile.

### Pain Point
Many professional CV formats (especially European standards) require a profile photo. Currently, users have no way to add photos to their CV. They must manually add photos after export, which breaks the automated workflow and produces inconsistent results.

### User Persona
**Job Seeker** who needs to create professional CVs with photos, particularly for:
- European job markets where photos are standard
- Industries where personal presentation matters (hospitality, sales, consulting)
- Users who want a complete, polished CV without post-processing

---

## 2. BDD Scenarios

```gherkin
Feature: Photo Management
  As a job seeker
  I want to upload and edit my profile photo
  So that my CV includes a professional headshot

  # Upload Scenarios

  Scenario: Upload photo via drag-and-drop
    Given I am on the profile page
    And no photo is currently set
    When I drag a JPEG image onto the upload zone
    Then the photo editor modal opens
    And the image is displayed in the editor

  Scenario: Upload photo via file picker
    Given I am on the profile page
    When I click the upload zone
    And I select a PNG image from my computer
    Then the photo editor modal opens
    And the image is displayed in the editor

  Scenario: Reject invalid file type
    Given I am on the profile page
    When I attempt to upload a PDF file
    Then I see an error message "Please upload an image (JPEG, PNG, or WebP)"
    And the photo editor does not open

  Scenario: Reject oversized file
    Given I am on the profile page
    When I attempt to upload an image larger than 10MB
    Then I see an error message "Image must be under 10MB"
    And the photo editor does not open

  # Editor Scenarios

  Scenario: Crop photo with square ratio
    Given the photo editor is open with my image
    When I adjust the crop area
    Then the crop maintains a 1:1 square aspect ratio
    And a 3x3 grid overlay helps with composition
    And the preview updates in real-time as a circle

  Scenario: Rotate photo
    Given the photo editor is open with my image
    When I click the rotate button
    Then the image rotates 90 degrees clockwise
    And the preview updates immediately

  Scenario: Zoom photo
    Given the photo editor is open with my image
    When I adjust the zoom slider
    Then the image scales up or down within the crop area
    And the preview updates in real-time

  Scenario: Reset to original
    Given the photo editor is open
    And I have cropped, rotated, and zoomed my image
    When I click "Reset"
    Then the image returns to its original state

  Scenario: Apply edits
    Given the photo editor is open
    And I have adjusted the crop
    When I click "Apply"
    Then the modal closes
    And the edited photo is saved to the backend
    And the photo appears on my profile

  Scenario: Cancel editing
    Given the photo editor is open
    And I have made some edits
    When I click "Cancel"
    Then the modal closes
    And no changes are saved
    And the original photo (if any) remains unchanged

  # Profile Display Scenarios

  Scenario: View photo on profile
    Given I have a saved photo
    When I view my profile page
    Then I see my photo displayed
    And I see an "Edit" button

  Scenario: No photo placeholder
    Given I have not uploaded a photo
    When I view my profile page
    Then I see a placeholder indicating no photo
    And I see an upload zone

  Scenario: Replace existing photo
    Given I have a saved photo
    When I click "Edit" on my photo
    And I upload a new image
    Then the photo editor opens with the new image
    And applying it replaces my old photo

  Scenario: Delete photo
    Given I have a saved photo
    When I click "Delete" on my photo
    And I confirm the deletion
    Then my photo is removed
    And the upload zone placeholder appears

  # Persistence Scenarios

  Scenario: Photo persists across sessions
    Given I have saved a photo
    When I close and reopen the application
    Then my photo is still displayed on my profile

  Scenario: Photo available for templates
    Given I have a saved photo
    When a template requests the photo field
    Then the photo data is available in base64 format
```

---

## 3. Requirements

### Must Have
- [ ] Drag-and-drop upload zone component
- [ ] Click-to-upload file picker fallback
- [ ] Client-side validation (JPEG, PNG, WebP only; max 10MB)
- [ ] Photo editor modal with Cropper.js integration
- [ ] Crop tool with fixed 1:1 square ratio and 3x3 grid overlay
- [ ] Rotate button (90° clockwise steps)
- [ ] Zoom/scale slider control
- [ ] Real-time preview during editing
- [ ] Reset to original button
- [ ] Apply/Cancel actions in editor
- [ ] Photo displayed as circle on profile page
- [ ] Circular placeholder when no photo set
- [ ] Edit/Replace photo capability
- [ ] Delete photo with confirmation
- [ ] Backend photo upload endpoint (POST /api/photos)
- [ ] Backend photo update endpoint (PUT /api/photos)
- [ ] Backend photo delete endpoint (DELETE /api/photos)
- [ ] Backend photo retrieval endpoint (GET /api/photos)
- [ ] Server-side image processing (resize to max 400x500px)
- [ ] Base64 storage in database (SQLite compatible)
- [ ] Photo field added to resume data model

### Should Have
- [ ] Loading indicators during upload/save
- [ ] "Saved" confirmation feedback

### Won't Have
- Template changes (separate European Templates feature)
- AI-powered photo enhancement
- Background removal
- Multiple photos per resume
- External file storage (S3, etc.)
- Fine rotation (continuous degrees)

---

## 4. Assumptions

| Assumption | Category | Notes |
|------------|----------|-------|
| Cropper.js is suitable for our needs | Library | Mature, touch support, handles crop/rotate/zoom, supports grid overlay |
| 400x400px output is sufficient | Architecture | Fixed square output for circular display |
| Base64 storage is acceptable for single-user app | Architecture | Simplifies architecture, no file system management |
| 85% JPEG quality is acceptable | Architecture | Good balance of quality/size for CVs |
| Single photo per user is sufficient | UX | No need for photo gallery |
| Frontend handles initial file validation | Architecture | Backend re-validates for security |
| Cropper.js works with Svelte 5 | Library | May need wrapper component |

---

## 5. Open Questions

- **Q1:** Should we support GIF format?
  - *Tentative:* No, animated images not appropriate for CVs

- **Q2:** Should the photo be included in PDF exports automatically?
  - *Answer:* No, this is handled by templates (European Templates feature)

- **Q3:** What happens if upload fails mid-way?
  - *Approach:* Show error, allow retry, original photo (if any) remains

---

## 6. Technical Context

### Existing Patterns to Follow

**Backend:**
- Routes: `/routes/photos.py` following existing RESTful patterns
- Service: `/services/photo_service.py` for image processing
- Schema: Add to `/schemas.py` with Pydantic validation
- Database: Add `photo` TEXT column to `personal_info` table

**Frontend:**
- Components: `/src/components/PhotoUpload.svelte`, `/src/components/PhotoEditor.svelte`
- API: Add photo methods to `/src/lib/api.js`
- Integration: Add to `/src/components/PersonalInfo.svelte`

**Storage Format:**
- `data:image/jpeg;base64,{encoded_data}`
- Max processed size: 400x500px
- JPEG quality: 85%

---

*Next: /v4-ux (UI changes required)*
