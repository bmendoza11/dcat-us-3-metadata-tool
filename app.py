import streamlit as st
import json
import os
import re
import datetime
from io import BytesIO

from openpyxl import Workbook, load_workbook
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter

from dcat_builder import build_dataset, build_catalog


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="DCAT-US 3.0 Metadata Builder",
    page_icon="📊",
    layout="wide",
)

CONTACTS_FILE = "contacts.json"
TAGS_FILE = "tags.json"
THEMES_FILE = "themes.json"


# ============================================================
# STYLE
# ============================================================

st.markdown(
    """
    <style>
    div[data-testid="stVerticalBlock"] > div {
        margin-bottom: 16px;
        margin-top: 8px;
    }

    html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"],
    [data-testid="stMain"], section.main, .main, .block-container {
        background: #ffffff !important;
        color: #222222 !important;
    }

    [data-testid="stHeader"], [data-testid="stToolbar"],
    [data-testid="stDecoration"] {
        background: #ffffff !important;
    }

    h1, h2, h3, h4, h5, h6, p, label,
    [data-testid="stMarkdownContainer"],
    [data-testid="stCaptionContainer"] {
        color: #222222 !important;
    }

    h1, h2, h3 {
        color: #005ea8 !important;
    }

    [data-testid="stTextInput"] *,
    [data-testid="stTextArea"] *,
    [data-testid="stNumberInput"] *,
    [data-testid="stDateInput"] *,
    [data-testid="stSelectbox"] *,
    [data-testid="stMultiSelect"] * {
        color: #222222 !important;
        -webkit-text-fill-color: #222222 !important;
    }

    [data-testid="stTextInput"] [data-baseweb="input"],
    [data-testid="stTextInput"] [data-baseweb="input"] > div,
    [data-testid="stTextArea"] [data-baseweb="textarea"],
    [data-testid="stTextArea"] [data-baseweb="textarea"] > div,
    [data-testid="stSelectbox"] [data-baseweb="select"],
    [data-testid="stSelectbox"] [data-baseweb="select"] > div,
    [data-testid="stMultiSelect"] [data-baseweb="select"],
    [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
        background: #ffffff !important;
        background-color: #ffffff !important;
        border-color: #b8b8b8 !important;
        box-shadow: none !important;
    }

    input, textarea {
        background: #ffffff !important;
        color: #222222 !important;
        -webkit-text-fill-color: #222222 !important;
        caret-color: #222222 !important;
    }

    input::placeholder, textarea::placeholder {
        color: #777777 !important;
        -webkit-text-fill-color: #777777 !important;
    }

    [data-baseweb="popover"], [data-baseweb="popover"] > div,
    [data-baseweb="menu"], [role="listbox"] {
        background: #ffffff !important;
        color: #222222 !important;
    }

    [role="option"] {
        background: #ffffff !important;
        color: #222222 !important;
    }

    [role="option"]:hover, [role="option"][aria-selected="true"] {
        background: #eaf3fb !important;
        color: #005ea8 !important;
    }

    [data-testid="stMultiSelect"] span[data-baseweb="tag"] {
        background: #eaf3fb !important;
        color: #005ea8 !important;
    }

    .stButton > button, .stDownloadButton > button {
        background: #005ea8 !important;
        background-color: #005ea8 !important;
        color: #ffffff !important;
        border: 1px solid #005ea8 !important;
    }

    .stButton > button:hover, .stDownloadButton > button:hover {
        background: #004b87 !important;
        background-color: #004b87 !important;
    }

    [data-testid="stExpander"], [data-testid="stExpander"] details,
    [data-testid="stExpander"] summary {
        background: #ffffff !important;
        color: #222222 !important;
        border-color: #dddddd !important;
    }

    [data-testid="stAlert"] {
        background: #f8f9fa !important;
        color: #222222 !important;
        border-color: #d6d6d6 !important;
    }

    [data-testid="stJson"], [data-testid="stCode"], pre, code {
        background: #f7f7f7 !important;
        color: #222222 !important;
    }

    hr { border-color: #dddddd !important; }
    a { color: #005ea8 !important; }

    .section-header {
        margin-top: 24px;
        margin-bottom: 10px;
    }

    .saved-indicator {
        background: #f0f7fc;
        border-left: 4px solid #005ea8;
        padding: 10px 14px;
        border-radius: 4px;
    }

    .question-help {
        background: #f7fbff;
        border: 1px solid #d6e8f5;
        padding: 12px 14px;
        border-radius: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# BUREAUS
# ============================================================

BUREAUS = {
    "Bureau of Economic Analysis": {
        "publisher": "Bureau of Economic Analysis",
        "identifier_code": "BEA",
        "bureauCode": ["006:02"],
        "programCode": ["006:000"],
        "homepage": "https://www.bea.gov/",
    },
    "Bureau of Industry and Security": {
        "publisher": "Bureau of Industry and Security",
        "identifier_code": "BIS",
        "bureauCode": ["006:03"],
        "programCode": ["006:000"],
        "homepage": "https://www.bis.gov/",
    },
    "Bureau of Labor Statistics": {
        "publisher": "Bureau of Labor Statistics",
        "identifier_code": "BLS",
        "bureauCode": ["006:04"],
        "programCode": ["006:000"],
        "homepage": "https://www.bls.gov/",
    },
    "Census Bureau": {
        "publisher": "United States Census Bureau",
        "identifier_code": "CEN",
        "bureauCode": ["006:07"],
        "programCode": ["006:000"],
        "homepage": "https://www.census.gov/",
    },
    "Economic Development Administration": {
        "publisher": "Economic Development Administration",
        "identifier_code": "EDA",
        "bureauCode": ["006:08"],
        "programCode": ["006:000"],
        "homepage": "https://www.eda.gov/",
    },
    "International Trade Administration": {
        "publisher": "International Trade Administration",
        "identifier_code": "ITA",
        "bureauCode": ["006:13"],
        "programCode": ["006:000"],
        "homepage": "https://www.trade.gov/",
    },
    "National Oceanic and Atmospheric Administration": {
        "publisher": "National Oceanic and Atmospheric Administration",
        "identifier_code": "NOAA",
        "bureauCode": ["006:20"],
        "programCode": ["006:000"],
        "homepage": "https://www.noaa.gov/",
    },
    "National Institute of Standards and Technology": {
        "publisher": "National Institute of Standards and Technology",
        "identifier_code": "NIST",
        "bureauCode": ["006:19"],
        "programCode": ["006:000"],
        "homepage": "https://www.nist.gov/",
    },
    "National Technical Information Service": {
        "publisher": "National Technical Information Service",
        "identifier_code": "NTIS",
        "bureauCode": ["006:21"],
        "programCode": ["006:000"],
        "homepage": "https://www.ntis.gov/",
    },
    "Patent and Trademark Office": {
        "publisher": "United States Patent and Trademark Office",
        "identifier_code": "USPTO",
        "bureauCode": ["006:25"],
        "programCode": ["006:000"],
        "homepage": "https://www.uspto.gov/",
    },
    "National Telecommunications and Information Administration": {
        "publisher": "National Telecommunications and Information Administration",
        "identifier_code": "NTIA",
        "bureauCode": ["006:18"],
        "programCode": ["006:000"],
        "homepage": "https://www.ntia.gov/",
    },
}


# ============================================================
# HELPERS
# ============================================================

def load_json_file(filename, default):
    if not os.path.exists(filename):
        return default
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json_file(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def normalize_text(value):
    if value is None:
        return ""
    return str(value).strip().lower()


def normalize_bureau(value):
    value = normalize_text(value)
    value = re.sub(r"\s*\([^)]*\)", "", value)
    variants = {
        "census bureau": "united states census bureau",
        "u.s. census bureau": "united states census bureau",
        "us census bureau": "united states census bureau",
    }
    value = variants.get(value, value)
    value = value.replace(
        "united states patent and trademark office",
        "patent and trademark office",
    )
    return value


def split_cell(value):
    """Excel convention: lists are entered as semicolon-separated values."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    return [x.strip() for x in str(value).split(";") if x.strip()]


def is_valid_dcat_date(value):
    value = normalize_text(value)
    if not value:
        return True
    if re.fullmatch(r"\d{4}", value):
        return True
    if re.fullmatch(r"\d{4}-\d{2}", value):
        return 1 <= int(value.split("-")[1]) <= 12
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        try:
            datetime.date.fromisoformat(value)
            return True
        except ValueError:
            return False
    return False


def contact_from_dataset(dataset):
    points = dataset.get("contactPoint", [])
    if not points:
        return {}
    point = points[0] or {}
    email = point.get("hasEmail", "")
    if isinstance(email, str):
        email = email.removeprefix("mailto:")
    return {
        "name": point.get("fn", ""),
        "email": email,
        "phone": point.get("hasTelephone", ""),
        "organization": point.get("organization-name", ""),
    }


def first_value(value):
    if isinstance(value, list):
        return value[0] if value else ""
    return value or ""


def contact_signature(contact):
    return (
        normalize_text(contact.get("bureau")),
        normalize_text(contact.get("name")),
        normalize_text(contact.get("email")),
        normalize_text(contact.get("phone")),
        normalize_text(contact.get("organization")),
    )


def ensure_contact_in_database(contact, bureau):
    if not contact.get("name"):
        return
    contacts = load_json_file(CONTACTS_FILE, [])
    candidate = dict(contact)
    candidate["bureau"] = bureau

    signatures = {contact_signature(x) for x in contacts}
    if contact_signature(candidate) not in signatures:
        contacts.append(candidate)
        save_json_file(CONTACTS_FILE, contacts)


def ensure_tags_in_database(tags):
    tags = [normalize_text(x) for x in tags if normalize_text(x)]
    if not tags:
        return
    existing = load_json_file(TAGS_FILE, [])
    combined = sorted(set(normalize_text(x) for x in existing + tags if normalize_text(x)))
    save_json_file(TAGS_FILE, combined)


def ensure_themes_in_database(themes, descriptions):
    theme_names = [normalize_text(x) for x in themes if normalize_text(x)]
    descriptions = [str(x).strip() for x in descriptions]
    desc_map = {}
    for i, name in enumerate(theme_names):
        desc_map[name] = descriptions[i] if i < len(descriptions) else ""

    existing = load_json_file(THEMES_FILE, [])
    by_name = {
        normalize_text(x.get("name", "")): x
        for x in existing
        if normalize_text(x.get("name", ""))
    }

    for name in theme_names:
        if name not in by_name:
            if not desc_map.get(name):
                raise ValueError(
                    f'New theme "{name}" needs a description in the '
                    f'"theme_descriptions" column.'
                )
            by_name[name] = {
                "name": name,
                "description": desc_map[name],
            }

    result = sorted(by_name.values(), key=lambda x: normalize_text(x.get("name", "")))
    save_json_file(THEMES_FILE, result)


def infer_bureau(catalog):
    publisher = normalize_bureau(
        (catalog.get("publisher") or {}).get("name", "")
    )
    for bureau_name, info in BUREAUS.items():
        if publisher == normalize_bureau(info["publisher"]):
            return bureau_name

    codes = catalog.get("bureauCode", [])
    for bureau_name, info in BUREAUS.items():
        if set(codes or []) & set(info.get("bureauCode", [])):
            return bureau_name

    return ""


# ============================================================
# EXCEL DATA DICTIONARY
# ============================================================

YES_NO = ["No", "Yes"]
ACCESS_RIGHTS_OPTIONS = [
    "These data are public",
    "These data are restricted",
    "These data are not public",
]
ACCESS_STATUS_OPTIONS = [
    "Restricted - Fully",
    "Restricted - Partly",
    "Restricted - Possibly",
    "Undetermined",
    "Unrestricted",
]
SPECIFIC_ACCESS_OPTIONS = [
    "FOIA (b)(1) National Security",
    "FOIA (b)(2) Internal Personnel Rules and Practices",
    "FOIA (b)(3) Statute",
    "FOIA (b)(4) Trade Secrets and Commercial Information",
    "FOIA (b)(5) Personal Information",
    "FOIA (b)(6) Personal Information",
    "FOIA (b)(7) Law Enforcement",
    "FOIA (b)(8) Financial Institutions",
    "FOIA (b)(9) Geological and Geophysical Information",
    "Other",
]
CUI_OPTIONS = [
    "CONTROLLED",
    "SP-PROPIN",
    "SP-CTI",
    "SP-PRVCY",
    "SP-PII",
    "SP-HLTH",
    "SP-FIN",
]
USE_TYPE_OPTIONS = ["Use restriction", "License", "Rights"]
SPECIFIC_USE_OPTIONS = ["Copyright", "Donor Restrictions", "Public Law", "Other"]
SPATIAL_GRANULARITY_OPTIONS = [
    "Continent", "Country", "State", "County", "City",
    "ZIP Code", "Census Tract", "Other",
]


QUESTION_DEFINITIONS = [
    {
        "column": "catalog_bureau",
        "question": "Which bureau are you submitting metadata for?",
        "expected": "Select one bureau from the list.",
        "type": "Dropdown",
        "options": list(BUREAUS.keys()),
        "required": "Required",
        "scope": "Catalog",
    },
    {
        "column": "catalog_contact_name",
        "question": "Who should be contacted with questions about this catalog? — Contact name",
        "expected": "Example: Census Bureau Call Center",
        "type": "Text",
        "options": [],
        "required": "Required",
        "scope": "Catalog",
    },
    {
        "column": "catalog_contact_email",
        "question": "Who should be contacted with questions about this catalog? — Email",
        "expected": "Example: help@example.gov",
        "type": "Text",
        "options": [],
        "required": "Optional",
        "scope": "Catalog",
    },
    {
        "column": "catalog_contact_phone",
        "question": "Who should be contacted with questions about this catalog? — Phone",
        "expected": "Example: 202-555-0100",
        "type": "Text",
        "options": [],
        "required": "Optional",
        "scope": "Catalog",
    },
    {
        "column": "catalog_contact_organization",
        "question": "Who should be contacted with questions about this catalog? — Organization",
        "expected": "Example: United States Census Bureau",
        "type": "Text",
        "options": [],
        "required": "Optional",
        "scope": "Catalog",
    },
    {
        "column": "dataset_title",
        "question": "What is the dataset called?",
        "expected": "A clear, human-readable dataset title.",
        "type": "Text",
        "options": [],
        "required": "Required",
        "scope": "Dataset",
    },
    {
        "column": "dataset_description",
        "question": "Dataset description in plain language.",
        "expected": "A plain-language description of what the data contain.",
        "type": "Long text",
        "options": [],
        "required": "Required",
        "scope": "Dataset",
    },
    {
        "column": "dataset_identifier",
        "question": "Dataset identifier",
        "expected": "Automatically assigned from the bureau code, e.g. CEN-000001. Leave blank for new datasets.",
        "type": "Auto",
        "options": [],
        "required": "Auto",
        "scope": "Dataset",
    },
    {
        "column": "publisher_office",
        "question": "Which office publishes these data?",
        "expected": "The office or organization that publishes the dataset.",
        "type": "Text",
        "options": [],
        "required": "Required",
        "scope": "Dataset",
    },
    {
        "column": "dataset_contact_name",
        "question": "What is the best contact for questions about this dataset? — Contact name",
        "expected": "Example: Current Population Survey Office",
        "type": "Text",
        "options": [],
        "required": "Required",
        "scope": "Dataset",
    },
    {
        "column": "dataset_contact_email",
        "question": "What is the best contact for questions about this dataset? — Email",
        "expected": "Example: dsd.cps@census.gov",
        "type": "Text",
        "options": [],
        "required": "Optional",
        "scope": "Dataset",
    },
    {
        "column": "dataset_contact_phone",
        "question": "What is the best contact for questions about this dataset? — Phone",
        "expected": "Example: 1-800-923-8282",
        "type": "Text",
        "options": [],
        "required": "Optional",
        "scope": "Dataset",
    },
    {
        "column": "dataset_contact_organization",
        "question": "What is the best contact for questions about this dataset? — Organization",
        "expected": "The contact's organization.",
        "type": "Text",
        "options": [],
        "required": "Optional",
        "scope": "Dataset",
    },
    {
        "column": "keywords",
        "question": "What words would someone use to search for these data?",
        "expected": "Semicolon-separated keywords, e.g. trade; exports; employment.",
        "type": "List",
        "options": [],
        "required": "Required",
        "scope": "Dataset",
    },
    {
        "column": "themes",
        "question": "What theme does this dataset belong to?",
        "expected": "Semicolon-separated theme names.",
        "type": "List",
        "options": [],
        "required": "Required",
        "scope": "Dataset",
    },
    {
        "column": "theme_descriptions",
        "question": "Description(s) for any new themes",
        "expected": "Use the same order as themes. Required only when adding a theme not already in themes.json.",
        "type": "List",
        "options": [],
        "required": "Conditional",
        "scope": "Helper",
    },
    {
        "column": "access_rights",
        "question": "Who is allowed to access these data?",
        "expected": "Select one controlled value.",
        "type": "Dropdown",
        "options": ACCESS_RIGHTS_OPTIONS,
        "required": "Required",
        "scope": "Dataset",
    },
    {
        "column": "has_access_restriction",
        "question": "Are there any restrictions on getting these data?",
        "expected": "Yes or No.",
        "type": "Dropdown",
        "options": YES_NO,
        "required": "Required",
        "scope": "Dataset",
    },
    {
        "column": "access_restriction_status",
        "question": "What is the data restriction status?",
        "expected": "Select one status when has_access_restriction = Yes.",
        "type": "Dropdown",
        "options": ACCESS_STATUS_OPTIONS,
        "required": "Conditional",
        "scope": "Dataset",
    },
    {
        "column": "access_specific_restriction",
        "question": "What is the specific access restriction?",
        "expected": "Semicolon-separated values. When applicable, use the controlled values listed here.",
        "type": "Multi-select list",
        "options": SPECIFIC_ACCESS_OPTIONS,
        "required": "Conditional",
        "scope": "Dataset",
    },
    {
        "column": "access_restriction_note",
        "question": "Additional information about the access restriction",
        "expected": "Additional explanatory text.",
        "type": "Long text",
        "options": [],
        "required": "Optional",
        "scope": "Dataset",
    },
    {
        "column": "has_cui",
        "question": "Does the dataset contain Controlled Unclassified Information (CUI)?",
        "expected": "Yes or No.",
        "type": "Dropdown",
        "options": YES_NO,
        "required": "Required",
        "scope": "Dataset",
    },
    {
        "column": "cui_banner",
        "question": "Which CUI Banner Marking are these data associated with?",
        "expected": "Select one marking when has_cui = Yes.",
        "type": "Dropdown",
        "options": CUI_OPTIONS,
        "required": "Conditional",
        "scope": "Dataset",
    },
    {
        "column": "cui_designation",
        "question": "Which agency designated the information as CUI? Include contact information when possible.",
        "expected": "Agency/designation information.",
        "type": "Long text",
        "options": [],
        "required": "Conditional",
        "scope": "Dataset",
    },
    {
        "column": "has_use_restriction",
        "question": "Are there any other rules about how these data may be used, such as use restriction, license, or rights?",
        "expected": "Yes or No.",
        "type": "Dropdown",
        "options": YES_NO,
        "required": "Required",
        "scope": "Dataset",
    },
    {
        "column": "restriction_types",
        "question": "What type of rule applies?",
        "expected": "Semicolon-separated values from the controlled list.",
        "type": "Multi-select list",
        "options": USE_TYPE_OPTIONS,
        "required": "Conditional",
        "scope": "Dataset",
    },
    {
        "column": "use_status",
        "question": "Use restriction status",
        "expected": "Select one status when Use restriction is included.",
        "type": "Dropdown",
        "options": ACCESS_STATUS_OPTIONS,
        "required": "Conditional",
        "scope": "Dataset",
    },
    {
        "column": "specific_use",
        "question": "Specific use restriction",
        "expected": "Semicolon-separated values.",
        "type": "Multi-select list",
        "options": SPECIFIC_USE_OPTIONS,
        "required": "Conditional",
        "scope": "Dataset",
    },
    {
        "column": "use_note",
        "question": "Use restriction note",
        "expected": "Additional explanatory text.",
        "type": "Long text",
        "options": [],
        "required": "Optional",
        "scope": "Dataset",
    },
    {
        "column": "license",
        "question": "What license applies to these data?",
        "expected": "License name or URI.",
        "type": "Text",
        "options": [],
        "required": "Conditional",
        "scope": "Dataset",
    },
    {
        "column": "rights",
        "question": "What other rights have not been covered?",
        "expected": "Other rights information.",
        "type": "Long text",
        "options": [],
        "required": "Conditional",
        "scope": "Dataset",
    },
    {
        "column": "temporal_start",
        "question": "Start date for the period covered by these data",
        "expected": "YYYY, YYYY-MM, or YYYY-MM-DD.",
        "type": "Date text",
        "options": [],
        "required": "Required",
        "scope": "Dataset",
    },
    {
        "column": "temporal_end",
        "question": "End date for the period covered by these data",
        "expected": "YYYY, YYYY-MM, or YYYY-MM-DD.",
        "type": "Date text",
        "options": [],
        "required": "Required",
        "scope": "Dataset",
    },
    {
        "column": "spatial_granularity",
        "question": "Spatial Granularity",
        "expected": "The geographic level at which the dataset's data are provided.",
        "type": "Dropdown",
        "options": [""] + SPATIAL_GRANULARITY_OPTIONS,
        "required": "Optional",
        "scope": "Dataset",
    },
    {
        "column": "spatial_granularity_other",
        "question": "Specify other spatial granularity",
        "expected": "Example: Watershed, School District, Parcel.",
        "type": "Text",
        "options": [],
        "required": "Conditional",
        "scope": "Dataset",
    },
    {
        "column": "spatial",
        "question": "Where do these data cover?",
        "expected": "Example: United States, Washington, DC, or worldwide.",
        "type": "Text",
        "options": [],
        "required": "Required",
        "scope": "Dataset",
    },
    {
        "column": "modified",
        "question": "When were these data last changed?",
        "expected": "YYYY, YYYY-MM, or YYYY-MM-DD.",
        "type": "Date text",
        "options": [],
        "required": "Required",
        "scope": "Dataset",
    },
    {
        "column": "has_dictionary",
        "question": "Does this dataset have a data dictionary?",
        "expected": "Yes or No.",
        "type": "Dropdown",
        "options": YES_NO,
        "required": "Optional",
        "scope": "Dataset",
    },
    {
        "column": "dictionary_url",
        "question": "Data dictionary URL",
        "expected": "A URL to the data dictionary.",
        "type": "Text",
        "options": [],
        "required": "Conditional",
        "scope": "Dataset",
    },
    {
        "column": "dictionary_format",
        "question": "Data dictionary format",
        "expected": "Example: HTML, PDF, CSV, XLSX.",
        "type": "Text",
        "options": [],
        "required": "Conditional",
        "scope": "Dataset",
    },
    {
        "column": "has_landing_page",
        "question": "Is there a webpage/landing page to get the data from?",
        "expected": "Yes or No.",
        "type": "Dropdown",
        "options": YES_NO,
        "required": "Optional",
        "scope": "Dataset",
    },
    {
        "column": "landing_page",
        "question": "Landing page URL",
        "expected": "A URL to the dataset landing page.",
        "type": "Text",
        "options": [],
        "required": "Conditional",
        "scope": "Dataset",
    },
    {
        "column": "contract_number",
        "question": "Contract number by which these data were acquired",
        "expected": "Up to 40 characters.",
        "type": "Text",
        "options": [],
        "required": "Optional",
        "scope": "Dataset",
    },
]


# ============================================================
# EXCEL CREATION
# ============================================================

def style_sheet(ws, widths):
    header_fill = PatternFill("solid", fgColor="005EA8")
    header_font = Font(color="FFFFFF", bold=True)
    thin = Side(style="thin", color="D9E2EA")

    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(
            horizontal="center",
            vertical="center",
            wrap_text=True,
        )
        cell.border = Border(bottom=thin)

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    ws.row_dimensions[1].height = 42

    for col_idx, width in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(col_idx)].width = width


def add_dropdown(ws, column_idx, options, max_row=1000):
    if not options:
        return
    # Put options on hidden Lists sheet and reference a named range-like range.
    lists_ws = ws.parent["Lists"]
    start_col = lists_ws.max_column + 1
    col_letter = get_column_letter(start_col)
    for row_idx, option in enumerate(options, start=1):
        lists_ws.cell(row=row_idx, column=start_col, value=option)
    range_name = f"ExcelOptions_{ws.title.replace(' ', '_')}_{start_col}"
    defined = DefinedName(
        range_name,
        attr_text=f"'Lists'!${col_letter}$1:${col_letter}${len(options)}",
    )
    try:
        ws.parent.defined_names.add(defined)
    except AttributeError:
        ws.parent.defined_names.append(defined)

    dv = DataValidation(
        type="list",
        formula1=f"={range_name}",
        allow_blank=True,
    )
    dv.error = "Please choose a value from the dropdown."
    dv.errorTitle = "Invalid value"
    ws.add_data_validation(dv)
    dv.add(f"{get_column_letter(column_idx)}2:{get_column_letter(column_idx)}{max_row}")


def catalog_to_excel_rows(catalog):
    datasets = catalog.get("dataset", []) or []
    bureau = infer_bureau(catalog)
    catalog_contact = contact_from_dataset(
        {"contactPoint": catalog.get("contactPoint", [])}
    )

    rows = []
    for ds in datasets:
        ds_contact = contact_from_dataset(ds)
        themes = ds.get("theme", []) or []
        theme_names = []
        for theme in themes:
            if isinstance(theme, dict):
                theme_names.append(
                    theme.get("prefLabel")
                    or theme.get("name")
                    or ""
                )
            else:
                theme_names.append(str(theme))

        temporal = first_value(ds.get("temporal", []))
        spatial = first_value(ds.get("spatial", []))
        if isinstance(spatial, dict):
            spatial_value = spatial.get("name") or spatial.get("prefLabel") or ""
        else:
            spatial_value = spatial

        access = first_value(ds.get("accessRestriction", [])) or {}
        use = first_value(ds.get("useRestriction", [])) or {}
        dictionary = ds.get("describedBy") or {}
        landing = ds.get("landingPage") or {}

        row = {
            "catalog_bureau": bureau,
            "catalog_contact_name": catalog_contact.get("name", ""),
            "catalog_contact_email": catalog_contact.get("email", ""),
            "catalog_contact_phone": catalog_contact.get("phone", ""),
            "catalog_contact_organization": catalog_contact.get("organization", ""),
            "dataset_title": ds.get("title", ""),
            "dataset_description": ds.get("description", ""),
            "dataset_identifier": ds.get("identifier", ""),
            "publisher_office": (ds.get("publisher") or {}).get("name", ""),
            "dataset_contact_name": ds_contact.get("name", ""),
            "dataset_contact_email": ds_contact.get("email", ""),
            "dataset_contact_phone": ds_contact.get("phone", ""),
            "dataset_contact_organization": ds_contact.get("organization", ""),
            "keywords": "; ".join(str(x) for x in ds.get("keyword", []) or []),
            "themes": "; ".join(theme_names),
            "theme_descriptions": "",
            "access_rights": ds.get("accessRights", ""),
            "has_access_restriction": "Yes" if access else "No",
            "access_restriction_status": access.get("restrictionStatus", ""),
            "access_specific_restriction": "; ".join(split_cell(access.get("specificRestriction", ""))),
            "access_restriction_note": access.get("restrictionNote", ""),
            "has_cui": "Yes" if ds.get("CUIRestriction") else "No",
            "cui_banner": (ds.get("CUIRestriction") or {}).get("cuiBannerMarking", ""),
            "cui_designation": (ds.get("CUIRestriction") or {}).get("designationIndicator", ""),
            "has_use_restriction": "Yes" if use or ds.get("license") or ds.get("rights") else "No",
            "restriction_types": "; ".join(
                x for x in [
                    "Use restriction" if use else "",
                    "License" if ds.get("license") else "",
                    "Rights" if ds.get("rights") else "",
                ] if x
            ),
            "use_status": use.get("restrictionStatus", ""),
            "specific_use": "; ".join(split_cell(use.get("specificRestriction", ""))),
            "use_note": use.get("restrictionNote", ""),
            "license": ds.get("license", ""),
            "rights": "; ".join(split_cell(ds.get("rights", ""))),
            "temporal_start": (temporal or {}).get("startDate", ""),
            "temporal_end": (temporal or {}).get("endDate", ""),
            "spatial_granularity": ds.get("spatialGranularity", ""),
            "spatial_granularity_other": "",
            "spatial": spatial_value,
            "modified": ds.get("modified", ""),
            "has_dictionary": "Yes" if dictionary else "No",
            "dictionary_url": dictionary.get("accessURL", "") if isinstance(dictionary, dict) else "",
            "dictionary_format": dictionary.get("format", "") if isinstance(dictionary, dict) else "",
            "has_landing_page": "Yes" if landing else "No",
            "landing_page": landing.get("accessURL", "") if isinstance(landing, dict) else "",
            "contract_number": ds.get("contractNumber", ""),
        }
        rows.append(row)

    # A catalog with no datasets still gets one blank row so the user can start.
    if not rows:
        rows.append({
            q["column"]: "" for q in QUESTION_DEFINITIONS
        })
        rows[0]["catalog_bureau"] = bureau

    return rows


def build_excel_workbook(catalog=None):
    wb = Workbook()
    data_ws = wb.active
    data_ws.title = "Data Entry"
    dict_ws = wb.create_sheet("Data Dictionary")
    instructions_ws = wb.create_sheet("Instructions")
    lists_ws = wb.create_sheet("Lists")

    columns = [q["column"] for q in QUESTION_DEFINITIONS]

    # Data entry
    data_ws.append(columns)
    rows = catalog_to_excel_rows(catalog or {})
    for row in rows:
        data_ws.append([row.get(col, "") for col in columns])

    style_sheet(
        data_ws,
        [22 if i == 1 else 18 for i in range(len(columns))]
    )

    # Dropdowns
    for idx, q in enumerate(QUESTION_DEFINITIONS, start=1):
        if q["type"] == "Dropdown" and q["options"]:
            add_dropdown(data_ws, idx, q["options"])

    # Dictionary
    dict_ws.append([
        "Column name",
        "Full question / field",
        "Expected / example response",
        "Input type",
        "Dropdown / allowed options",
        "Required?",
        "Scope",
    ])
    for q in QUESTION_DEFINITIONS:
        dict_ws.append([
            q["column"],
            q["question"],
            q["expected"],
            q["type"],
            "; ".join(q["options"]),
            q["required"],
            q["scope"],
        ])
    style_sheet(dict_ws, [28, 58, 60, 20, 65, 18, 15])

    # Instructions
    instructions = [
        ["DCAT-US 3.0 Excel Mode"],
        ["How to use this workbook"],
        ["1. Fill out one row per dataset on the Data Entry sheet."],
        ["2. Do not rename columns."],
        ["3. Use semicolons (;) to separate multiple keywords, themes, restrictions, or rule types."],
        ["4. Dropdown columns contain controlled values. The complete options are also listed in Data Dictionary."],
        ["5. dataset_identifier is automatically assigned for new datasets. Leave it blank for new datasets."],
        ["6. If you enter a new theme, also enter its description in theme_descriptions using the same order."],
        ["7. Contact information is stored back into contacts.json when it is not already present."],
        ["8. New keywords are added to tags.json."],
        ["9. New themes are added to themes.json."],
        ["10. Conditional questions only need values when their parent Yes/No or type selection makes them applicable."],
        ["11. After filling this workbook, upload it back into the app to create the DCAT-US JSON."],
        ["12. The app will validate required fields and date formats before creating JSON."],
    ]
    for row in instructions:
        instructions_ws.append(row)
    instructions_ws.column_dimensions["A"].width = 110
    instructions_ws["A1"].font = Font(size=18, bold=True, color="005EA8")
    instructions_ws["A2"].font = Font(size=13, bold=True)
    for row in instructions_ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
    instructions_ws.freeze_panes = "A3"

    # Hidden list sheet
    lists_ws.sheet_state = "hidden"

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue()


# ============================================================
# EXCEL IMPORT / VALIDATION
# ============================================================

def read_excel_rows(uploaded_file):
    wb = load_workbook(uploaded_file, data_only=True)
    if "Data Entry" not in wb.sheetnames:
        raise ValueError('The workbook must contain a sheet named "Data Entry".')

    ws = wb["Data Entry"]
    headers = [cell.value for cell in ws[1]]
    expected = [q["column"] for q in QUESTION_DEFINITIONS]

    if headers != expected:
        missing = [x for x in expected if x not in headers]
        extra = [x for x in headers if x not in expected]
        problems = []
        if missing:
            problems.append("Missing columns: " + ", ".join(missing))
        if extra:
            problems.append("Unexpected columns: " + ", ".join(extra))
        raise ValueError(
            "The Data Entry sheet does not match the template. "
            + " ".join(problems)
        )

    rows = []
    for values in ws.iter_rows(min_row=2, values_only=True):
        row = dict(zip(headers, values))
        if any(v not in (None, "") for v in row.values()):
            rows.append({k: "" if v is None else str(v).strip() for k, v in row.items()})

    return rows


def validate_excel_rows(rows):
    errors = []

    for row_num, row in enumerate(rows, start=2):
        required = [
            ("catalog_bureau", "Bureau"),
            ("catalog_contact_name", "Catalog contact name"),
            ("dataset_title", "Dataset title"),
            ("dataset_description", "Dataset description"),
            ("publisher_office", "Publishing office"),
            ("dataset_contact_name", "Dataset contact name"),
            ("keywords", "Keywords"),
            ("themes", "Themes"),
            ("access_rights", "Access rights"),
            ("has_access_restriction", "Access restriction Yes/No"),
            ("has_cui", "CUI Yes/No"),
            ("has_use_restriction", "Use restriction Yes/No"),
            ("temporal_start", "Temporal start"),
            ("temporal_end", "Temporal end"),
            ("spatial", "Geographic coverage"),
            ("modified", "Modified date"),
        ]
        for key, label in required:
            if not normalize_text(row.get(key)):
                errors.append(f"Row {row_num}: {label} is required.")

        bureau = row.get("catalog_bureau", "")
        if bureau and bureau not in BUREAUS:
            errors.append(f"Row {row_num}: '{bureau}' is not a recognized bureau.")

        for key, label in [
            ("temporal_start", "Temporal start"),
            ("temporal_end", "Temporal end"),
            ("modified", "Modified date"),
        ]:
            if row.get(key) and not is_valid_dcat_date(row[key]):
                errors.append(
                    f"Row {row_num}: {label} must be YYYY, YYYY-MM, or YYYY-MM-DD."
                )

        if row.get("has_access_restriction") == "Yes":
            if not row.get("access_restriction_status"):
                errors.append(f"Row {row_num}: access restriction status is required.")
            if not split_cell(row.get("access_specific_restriction")):
                errors.append(f"Row {row_num}: specific access restriction is required.")

        if row.get("has_cui") == "Yes":
            if not row.get("cui_banner"):
                errors.append(f"Row {row_num}: CUI banner marking is required.")
            if not row.get("cui_designation"):
                errors.append(f"Row {row_num}: CUI designation is required.")

        if row.get("has_use_restriction") == "Yes":
            types = split_cell(row.get("restriction_types"))
            if not types:
                errors.append(f"Row {row_num}: restriction type is required.")
            if "Use restriction" in types:
                if not row.get("use_status"):
                    errors.append(f"Row {row_num}: use restriction status is required.")
                if not split_cell(row.get("specific_use")):
                    errors.append(f"Row {row_num}: specific use restriction is required.")
            if "License" in types and not row.get("license"):
                errors.append(f"Row {row_num}: license is required.")
            if "Rights" in types and not row.get("rights"):
                errors.append(f"Row {row_num}: rights is required.")

        if row.get("spatial_granularity") == "Other" and not row.get("spatial_granularity_other"):
            errors.append(f"Row {row_num}: specify the other spatial granularity.")

        if row.get("has_dictionary") == "Yes":
            if not row.get("dictionary_url"):
                errors.append(f"Row {row_num}: data dictionary URL is required.")
            if not row.get("dictionary_format"):
                errors.append(f"Row {row_num}: data dictionary format is required.")

        if row.get("has_landing_page") == "Yes" and not row.get("landing_page"):
            errors.append(f"Row {row_num}: landing page URL is required.")

    return errors


def build_catalog_from_excel(rows):
    if not rows:
        raise ValueError("The workbook contains no data rows.")

    # Catalog fields are taken from the first row; users normally repeat them
    # because the workbook is intentionally flat.
    first = rows[0]
    bureau_name = first["catalog_bureau"]
    bureau_info = BUREAUS[bureau_name]

    catalog_contact = {
        "name": first["catalog_contact_name"],
        "email": first["catalog_contact_email"],
        "phone": first["catalog_contact_phone"],
        "organization": first["catalog_contact_organization"],
    }
    ensure_contact_in_database(catalog_contact, bureau_name)

    datasets = []

    # Continue identifiers after the largest existing numeric identifier.
    used_numbers = []
    for row in rows:
        identifier = row.get("dataset_identifier", "")
        m = re.search(r"-(\d{6})$", identifier)
        if m:
            used_numbers.append(int(m.group(1)))
    next_number = max(used_numbers, default=0) + 1

    for row in rows:
        identifier = row.get("dataset_identifier", "")
        m = re.search(r"-(\d{6})$", identifier)
        if m:
            dataset_number = int(m.group(1))
        else:
            dataset_number = next_number
            next_number += 1

        keywords = split_cell(row["keywords"])
        themes = split_cell(row["themes"])
        theme_descriptions = split_cell(row.get("theme_descriptions", ""))

        ensure_tags_in_database(keywords)
        ensure_themes_in_database(themes, theme_descriptions)

        dataset_contact = {
            "name": row["dataset_contact_name"],
            "email": row["dataset_contact_email"],
            "phone": row["dataset_contact_phone"],
            "organization": row["dataset_contact_organization"] or row["publisher_office"],
        }
        ensure_contact_in_database(dataset_contact, bureau_name)

        access_restriction = None
        if row["has_access_restriction"] == "Yes":
            access_restriction = {
                "restrictionStatus": row["access_restriction_status"],
                "specificRestriction": split_cell(row["access_specific_restriction"]),
                "restrictionNote": row.get("access_restriction_note", ""),
            }

        cui_restriction = None
        if row["has_cui"] == "Yes":
            cui_restriction = {
                "cuiBannerMarking": row["cui_banner"],
                "designationIndicator": row["cui_designation"],
            }

        use_restriction = None
        types = split_cell(row.get("restriction_types", ""))
        if "Use restriction" in types:
            use_restriction = {
                "restrictionStatus": row["use_status"],
                "specificRestriction": split_cell(row["specific_use"]),
                "restrictionNote": row.get("use_note", ""),
            }

        data_dictionary = None
        if row.get("has_dictionary") == "Yes":
            data_dictionary = {
                "url": row["dictionary_url"],
                "format": row["dictionary_format"],
            }

        spatial_granularity = row.get("spatial_granularity", "")
        if spatial_granularity == "Other":
            spatial_granularity = row.get("spatial_granularity_other", "")

        dataset = build_dataset(
            bureau_info=bureau_info,
            dataset_number=dataset_number,
            title=row["dataset_title"],
            description=row["dataset_description"],
            office=row["publisher_office"],
            contact_name=dataset_contact["name"],
            contact_email=dataset_contact["email"],
            contact_phone=dataset_contact["phone"],
            contact_organization=dataset_contact["organization"],
            keywords=keywords,
            themes=themes,
            access_rights=row["access_rights"],
            access_restriction=access_restriction,
            cui_restriction=cui_restriction,
            use_restriction=use_restriction,
            license=row.get("license", ""),
            rights=split_cell(row.get("rights", "")),
            temporal_start=row["temporal_start"],
            temporal_end=row["temporal_end"],
            spatial=row["spatial"],
            modified=row["modified"],
            data_dictionary=data_dictionary,
            landing_page=row.get("landing_page", "") if row.get("has_landing_page") == "Yes" else "",
            spatial_granularity=spatial_granularity,
            contract_number=row.get("contract_number", ""),
            existing_identifier=identifier or None,
        )
        datasets.append(dataset)

    return build_catalog(
        bureau_info=bureau_info,
        catalog_contact_name=catalog_contact["name"],
        catalog_contact_email=catalog_contact["email"],
        catalog_contact_phone=catalog_contact["phone"],
        catalog_contact_organization=catalog_contact["organization"],
        datasets=datasets,
    )


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "datasets": [],
    "current_dataset": 1,
    "mode": None,
    "catalog_loaded": False,
    "uploaded_catalog": None,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# HEADER
# ============================================================

st.title("DCAT-US 3.0 Metadata Builder")
st.write(
    "Build DCAT-US 3.0 metadata either with the guided form or by "
    "downloading and completing an Excel workbook."
)


# ============================================================
# STEP 1 — EXISTING JSON
# ============================================================

st.markdown("## 1. Start with an existing catalog")

existing_choice = st.radio(
    "Do you have an existing catalog JSON file?",
    ["No, start a new catalog", "Yes, upload an existing catalog"],
    horizontal=True,
    key="existing_choice",
)

if existing_choice.startswith("Yes"):
    uploaded_json = st.file_uploader(
        "Upload your existing catalog JSON",
        type=["json"],
        key="existing_json_upload",
    )

    if uploaded_json:
        try:
            catalog = json.load(uploaded_json)
            st.session_state.uploaded_catalog = catalog
            st.session_state.catalog_loaded = True
            st.session_state.datasets = catalog.get("dataset", []) or []
            st.session_state.current_dataset = len(st.session_state.datasets) + 1
            st.success(
                f"Loaded {len(st.session_state.datasets)} existing dataset(s)."
            )
        except Exception as exc:
            st.error(f"The uploaded file could not be read as JSON: {exc}")


# ============================================================
# STEP 2 — MODE
# ============================================================

st.markdown("## 2. Choose how you want to enter metadata")

mode = st.radio(
    "Do you want to use Excel mode?",
    [
        "No, guide me through the questions in this web app",
        "Yes, use Excel mode",
    ],
    horizontal=True,
    key="entry_mode",
)

if mode.startswith("Yes"):
    st.session_state.mode = "excel"
    st.markdown("### Excel mode")

    st.write(
        "Download the workbook, fill out one row per dataset, and upload it "
        "back here. The workbook contains a Data Entry sheet and a Data "
        "Dictionary with the full question, examples, input type, options, "
        "and required/optional status."
    )

    if st.session_state.uploaded_catalog:
        excel_seed = st.session_state.uploaded_catalog
    else:
        excel_seed = {}

    workbook_bytes = build_excel_workbook(excel_seed)

    st.download_button(
        "⬇ Download Excel Template",
        data=workbook_bytes,
        file_name="dcat_us_3_metadata_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_excel_template",
    )

    st.markdown("---")
    completed_excel = st.file_uploader(
        "Upload your completed Excel workbook",
        type=["xlsx"],
        key="completed_excel",
    )

    if completed_excel:
        try:
            excel_rows = read_excel_rows(completed_excel)
            errors = validate_excel_rows(excel_rows)

            if errors:
                st.error("Please fix these issues in the workbook before importing:")
                for error in errors:
                    st.write(f"• {error}")
            else:
                if st.button("Convert Excel to DCAT-US JSON", type="primary"):
                    catalog = build_catalog_from_excel(excel_rows)
                    st.session_state.excel_catalog_result = catalog
                    st.session_state.excel_rows = excel_rows
                    st.success("Excel successfully converted to DCAT-US 3.0 JSON.")

        except Exception as exc:
            st.error(f"Could not read the Excel workbook: {exc}")

    if "excel_catalog_result" in st.session_state:
        catalog = st.session_state.excel_catalog_result

        st.markdown("### JSON output")

        st.download_button(
            "⬇ Download Catalog JSON",
            data=json.dumps(catalog, indent=2, ensure_ascii=False),
            file_name="data.json",
            mime="application/json",
            key="download_excel_json",
        )

        st.json(catalog)

    st.info(
        "Excel mode intentionally skips the Additional DCAT-US Properties "
        "question for this phase."
    )

    st.stop()


# ============================================================
# GUIDED MODE
# ============================================================

st.session_state.mode = "guided"

st.markdown("## Guided mode")
st.caption(
    "This keeps the current question-by-question workflow. The Additional "
    "DCAT-US Properties section is intentionally excluded in this phase."
)


# ------------------------------------------------------------
# Catalog / bureau
# ------------------------------------------------------------

catalog_seed = st.session_state.uploaded_catalog or {}
inferred_bureau = infer_bureau(catalog_seed)

bureau_names = list(BUREAUS.keys())
bureau_default = bureau_names.index(inferred_bureau) if inferred_bureau in bureau_names else 0

selected_bureau = st.selectbox(
    "Which bureau are you submitting metadata for? **(Required)**",
    bureau_names,
    index=bureau_default,
)
bureau_info = BUREAUS[selected_bureau]

catalog_contact_seed = contact_from_dataset(
    {"contactPoint": catalog_seed.get("contactPoint", [])}
)

st.markdown("### Catalog contact")
catalog_contact_name = st.text_input(
    "Who should be contacted with questions about this catalog? — Contact name **(Required)**",
    value=catalog_contact_seed.get("name", ""),
)
catalog_contact_email = st.text_input(
    "Catalog contact email",
    value=catalog_contact_seed.get("email", ""),
)
catalog_contact_phone = st.text_input(
    "Catalog contact phone",
    value=catalog_contact_seed.get("phone", ""),
)
catalog_contact_organization = st.text_input(
    "Catalog contact organization",
    value=catalog_contact_seed.get("organization", bureau_info["publisher"]),
)


# ------------------------------------------------------------
# Dataset loop
# ------------------------------------------------------------

existing_datasets = st.session_state.datasets or []

if existing_datasets:
    st.info(
        f"{len(existing_datasets)} dataset(s) were loaded from the existing JSON. "
        "The guided form is primarily intended for editing/continuing the catalog."
    )

dataset_number = st.session_state.current_dataset
seed = (
    existing_datasets[dataset_number - 1]
    if len(existing_datasets) >= dataset_number
    else {}
)

seed_contact = contact_from_dataset(seed)
seed_temporal = first_value(seed.get("temporal", [])) or {}
seed_spatial = first_value(seed.get("spatial", [])) or {}
seed_access = first_value(seed.get("accessRestriction", [])) or {}
seed_use = first_value(seed.get("useRestriction", [])) or {}
seed_cui = seed.get("CUIRestriction") or {}
seed_dictionary = seed.get("describedBy") or {}
seed_landing = seed.get("landingPage") or {}

st.markdown(f"## Dataset {dataset_number}")

title = st.text_input(
    "What is the dataset called? **(Required)**",
    value=seed.get("title", ""),
)
description = st.text_area(
    "Dataset description in plain language. **(Required)**",
    value=seed.get("description", ""),
    height=160,
)

identifier = seed.get("identifier", f"{bureau_info['identifier_code']}-{dataset_number:06d}")
st.markdown(
    f'<div class="saved-indicator">Automatically assigned identifier: '
    f'<strong>{identifier}</strong></div>',
    unsafe_allow_html=True,
)

publisher_office = st.text_input(
    "Which office publishes these data? **(Required)**",
    value=(seed.get("publisher") or {}).get("name", ""),
)

st.markdown("### Dataset contact")
dataset_contact_name = st.text_input(
    "Best dataset contact — Name **(Required)**",
    value=seed_contact.get("name", ""),
)
dataset_contact_email = st.text_input(
    "Dataset contact email",
    value=seed_contact.get("email", ""),
)
dataset_contact_phone = st.text_input(
    "Dataset contact phone",
    value=seed_contact.get("phone", ""),
)
dataset_contact_organization = st.text_input(
    "Dataset contact organization",
    value=seed_contact.get("organization", publisher_office or bureau_info["publisher"]),
)

tags_db = sorted(set(normalize_text(x) for x in load_json_file(TAGS_FILE, []) if normalize_text(x)))
seed_keywords = [str(x) for x in seed.get("keyword", []) or []]

keywords = st.multiselect(
    "What words would someone use to search for these data? **(Required)**",
    tags_db,
    default=[x for x in seed_keywords if x in tags_db],
)
new_keywords = st.text_input(
    "Add new keywords (optional, semicolon-separated)",
    placeholder="trade; exports; employment",
)
keywords = list(dict.fromkeys(keywords + split_cell(new_keywords)))
if new_keywords:
    ensure_tags_in_database(split_cell(new_keywords))

themes_db = load_json_file(THEMES_FILE, [])
theme_names = [normalize_text(x.get("name", "")) for x in themes_db if normalize_text(x.get("name", ""))]
seed_themes = []
for x in seed.get("theme", []) or []:
    if isinstance(x, dict):
        seed_themes.append(normalize_text(x.get("prefLabel") or x.get("name", "")))
    else:
        seed_themes.append(normalize_text(x))

themes = st.multiselect(
    "What theme does this dataset belong to? **(Required)**",
    theme_names,
    default=[x for x in seed_themes if x in theme_names],
)
new_themes = st.text_input(
    "Add new themes (optional, semicolon-separated)",
    placeholder="climate; public health",
)
new_theme_descriptions = st.text_area(
    "Descriptions for new themes (same order, semicolon-separated)",
    placeholder="Description for climate; Description for public health",
)
themes = list(dict.fromkeys(themes + split_cell(new_themes)))
if new_themes:
    try:
        ensure_themes_in_database(themes, split_cell(new_theme_descriptions))
    except ValueError:
        pass


# Access
st.markdown("### Access & Restrictions")

access_rights = st.selectbox(
    "Who is allowed to access these data? **(Required)**",
    ACCESS_RIGHTS_OPTIONS,
    index=(
        ACCESS_RIGHTS_OPTIONS.index(seed.get("accessRights"))
        if seed.get("accessRights") in ACCESS_RIGHTS_OPTIONS else 0
    ),
)

has_access_restriction = st.radio(
    "Are there any restrictions on getting these data? **(Required)**",
    YES_NO,
    index=1 if seed_access else 0,
    horizontal=True,
)

access_restriction = None
if has_access_restriction == "Yes":
    access_status = st.selectbox(
        "What is the data restriction status? **(Required)**",
        ACCESS_STATUS_OPTIONS,
        index=(
            ACCESS_STATUS_OPTIONS.index(seed_access.get("restrictionStatus"))
            if seed_access.get("restrictionStatus") in ACCESS_STATUS_OPTIONS else 0
        ),
    )
    access_specific = st.multiselect(
        "What is the specific access restriction? **(Required)**",
        SPECIFIC_ACCESS_OPTIONS,
        default=split_cell(seed_access.get("specificRestriction", "")),
    )
    access_note = st.text_area(
        "Additional information about the restriction (Optional)",
        value=seed_access.get("restrictionNote", ""),
    )
    access_restriction = {
        "restrictionStatus": access_status,
        "specificRestriction": access_specific,
        "restrictionNote": access_note,
    }


# CUI
st.markdown("### Controlled Unclassified Information")

has_cui = st.radio(
    "Does the dataset contain Controlled Unclassified Information (CUI)? **(Required)**",
    YES_NO,
    index=1 if seed_cui else 0,
    horizontal=True,
)
cui_restriction = None
if has_cui == "Yes":
    cui_banner = st.selectbox(
        "Which CUI Banner Marking are these data associated with? **(Required)**",
        CUI_OPTIONS,
        index=CUI_OPTIONS.index(seed_cui.get("cuiBannerMarking"))
        if seed_cui.get("cuiBannerMarking") in CUI_OPTIONS else 0,
    )
    cui_designation = st.text_area(
        "Which agency designated the information as CUI? Include contact information when possible. **(Required)**",
        value=seed_cui.get("designationIndicator", ""),
    )
    cui_restriction = {
        "cuiBannerMarking": cui_banner,
        "designationIndicator": cui_designation,
    }


# Use restrictions
st.markdown("### Use Restrictions")

has_use_restriction = st.radio(
    "Are there any other rules about how these data may be used, such as use restriction, license, or rights? **(Required)**",
    YES_NO,
    index=1 if seed_use or seed.get("license") or seed.get("rights") else 0,
    horizontal=True,
)

use_restriction = None
license_value = seed.get("license", "")
rights_value = "; ".join(split_cell(seed.get("rights", "")))

if has_use_restriction == "Yes":
    default_types = []
    if seed_use:
        default_types.append("Use restriction")
    if seed.get("license"):
        default_types.append("License")
    if seed.get("rights"):
        default_types.append("Rights")

    restriction_types = st.multiselect(
        "What type of rule applies? **(Required)**",
        USE_TYPE_OPTIONS,
        default=default_types,
    )

    if "Use restriction" in restriction_types:
        use_status = st.selectbox(
            "Use restriction status **(Required)**",
            ACCESS_STATUS_OPTIONS,
            index=(
                ACCESS_STATUS_OPTIONS.index(seed_use.get("restrictionStatus"))
                if seed_use.get("restrictionStatus") in ACCESS_STATUS_OPTIONS else 0
            ),
        )
        specific_use = st.multiselect(
            "Specific use restriction **(Required)**",
            SPECIFIC_USE_OPTIONS,
            default=split_cell(seed_use.get("specificRestriction", "")),
        )
        use_note = st.text_area(
            "Use restriction note (Optional)",
            value=seed_use.get("restrictionNote", ""),
        )
        use_restriction = {
            "restrictionStatus": use_status,
            "specificRestriction": specific_use,
            "restrictionNote": use_note,
        }

    if "License" in restriction_types:
        license_value = st.text_input(
            "What license applies to these data? **(Required)**",
            value=license_value,
        )

    if "Rights" in restriction_types:
        rights_value = st.text_area(
            "What other rights have not been covered? **(Required)**",
            value=rights_value,
        )


# Coverage
st.markdown("### Coverage & Dates")

temporal_start = st.text_input(
    "Start date **(Required)**",
    value=seed_temporal.get("startDate", ""),
    placeholder="YYYY, YYYY-MM, or YYYY-MM-DD",
)
temporal_end = st.text_input(
    "End date **(Required)**",
    value=seed_temporal.get("endDate", ""),
    placeholder="YYYY, YYYY-MM, or YYYY-MM-DD",
)

spatial_granularity = st.selectbox(
    "Spatial Granularity",
    [""] + SPATIAL_GRANULARITY_OPTIONS,
    index=(
        ([""] + SPATIAL_GRANULARITY_OPTIONS).index(seed.get("spatialGranularity"))
        if seed.get("spatialGranularity") in ([""] + SPATIAL_GRANULARITY_OPTIONS)
        else 0
    ),
)
spatial_granularity_other = ""
if spatial_granularity == "Other":
    spatial_granularity_other = st.text_input(
        "Specify other spatial granularity",
        value=seed.get("spatialGranularity", ""),
    )

spatial_value = (
    seed_spatial.get("name")
    if isinstance(seed_spatial, dict)
    else str(seed_spatial or "")
)
spatial = st.text_input(
    "Geographic coverage **(Required)**",
    value=spatial_value,
    placeholder="Example: United States, Washington, DC, or worldwide",
)

modified = st.text_input(
    "When were these data last changed? **(Required)**",
    value=seed.get("modified", ""),
    placeholder="YYYY, YYYY-MM, or YYYY-MM-DD",
)


# Optional documentation
st.markdown("### Documentation")

has_dictionary = st.radio(
    "Does this dataset have a data dictionary? **(Optional)**",
    YES_NO,
    index=1 if seed_dictionary else 0,
    horizontal=True,
)
dictionary_url = ""
dictionary_format = ""
if has_dictionary == "Yes":
    dictionary_url = st.text_input(
        "Data dictionary URL **(Required)**",
        value=seed_dictionary.get("accessURL", ""),
    )
    dictionary_format = st.text_input(
        "Data dictionary format **(Required)**",
        value=seed_dictionary.get("format", ""),
        placeholder="HTML, PDF, CSV, XLSX",
    )

has_landing_page = st.radio(
    "Is there a webpage/landing page to get the data from? **(Optional)**",
    YES_NO,
    index=1 if seed_landing else 0,
    horizontal=True,
)
landing_page = ""
if has_landing_page == "Yes":
    landing_page = st.text_input(
        "Landing page URL **(Required)**",
        value=seed_landing.get("accessURL", ""),
    )

contract_number = st.text_input(
    "Contract number by which these data were acquired (Optional)",
    value=seed.get("contractNumber", ""),
    max_chars=40,
)


# ------------------------------------------------------------
# Save / catalog
# ------------------------------------------------------------

st.markdown("---")

if st.button(f"Save Dataset {dataset_number}", type="primary"):
    required = {
        "Dataset title": title,
        "Dataset description": description,
        "Publishing office": publisher_office,
        "Dataset contact": dataset_contact_name,
        "Keywords": keywords,
        "Themes": themes,
        "Temporal start": temporal_start,
        "Temporal end": temporal_end,
        "Geographic coverage": spatial,
        "Modified date": modified,
    }

    missing = [k for k, v in required.items() if not v]
    invalid_dates = [
        label
        for label, value in [
            ("Temporal start", temporal_start),
            ("Temporal end", temporal_end),
            ("Modified date", modified),
        ]
        if value and not is_valid_dcat_date(value)
    ]

    conditional_errors = []
    if has_cui == "Yes" and (not cui_restriction or not cui_restriction["cuiBannerMarking"] or not cui_restriction["designationIndicator"]):
        conditional_errors.append("CUI banner marking and designation are required.")
    if has_dictionary == "Yes" and (not dictionary_url or not dictionary_format):
        conditional_errors.append("Data dictionary URL and format are required.")
    if has_landing_page == "Yes" and not landing_page:
        conditional_errors.append("Landing page URL is required.")
    if has_access_restriction == "Yes" and (
        not access_restriction
        or not access_restriction["restrictionStatus"]
        or not access_restriction["specificRestriction"]
    ):
        conditional_errors.append("Access restriction status and specific restriction are required.")
    if has_use_restriction == "Yes":
        if "Use restriction" in restriction_types and (
            not use_restriction
            or not use_restriction["restrictionStatus"]
            or not use_restriction["specificRestriction"]
        ):
            conditional_errors.append("Use restriction status and specific restriction are required.")
        if "License" in restriction_types and not license_value:
            conditional_errors.append("License is required when License is selected.")
        if "Rights" in restriction_types and not rights_value:
            conditional_errors.append("Rights are required when Rights is selected.")

    if missing:
        st.error("Please complete the required fields: " + ", ".join(missing))
    elif invalid_dates:
        st.error("Please correct these date fields: " + ", ".join(invalid_dates))
    elif conditional_errors:
        for error in conditional_errors:
            st.error(error)
    else:
        ensure_tags_in_database(keywords)
        ensure_themes_in_database(themes, [])

        ensure_contact_in_database(
            {
                "name": catalog_contact_name,
                "email": catalog_contact_email,
                "phone": catalog_contact_phone,
                "organization": catalog_contact_organization,
            },
            selected_bureau,
        )
        ensure_contact_in_database(
            {
                "name": dataset_contact_name,
                "email": dataset_contact_email,
                "phone": dataset_contact_phone,
                "organization": dataset_contact_organization or publisher_office,
            },
            selected_bureau,
        )

        data_dictionary = (
            {"url": dictionary_url, "format": dictionary_format}
            if has_dictionary == "Yes"
            else None
        )

        dataset = build_dataset(
            bureau_info=bureau_info,
            dataset_number=dataset_number,
            title=title,
            description=description,
            office=publisher_office,
            contact_name=dataset_contact_name,
            contact_email=dataset_contact_email,
            contact_phone=dataset_contact_phone,
            contact_organization=dataset_contact_organization or publisher_office,
            keywords=keywords,
            themes=themes,
            access_rights=access_rights,
            access_restriction=access_restriction,
            cui_restriction=cui_restriction,
            use_restriction=use_restriction,
            license=license_value,
            rights=split_cell(rights_value),
            temporal_start=temporal_start,
            temporal_end=temporal_end,
            spatial=spatial,
            modified=modified,
            data_dictionary=data_dictionary,
            landing_page=landing_page,
            spatial_granularity=(
                spatial_granularity_other
                if spatial_granularity == "Other"
                else spatial_granularity
            ),
            contract_number=contract_number,
            existing_identifier=identifier if identifier else None,
        )

        while len(st.session_state.datasets) <= dataset_number - 1:
            st.session_state.datasets.append({})

        st.session_state.datasets[dataset_number - 1] = dataset
        st.success(f"Dataset {dataset_number} saved successfully.")

if (
    len(st.session_state.datasets) >= dataset_number
    and st.session_state.datasets[dataset_number - 1]
):
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("＋ Add Another Dataset"):
            st.session_state.current_dataset += 1
            st.rerun()

    with col2:
        catalog = build_catalog(
            bureau_info=bureau_info,
            catalog_contact_name=catalog_contact_name,
            catalog_contact_email=catalog_contact_email,
            catalog_contact_phone=catalog_contact_phone,
            catalog_contact_organization=catalog_contact_organization,
            datasets=st.session_state.datasets,
        )
        st.download_button(
            "⬇ Download Catalog JSON",
            data=json.dumps(catalog, indent=2, ensure_ascii=False),
            file_name="data.json",
            mime="application/json",
        )

    st.markdown("### Catalog Preview")
    catalog = build_catalog(
        bureau_info=bureau_info,
        catalog_contact_name=catalog_contact_name,
        catalog_contact_email=catalog_contact_email,
        catalog_contact_phone=catalog_contact_phone,
        catalog_contact_organization=catalog_contact_organization,
        datasets=st.session_state.datasets,
    )
    st.json(catalog)
