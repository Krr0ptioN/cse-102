# UI Kit Library

Internal reusable UI library for this app.

## Package

- `app.libs.ui_kit`

## Contains

- `components/` (including `primitives/` and `composed/`)
- `design_system/` (tokens, variants, typography)
- `design/` (theme/token bridge for Tk/CTk)
- `theme.py`

## Usage

```python
from app.libs.ui_kit.components import Button, Card, Input
from app.libs.ui_kit.design_system.tokens import palette
```

## Notes

- UI screens should import components from `app.libs.ui_kit.*` rather than `app.ui.shared.*`.
- `app/ui/shared` remains for non-library shared app concerns (navigation, paths, forms, vm, dashboard scaffolding).

