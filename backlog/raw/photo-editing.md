# Photo Editing Feature

Source: PHOTO-MANAGEMENT retrospective
Date: 2026-01-04

The photo editor (crop, rotate, zoom) was planned for the Photo Management feature but had to be removed due to Cropper.js v2 web components integration failures.

## Why It Matters

Users uploading profile photos may want to:
- Crop to focus on their face
- Rotate photos taken in wrong orientation
- Zoom to adjust framing

Currently, they must pre-edit photos before uploading.

## Failed Approach

Cropper.js v2 web components (`cropper-canvas`, `cropper-image`, etc.) had multiple issues:
- Zoom API uses percentage factors, not absolute values
- Event binding with Svelte 5 unreliable
- `$toCanvas()` silently failed
- Transform matrix reset didn't restore "fit to canvas" state

## Potential Approaches

1. **Cropper.js v1 (classic API)** - More stable, well-documented, but jQuery-style
2. **Canvas API manual implementation** - Full control, more code
3. **Server-side cropping** - Send crop coordinates, process on backend
4. **Simpler library** - Investigate alternatives like Pica, Compressor.js

## Notes

- Consider making this a "nice to have" rather than must-have
- Users can always edit photos externally before upload
- European CV templates may have fixed photo dimensions anyway
