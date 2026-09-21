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
    layout="wide"
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
# Keep Streamlit/BaseWeb components light even when the user's
# system/browser preference is dark mode.
st.markdown(
    """
    <style>
    div[data-testid="stVerticalBlock"] > div {
    margin-bottom: 26px;
    }
    html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"],
    [data-testid="stMain"], section.main, .main, .block-container {
        background: #ffffff !important;
        color: #222222 !important;
    }

    /* Top-level Streamlit chrome */
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"] {
        background: #ffffff !important;
    }

    /* Text */
    h1, h2, h3, h4, h5, h6, p, label,
    [data-testid="stMarkdownContainer"],
    [data-testid="stCaptionContainer"] {
        color: #222222 !important;
    }

    h1, h2, h3 {
        color: #005ea8 !important;
    }

    /* Inputs: force every nested BaseWeb layer to white */
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

    /* Dropdown popup */
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

    /* Multiselect chips */
    [data-testid="stMultiSelect"] span[data-baseweb="tag"] {
        background: #eaf3fb !important;
        color: #005ea8 !important;
    }

    [data-testid="stMultiSelect"] span[data-baseweb="tag"] * {
        color: #005ea8 !important;
        -webkit-text-fill-color: #005ea8 !important;
    }

    /* Buttons */
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

    /* Expander */
    [data-testid="stExpander"],
    [data-testid="stExpander"] details,
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary > div {
        background: #ffffff !important;
        background-color: #ffffff !important;
        color: #222222 !important;
        border-color: #dddddd !important;
    }

    /* Alerts/messages should stay light */
    [data-testid="stAlert"] {
        background: #f8f9fa !important;
        color: #222222 !important;
        border-color: #d6d6d6 !important;
    }

    /* JSON/code output */
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
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# JSON HELPERS
# ============================================================

def load_json_file(filename, default):

    if not os.path.exists(filename):
        return default

    try:
        with open(
            filename,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)

    except Exception:
        return default


def save_json_file(filename, data):

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_text(value):

    if not value:
        return ""

    return (
        str(value)
        .strip()
        .lower()
    )


def normalize_tag(value):

    return normalize_text(value)


def normalize_theme_name(value):

    return normalize_text(value)


# ============================================================
# DATE VALIDATION
# ============================================================

def is_valid_dcat_date(value):
    """Allow YYYY, YYYY-MM, or YYYY-MM-DD and validate real dates."""
    value = normalize_text(value)
    if not value:
        return True

    if re.fullmatch(r"\\d{4}", value):
        return True

    if re.fullmatch(r"\\d{4}-\\d{2}", value):
        year, month = map(int, value.split("-"))
        return 1 <= month <= 12

    if re.fullmatch(r"\\d{4}-\\d{2}-\\d{2}", value):
        try:
            datetime.date.fromisoformat(value)
            return True
        except ValueError:
            return False

    return False


def validate_date_field(label, value):
    if value and not is_valid_dcat_date(value):
        st.warning(
            f"{label} must use YYYY, YYYY-MM, or YYYY-MM-DD. "
            "Please correct the format before saving."
        )


# ============================================================
# DCAT-US DATASET PROPERTIES
# ============================================================

DCAT_DATASET_PROPERTIES = [
    "accessRights", "accessRestriction", "accrualPeriodicity",
    "category", "conformsTo", "contributor", "created", "creator",
    "description", "distribution", "first", "hasCurrentVersion",
    "hasPart", "hasQualityMeasurement", "hasVersion", "image",
    "inventoried", "isReferencedBy", "issued", "keyword", "language",
    "landingPage", "liabilityStatement", "metadataDistribution",
    "modified", "otherIdentifier", "page", "previousVersion",
    "provenance", "purpose", "qualifiedAttribution", "qualifiedRelation",
    "relation", "replaces", "rights", "rightsHolder", "sample",
    "scopeNote", "source", "spatial", "spatialResolutionInMeters",
    "status", "subject", "supportedSchema", "temporal",
    "temporalResolution", "theme", "title", "useRestriction",
    "version", "versionNotes", "wasAttributedTo", "wasGeneratedBy",
    "wasUsedBy", "cuiRestriction", "describedBy", "identifier",
    "license", "publisher", "contactPoint",
]

ADDITIONAL_PROPERTY_OPTIONS = [
    p for p in DCAT_DATASET_PROPERTIES
    if p not in {
        "title", "description", "identifier", "publisher", "contactPoint",
        "keyword", "theme", "accessRights", "accessRestriction",
        "cuiRestriction", "useRestriction", "license", "rights",
        "temporal", "spatial", "modified", "describedBy", "landingPage",
    }
]


# ============================================================
# CONTACT HELPERS
# ============================================================

def normalize_bureau(value):

    """
    Makes bureau names comparable.

    Examples:

    Bureau of Economic Analysis
    Bureau of Economic Analysis (BEA)

    become comparable.
    """

    if not value:
        return ""

    value = str(value).strip().lower()

    # Remove parenthetical acronym.
    value = re.sub(
        r"\s*\([^)]*\)",
        "",
        value
    )

    # Normalize common Census naming differences.
    census_variants = {
        "census bureau":
            "united states census bureau",

        "u.s. census bureau":
            "united states census bureau",

        "us census bureau":
            "united states census bureau"
    }

    value = census_variants.get(
        value,
        value
    )

    # Remove "united states" from USPTO
    # only for comparison purposes.
    value = value.replace(
        "united states patent and trademark office",
        "patent and trademark office"
    )

    return value


# ============================================================
# CONTACT HELPERS
# ============================================================

def get_contacts_for_bureau(
    contacts,
    selected_bureau
):

    selected_normalized = normalize_bureau(
        selected_bureau
    )

    matching_contacts = []

    for contact in contacts:

        contact_bureau = normalize_bureau(
            contact.get("bureau", "")
        )

        contact_organization = normalize_bureau(
            contact.get("organization", "")
        )

        # Match either the bureau field OR
        # the organization field.
        if (
            contact_bureau == selected_normalized
            or
            contact_organization == selected_normalized
        ):

            matching_contacts.append(
                contact
            )

    return matching_contacts


def contact_display(contact):

    name = contact.get(
        "name",
        "Unnamed contact"
    )

    organization = contact.get(
        "organization",
        ""
    )

    email = contact.get(
        "email",
        ""
    )

    if organization and email:
        return (
            f"{name} — "
            f"{organization} — "
            f"{email}"
        )

    if organization:
        return (
            f"{name} — {organization}"
        )

    return name


def default_contact_index(options):
    """
    Prefer a bureau's general call/customer/information center
    when one is available. The first option remains the manual
    "Select" option when no general contact is present.
    """
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
        if any(term in normalized for term in preferred_terms):
            return index

    return 0


# ============================================================
# SAVE CONTACT
# ============================================================

def save_contact(
    selected_bureau,
    name,
    email,
    phone,
    organization
):

    contacts = load_json_file(
        CONTACTS_FILE,
        []
    )

    new_contact = {
        "bureau": selected_bureau,
        "name": name.strip(),
        "email": email.strip(),
        "phone": phone.strip(),
        "organization": organization.strip()
    }

    contacts.append(
        new_contact
    )

    save_json_file(
        CONTACTS_FILE,
        contacts
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
        "homepage": "https://www.bea.gov/"
    },

    "Bureau of Industry and Security": {
        "publisher": "Bureau of Industry and Security",
        "identifier_code": "BIS",
        "bureauCode": ["006:03"],
        "programCode": ["006:000"],
        "homepage": "https://www.bis.gov/"
    },

    "Bureau of Labor Statistics": {
        "publisher": "Bureau of Labor Statistics",
        "identifier_code": "BLS",
        "bureauCode": ["006:04"],
        "programCode": ["006:000"],
        "homepage": "https://www.bls.gov/"
    },

    "Census Bureau": {
        "publisher": "United States Census Bureau",
        "identifier_code": "CEN",
        "bureauCode": ["006:07"],
        "programCode": ["006:000"],
        "homepage": "https://www.census.gov/"
    },

    "Economic Development Administration": {
        "publisher": "Economic Development Administration",
        "identifier_code": "EDA",
        "bureauCode": ["006:08"],
        "programCode": ["006:000"],
        "homepage": "https://www.eda.gov/"
    },

    "International Trade Administration": {
        "publisher": "International Trade Administration",
        "identifier_code": "ITA",
        "bureauCode": ["006:13"],
        "programCode": ["006:000"],
        "homepage": "https://www.trade.gov/"
    },

    "National Oceanic and Atmospheric Administration": {
        "publisher": "National Oceanic and Atmospheric Administration",
        "identifier_code": "NOAA",
        "bureauCode": ["006:20"],
        "programCode": ["006:000"],
        "homepage": "https://www.noaa.gov/"
    },

    "National Institute of Standards and Technology": {
        "publisher": "National Institute of Standards and Technology",
        "identifier_code": "NIST",
        "bureauCode": ["006:19"],
        "programCode": ["006:000"],
        "homepage": "https://www.nist.gov/"
    },

    "National Technical Information Service": {
        "publisher": "National Technical Information Service",
        "identifier_code": "NTIS",
        "bureauCode": ["006:21"],
        "programCode": ["006:000"],
        "homepage": "https://www.ntis.gov/"
    },

    "Patent and Trademark Office": {
        "publisher": "United States Patent and Trademark Office",
        "identifier_code": "USPTO",
        "bureauCode": ["006:25"],
        "programCode": ["006:000"],
        "homepage": "https://www.uspto.gov/"
    },

    "National Telecommunications and Information Administration": {
        "publisher": "National Telecommunications and Information Administration",
        "identifier_code": "NTIA",
        "bureauCode": ["006:18"],
        "programCode": ["006:000"],
        "homepage": "https://www.ntia.gov/"
    }
}


# ============================================================
# SESSION STATE
# ============================================================

if "datasets" not in st.session_state:
    st.session_state.datasets = []

if "current_dataset" not in st.session_state:
    st.session_state.current_dataset = 1

if "bureau" not in st.session_state:
    st.session_state.bureau = None


# ============================================================
# HEADER
# ============================================================

st.title(
    "DCAT-US 3.0 Metadata Builder"
)

st.write(
    "Build a DCAT-US 3.0 catalog by answering "
    "questions about each dataset."
)


# ============================================================
# EXISTING CATALOG
# ============================================================

st.markdown(
    '<div class="section-header">'
    '<h2>Start a Catalog</h2>'
    '</div>',
    unsafe_allow_html=True
)

existing_catalog = st.radio(
    "Do you have an existing catalog JSON file?",
    [
        "No — start a new catalog",
        "Yes — upload an existing catalog"
    ],
    horizontal=True
)


if existing_catalog.startswith("Yes"):

    uploaded_file = st.file_uploader(
        "Upload your existing catalog JSON",
        type=["json"]
    )

    if uploaded_file:

        try:

            uploaded_catalog = json.load(
                uploaded_file
            )

            existing_datasets = (
                uploaded_catalog.get(
                    "dataset",
                    []
                )
            )

            st.session_state.datasets = (
                existing_datasets
            )

            # Continue numbering after the
            # last existing dataset.
            st.session_state.current_dataset = (
                len(existing_datasets) + 1
            )

            st.success(
                f"✓ Loaded {len(existing_datasets)} "
                "existing dataset(s)."
            )

        except Exception:

            st.error(
                "The uploaded file could not be "
                "read as JSON."
            )


# ============================================================
# BUREAU
# ============================================================

st.markdown(
    '<div class="section-header">'
    '<h2>1. Bureau Information</h2>'
    '</div>',
    unsafe_allow_html=True
)

bureau_names = list(
    BUREAUS.keys()
)

selected_bureau = st.selectbox(
    "Which bureau are you submitting metadata for? "
    "**(Required)**",
    bureau_names
)

st.session_state.bureau = selected_bureau

bureau_info = BUREAUS[
    selected_bureau
]


# ============================================================
# CATALOG INFORMATION
# ============================================================

st.markdown(
    '<div class="section-header">'
    '<h2>2. Catalog Information</h2>'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div class="question-help">
    <strong>Catalog name:</strong>
    {bureau_info['publisher']} Data Catalog
    <br><br>
    <strong>Description:</strong>
    These data are cataloged by {bureau_info['publisher']}.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CATALOG CONTACT
# ============================================================

contacts = load_json_file(
    CONTACTS_FILE,
    []
)

bureau_contacts = get_contacts_for_bureau(
    contacts,
    selected_bureau
)

catalog_contact_options = [
    "Select a catalog contact",
    "＋ Add a new contact"
]

catalog_contact_options.extend(
    [
        contact_display(contact)
        for contact in bureau_contacts
    ]
)

catalog_contact_choice = st.selectbox(
    "Who should be contacted with questions "
    "about this catalog? **(Required)**",
    catalog_contact_options,
    index=default_contact_index(catalog_contact_options),
    key=f"catalog_contact_{normalize_text(selected_bureau)}"
)


catalog_contact_name = ""
catalog_contact_email = ""
catalog_contact_phone = ""
catalog_contact_organization = ""


if catalog_contact_choice == "＋ Add a new contact":

    catalog_contact_name = st.text_input(
        "Contact name",
        key="catalog_new_name"
    )

    catalog_contact_email = st.text_input(
        "Email",
        key="catalog_new_email"
    )

    catalog_contact_phone = st.text_input(
        "Phone",
        key="catalog_new_phone"
    )

    catalog_contact_organization = st.text_input(
        "Organization",
        value=bureau_info["publisher"],
        key="catalog_new_org"
    )

    if st.button(
        "Save Catalog Contact",
        key="save_catalog_contact"
    ):

        if not catalog_contact_name.strip():

            st.error(
                "Contact name is required."
            )

        else:

            save_contact(
                selected_bureau,
                catalog_contact_name,
                catalog_contact_email,
                catalog_contact_phone,
                catalog_contact_organization
            )

            st.success(
                "✓ Contact saved successfully."
            )

            st.rerun()


elif (
    catalog_contact_choice
    != "Select a catalog contact"
):

    selected_contact = next(
        (
            contact
            for contact in bureau_contacts
            if contact_display(contact)
            == catalog_contact_choice
        ),
        None
    )

    if selected_contact:

        catalog_contact_name = selected_contact.get(
            "name",
            ""
        )

        catalog_contact_email = selected_contact.get(
            "email",
            ""
        )

        catalog_contact_phone = selected_contact.get(
            "phone",
            ""
        )

        catalog_contact_organization = (
            selected_contact.get(
                "organization",
                ""
            )
        )

        st.markdown(
            '<div class="saved-indicator">'
            '✓ Catalog contact selected'
            '</div>',
            unsafe_allow_html=True
        )


# ============================================================
# DATASET
# ============================================================

dataset_number = (
    st.session_state.current_dataset
)

st.markdown(
    f"""
    <div class="section-header">
    <h2>3. Dataset {dataset_number}</h2>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# Q3 TITLE
# ============================================================

title = st.text_input(
    "What is the dataset called? **(Required)**",
    key=f"title_{dataset_number}"
)


# ============================================================
# Q4 DESCRIPTION
# ============================================================

st.markdown(
    """
    <div class="question-help">
    <strong>Describe what these data contain in plain language.</strong><br><br>
    Example:<br>
    “The Current Population Survey (CPS) is a monthly survey of households conducted
    by the Census Bureau for the Bureau of Labor Statistics. In addition to the
    national unemployment rate, it provides data on employment, the unemployment
    rate, persons not in the labor force, hours of work, earnings, and other
    demographic and labor force characteristics.”
    </div>
    """,
    unsafe_allow_html=True
)

description = st.text_area(
    "Dataset description in plain language. **(Required)**",
    height=160,
    key=f"description_{dataset_number}"
)


# ============================================================
# Q5 IDENTIFIER
# ============================================================

st.markdown(
    "### Dataset identifier"
)

identifier = (
    f"{bureau_info['identifier_code']}-"
    f"{dataset_number:06d}"
)

st.markdown(
    f"""
    <div class="saved-indicator">
    Automatically assigned identifier:
    <strong>{identifier}</strong>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# Q6 PUBLISHER
# ============================================================

office_options = [
    "Select an office",
    "＋ Add a new office"
]

office_options.extend(
    sorted(
        set(
            contact.get("organization")
            for contact in bureau_contacts
            if contact.get("organization")
        )
    )
)

selected_office = st.selectbox(
    "Which office publishes these data? **(Required)**",
    office_options,
    key=f"office_{dataset_number}"
)

if selected_office == "＋ Add a new office":

    publisher_office = st.text_input(
        "New office name",
        key=f"new_office_{dataset_number}"
    )

elif selected_office == "Select an office":

    publisher_office = ""

else:

    publisher_office = selected_office


# ============================================================
# Q7 DATASET CONTACT
# ============================================================

dataset_contact_options = [
    "Select a contact",
    "＋ Add a new contact"
]

dataset_contact_options.extend(
    [
        contact_display(contact)
        for contact in bureau_contacts
    ]
)

dataset_contact_choice = st.selectbox(
    "What is the best contact for questions "
    "about this dataset? **(Required)**",
    dataset_contact_options,
    index=default_contact_index(dataset_contact_options),
    key=f"dataset_contact_{dataset_number}_{normalize_text(selected_bureau)}"
)


contact_name = ""
contact_email = ""
contact_phone = ""
contact_organization = ""


if dataset_contact_choice == "＋ Add a new contact":

    contact_name = st.text_input(
        "Contact name",
        key=f"contact_name_{dataset_number}"
    )

    contact_email = st.text_input(
        "Email",
        key=f"contact_email_{dataset_number}"
    )

    contact_phone = st.text_input(
        "Phone",
        key=f"contact_phone_{dataset_number}"
    )

    contact_organization = st.text_input(
        "Organization",
        value=(
            publisher_office
            or bureau_info["publisher"]
        ),
        key=f"contact_org_{dataset_number}"
    )

    if st.button(
        "Save Contact",
        key=f"save_contact_{dataset_number}"
    ):

        if not contact_name.strip():

            st.error(
                "Contact name is required."
            )

        else:

            save_contact(
                selected_bureau,
                contact_name,
                contact_email,
                contact_phone,
                contact_organization
            )

            st.success(
                "✓ Contact saved successfully. "
                "It is now available for this bureau."
            )

            st.rerun()


elif (
    dataset_contact_choice
    != "Select a contact"
):

    selected_contact = next(
        (
            contact
            for contact in bureau_contacts
            if contact_display(contact)
            == dataset_contact_choice
        ),
        None
    )

    if selected_contact:

        contact_name = selected_contact.get(
            "name",
            ""
        )

        contact_email = selected_contact.get(
            "email",
            ""
        )

        contact_phone = selected_contact.get(
            "phone",
            ""
        )

        contact_organization = (
            selected_contact.get(
                "organization",
                ""
            )
        )

        st.markdown(
            '<div class="saved-indicator">'
            '✓ Dataset contact selected'
            '</div>',
            unsafe_allow_html=True
        )


# ============================================================
# Q8 KEYWORDS
# ============================================================

st.markdown(
    "### What words would someone use to search "
    "for these data? **(Required)**"
)

tags = load_json_file(
    TAGS_FILE,
    []
)

tags = sorted(
    set(
        normalize_tag(tag)
        for tag in tags
        if normalize_tag(tag)
    )
)

keyword_state_key = (
    f"selected_keywords_{dataset_number}"
)

keyword_widget_key = (
    f"keyword_widget_{dataset_number}"
)

if keyword_state_key not in st.session_state:
    st.session_state[keyword_state_key] = []


selected_tags = st.multiselect(
    "Select keywords",
    tags,
    key=keyword_widget_key
)

# Synchronize the separate application state
# with the widget.
st.session_state[keyword_state_key] = (
    selected_tags
)


new_tag = st.text_input(
    "Add a new keyword",
    placeholder="Example: trade, exports, employment",
    key=f"new_tag_{dataset_number}"
)


if st.button(
    "Save Keyword",
    key=f"save_tag_{dataset_number}"
):

    normalized_tag = normalize_tag(
        new_tag
    )

    if not normalized_tag:

        st.error(
            "Please enter a keyword."
        )

    else:

        tags = load_json_file(
            TAGS_FILE,
            []
        )

        normalized_tags = sorted(
            set(
                normalize_tag(tag)
                for tag in tags
                if normalize_tag(tag)
            )
        )

        if normalized_tag not in normalized_tags:

            normalized_tags.append(
                normalized_tag
            )

            normalized_tags.sort()

            save_json_file(
                TAGS_FILE,
                normalized_tags
            )

        # Add the new keyword to the dataset's
        # selected values.
        current_keywords = list(
            st.session_state.get(
                keyword_state_key,
                []
            )
        )

        if normalized_tag not in current_keywords:

            current_keywords.append(
                normalized_tag
            )

        # IMPORTANT:
        # Do NOT directly modify the widget's
        # session-state key here.
        #
        # Store the selection separately and
        # use a pending value to initialize the
        # widget after rerun.
        st.session_state[
            f"pending_keywords_{dataset_number}"
        ] = current_keywords

        st.session_state[
            f"keyword_success_{dataset_number}"
        ] = (
            f'✓ "{normalized_tag}" was saved '
            "and selected for this dataset."
        )

        st.rerun()


# Apply pending keyword selections AFTER the
# widget has been created.
pending_keywords_key = (
    f"pending_keywords_{dataset_number}"
)

if pending_keywords_key in st.session_state:

    pending_keywords = (
        st.session_state[
            pending_keywords_key
        ]
    )

    st.session_state[
        keyword_state_key
    ] = pending_keywords

    # Remove pending state so this only happens
    # once.
    del st.session_state[
        pending_keywords_key
    ]


if (
    f"keyword_success_{dataset_number}"
    in st.session_state
):

    st.markdown(
        f"""
        <div class="saved-indicator">
        {st.session_state[
            f"keyword_success_{dataset_number}"
        ]}
        </div>
        """,
        unsafe_allow_html=True
    )

    del st.session_state[
        f"keyword_success_{dataset_number}"
    ]


# ============================================================
# Q9 THEMES
# ============================================================

st.markdown(
    "### What theme does this dataset belong to? "
    "**(Required)**"
)

themes = load_json_file(
    THEMES_FILE,
    []
)

themes = sorted(
    themes,
    key=lambda x: normalize_theme_name(
        x.get("name", "")
    )
)

theme_names = [
    normalize_theme_name(
        theme.get("name", "")
    )
    for theme in themes
]

theme_descriptions = {
    normalize_theme_name(
        theme.get("name", "")
    ): theme.get(
        "description",
        ""
    )
    for theme in themes
}


def format_theme(theme_name):

    description = (
        theme_descriptions.get(
            theme_name,
            ""
        )
    )

    if description:

        return (
            f"{theme_name} — "
            f"{description}"
        )

    return theme_name


theme_state_key = (
    f"selected_themes_{dataset_number}"
)

theme_widget_key = (
    f"theme_widget_{dataset_number}"
)

if theme_state_key not in st.session_state:
    st.session_state[theme_state_key] = []


selected_themes = st.multiselect(
    "Select themes",
    theme_names,
    format_func=format_theme,
    key=theme_widget_key
)

st.session_state[theme_state_key] = (
    selected_themes
)


with st.expander(
    "＋ Add a new theme"
):

    new_theme_name = st.text_input(
        "Theme name",
        key=f"new_theme_name_{dataset_number}"
    )

    new_theme_description = st.text_area(
        "Short description **(Required)**",
        placeholder=(
            "Describe what this theme covers "
            "and when it should be used."
        ),
        key=f"new_theme_description_{dataset_number}"
    )

    if st.button(
        "Save Theme",
        key=f"save_theme_{dataset_number}"
    ):

        normalized_theme = (
            normalize_theme_name(
                new_theme_name
            )
        )

        description_text = (
            new_theme_description.strip()
        )

        if not normalized_theme:

            st.error(
                "Please enter a theme name."
            )

        elif not description_text:

            st.error(
                "Please provide a short description "
                "of the theme."
            )

        else:

            themes = load_json_file(
                THEMES_FILE,
                []
            )

            existing_theme = any(
                normalize_theme_name(
                    theme.get("name", "")
                )
                == normalized_theme
                for theme in themes
            )

            if existing_theme:

                st.error(
                    "That theme already exists."
                )

            else:

                themes.append(
                    {
                        "name": normalized_theme,
                        "description": (
                            description_text
                        )
                    }
                )

                themes.sort(
                    key=lambda x:
                    normalize_theme_name(
                        x.get("name", "")
                    )
                )

                save_json_file(
                    THEMES_FILE,
                    themes
                )

                current_themes = list(
                    st.session_state.get(
                        theme_state_key,
                        []
                    )
                )

                if (
                    normalized_theme
                    not in current_themes
                ):

                    current_themes.append(
                        normalized_theme
                    )

                # Store as pending rather than
                # directly modifying the widget.
                st.session_state[
                    f"pending_themes_{dataset_number}"
                ] = current_themes

                st.session_state[
                    f"theme_success_{dataset_number}"
                ] = (
                    f'✓ "{normalized_theme}" '
                    "was saved and selected "
                    "for this dataset."
                )

                st.rerun()


# Apply pending theme selections after rerun.
pending_themes_key = (
    f"pending_themes_{dataset_number}"
)

if pending_themes_key in st.session_state:

    pending_themes = (
        st.session_state[
            pending_themes_key
        ]
    )

    st.session_state[
        theme_state_key
    ] = pending_themes

    del st.session_state[
        pending_themes_key
    ]


if (
    f"theme_success_{dataset_number}"
    in st.session_state
):

    st.markdown(
        f"""
        <div class="saved-indicator">
        {st.session_state[
            f"theme_success_{dataset_number}"
        ]}
        </div>
        """,
        unsafe_allow_html=True
    )

    del st.session_state[
        f"theme_success_{dataset_number}"
    ]


# ============================================================
# Q10 ACCESS RIGHTS
# ============================================================

st.markdown(
    '<div class="section-header">'
    '<h2>Access & Restrictions</h2>'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    **Reference definitions:**

    [NARA Access Restriction Status Authority List](https://www.archives.gov/research/catalog/lcdrg/authority-lists/access-restriction-status)

    [NARA Specific Access Restriction Authority List](https://www.archives.gov/research/catalog/lcdrg/authority-lists/specific-access-restriction)
    """
)

access_rights = st.selectbox(
    "Who is allowed to access these data? "
    "**(Required)**",
    [
        "These data are public",
        "These data are restricted",
        "These data are not public"
    ],
    key=f"access_rights_{dataset_number}"
)


# ============================================================
# Q11 ACCESS RESTRICTION
# ============================================================

has_access_restriction = st.radio(
    "Are there any restrictions on getting these data? "
    "**(Required)**",
    [
        "No",
        "Yes"
    ],
    horizontal=True,
    key=f"has_access_restriction_{dataset_number}"
)

access_restriction = None


if has_access_restriction == "Yes":

    access_status = st.selectbox(
        "What is these data' restriction status? "
        "**(Required)**",
        [
            "Restricted - Fully",
            "Restricted - Partly",
            "Restricted - Possibly",
            "Undetermined",
            "Unrestricted"
        ],
        key=f"access_status_{dataset_number}"
    )

    specific_access = st.multiselect(
        "What is the specific access restriction? "
        "**(Required)**",
        [
            "FOIA (b)(1) National Security",
            "FOIA (b)(2) Internal Personnel Rules and Practices",
            "FOIA (b)(3) Statute",
            "FOIA (b)(4) Trade Secrets and Commercial Information",
            "FOIA (b)(5) Privileged Inter-Agency or Intra-Agency Information",
            "FOIA (b)(6) Personal Information",
            "FOIA (b)(7) Law Enforcement",
            "FOIA (b)(8) Financial Institutions",
            "FOIA (b)(9) Geological and Geophysical Information",
            "Other"
        ],
        key=f"specific_access_{dataset_number}"
    )

    access_note = st.text_area(
        "Additional information about the restriction "
        "(Optional)",
        key=f"access_note_{dataset_number}"
    )

    access_restriction = {
        "restrictionStatus": access_status,
        "specificRestriction": specific_access,
        "restrictionNote": access_note
    }


# ============================================================
# Q12 CUI
# ============================================================

st.markdown(
    '<div class="section-header">'
    '<h2>Controlled Unclassified Information</h2>'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    **Reference definitions:**

    [NARA CUI Markings](https://www.archives.gov/cui/registry/category-marking-list)

    [NARA CUI Registry](https://www.archives.gov/cui)
    """
)

has_cui = st.radio(
    "Does the dataset contain Controlled "
    "Unclassified Information (CUI)? **(Required)**",
    [
        "No",
        "Yes"
    ],
    horizontal=True,
    key=f"has_cui_{dataset_number}"
)

cui_restriction = None


if has_cui == "Yes":

    cui_banner = st.selectbox(
        "Which CUI Banner Marking are these data "
        "associated with? **(Required)**",
        [
            "CONTROLLED",
            "SP-PROPIN",
            "SP-CTI",
            "SP-PRVCY",
            "SP-PII",
            "SP-HLTH",
            "SP-FIN"
        ],
        key=f"cui_banner_{dataset_number}"
    )

    cui_designation = st.text_area(
        "Which agency designated the information "
        "as CUI? Include contact information when "
        "possible. **(Required)**",
        key=f"cui_designation_{dataset_number}"
    )

    cui_restriction = {
        "cuiBannerMarking": cui_banner,
        "designationIndicator": cui_designation
    }


# ============================================================
# Q13 USE RESTRICTIONS
# ============================================================

st.markdown(
    '<div class="section-header">'
    '<h2>Use Restrictions</h2>'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    **Reference definitions:**

    [NARA Use Restriction Status Authority List](https://www.archives.gov/research/catalog/lcdrg/authority-lists/use-restriction-status)

    [NARA Specific Use Restriction Authority List](https://www.archives.gov/research/catalog/lcdrg/authority-lists/specific-use-restriction)
    """
)

has_use_restriction = st.radio(
    "Are there any other rules about how these data "
    "may be used, such as use restriction, license, "
    "or rights? **(Required)**",
    [
        "No",
        "Yes"
    ],
    horizontal=True,
    key=f"has_use_restriction_{dataset_number}"
)

use_restriction = None
license = ""
rights = ""


if has_use_restriction == "Yes":

    restriction_types = st.multiselect(
        "What type of rule applies? **(Required)**",
        [
            "Use restriction",
            "License",
            "Rights"
        ],
        key=f"restriction_types_{dataset_number}"
    )

    if "Use restriction" in restriction_types:

        use_status = st.selectbox(
            "Use restriction status **(Required)**",
            [
                "Restricted - Fully",
                "Restricted - Partly",
                "Restricted - Possibly",
                "Undetermined",
                "Unrestricted"
            ],
            key=f"use_status_{dataset_number}"
        )

        specific_use = st.multiselect(
            "Specific use restriction **(Required)**",
            [
                "Copyright",
                "Donor Restrictions",
                "Public Law",
                "Other"
            ],
            key=f"specific_use_{dataset_number}"
        )

        use_note = st.text_area(
            "Use restriction note (Optional)",
            key=f"use_note_{dataset_number}"
        )

        use_restriction = {
            "restrictionStatus": use_status,
            "specificRestriction": specific_use,
            "restrictionNote": use_note
        }

    if "License" in restriction_types:

        license = st.text_input(
            "What license applies to these data? "
            "**(Required)**",
            key=f"license_{dataset_number}"
        )

    if "Rights" in restriction_types:

        rights = st.text_area(
            "What other rights have not been covered? "
            "**(Required)**",
            key=f"rights_{dataset_number}"
        )


# ============================================================
# Q14 TEMPORAL
# ============================================================

st.markdown(
    '<div class="section-header">'
    '<h2>Coverage & Dates</h2>'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    "### What time period do these data cover?"
)

st.caption(
    "Enter YYYY, YYYY-MM, or YYYY-MM-DD."
)

temporal_start = st.text_input(
    "Start date **(Required)**",
    placeholder="YYYY, YYYY-MM, or YYYY-MM-DD",
    key=f"temporal_start_{dataset_number}"
)

temporal_end = st.text_input(
    "End date **(Required)**",
    placeholder="YYYY, YYYY-MM, or YYYY-MM-DD",
    key=f"temporal_end_{dataset_number}"
)


# ============================================================
# Q15 SPATIAL
# ============================================================

st.markdown(
    "### Where do these data cover?"
)

spatial = st.text_input(
    "Geographic coverage **(Required)**",
    placeholder=(
        "Example: United States, Washington, DC, "
        "or worldwide"
    ),
    key=f"spatial_{dataset_number}"
)


# ============================================================
# Q16 MODIFIED
# ============================================================

modified = st.text_input(
    "When were these data last changed? **(Required)**",
    placeholder="YYYY, YYYY-MM, or YYYY-MM-DD",
    key=f"modified_{dataset_number}"
)

validate_date_field("Modified date", modified)


# ============================================================
# Q17 DATA DICTIONARY
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
