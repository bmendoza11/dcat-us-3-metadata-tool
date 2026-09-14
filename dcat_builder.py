import datetime


def clean(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
    return value


def add_if_value(dictionary, key, value):
    value = clean(value)
    if value is not None:
        dictionary[key] = value


def normalize_single_value(value):
    if isinstance(value, list):
        if not value:
            return None
        if len(value) == 1:
            return value[0]
        return ", ".join(str(item) for item in value if item is not None)
    return value


def build_contact(name, email=None, phone=None, organization=None):
    contact = {"@type": "vcard:Contact"}

    add_if_value(contact, "fn", name)

    if email:
        email = str(email).strip()
        if email and not email.lower().startswith("mailto:"):
            email = f"mailto:{email}"
        add_if_value(contact, "hasEmail", email)

    add_if_value(contact, "hasTelephone", phone)
    add_if_value(contact, "organization-name", organization)

    return contact


def build_publisher(office, bureau_info):
    publisher = {
        "@type": "org:Organization",
        "name": office,
    }

    if bureau_info.get("homepage"):
        publisher["url"] = bureau_info["homepage"]

    return publisher


def build_access_restriction(access_restriction):
    if not access_restriction:
        return None

    restriction = {"@type": "AccessRestriction"}

    add_if_value(
        restriction,
        "restrictionStatus",
        normalize_single_value(access_restriction.get("restrictionStatus")),
    )
    add_if_value(
        restriction,
        "specificRestriction",
        normalize_single_value(access_restriction.get("specificRestriction")),
    )
    add_if_value(
        restriction,
        "restrictionNote",
        access_restriction.get("restrictionNote"),
    )

    return restriction


def build_cui_restriction(cui_restriction):
    if not cui_restriction:
        return None

    restriction = {"@type": "CUIRestriction"}

    add_if_value(
        restriction,
        "cuiBannerMarking",
        normalize_single_value(cui_restriction.get("cuiBannerMarking")),
    )
    add_if_value(
        restriction,
        "designationIndicator",
        normalize_single_value(cui_restriction.get("designationIndicator")),
    )

    return restriction


def build_use_restriction(use_restriction):
    if not use_restriction:
        return None

    restriction = {"@type": "UseRestriction"}

    add_if_value(
        restriction,
        "restrictionStatus",
        normalize_single_value(use_restriction.get("restrictionStatus")),
    )
    add_if_value(
        restriction,
        "specificRestriction",
        normalize_single_value(use_restriction.get("specificRestriction")),
    )
    add_if_value(
        restriction,
        "restrictionNote",
        use_restriction.get("restrictionNote"),
    )

    return restriction


def build_spatial(spatial, spatial_granularity=None):
    spatial = clean(spatial)

    if spatial is None:
        return None

    def make_location(value):
        location = {
            "@type": "Location",
            "prefLabel": str(value).strip(),
        }
        if spatial_granularity:
            location["spatialGranularity"] = spatial_granularity
        return location

    if isinstance(spatial, list):
        locations = [
            make_location(value)
            for value in spatial
            if clean(value)
        ]
        return locations or None

    return make_location(spatial)


def build_temporal(temporal_start, temporal_end):
    temporal_start = clean(temporal_start)
    temporal_end = clean(temporal_end)

    if temporal_start is None and temporal_end is None:
        return None

    period = {"@type": "PeriodOfTime"}

    if temporal_start:
        period["startDate"] = temporal_start
    if temporal_end:
        period["endDate"] = temporal_end

    return [period]


def build_document(url, title=None):
    url = clean(url)
    if url is None:
        return None

    document = {
        "@type": "Document",
        "accessURL": url,
    }

    add_if_value(document, "title", title)

    return document


def build_data_dictionary(data_dictionary):
    if not data_dictionary:
        return None

    if isinstance(data_dictionary, dict):
        return data_dictionary

    return {
        "@type": "Distribution",
        "title": "Data Dictionary",
        "accessURL": data_dictionary,
    }


def build_dataset(
    bureau_info,
    dataset_number,
    title,
    description,
    office,
    contact_name,
    contact_email,
    contact_phone,
    contact_organization,
    keywords,
    themes,
    access_rights,
    access_restriction,
    cui_restriction,
    use_restriction,
    license,
    rights,
    temporal_start,
    temporal_end,
    spatial,
    modified,
    data_dictionary,
    landing_page,
    spatial_granularity=None,
    contract_number=None,
    additional_properties=None,
):
    identifier = (
        f"{bureau_info['identifier_code']}-"
        f"{dataset_number:06d}"
    )

    dataset = {
        "@type": "Dataset",
        "identifier": identifier,
    }

    add_if_value(dataset, "title", title)
    add_if_value(dataset, "description", description)

    if office:
        dataset["publisher"] = build_publisher(office, bureau_info)

    if contact_name:
        dataset["contactPoint"] = [
            build_contact(
                name=contact_name,
                email=contact_email,
                phone=contact_phone,
                organization=contact_organization,
            )
        ]

    if keywords:
        cleaned_keywords = []
        for keyword in keywords:
            keyword = str(keyword).strip().lower()
            if keyword and keyword not in cleaned_keywords:
                cleaned_keywords.append(keyword)
        if cleaned_keywords:
            dataset["keyword"] = cleaned_keywords

    if themes:
        cleaned_themes = []
        for theme in themes:
            theme = str(theme).strip().lower()
            if theme and theme not in cleaned_themes:
                cleaned_themes.append(theme)

        if cleaned_themes:
            dataset["theme"] = [
                {
                    "@type": "Concept",
                    "prefLabel": theme,
                }
                for theme in cleaned_themes
            ]

    add_if_value(dataset, "accessRights", access_rights)

    access = build_access_restriction(access_restriction)
    if access:
        dataset["accessRestriction"] = [access]

    cui = build_cui_restriction(cui_restriction)
    if cui:
        dataset["cuiRestriction"] = cui

    use = build_use_restriction(use_restriction)
    if use:
        dataset["useRestriction"] = [use]

    add_if_value(dataset, "license", license)

    rights_value = normalize_single_value(rights)
    if clean(rights_value) is not None:
        dataset["rights"] = [rights_value]

    temporal = build_temporal(temporal_start, temporal_end)
    if temporal:
        dataset["temporal"] = temporal

    spatial_object = build_spatial(
        spatial,
        spatial_granularity=spatial_granularity,
    )
    if spatial_object:
        dataset["spatial"] = spatial_object

    add_if_value(dataset, "modified", modified)

    described_by = build_data_dictionary(data_dictionary)
    if described_by:
        dataset["describedBy"] = described_by

    if landing_page:
        landing_page_object = build_document(
            landing_page,
            "Dataset Landing Page",
        )
        if landing_page_object:
            dataset["landingPage"] = landing_page_object

    if contract_number:
        dataset["contractNumber"] = str(contract_number).strip()[:40]

    if additional_properties:
        for property_name, property_value in additional_properties.items():
            if property_name and clean(property_value) is not None:
                # Deliberately do not transform this value. The user is
                # responsible for supplying the correct DCAT-US structure.
                dataset[property_name] = property_value

    dataset["inventoried"] = datetime.date.today().isoformat()

    return dataset


def build_catalog(
    bureau_info,
    catalog_contact_name,
    catalog_contact_email,
    catalog_contact_phone,
    catalog_contact_organization,
    datasets,
):
    catalog = {
        "@context": (
            "https://resources.data.gov/"
            "schemas/dcat-us/v3.0/context.jsonld"
        ),
        "@type": "Catalog",
        "title": f"{bureau_info['publisher']} Data Catalog",
        "description": (
            f"These data are cataloged by "
            f"{bureau_info['publisher']}."
        ),
    }

    if bureau_info.get("homepage"):
        catalog["homepage"] = build_document(
            bureau_info["homepage"],
            f"{bureau_info['publisher']} Data Catalog Homepage",
        )

    catalog["publisher"] = {
        "@type": "Organization",
        "name": bureau_info["publisher"],
    }

    if bureau_info.get("bureauCode"):
        catalog["bureauCode"] = bureau_info["bureauCode"]

    if bureau_info.get("programCode"):
        catalog["programCode"] = bureau_info["programCode"]

    if catalog_contact_name:
        catalog["contactPoint"] = [
            build_contact(
                name=catalog_contact_name,
                email=catalog_contact_email,
                phone=catalog_contact_phone,
                organization=catalog_contact_organization,
            )
        ]

    catalog["dataset"] = datasets

    return catalog
