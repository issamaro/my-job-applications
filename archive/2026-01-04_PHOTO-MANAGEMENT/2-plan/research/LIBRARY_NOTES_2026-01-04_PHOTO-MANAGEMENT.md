# Library Notes: Photo Management System

**Date:** 2026-01-04
**Purpose:** Ecosystem prerequisites and syntax reference

---

## 0. Ecosystem Prerequisites

### Runtime
| Runtime | Version | Reason |
|---------|---------|--------|
| Python | 3.13 | Already configured in `.python-version` |
| Node.js | 20.x | Already configured in `package.json` engines |

### Tooling
| Tool | Purpose | Verify |
|------|---------|--------|
| uv | Python version + venv + packages | `uv --version` |
| npm | Node package management | `npm --version` |

### Setup Commands
```bash
# Python (already configured)
uv venv --python 3.13
source .venv/bin/activate
uv pip install -r requirements.txt

# Node (already configured)
npm install
```

---

## 1. Architecture Decision: Client-Side Processing

### Why No Server-Side Image Processing (No Pillow)

All image processing happens **client-side** via Cropper.js:
- Crop, rotate, zoom → Cropper.js handles all transformations
- Resize to 400x400 → `$toCanvas({ width: 400, height: 400 })`
- Convert to JPEG → `canvas.toDataURL('image/jpeg', 0.85)`

The backend only needs to:
1. Validate the data URL format (regex check)
2. Validate size (base64 string length)
3. Store/retrieve from database

**Benefits:**
- Simpler backend (no image library dependency)
- Faster uploads (smaller processed image sent)
- Less server CPU usage
- Fewer dependencies to maintain

---

## 2. Cropper.js v2 (Client-Side Image Editing)

**Version Constraint:** `cropperjs@^2.0.0`

### Why Cropper.js v2
- Latest version (2.1.0) with web components architecture
- Native support for crop, rotate, zoom
- Works well with modern frameworks via vanilla JS integration
- Touch support for mobile devices

### Architecture Change (v1 → v2)
Cropper.js v2 uses **Web Components** instead of the old class-based API:
- `<cropper-canvas>` - Container element
- `<cropper-image>` - Image element with transform support
- `<cropper-selection>` - Crop selection area
- `<cropper-grid>` - Grid overlay (guides)
- `<cropper-handle>` - Resize/move handles

### Correct Patterns

#### Installation
```bash
npm install cropperjs
```

#### Import and Define Custom Elements
```javascript
import Cropper from 'cropperjs';
import 'cropperjs/dist/cropper.css';

// The import auto-registers the custom elements
```

#### Basic HTML Structure
```html
<cropper-canvas background>
  <cropper-image
    src="/path/to/image.jpg"
    alt="Photo"
    rotatable
    scalable
    translatable>
  </cropper-image>
  <cropper-selection
    aspectRatio="1"
    movable
    resizable
    initialCoverage="0.8">
    <cropper-grid covered></cropper-grid>
    <cropper-handle action="move" plain></cropper-handle>
    <cropper-handle action="n-resize"></cropper-handle>
    <cropper-handle action="e-resize"></cropper-handle>
    <cropper-handle action="s-resize"></cropper-handle>
    <cropper-handle action="w-resize"></cropper-handle>
    <cropper-handle action="ne-resize"></cropper-handle>
    <cropper-handle action="nw-resize"></cropper-handle>
    <cropper-handle action="se-resize"></cropper-handle>
    <cropper-handle action="sw-resize"></cropper-handle>
  </cropper-selection>
</cropper-canvas>
```

#### Set Fixed Aspect Ratio (1:1 Square)
```html
<cropper-selection aspectRatio="1" movable resizable>
  <!-- ... -->
</cropper-selection>
```

#### Rotate Image 90 Degrees
```javascript
// Get the cropper-image element
const cropperImage = document.querySelector('cropper-image');

// Rotate 90 degrees clockwise
cropperImage.$rotate('90deg');
```

#### Get Cropped Canvas
```javascript
const cropperSelection = document.querySelector('cropper-selection');

// Get canvas with specific dimensions
const canvas = await cropperSelection.$toCanvas({
  width: 400,
  height: 400
});

// Convert to data URL
const dataUrl = canvas.toDataURL('image/jpeg', 0.85);
```

#### Reset Selection
```javascript
const cropperSelection = document.querySelector('cropper-selection');
cropperSelection.$reset();
```

#### Zoom Selection
```javascript
const cropperSelection = document.querySelector('cropper-selection');

// Zoom in by 10%
cropperSelection.$zoom(0.1);

// Zoom out by 10%
cropperSelection.$zoom(-0.1);
```

### Key Properties Reference

| Element | Property | Type | Description |
|---------|----------|------|-------------|
| `cropper-selection` | `aspectRatio` | number | Fixed aspect ratio (1 = square) |
| `cropper-selection` | `movable` | boolean | Allow moving selection |
| `cropper-selection` | `resizable` | boolean | Allow resizing selection |
| `cropper-selection` | `initialCoverage` | number | Initial coverage (0-1) |
| `cropper-image` | `rotatable` | boolean | Allow rotation |
| `cropper-image` | `scalable` | boolean | Allow scaling |
| `cropper-image` | `translatable` | boolean | Allow panning |

### Key Methods Reference

| Element | Method | Returns | Description |
|---------|--------|---------|-------------|
| `cropper-image` | `$rotate(angle)` | CropperImage | Rotate by angle ('90deg') |
| `cropper-image` | `$ready(callback)` | Promise | Wait for image load |
| `cropper-selection` | `$toCanvas(options)` | Promise<Canvas> | Get cropped canvas |
| `cropper-selection` | `$reset()` | CropperSelection | Reset to initial state |
| `cropper-selection` | `$zoom(scale)` | CropperSelection | Zoom selection |

---

## 3. Svelte 5 Integration

**Version Constraint:** `svelte@^5.0.0` (already installed)

### Integrating Vanilla JS Libraries

#### Pattern 1: Using `bind:this` + `$effect`
```svelte
<script>
  import Cropper from 'cropperjs';
  import 'cropperjs/dist/cropper.css';

  /** @type {HTMLElement} */
  let container;

  $effect(() => {
    // Setup when container is mounted
    if (container) {
      // Initialize library here
    }

    return () => {
      // Cleanup on unmount
    };
  });
</script>

<div bind:this={container}>
  <!-- Web components go here -->
</div>
```

#### Pattern 2: Using Svelte Actions
```svelte
<script>
  /** @type {import('svelte/action').Action} */
  function cropper(node) {
    // node is the DOM element

    $effect(() => {
      // Setup code

      return () => {
        // Teardown code
      };
    });
  }
</script>

<div use:cropper>...</div>
```

#### Pattern 3: onMount for Browser-Only Code
```svelte
<script>
  import { onMount } from 'svelte';

  onMount(async () => {
    // Dynamically import browser-only library
    const Cropper = (await import('cropperjs')).default;
    await import('cropperjs/dist/cropper.css');

    // Initialize...

    return () => {
      // Cleanup on component destroy
    };
  });
</script>
```

### Recommended Approach for Cropper.js + Svelte 5
Use Pattern 3 (onMount) because:
- Cropper.js registers web components on import
- Web components need browser environment
- onMount ensures SSR safety (not applicable here but good practice)

---

## 4. FastAPI File Upload

**Version Constraint:** `fastapi>=0.100.0` (already installed)

### Correct Pattern for Base64 Upload
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

class PhotoUpload(BaseModel):
    image_data: str  # base64 data URL

router = APIRouter(prefix="/api/photos", tags=["photos"])

@router.post("")
async def upload_photo(photo: PhotoUpload):
    """Upload a photo as base64 data URL."""
    if not photo.image_data.startswith("data:image/"):
        raise HTTPException(400, "Invalid image data format")
    # Process image...
```

### Correct Pattern for File Upload (Alternative)
```python
from fastapi import APIRouter, File, UploadFile, HTTPException

router = APIRouter(prefix="/api/photos", tags=["photos"])

@router.post("")
async def upload_photo(file: UploadFile = File(...)):
    """Upload a photo file."""
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(400, "Invalid file type")

    contents = await file.read()
    # Process image bytes...
```

---

## 5. Pydantic v2 Patterns

**Version Constraint:** `pydantic>=2.0` (already installed)

### Correct Model Definition
```python
from pydantic import BaseModel, Field

class PhotoCreate(BaseModel):
    image_data: str = Field(..., description="Base64 encoded image data URL")

class PhotoResponse(BaseModel):
    id: int
    image_data: str
    created_at: str

    model_config = {"from_attributes": True}
```

### Deprecated (Avoid)
- `class Config:` → Use `model_config = {}`
- `orm_mode = True` → Use `from_attributes = True`

---

## Dependencies Summary

**ADD TO package.json dependencies:**
```json
"cropperjs": "^2.0.0"
```

**No new Python dependencies required.**

---

## Quick Reference Card

### Client-Side (JavaScript) - All Processing Here
```javascript
// Rotate 90° clockwise
cropperImage.$rotate('90deg');

// Get cropped canvas (resized to final dimensions)
const canvas = await cropperSelection.$toCanvas({ width: 400, height: 400 });

// To data URL (JPEG at 85% quality)
const dataUrl = canvas.toDataURL('image/jpeg', 0.85);

// Reset to original
cropperSelection.$reset();
```

### Server-Side (Python) - Storage Only
```python
import re

# Validate data URL format
def is_valid_image_data_url(data_url: str) -> bool:
    return bool(re.match(r'^data:image/(jpeg|png|webp);base64,[A-Za-z0-9+/=]+$', data_url))

# Validate size (400x400 JPEG at 85% ≈ 50-150KB base64)
MAX_DATA_URL_LENGTH = 500_000  # ~375KB decoded, generous limit
```

---

*Reference for /v4-design and /v4-checklist*
