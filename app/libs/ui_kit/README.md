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
from app.libs.ui_kit import Button, Card, Input, Flex, Grid
from app.libs.ui_kit.design_system.tokens import palette

toolbar = Flex(parent, direction="row", gap="xs")
toolbar.pack(fill="x")
toolbar.add(Button(toolbar, text="Save"))
toolbar.push()
toolbar.add(Button(toolbar, text="Delete", variant="danger"))

form = Grid(parent, columns=2, gap="sm")
form.pack(fill="x")
name = Input(form)
email = Input(form)
form.add(name, row=0, column=0)
form.add(email, row=0, column=1)
```

## Notes

- UI screens should import components from `app.libs.ui_kit.*` rather than `app.ui.shared.*`.
- `app/ui/shared` remains for non-library shared app concerns (navigation, paths, forms, vm, dashboard scaffolding).
