from app.libs.ui_kit.components.actions import ButtonBar, add_modal_actions, bind_modal_keys
from app.libs.ui_kit.components.cards import DetailsDrawer, StatCard
from app.libs.ui_kit.components.composed import (
    AuthCard,
    EmptyState,
    FormDialog,
    FormField,
    SectionHeader,
    SignInAuthCard,
    SignUpAuthCard,
    ToggleSelectionList,
    topbar_action,
)
from app.libs.ui_kit.components.drawers import TeamDrawer
from app.libs.ui_kit.components.inputs import LabeledCombobox, LabeledEntry
from app.libs.ui_kit.components.layout import AppShell, Section, Sidebar, Topbar
from app.libs.ui_kit.components.primitives import (
    Alert,
    Badge,
    Button,
    Card,
    Dialog,
    Input,
    Label,
    Select,
    Table,
    Tabs,
    TextArea,
    add_tab,
)

# Optional CTk primitives (available when customtkinter is installed and APP_UI=ctk)
from app.libs.ui_kit.components.ctk_primitives import (
    CtkButton,
    CtkInput,
    CtkCard,
    CtkModal,
    CtkProgress,
)
from app.libs.ui_kit.components.modals import Modal
from app.libs.ui_kit.components.tables import DataTable

__all__ = [
    "AppShell",
    "Sidebar",
    "Topbar",
    "Section",
    "DataTable",
    "StatCard",
    "DetailsDrawer",
    "TeamDrawer",
    "Modal",
    "LabeledEntry",
    "LabeledCombobox",
    "ButtonBar",
    "add_modal_actions",
    "bind_modal_keys",
    "Button",
    "Input",
    "Select",
    "TextArea",
    "Label",
    "Card",
    "Badge",
    "Alert",
    "Tabs",
    "add_tab",
    "Dialog",
    "Table",
    "FormField",
    "FormDialog",
    "ToggleSelectionList",
    "SectionHeader",
    "EmptyState",
    "AuthCard",
    "SignInAuthCard",
    "SignUpAuthCard",
    "topbar_action",
]
