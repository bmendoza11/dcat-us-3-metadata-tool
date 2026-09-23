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
    publisher = {"@type": "org:Organization", "name": office}
    if bureau_info.get("homepage"):
        publisher["url"] = bureau_info["homepage"]
    return publisher


def build_access_restriction(value):
    if not value:
        return None
    restriction = {"@type": "AccessRestriction"}
    add_if_value(restriction, "restrictionStatus", normalize_single_value(value.get("restrictionStatus")))
    add_if_value(restriction, "specificRestriction", normalize_single_value(value.get("specificRestriction")))
    add_if_value(restriction, "restrictionNote", value.get("restrictionNote"))
    return restriction


def build_cui_restriction(value):
    if not value:
        return None
    restriction = {"@type": "CUIRestriction"}
    add_if_value(restriction, "cuiBannerMarking", normalize_single_value(value.get("cuiBannerMarking")))
    add_if_value(restriction, "designationIndicator", normalize_single_value(value.get("designationIndicator")))
    return restriction


def build_use_restriction(value):
    if not value:
        return None
    restriction = {"@type": "UseRestriction"}
    add_if_value(restriction, "restrictionStatus", normalize_single_value(value.get("restrictionStatus")))
    add_if_value(restriction, "specificRestriction", normalize_single_value(value.get("specificRestriction")))
    add_if_value(restriction, "restrictionNote", value.get("restrictionNote"))
    return restriction


def build_spatial(spatial, spatial_granularity=None):
    spatial = clean(spatial)
    if spatial is None:
        return None
    def make_location(value):
        obj = {"@type": "Location", "prefLabel": str(value).strip()}
        if spatial_granularity:
            obj["spatialGranularity"] = spatial_granularity
        return obj
    if isinstance(spatial, list):
        return [make_location(v) for v in spatial if clean(v)] or None
    return make_location(spatial)


def build_temporal(start, end):
    start, end = clean(start), clean(end)
    if start is None and end is None:
        return None
    obj = {"@type": "PeriodOfTime"}
    if start: obj["startDate"] = start
    if end: obj["endDate"] = end
    return [obj]


def build_document(url, title=None):
    url = clean(url)
    if url is None:
        return None
    obj = {"@type": "Document", "accessURL": url}
    add_if_value(obj, "title", title)
    return obj


def build_data_dictionary(value):
    if not value:
        return None
    if isinstance(value, dict):
        return value
    return {"@type": "Distribution", "title": "Data Dictionary", "accessURL": value}


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
    identifier = f"{bureau_info['identifier_code']}-{dataset_number:06d}"
    dataset = {"@type": "Dataset", "identifier": identifier}
    add_if_value(dataset, "title", title)
    add_if_value(dataset, "description", description)
    if office: dataset["publisher"] = build_publisher(office, bureau_info)
    if contact_name:
        dataset["contactPoint"] = [
            build_contact(
                contact_name,
                contact_email,
                contact_phone,
                contact_organization,
            )
        ]
    if keywords:
        cleaned = list(
            dict.fromkeys(
                str(x).strip().lower()
                for x in keywords
                if str(x).strip()
            )
        )
        if cleaned: dataset["keyword"] = cleaned
    if themes:
        cleaned = list(dict.fromkeys(str(x).strip().lower() for x in themes if str(x).strip()))
        if cleaned:
            dataset["theme"] = [
                {
                    "@type": "Concept",
                    "prefLabel": x,
                }
                for x in cleaned
            ]
    add_if_value(dataset, "accessRights", access_rights)
    access = build_access_restriction(access_restriction)
    if access: dataset["accessRestriction"] = [access]
    cui = build_cui_restriction(cui_restriction)
    if cui: dataset["cuiRestriction"] = cui
    use = build_use_restriction(use_restriction)
    if use: dataset["useRestriction"] = [use]
    add_if_value(dataset, "license", license)
    rights_value = normalize_single_value(rights)
    if clean(rights_value) is not None: dataset["rights"] = [rights_value]
    temporal = build_temporal(temporal_start, temporal_end)
    if temporal: dataset["temporal"] = temporal
    spatial_obj = build_spatial(spatial, spatial_granularity)
    if spatial_obj: dataset["spatial"] = spatial_obj
    add_if_value(dataset, "modified", modified)
    described = build_data_dictionary(data_dictionary)
    if described: dataset["describedBy"] = described
    if landing_page:
        doc = build_document(landing_page, "Dataset Landing Page")
        if doc: dataset["landingPage"] = doc
    if contract_number: dataset["contractNumber"] = str(contract_number).strip()[:40]
    if additional_properties:
        for k, v in additional_properties.items():
            if k and clean(v) is not None:
                dataset[k] = v
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
        "@context": "https://resources.data.gov/schemas/dcat-us/v3.0/context.jsonld",
        "@type": "Catalog",
        "title": f"{bureau_info['publisher']} Data Catalog",
        "description": f"This is a catalog of {bureau_info['publisher']} data.",
    }
    if bureau_info.get("homepage"):
        catalog["homepage"] = build_document(
            bureau_info["homepage"],
            (
                f"{bureau_info['publisher']} "
                "Data Catalog Homepage"
            ),
        )
    catalog["publisher"] = {
        "@type": "Organization",
        "name": bureau_info["publisher"],
    }
    if bureau_info.get("bureauCode"): catalog["bureauCode"] = bureau_info["bureauCode"]
    if bureau_info.get("programCode"): catalog["programCode"] = bureau_info["programCode"]
    if catalog_contact_name:
        catalog["contactPoint"] = [
            build_contact(
                catalog_contact_name,
                catalog_contact_email,
                catalog_contact_phone,
                catalog_contact_organization,
            )
        ]
    catalog["dataset"] = datasets
    return catalog

