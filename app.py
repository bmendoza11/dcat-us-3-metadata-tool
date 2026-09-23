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


has_dictionary = st.radio(
    "Does this dataset have a data dictionary? "
    "**(Optional)**",
    [
        "No",
        "Yes"
    ],
    horizontal=True,
    key=f"has_dictionary_{dataset_number}"
)

data_dictionary = None


if has_dictionary == "Yes":

    dictionary_url = st.text_input(
        "Data dictionary URL **(Required)**",
        key=f"dictionary_url_{dataset_number}"
    )

    dictionary_format = st.text_input(
        "Data dictionary format **(Required)**",
        placeholder="Example: HTML, PDF, CSV, XLSX",
        key=f"dictionary_format_{dataset_number}"
    )

    if dictionary_url:

        data_dictionary = {
            "url": dictionary_url,
            "format": dictionary_format
        }


# ============================================================
# Q18 LANDING PAGE
# ============================================================

has_landing_page = st.radio(
    "Is there a webpage/landing page to get the "
    "data from? **(Optional)**",
    [
        "No",
        "Yes"
    ],
    horizontal=True,
    key=f"has_landing_page_{dataset_number}"
)

landing_page = None


if has_landing_page == "Yes":

    landing_page = st.text_input(
        "Landing page URL **(Required)**",
        key=f"landing_page_{dataset_number}"
    )


# ============================================================
# Q19 CONTRACT NUMBER
# ============================================================

contract_number = st.text_input(
    "Contract number by which these data were acquired (Optional)",
    max_chars=40,
    placeholder="Up to 40 characters",
    key=f"contract_number_{dataset_number}"
)

# ============================================================
# Q20 ADDITIONAL DCAT-US PROPERTIES
# ============================================================

st.markdown(
    '<div class="section-header">'
    '<h2>Additional DCAT-US Properties</h2>'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="question-help">
    <strong>Optional:</strong> Add any DCAT-US 3.0 dataset properties that
    were not collected in the questions above.
    <br><br>
    Select a property to see what it means and what kind of value it expects.
    For properties that require a structured DCAT-US object or array, you can
    enter the value as JSON.
    </div>
    """,
    unsafe_allow_html=True
)

# These are the Dataset properties documented by resources.data.gov that
# are not already collected by the questions above.
#
# Source:
# https://resources.data.gov/standards/catalog/dcat-us-3/dataset/
#
# "input" controls the UI:
#   text       = one string / URI / date / duration
#   select     = controlled value
#   json       = object or array of DCAT-US values
#   json_array = array of simple values
#
# The descriptions and examples below follow the DCAT-US 3.0 Dataset
# reference on resources.data.gov.
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
        "help": (
            "resources.data.gov also permits ISO 8601 recurring values "
            "(for example, R/P1Y) and Dublin Core frequency terms. "
            "Use JSON mode below if you need one of those values."
        ),
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
        "description": (
            "Quality measurements for the dataset, such as completeness, "
            "accuracy, or timeliness."
        ),
        "input": "json",
        "example": (
            '[{"@type": "QualityMeasurement", '
            '"value": 0.98}]'
        ),
    },
    "hasVersion": {
        "label": "hasVersion",
        "description": "Related datasets that are versions, editions, or adaptations of this dataset.",
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
        "description": "Links to related resources that reference or cite the dataset.",
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
        "description": (
            "A statement about limitations of responsibility, accuracy, "
            "reliability, completeness, or endorsement."
        ),
        "input": "text",
        "placeholder": "Enter the liability statement.",
    },
    "metadataDistribution": {
        "label": "metadataDistribution",
        "description": "Distribution of the original metadata document from which this dataset metadata was derived.",
        "input": "json",
        "example": (
            '[{"@type": "Distribution", '
            '"accessURL": "https://example.gov/metadata/data.json", '
            '"mediaType": "application/json"}]'
        ),
    },
    "otherIdentifier": {
        "label": "otherIdentifier",
        "description": "Additional identifiers, such as a DOI or other persistent identifier.",
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
        "description": (
            "A detailed relationship between the dataset and another "
            "resource, including the role of that relationship."
        ),
        "input": "json",
        "example": (
            '[{"@type": "Relationship", '
            '"hadRole": {"@type": "Concept", "prefLabel": "source"}}]'
        ),
    },
    "relation": {
        "label": "relation",
        "description": "Links to related resources when the relationship is not otherwise specified.",
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
        "description": (
            "The lifecycle status of the dataset, such as completed, "
            "deprecated, under development, or withdrawn."
        ),
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
        "example": '{"@type": "Dataset", "@id": "https://example.gov/schema"}',
    },
    "temporalResolution": {
        "label": "temporalResolution",
        "description": "The smallest time interval between data points, using xsd:duration format.",
        "input": "text",
        "placeholder": "Example: P1D",
    },
    "version": {
        "label": "version",
        "description": "The version indicator or identifier of the resource.",
        "input": "text",
        "placeholder": "Example: 2024.1",
    },
    "versionNotes": {
        "label": "versionNotes",
        "description": "Notes describing how this version differs from earlier versions.",
        "input": "text",
        "placeholder": "Describe the changes in this version.",
    },
    "wasAttributedTo": {
        "label": "wasAttributedTo",
        "description": "Agents attributed to this dataset.",
        "input": "json",
        "example": '[{"@type": "Agent", "name": "Example Agency"}]',
    },
    "wasGeneratedBy": {
        "label": "wasGeneratedBy",
        "description": "Activities that generated or provide business context for creation of the dataset.",
        "input": "json",
        "example": '[{"@type": "Activity", "name": "Example project"}]',
    },
    "wasUsedBy": {
        "label": "wasUsedBy",
        "description": "Activities that used the dataset.",
        "input": "json",
        "example": '[{"@type": "Activity", "name": "Example analysis"}]',
    },
}

# Keep this list synchronized with the definitions above. The existing
# questions already collect these properties, so they should not appear
# in the additional-property selector.
ADDITIONAL_PROPERTY_OPTIONS = [
    property_name
    for property_name in ADDITIONAL_PROPERTY_DEFINITIONS
    if property_name not in {
        "title",
        "description",
        "identifier",
        "publisher",
        "contactPoint",
        "keyword",
        "theme",
        "accessRights",
        "accessRestriction",
        "cuiRestriction",
        "useRestriction",
        "license",
        "rights",
        "temporal",
        "spatial",
        "modified",
        "describedBy",
        "landingPage",
    }
]

additional_key = f"additional_properties_{dataset_number}"

if additional_key not in st.session_state:
    st.session_state[additional_key] = {}

saved_additional = st.session_state[additional_key]

# Show properties already added to this dataset.
if saved_additional:
    st.markdown("**Properties added to this dataset**")

    for property_name, property_value in saved_additional.items():
        display_value = json.dumps(
            property_value,
            ensure_ascii=False
        )

        col_property, col_remove = st.columns([5, 1])

        with col_property:
            st.markdown(
                f"""
                <div class="saved-indicator">
                <strong>{property_name}</strong><br>
                <code>{display_value}</code>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_remove:
            st.write("")
            if st.button(
                "Remove",
                key=f"remove_additional_{dataset_number}_{property_name}"
            ):
                del saved_additional[property_name]
                st.session_state[additional_key] = saved_additional
                st.rerun()

    st.markdown("")

available_properties = [
    property_name
    for property_name in ADDITIONAL_PROPERTY_OPTIONS
    if property_name not in saved_additional
]

if available_properties:

    selected_additional_property = st.selectbox(
        "Select a DCAT-US property to add",
        ["Select a property"] + sorted(available_properties),
        key=f"additional_property_{dataset_number}"
    )

    if selected_additional_property != "Select a property":

        property_definition = ADDITIONAL_PROPERTY_DEFINITIONS[
            selected_additional_property
        ]

        st.markdown(
            f"**{property_definition['label']}**"
        )

        st.caption(
            property_definition["description"]
        )

        input_type = property_definition["input"]

        if input_type == "select":

            selected_additional_value = st.selectbox(
                "Value",
                property_definition["options"],
                key=f"additional_select_{dataset_number}"
            )

            if property_definition.get("help"):
                st.caption(property_definition["help"])

        elif input_type == "json":

            example = property_definition.get(
                "example",
                "{}"
            )

            st.caption(
                "This property expects a structured DCAT-US value. "
                "Enter valid JSON."
            )

            selected_additional_value = st.text_area(
                "Value (JSON)",
                placeholder=example,
                height=150,
                key=f"additional_json_{dataset_number}"
            )

            with st.expander("Show example"):
                st.code(example, language="json")

        elif input_type == "json_array":

            example = property_definition.get(
                "example",
                "[]"
            )

            st.caption(
                "This property expects an array. "
                "Enter a JSON array, for example [\"value1\", \"value2\"]."
            )

            selected_additional_value = st.text_area(
                "Value (JSON array)",
                placeholder=example,
                height=120,
                key=f"additional_json_array_{dataset_number}"
            )

            with st.expander("Show example"):
                st.code(example, language="json")

        else:

            selected_additional_value = st.text_input(
                "Value",
                placeholder=property_definition.get(
                    "placeholder",
                    ""
                ),
                key=f"additional_text_{dataset_number}"
            )

        if st.button(
            "＋ Add Property",
            key=f"add_property_{dataset_number}"
        ):

            raw_value = str(
                selected_additional_value
            ).strip()

            if not raw_value:

                st.warning(
                    "Enter a value before adding this property."
                )

            else:

                final_value = raw_value

                # Parse structured values so the generated dataset contains
                # actual JSON arrays/objects rather than strings containing
                # JSON text.
                if input_type in {"json", "json_array"}:

                    try:

                        final_value = json.loads(
                            raw_value
                        )

                    except json.JSONDecodeError as error:

                        st.error(
                            "The value is not valid JSON. "
                            f"Check the brackets, quotes, and commas. "
                            f"Details: {error.msg}"
                        )

                        final_value = None

                    if (
                        final_value is not None
                        and input_type == "json_array"
                        and not isinstance(final_value, list)
                    ):

                        st.error(
                            "This property expects a JSON array, "
                            "such as [\"value1\", \"value2\"]."
                        )

                        final_value = None

                if final_value is not None:

                    saved_additional[
                        selected_additional_property
                    ] = final_value

                    st.session_state[
                        additional_key
                    ] = saved_additional

                    st.success(
                        f"✓ {selected_additional_property} "
                        "was added to this dataset."
                    )

                    st.rerun()

else:

    st.success(
        "✓ All available additional Dataset properties "
        "have been added."
    )

st.markdown(
    """
    <div class="question-help">
    <strong>Important:</strong> This section follows the DCAT-US 3.0
    Dataset property definitions in <a href="https://resources.data.gov/standards/catalog/dcat-us-3/dataset/" target="_blank">resources.data.gov</a>.
    Structured properties are entered as JSON so that objects and arrays
    remain correctly typed in the generated metadata. The tool checks that
    JSON is syntactically valid, but it does not perform full DCAT-US schema
    validation.
    </div>
    """,
    unsafe_allow_html=True
)

st.warning(
    "After generating your catalog, validate the complete JSON against "
    "the DCAT-US 3.0 schema before publishing."
)

# ============================================================
# SAVE DATASET
# ============================================================

st.markdown("---")

if st.button(
    f"Save Dataset {dataset_number}",
    key=f"save_dataset_{dataset_number}"
):

    selected_keywords = st.session_state.get(
        keyword_state_key,
        []
    )

    selected_theme_values = st.session_state.get(
        theme_state_key,
        []
    )

    required_fields = {
        "Dataset title": title,
        "Dataset description": description,
        "Publishing office": publisher_office,
        "Dataset contact": contact_name,
        "Keywords": selected_keywords,
        "Themes": selected_theme_values,
        "Temporal start": temporal_start,
        "Temporal end": temporal_end,
        "Spatial coverage": spatial,
        "Modified date": modified
    }

    invalid_dates = []
    if temporal_start and not is_valid_dcat_date(temporal_start):
        invalid_dates.append("Temporal start")
    if temporal_end and not is_valid_dcat_date(temporal_end):
        invalid_dates.append("Temporal end")
    if modified and not is_valid_dcat_date(modified):
        invalid_dates.append("Modified date")

    missing = [
        name
        for name, value
        in required_fields.items()
        if not value
    ]

    if missing:

        st.error(
            "Please complete these required fields:"
        )

        for field in missing:
            st.write(f"• {field}")

    elif invalid_dates:

        st.error(
            "Please correct the following date fields before saving:"
        )

        for field in invalid_dates:
            st.write(f"• {field}")

    else:

        dataset = build_dataset(
            bureau_info=bureau_info,
            dataset_number=dataset_number,
            title=title,
            description=description,
            office=publisher_office,
            contact_name=contact_name,
            contact_email=contact_email,
            contact_phone=contact_phone,
            contact_organization=contact_organization,
            keywords=selected_keywords,
            themes=selected_theme_values,
            access_rights=access_rights,
            access_restriction=access_restriction,
            cui_restriction=cui_restriction,
            use_restriction=use_restriction,
            license=license,
            rights=rights,
            temporal_start=temporal_start,
            temporal_end=temporal_end,
            spatial=spatial,
            modified=modified,
            data_dictionary=data_dictionary,
            landing_page=landing_page,
            spatial_granularity=(
                spatial_other
                if spatial_granularity == "Other"
                else spatial_granularity
            ),
            contract_number=contract_number,
            additional_properties=saved_additional
        )

        dataset_index = (
            dataset_number - 1
        )

        while len(
            st.session_state.datasets
        ) <= dataset_index:

            st.session_state.datasets.append({})

        st.session_state.datasets[
            dataset_index
        ] = dataset

        st.success(
            f"✓ Dataset {dataset_number} "
            "saved successfully!"
        )


# ============================================================
# ADD DATASET / DOWNLOAD
# ============================================================

if (
    len(st.session_state.datasets)
    >= dataset_number
    and st.session_state.datasets[
        dataset_number - 1
    ]
):

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "＋ Add Another Dataset",
            key=f"add_dataset_{dataset_number}"
        ):

            st.session_state.current_dataset += 1

            st.rerun()

    with col2:

        catalog = build_catalog(
            bureau_info=bureau_info,
            catalog_contact_name=(
                catalog_contact_name
            ),
            catalog_contact_email=(
                catalog_contact_email
            ),
            catalog_contact_phone=(
                catalog_contact_phone
            ),
            catalog_contact_organization=(
                catalog_contact_organization
            ),
            datasets=(
                st.session_state.datasets
            )
        )

        st.warning(
            "Before using or publishing this JSON, validate it with the "
            "Data.gov DCAT-US 3.0 validator: "
            "https://harvest.data.gov/validate/"
        )

        st.download_button(
            "Download Catalog JSON",
            data=json.dumps(
                catalog,
                indent=2,
                ensure_ascii=False
            ),
            file_name="data.json",
            mime="application/json"
        )


# ============================================================
# CATALOG PREVIEW
# ============================================================

if st.session_state.datasets:

    st.warning(
        "Before using or publishing this JSON, validate it with the "
        "Data.gov DCAT-US 3.0 validator: "
        "https://harvest.data.gov/validate/"
    )

    st.markdown("---")

    st.markdown(
        '<div class="section-header">'
        '<h2>Catalog Preview</h2>'
        '</div>',
        unsafe_allow_html=True
    )

    catalog = build_catalog(
        bureau_info=bureau_info,
        catalog_contact_name=catalog_contact_name,
        catalog_contact_email=catalog_contact_email,
        catalog_contact_phone=catalog_contact_phone,
        catalog_contact_organization=(
            catalog_contact_organization
        ),
        datasets=st.session_state.datasets
    )

    st.json(catalog)
