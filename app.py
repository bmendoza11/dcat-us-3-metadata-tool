import streamlit as st
import json
import os
import datetime
import re

from dcat_builder import build_dataset, build_catalog


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="DCAT-US 3.0 Metadata Builder",
    page_icon="📊",
    layout="wide",
)


# ============================================================
# FILE LOCATIONS
# ============================================================

CONTACTS_FILE = "contacts.json"
TAGS_FILE = "tags.json"
THEMES_FILE = "themes.json"


# ============================================================
# LIGHT BLUE / WHITE STYLING
# ============================================================

st.markdown(
    """
    <style>
    div[data-testid="stVerticalBlock"] > div {
        margin-bottom: 20px;
        margin-top: 20px;
    }

    html, body,
    [data-testid="stApp"],
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    section.main,
    .main,
    .block-container {
        background: #ffffff !important;
        color: #222222 !important;
    }

    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"] {
        background: #ffffff !important;
    }

    h1, h2, h3, h4, h5, h6,
    p, label,
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
    [data-testid="stNumberInput"] [data-baseweb="input"],
    [data-testid="stNumberInput"] [data-baseweb="input"] > div,
    [data-testid="stDateInput"] [data-baseweb="input"],
    [data-testid="stDateInput"] [data-baseweb="input"] > div,
    [data-testid="stSelectbox"] [data-baseweb="select"],
    [data-testid="stSelectbox"] [data-baseweb="select"] > div,
    [data-testid="stMultiSelect"] [data-baseweb="select"],
    [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
        background: #ffffff !important;
        background-color: #ffffff !important;
        border-color: #b8b8b8 !important;
        box-shadow: none !important;
    }

    input,
    textarea {
        background: #ffffff !important;
        color: #222222 !important;
        -webkit-text-fill-color: #222222 !important;
        caret-color: #222222 !important;
    }

    input::placeholder,
    textarea::placeholder {
        color: #777777 !important;
        -webkit-text-fill-color: #777777 !important;
    }

    [data-baseweb="popover"],
    [data-baseweb="popover"] > div,
    [data-baseweb="menu"],
    [role="listbox"] {
        background: #ffffff !important;
        background-color: #ffffff !important;
        color: #222222 !important;
    }

    [role="option"] {
        background: #ffffff !important;
        color: #222222 !important;
    }

    [role="option"]:hover,
    [role="option"][aria-selected="true"] {
        background: #eaf3fb !important;
        color: #005ea8 !important;
    }

    [data-testid="stMultiSelect"] span[data-baseweb="tag"] {
        background: #eaf3fb !important;
        color: #005ea8 !important;
    }

    [data-testid="stMultiSelect"] span[data-baseweb="tag"] * {
        color: #005ea8 !important;
        -webkit-text-fill-color: #005ea8 !important;
    }

    .stButton > button,
    .stDownloadButton > button {
        background: #005ea8 !important;
        background-color: #005ea8 !important;
        color: #ffffff !important;
        border: 1px solid #005ea8 !important;
        box-shadow: none !important;
    }

    .stButton > button *,
    .stDownloadButton > button * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background: #004b87 !important;
        background-color: #004b87 !important;
    }

    [data-testid="stExpander"],
    [data-testid="stExpander"] details,
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary > div {
        background: #ffffff !important;
        background-color: #ffffff !important;
        color: #222222 !important;
        border-color: #dddddd !important;
    }

    [data-testid="stAlert"] {
        background: #f8f9fa !important;
        color: #222222 !important;
        border-color: #d6d6d6 !important;
    }

    [data-testid="stJson"],
    [data-testid="stCode"],
    pre,
    code {
        background: #f7f7f7 !important;
        background-color: #f7f7f7 !important;
        color: #222222 !important;
    }

    hr {
        border-color: #dddddd !important;
    }

    a {
        color: #005ea8 !important;
    }

    .section-header {
        margin-top: 25px;
        margin-bottom: 15px;
    }

    .question-help {
        background: #f4f9fd;
        border-left: 4px solid #005ea8;
        padding: 12px 16px;
        margin: 10px 0 20px 0;
        color: #333333;
    }

    .saved-indicator {
        background: #eef8f0;
        border-left: 4px solid #2e7d32;
        padding: 10px 14px;
        margin: 8px 0;
        color: #1b5e20;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# JSON HELPERS
# ============================================================

def load_json_file(filename, default):
    if not os.path.exists(filename):
        return default

    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return default


def save_json_file(filename, data):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
        )


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_text(value):
    if not value:
        return ""

    return str(value).strip().lower()


def normalize_tag(value):
    return normalize_text(value)


def normalize_theme_name(value):
    return normalize_text(value)


# ============================================================
# DATE VALIDATION
# ============================================================

def is_valid_dcat_date(value):
    """
    Allow:
      YYYY
      YYYY-MM
      YYYY-MM-DD

    and validate real month/day values.
    """

    value = normalize_text(value)

    if not value:
        return True

    if re.fullmatch(r"\d{4}", value):
        return True

    if re.fullmatch(r"\d{4}-\d{2}", value):
        year, month = map(int, value.split("-"))
        return 1 <= month <= 12

    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        try:
            datetime.date.fromisoformat(value)
            return True
        except ValueError:
            return False

    return False


def validate_date_field(label, value):
    if value and not is_valid_dcat_date(value):
        st.warning(
            f"{label} must use YYYY, YYYY-MM, or YYYY-MM-DD."
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
# CONTACT HELPERS
# ============================================================

def normalize_bureau(value):
    if not value:
        return ""

    value = str(value).strip().lower()

    value = re.sub(r"\s*\([^)]*\)", "", value)

    census_variants = {
        "census bureau": "united states census bureau",
        "u.s. census bureau": "united states census bureau",
        "us census bureau": "united states census bureau",
    }

    value = census_variants.get(value, value)

    value = value.replace(
        "united states patent and trademark office",
        "patent and trademark office",
    )

    return value


def get_contacts_for_bureau(contacts, selected_bureau):
    selected_normalized = normalize_bureau(selected_bureau)

    matching_contacts = []

    for contact in contacts:
        contact_bureau = normalize_bureau(
            contact.get("bureau", "")
        )

        contact_organization = normalize_bureau(
            contact.get("organization", "")
        )

        if (
            contact_bureau == selected_normalized
            or contact_organization == selected_normalized
        ):
            matching_contacts.append(contact)

    return matching_contacts


def contact_display(contact):
    name = contact.get("name", "Unnamed contact")
    organization = contact.get("organization", "")
    email = contact.get("email", "")

    if organization and email:
        return f"{name} — {organization} — {email}"

    if organization:
        return f"{name} — {organization}"

    if email:
        return f"{name} — {email}"

    return name


def default_contact_index(options):
    preferred_terms = (
        "call center",
        "contact center",
        "customer service",
        "customer contact",
        "information center",
        "general information",
        "information services",
    )

    for index, option in enumerate(options):
        normalized = normalize_text(option)

        if any(
            term in normalized
            for term in preferred_terms
        ):
            return index

    return 0


def save_contact(
    selected_bureau,
    name,
    email,
    phone,
    organization,
):
    contacts = load_json_file(
        CONTACTS_FILE,
        [],
    )

    contacts.append(
        {
            "bureau": selected_bureau,
            "name": name.strip(),
            "email": email.strip(),
            "phone": phone.strip(),
            "organization": organization.strip(),
        }
    )

    save_json_file(
        CONTACTS_FILE,
        contacts,
    )


# ============================================================
# ADDITIONAL DCAT-US PROPERTY DEFINITIONS
# ============================================================

ADDITIONAL_PROPERTY_DEFINITIONS = {
    "@id": {
        "label": "@id",
        "description": "A URI identifying the Dataset.",
        "input": "text",
        "placeholder": "https://example.gov/datasets/example",
    },
    "accrualPeriodicity": {
        "label": "accrualPeriodicity",
        "description": "The frequency at which the Dataset is updated.",
        "input": "select",
        "options": [
            "continual",
            "daily",
            "weekly",
            "fortnightly",
            "monthly",
            "quarterly",
            "biannually",
            "annually",
            "asNeeded",
            "irregular",
            "notPlanned",
            "unknown",
        ],
    },
    "category": {
        "label": "category",
        "description": "High-level categories for the dataset.",
        "input": "json",
        "example": '[{"@type": "Concept", "prefLabel": "Climate"}]',
    },
    "conformsTo": {
        "label": "conformsTo",
        "description": "Standards, schemas, or profiles the dataset follows.",
        "input": "json",
        "example": (
            '[{"@type": "Standard", "title": "DCAT-US 3.0", '
            '"identifier": "https://resources.data.gov/dcat-us/3.0.0"}]'
        ),
    },
    "contributor": {
        "label": "contributor",
        "description": "Agents that contributed to the Dataset.",
        "input": "json",
        "example": '[{"@type": "Agent", "name": "Example Agency"}]',
    },
    "created": {
        "label": "created",
        "description": "The date on which the Dataset was first created.",
        "input": "text",
        "placeholder": "YYYY, YYYY-MM, or YYYY-MM-DD",
    },
    "creator": {
        "label": "creator",
        "description": "The person or organization responsible for creating the dataset.",
        "input": "json",
        "example": '{"@type": "Agent", "name": "Example Agency"}',
    },
    "first": {
        "label": "first",
        "description": "The first Dataset in the sequence to which this dataset belongs.",
        "input": "json",
        "example": '{"@type": "Dataset", "@id": "https://example.gov/datasets/2000"}',
    },
    "hasCurrentVersion": {
        "label": "hasCurrentVersion",
        "description": "Reference to the current/latest version of the dataset.",
        "input": "json",
        "example": '{"@type": "Dataset", "@id": "https://example.gov/datasets/example-v2"}',
    },
    "hasPart": {
        "label": "hasPart",
        "description": "Related datasets that are part of this dataset.",
        "input": "json",
        "example": '[{"@type": "Dataset", "@id": "https://example.gov/datasets/part-1"}]',
    },
    "hasQualityMeasurement": {
        "label": "hasQualityMeasurement",
        "description": "Quality measurements for the dataset.",
        "input": "json",
        "example": '[{"@type": "QualityMeasurement", "value": 0.98}]',
    },
    "hasVersion": {
        "label": "hasVersion",
        "description": "Related datasets that are versions or editions of this dataset.",
        "input": "json",
        "example": '[{"@type": "Dataset", "@id": "https://example.gov/datasets/example-v2"}]',
    },
    "image": {
        "label": "image",
        "description": "A thumbnail image illustrating the dataset.",
        "input": "text",
        "placeholder": "https://example.gov/images/dataset.png",
    },
    "isReferencedBy": {
        "label": "isReferencedBy",
        "description": "Resources that reference or cite the dataset.",
        "input": "json_array",
        "example": '["https://example.gov/publications/report.pdf"]',
    },
    "issued": {
        "label": "issued",
        "description": "The date when the dataset was first published.",
        "input": "text",
        "placeholder": "YYYY, YYYY-MM, or YYYY-MM-DD",
    },
    "language": {
        "label": "language",
        "description": "ISO 639-1 language code(s), such as en or es.",
        "input": "json_array",
        "example": '["en"]',
    },
    "liabilityStatement": {
        "label": "liabilityStatement",
        "description": "A statement about limitations of responsibility or accuracy.",
        "input": "text",
        "placeholder": "Enter the liability statement.",
    },
    "metadataDistribution": {
        "label": "metadataDistribution",
        "description": "Distribution of the metadata document from which the metadata was derived.",
        "input": "json",
        "example": (
            '[{"@type": "Distribution", '
            '"accessURL": "https://example.gov/metadata/data.json", '
            '"mediaType": "application/json"}]'
        ),
    },
    "otherIdentifier": {
        "label": "otherIdentifier",
        "description": "Additional identifiers such as a DOI.",
        "input": "json",
        "example": '[{"notation": "10.1234/example"}]',
    },
    "page": {
        "label": "page",
        "description": "Pages or documents about the dataset.",
        "input": "json",
        "example": (
            '[{"@type": "Document", '
            '"accessURL": "https://example.gov/about-dataset"}]'
        ),
    },
    "previousVersion": {
        "label": "previousVersion",
        "description": "Reference to the previous version of the dataset.",
        "input": "json",
        "example": '{"@type": "Dataset", "@id": "https://example.gov/datasets/example-v1"}',
    },
    "provenance": {
        "label": "provenance",
        "description": "Statements about the lineage of the dataset.",
        "input": "json_array",
        "example": '["Derived from administrative records collected by Example Agency."]',
    },
    "purpose": {
        "label": "purpose",
        "description": "The purpose of the dataset.",
        "input": "text",
        "placeholder": "Describe why the dataset was created.",
    },
    "qualifiedAttribution": {
        "label": "qualifiedAttribution",
        "description": "Agents with specific responsibilities for the dataset.",
        "input": "json",
        "example": (
            '[{"@type": "Attribution", '
            '"agent": {"@type": "Agent", "name": "Example Agency"}}]'
        ),
    },
    "qualifiedRelation": {
        "label": "qualifiedRelation",
        "description": "A detailed relationship between the dataset and another resource.",
        "input": "json",
        "example": (
            '[{"@type": "Relationship", '
            '"hadRole": {"@type": "Concept", "prefLabel": "source"}}]'
        ),
    },
    "relation": {
        "label": "relation",
        "description": "Links to related resources.",
        "input": "json_array",
        "example": '["https://example.gov/related-resource"]',
    },
    "replaces": {
        "label": "replaces",
        "description": "Datasets replaced by this dataset.",
        "input": "json",
        "example": '[{"@type": "Dataset", "@id": "https://example.gov/datasets/old"}]',
    },
    "rightsHolder": {
        "label": "rightsHolder",
        "description": "Organizations holding rights on the dataset.",
        "input": "json",
        "example": '[{"@type": "Organization", "name": "Example Agency"}]',
    },
    "sample": {
        "label": "sample",
        "description": "Sample distributions for the dataset.",
        "input": "json",
        "example": (
            '[{"@type": "Distribution", '
            '"accessURL": "https://example.gov/sample.csv", '
            '"mediaType": "text/csv"}]'
        ),
    },
    "scopeNote": {
        "label": "scopeNote",
        "description": "A usage note for the dataset.",
        "input": "text",
        "placeholder": "Enter a note about the scope of the dataset.",
    },
    "source": {
        "label": "source",
        "description": "Datasets from which this dataset was derived.",
        "input": "json",
        "example": '[{"@type": "Dataset", "@id": "https://example.gov/datasets/source"}]',
    },
    "spatialResolutionInMeters": {
        "label": "spatialResolutionInMeters",
        "description": "The smallest spatial distance between data points, in meters.",
        "input": "text",
        "placeholder": "Example: 100",
    },
    "status": {
        "label": "status",
        "description": "The lifecycle status of the dataset.",
        "input": "json",
        "example": '{"@type": "Concept", "prefLabel": "completed"}',
    },
    "subject": {
        "label": "subject",
        "description": "Primary subjects for the dataset.",
        "input": "json",
        "example": '[{"@type": "Concept", "prefLabel": "Employment"}]',
    },
    "supportedSchema": {
        "label": "supportedSchema",
        "description": "The schema supported by the dataset.",
        "input": "json",
        "example": '{"@type": "Dataset", "@id": "https://example
