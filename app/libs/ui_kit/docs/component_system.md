# Component System (shadcn-inspired, Tk/CTk)

## Token layers

- `app/libs/ui_kit/design_system/core_tokens.py`
  - immutable base scales (colors, spacing, radius)
- `app/libs/ui_kit/design_system/semantic_tokens.py`
  - semantic UI tokens (`bg`, `text`, `primary`, `danger`, etc.)
- `app/libs/ui_kit/design_system/component_tokens.py`
  - component-level styles (`button_variants`, size maps)
- `app/libs/ui_kit/design_system/variants.py`
  - strict option normalization with safe fallbacks

Backwards compatibility is preserved through `app/libs/ui_kit/design_system/tokens.py::palette()`.

## Primitive catalog

Location: `app/libs/ui_kit/components/primitives`

- `Button(text, variant, size, command)`
- `Input(size, placeholder, ...)`
- `Select(values, variable, ...)`
- `TextArea(height, ...)`
- `Label(text, variant, weight, ...)`
- `Card(...)`
- `Badge(text, variant)`
- `Alert(title, description, variant)`
- `Tabs(...)` + `add_tab(...)`
- `Dialog(title)`
- `Table(columns, height)`

## Variant conventions

- Button variants: `default | secondary | outline | ghost | danger`
- Button sizes: `sm | md | lg`
- Label variants: `default | muted | accent | danger`
- Badge variants: `default | success | warning | danger`

Unknown/empty values automatically fallback to defaults via `resolve_variant`.

## Composed components

Location: `app/libs/ui_kit/components/composed`

- `FormField`
- `SectionHeader`
- `EmptyState`
- `AuthCard`
- `topbar_action`

## Usage example

```python
from app.ui.shared.components.primitives import Button, Card, Input, Label

panel = Card(parent)
panel.pack(fill="x")

Label(panel, text="Profile", weight="bold").pack(anchor="w")
name = Input(panel, placeholder="Your name")
name.pack(fill="x")
Button(panel, text="Save", variant="default", size="sm", command=on_save).pack()
```
