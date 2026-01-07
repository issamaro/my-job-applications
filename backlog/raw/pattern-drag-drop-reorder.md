# Pattern: Drag-and-Drop Reordering

**Source:** add-language retrospective
**Date:** 2026-01-07

## Description

Document the drag-and-drop reordering pattern used in Languages section:
- Visual drag handles (⋮⋮) on each item
- HTML5 drag-and-drop events (ondragstart, ondragover, ondrop)
- display_order field in database for persistence
- PUT /reorder endpoint for batch order updates

## Potential Approaches

1. Create a patterns documentation file in docs/
2. Extract reusable DraggableList component
3. Document as inline comments in Languages.svelte

## Files Involved

- `Languages.svelte` - Drag-and-drop implementation
- `routes/languages.py` - /reorder endpoint
- `database.py` - display_order column

## Value

Future features needing reorderable lists can reference or reuse this pattern.
