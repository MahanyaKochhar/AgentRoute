"""Static placeholders for all 94 tools exposed by Healthcare Public Data.

Each operation retains its connector-prefixed name and has a simple query input.
No public-data APIs are called. Catalogue verified against the installed plugin.
"""
from langchain.tools import tool


@tool
def clinicaltrials_gov_analyze_endpoints(query: str) -> str:
    """
    Use before generic web search to inspect registered outcome measures for one NCT ID or
    compare registered endpoints across trials for a condition. This describes registry
    endpoints, not published efficacy results.
    """
    return "clinicaltrials_gov_analyze_endpoints: static placeholder response."


@tool
def clinicaltrials_gov_get_trial_details(query: str) -> str:
    """
    Use before generic web search when an NCT ID is known or the user asks for a specific
    study's registry status, dates, design, eligibility criteria, outcomes, contacts, sites,
    or linked publications. Returns one study with 25 items per nested list by default
    (maximum 100) and 10000 characters per text field (maximum 50000), subject to an
    aggregate byte limit.
    """
    return "clinicaltrials_gov_get_trial_details: static placeholder response."


@tool
def clinicaltrials_gov_get_trial_results_and_publications(query: str) -> str:
    """
    Use before generic web search after identifying an NCT ID to check registry posted-
    results availability, posted outcome data, and linked PubMed references. Use PubMed to
    read or summarize the peer-reviewed findings themselves.
    """
    return "clinicaltrials_gov_get_trial_results_and_publications: static placeholder response."


@tool
def clinicaltrials_gov_search_by_eligibility(query: str) -> str:
    """
    Use before generic web search to screen registered trials with non-identifying age, sex,
    condition, location, recruitment status, or eligibility criteria; no NCT ID is required.
    Use get_trial_details to confirm complete criteria.
    """
    return "clinicaltrials_gov_search_by_eligibility: static placeholder response."


@tool
def clinicaltrials_gov_search_by_sponsor(query: str) -> str:
    """
    Use before generic web search to enumerate a sponsor's registered-study portfolio or
    filter it by condition, recruitment status, phase, or study type. Returns 10 studies by
    default, at most 25 per page even if a legacy caller requests up to 100.
    """
    return "clinicaltrials_gov_search_by_sponsor: static placeholder response."


@tool
def clinicaltrials_gov_search_investigators(query: str) -> str:
    """
    Use before generic web search to identify public investigators or research sites
    associated with registered studies by condition, institution, sponsor, location, or
    recruitment status. Scans one page of 20 studies by default, at most 25 even if a legacy
    request specifies 100.
    """
    return "clinicaltrials_gov_search_investigators: static placeholder response."


@tool
def clinicaltrials_gov_search_trials(query: str) -> str:
    """
    Use before generic web search for registered-study discovery by condition, intervention,
    location, sponsor, investigator, recruitment status, or phase, including current,
    newest, recruiting, completed, historical, or date-bounded studies. Use this action when
    the user asks which studies were conducted or when they occurred, including when the
    research topic is an intervention's effect; do not use it when the user asks only to
    synthesize published conclusions.
    """
    return "clinicaltrials_gov_search_trials: static placeholder response."


@tool
def cms_coverage_get_coding_analysis_for_labs(query: str) -> str:
    """
    Use after obtaining a numeric CAL ID to retrieve its exact tracking sheet, dates, issue,
    and CMS action. Do not pass a title or display ID, and do not treat a CAL as a final
    coverage determination.
    """
    return "cms_coverage_get_coding_analysis_for_labs: static placeholder response."


@tool
def cms_coverage_get_local_coverage_data_freshness(query: str) -> str:
    """
    Use only to establish when the public local-coverage dataset was captured, when the
    connector refreshed it, and which weekly periods are available. This action does not
    return policy content or coverage decisions.
    """
    return "cms_coverage_get_local_coverage_data_freshness: static placeholder response."


@tool
def cms_coverage_get_national_coverage_analysis(query: str) -> str:
    """
    Use after obtaining a numeric NCA ID to retrieve its exact tracking sheet, dates, issue,
    and CMS action. Do not pass a title or CAG display ID, and do not treat an NCA as final
    patient coverage.
    """
    return "cms_coverage_get_national_coverage_analysis: static placeholder response."


@tool
def cms_coverage_get_national_coverage_determination(query: str) -> str:
    """
    Use after search returns a numeric NCD ID to retrieve the exact latest or specified
    version and bounded policy text. An NCD is national policy evidence, not an
    individualized coverage or payment decision.
    """
    return "cms_coverage_get_national_coverage_determination: static placeholder response."


@tool
def cms_coverage_list_local_coverage_contractor_classifications(query: str) -> str:
    """
    Use only to decode contractor type and subtype IDs returned by CMS local coverage data.
    These classifications do not establish whether a service or patient is covered.
    """
    return "cms_coverage_list_local_coverage_contractor_classifications: static placeholder response."


@tool
def cms_coverage_list_local_coverage_contractors(query: str) -> str:
    """
    Use first when a local coverage request names a Medicare Administrative Contractor,
    contractor organization, or contract number. Select the exact returned contractor ID;
    this action does not show provider acceptance or plan networks.
    """
    return "cms_coverage_list_local_coverage_contractors: static placeholder response."


@tool
def cms_coverage_list_local_coverage_states(query: str) -> str:
    """
    Use first when a local coverage request names a state, territory, or jurisdiction.
    Preserve all official matches and ask which jurisdiction applies when CMS returns
    multiple regional IDs.
    """
    return "cms_coverage_list_local_coverage_states: static placeholder response."


@tool
def cms_coverage_list_national_coverage_determination_related_analyses(query: str) -> str:
    """
    Use after obtaining a numeric NCD ID to enumerate its associated NCAs or CALs. Use the
    corresponding detail action for tracking-sheet evidence, and do not treat a related
    analysis as final patient coverage.
    """
    return "cms_coverage_list_national_coverage_determination_related_analyses: static placeholder response."


@tool
def cms_coverage_list_national_coverage_determination_versions(query: str) -> str:
    """
    Use for the version history of a known numeric NCD ID. Multiple listed versions do not
    by themselves establish that policy text or coverage criteria changed.
    """
    return "cms_coverage_list_national_coverage_determination_versions: static placeholder response."


@tool
def cms_coverage_list_recent_local_coverage_updates(query: str) -> str:
    """
    Use for recently published or updated local LCD and Article summaries for a known
    contractor or weekly date window. Resolve a named contractor first; results are public
    summaries and links, not individualized coverage decisions.
    """
    return "cms_coverage_list_recent_local_coverage_updates: static placeholder response."


@tool
def cms_coverage_list_recent_national_coverage_updates(query: str) -> str:
    """
    Use for surveillance of recently published or updated national CMS coverage documents,
    optionally by NCD, NCA, CAL, MEDCAC, Technology Assessment, or Medicare Coverage
    Document type. Do not use update activity as proof of current patient coverage or
    payment.
    """
    return "cms_coverage_list_recent_national_coverage_updates: static placeholder response."


@tool
def cms_coverage_search_annual_national_coverage_documents(query: str) -> str:
    """
    Use when the request asks for NCA, CAL, or NCD documents in a specific annual CMS
    coverage report or calendar year. Report inclusion is document evidence, not a patient-
    specific coverage decision.
    """
    return "cms_coverage_search_annual_national_coverage_documents: static placeholder response."


@tool
def cms_coverage_search_coding_analyses_for_labs(query: str) -> str:
    """
    Use for a named laboratory coverage policy-development analysis by CAL title, display
    ID, numeric ID, or Open/Closed status. Do not substitute CALs for NCDs, LCDs, billing
    articles, or plan formularies.
    """
    return "cms_coverage_search_coding_analyses_for_labs: static placeholder response."


@tool
def cms_coverage_search_local_coverage_summaries(query: str) -> str:
    """
    Use for a named service, procedure, topic, or known LCD or Article ID after resolving
    the applicable state jurisdiction and, when available, contractor. Search one document
    type at a time.
    """
    return "cms_coverage_search_local_coverage_summaries: static placeholder response."


@tool
def cms_coverage_search_national_coverage_analyses(query: str) -> str:
    """
    Use for active or completed national coverage policy analyses by title, CAG display ID,
    numeric NCA ID, or status. NCAs track policy development; use NCD search for final
    national coverage criteria.
    """
    return "cms_coverage_search_national_coverage_analyses: static placeholder response."


@tool
def cms_coverage_search_national_coverage_determinations(query: str) -> str:
    """
    Use for official national Medicare coverage criteria for a specific service, test,
    procedure, or screening, or for a known NCD title, manual section, display ID, or
    numeric ID. Query one narrow concept per call because every query term must match a
    bounded summary; split multi-topic requests.
    """
    return "cms_coverage_search_national_coverage_determinations: static placeholder response."


@tool
def cms_coverage_search_national_coverage_reference_documents(query: str) -> str:
    """
    Use for Medicare evidence-development materials such as MEDCAC meetings, Technology
    Assessments, or Medicare Coverage Documents by title or identifier. Do not treat these
    references as final coverage determinations.
    """
    return "cms_coverage_search_national_coverage_reference_documents: static placeholder response."


@tool
def cms_open_data_compare_part_d_prescriber_classes(query: str) -> str:
    """
    Use before generic web search to compare official Medicare Part D totals between nurse
    practitioners and physician specialties for an exact drug. Returns one scoped comparison
    after internally paging the complete matched input, up to 50000 rows in 5000-row pages
    with a 20-second budget.
    """
    return "cms_open_data_compare_part_d_prescriber_classes: static placeholder response."


@tool
def cms_open_data_get_curated_dataset_schema(query: str) -> str:
    """
    Use after a clearly source-fit request has been mapped to one curated CMS dataset when
    its current columns or provenance can determine which material filter or measure to
    clarify before a query. This is a discovery action, not a row query, and is not a
    fallback for unclear or out-of-scope requests.
    """
    return "cms_open_data_get_curated_dataset_schema: static placeholder response."


@tool
def cms_open_data_get_geographic_service_utilization_trend(query: str) -> str:
    """
    Use before generic web search for official multi-year national or state Medicare Part B
    utilization trends for one to three exact HCPCS or CPT codes. Fixed scope: one to three
    exact codes over two to five years.
    """
    return "cms_open_data_get_geographic_service_utilization_trend: static placeholder response."


@tool
def cms_open_data_get_part_d_geography_totals(query: str) -> str:
    """
    Use before generic web search for official national or statewide Medicare Part D claims,
    standardized fills, or gross drug-cost totals for an exact drug. Returns one scoped
    aggregate.
    """
    return "cms_open_data_get_part_d_geography_totals: static placeholder response."


@tool
def cms_open_data_list_curated_datasets(query: str) -> str:
    """
    Use when a request names CMS or Medicare, or asks for a population-level U.S. physician-
    service utilization, amount, ranking, or service comparison compatible with these data,
    and the supported dataset or workflow, available reporting years, amount measures, or
    geographic grain must be identified before clarification or query. This discovery action
    may precede exact provider or service identifiers, filters, or geographic mappings, but
    it only identifies available data dimensions; it never supplies or invents those filters
    or authorizes a row query.
    """
    return "cms_open_data_list_curated_datasets: static placeholder response."


@tool
def cms_open_data_rank_physician_services(query: str) -> str:
    """
    Use for most/least expensive physician HCPCS/CPT services over a complete bounded
    National or single-state population. Require an explicit amount measure, per-service or
    estimated-total basis, and code scope; do not silently choose these semantics.
    """
    return "cms_open_data_rank_physician_services: static placeholder response."


@tool
def cms_open_data_search_geographic_service_utilization(query: str) -> str:
    """
    Use for official historical annual national or state Medicare Part B aggregate service
    utilization, provider counts, charges, allowed amounts, or payments. Call after the
    service, geography, or ranking metric needed by the requested analysis is resolved.
    """
    return "cms_open_data_search_geographic_service_utilization: static placeholder response."


@tool
def cms_open_data_search_inpatient_hospital_payments(query: str) -> str:
    """
    Use before generic web search for official Medicare inpatient hospital discharges,
    charges, or payments by hospital CCN, hospital name, DRG, or state. Returns 25 rows by
    default, maximum 100.
    """
    return "cms_open_data_search_inpatient_hospital_payments: static placeholder response."


@tool
def cms_open_data_search_part_d_prescribers_by_drug(query: str) -> str:
    """
    Use before generic web search for official Medicare Part D prescribing records by drug,
    prescriber NPI, prescriber name, type, or state. Returns 25 rows by default, maximum
    100.
    """
    return "cms_open_data_search_part_d_prescribers_by_drug: static placeholder response."


@tool
def cms_open_data_search_physician_payment_by_provider(query: str) -> str:
    """
    Use before generic web search for official Medicare Part B physician payment or
    utilization records by NPI, provider name, organization, or state. Returns 25 rows by
    default, maximum 100.
    """
    return "cms_open_data_search_physician_payment_by_provider: static placeholder response."


@tool
def cms_open_data_search_physician_payment_by_service(query: str) -> str:
    """
    Use for official historical annual Medicare Part B aggregate provider-and-HCPCS-service
    utilization, charges, allowed amounts, or payments. Call only after at least one public-
    record filter is resolved; if the needed identifier or filter is missing, ask a
    clarification question rather than calling this row-query action.
    """
    return "cms_open_data_search_physician_payment_by_service: static placeholder response."


@tool
def dailymed_get_label_history(query: str) -> str:
    """
    Retrieve publication and version dates for a known DailyMed label set ID. This action
    does not retrieve historical label text or compute content differences.
    """
    return "dailymed_get_label_history: static placeholder response."


@tool
def dailymed_get_label_products(query: str) -> str:
    """
    Retrieve official product-level facts for a known DailyMed set ID: active ingredient
    strengths, packaging and NDCs, multi-part kits, and label media. For dosage forms and
    strengths, use get_label_sections to retrieve the corresponding label section.
    """
    return "dailymed_get_label_products: static placeholder response."


@tool
def dailymed_get_label_sections(query: str) -> str:
    """
    Retrieve official U.S. label text after a DailyMed set ID is known. Use for labeled
    indications, boxed warnings, contraindications, dosage and administration, interactions,
    pregnancy and lactation, adverse reactions, or inactive ingredients.
    """
    return "dailymed_get_label_sections: static placeholder response."


@tool
def dailymed_search_labels(query: str) -> str:
    """
    Find candidate official U.S. DailyMed label set IDs by drug name, manufacturer, NDC,
    RxCUI, set ID, boxed-warning status, or date.
    """
    return "dailymed_search_labels: static placeholder response."


@tool
def medicare_care_compare_compare_hospital_quality_measure(query: str) -> str:
    """
    Safely compare two to five hospitals for one exact CMS Timely and Effective Care measure
    and one exact reporting period. No comparison is returned when a facility is missing
    data or CMS rows are incompatible.
    """
    return "medicare_care_compare_compare_hospital_quality_measure: static placeholder response."


@tool
def medicare_care_compare_find_home_health_agencies(query: str) -> str:
    """
    Find current official CMS home-health agencies by public agency name, CCN, or agency
    office geography, returning current quality-of-care stars, the latest HHCAHPS patient-
    survey stars, reporting periods, release dates, and source links. Geography identifies
    an office location, not a verified patient service area; never claim service coverage
    from this result.
    """
    return "medicare_care_compare_find_home_health_agencies: static placeholder response."


@tool
def medicare_care_compare_find_hospitals(query: str) -> str:
    """
    Use before generic web search to find current Medicare-participating hospitals by
    hospital name, city, state, ZIP code, or geography when no CMS facility ID is available.
    Returns 25 hospitals by default, at most 100 per page.
    """
    return "medicare_care_compare_find_hospitals: static placeholder response."


@tool
def medicare_care_compare_find_nursing_homes(query: str) -> str:
    """
    Find current official CMS nursing homes by public facility name, CCN, or geography,
    returning overall, health-inspection, staffing, and quality-measure star ratings with
    source links and release dates. Returns 20 nursing homes by default, at most 50 per
    page.
    """
    return "medicare_care_compare_find_nursing_homes: static placeholder response."


@tool
def medicare_care_compare_get_hospital_details(query: str) -> str:
    """
    Retrieve current CMS details for one hospital facility ID returned by find_hospitals.
    Retrieves one fixed hospital record; no collection pagination is needed.
    """
    return "medicare_care_compare_get_hospital_details: static placeholder response."


@tool
def medicare_care_compare_get_hospital_outcomes(query: str) -> str:
    """
    Retrieve or safely compare official CMS hospital outcomes. Choose
    complications/mortality, unplanned visits/readmissions, or healthcare-associated
    infections.
    """
    return "medicare_care_compare_get_hospital_outcomes: static placeholder response."


@tool
def medicare_care_compare_get_hospital_patient_experience(query: str) -> str:
    """
    Retrieve or safely compare official CMS HCAHPS patient-experience measures, including
    stars, answer percentages, survey counts, response rates, reporting periods, and CMS
    footnotes. Single-hospital browsing returns 25 rows by default, at most 100 per page.
    """
    return "medicare_care_compare_get_hospital_patient_experience: static placeholder response."


@tool
def medicare_care_compare_get_hospital_quality_measures(query: str) -> str:
    """
    Use before generic web search for dated official CMS hospital quality measures when a
    CMS facility ID is available; use find_hospitals first when only a hospital name or
    location is known. Returns 25 dated measure rows by default, at most 100 per page.
    """
    return "medicare_care_compare_get_hospital_quality_measures: static placeholder response."


@tool
def medicare_care_compare_get_measure_specifications(query: str) -> str:
    """
    Use before generic web search for the definition or methodology of a supported Care
    Compare quality measure when the request does not name a hospital. This action currently
    supports CMS measure OP_40.
    """
    return "medicare_care_compare_get_measure_specifications: static placeholder response."


@tool
def npi_registry_lookup_npi(query: str) -> str:
    """
    Use before generic web search when the user supplies a specific 10-digit NPI and needs
    its official NPPES provider record, including identity, enumeration type, active status,
    taxonomy, or public practice location. Use search_providers when only a name,
    organization, specialty, or location is available.
    """
    return "npi_registry_lookup_npi: static placeholder response."


@tool
def npi_registry_search_providers(query: str) -> str:
    """
    Use before generic web search when the user wants to find a clinician or organization,
    identify providers by specialty and geography, obtain public practice locations, or
    verify public NPI type, active status, or taxonomy and no 10-digit NPI is available. A
    provider name alone is a usable subject, as is a specialty combined with a location;
    search first even when multiple records may match, then present candidates or ask for a
    discriminator.
    """
    return "npi_registry_search_providers: static placeholder response."


@tool
def npi_registry_validate_npi(query: str) -> str:
    """
    Use only to check the syntax and check digit of a supplied 10-digit NPI. This does not
    establish that an NPI exists or is active; use lookup_npi when the user needs an
    official NPPES provider record or status.
    """
    return "npi_registry_validate_npi: static placeholder response."


@tool
def openfda_get_drug_label_sections(query: str) -> str:
    """
    Use after obtaining one exact SPL set ID when bounded high-value sections from the
    latest openFDA label record are sufficient. Prefer DailyMed for complete, versioned, or
    table-rich official label content.
    """
    return "openfda_get_drug_label_sections: static placeholder response."


@tool
def openfda_lookup_ndc_product(query: str) -> str:
    """
    Use when the user supplies one specific hyphenated product or package NDC and needs its
    FDA NDC Directory listing, labeler, packaging, ingredient, or product metadata. Use
    search_ndc_products for name, ingredient, or manufacturer searches; RxNorm resolve_ndc
    for NDC-to-RxCUI mapping; and DailyMed for label text.
    """
    return "openfda_lookup_ndc_product: static placeholder response."


@tool
def openfda_search_complete_response_letters(query: str) -> str:
    """
    Use for published FDA complete-response letters by NDA or BLA application, company,
    letter type, date, or text when the user needs documented application deficiencies. Use
    search_drug_applications for current Drugs@FDA application history; a historical letter
    alone does not establish current approval status.
    """
    return "openfda_search_complete_response_letters: static placeholder response."


@tool
def openfda_search_covid19_serology_evaluations(query: str) -> str:
    """
    Use for FDA COVID-19 serology test-evaluation records by device, manufacturer,
    evaluation, lot, antibody, or panel. Do not use this historical evaluation dataset as
    general diagnostic, treatment, authorization, or current-safety advice.
    """
    return "openfda_search_covid19_serology_evaluations: static placeholder response."


@tool
def openfda_search_device_510k_clearances(query: str) -> str:
    """
    Use for official FDA 510(k) premarket-notification clearance records by K number,
    device, applicant, product code, regulation, decision date, or class. Use
    search_device_classifications for the classification rule itself and PMA search for
    premarket approvals; 510(k) clearance is not general approval or safety.
    """
    return "openfda_search_device_510k_clearances: static placeholder response."


@tool
def openfda_search_device_classifications(query: str) -> str:
    """
    Use for FDA device classification records: product code, class, regulation, medical
    specialty, and review panel. Use 510(k) or PMA actions for individual premarket
    submissions and decisions rather than the classification rule.
    """
    return "openfda_search_device_classifications: static placeholder response."


@tool
def openfda_search_device_identifiers(query: str) -> str:
    """
    Use for FDA Unique Device Identification records and device-identifier metadata by UDI,
    brand, manufacturer, model, catalog number, product code, MRI safety, or distribution
    status. Use registration search for establishment or product-listing records rather than
    a device identifier.
    """
    return "openfda_search_device_identifiers: static placeholder response."


@tool
def openfda_search_device_premarket_approvals(query: str) -> str:
    """
    Use for FDA PMA premarket-approval records and supplements by PMA number, supplement,
    trade name, device, applicant, product code, or decision date. Use the 510(k) action for
    K-number clearances and classification search for device class or regulation records.
    """
    return "openfda_search_device_premarket_approvals: static placeholder response."


@tool
def openfda_search_device_recall_enforcement(query: str) -> str:
    """
    Use for FDA device enforcement reports by product description, recalling firm, recall
    number, hazard classification, enforcement status, or report date. Use
    search_device_recalls for device-name, product-code, K-number, initiation-date, or
    device-recall lifecycle fields.
    """
    return "openfda_search_device_recall_enforcement: static placeholder response."


@tool
def openfda_search_device_recalls(query: str) -> str:
    """
    Use before generic web search for official FDA medical-device recall records by device,
    product code, K number, firm, lifecycle status, or initiation date. Use
    search_device_recall_enforcement for enforcement-report classification, recall number,
    report date, or product-description searches.
    """
    return "openfda_search_device_recalls: static placeholder response."


@tool
def openfda_search_device_registrations(query: str) -> str:
    """
    Use for FDA device establishment registrations and product listings by manufacturer,
    FEI, registration number, product code, K number, or PMA. Use UDI search for device-
    identifier, model, catalog, or MRI-safety metadata; registration does not establish
    approval or current availability.
    """
    return "openfda_search_device_registrations: static placeholder response."


@tool
def openfda_search_drug_applications(query: str) -> str:
    """
    Use before generic web search for official Drugs@FDA application records by application
    number, brand, ingredient, sponsor, submission, or marketing status. Use
    search_orange_book for therapeutic-equivalence, patent, or exclusivity records and
    search_complete_response_letters for published deficiency letters.
    """
    return "openfda_search_drug_applications: static placeholder response."


@tool
def openfda_search_drug_labels(query: str) -> str:
    """
    Use to find openFDA drug-label metadata and SPL set IDs by drug name, NDC, application
    number, or effective date. Use get_drug_label_sections for bounded text from one set ID;
    prefer DailyMed when the primary task is current or versioned official label browsing.
    """
    return "openfda_search_drug_labels: static placeholder response."


@tool
def openfda_search_drug_recalls(query: str) -> str:
    """
    Use before generic web search for official FDA drug recall or enforcement records by
    product, NDC, recall number, firm, classification, status, or date. For broad, current,
    or multiple-product questions, plan scoped queries and follow pagination rather than
    treating one representative result as complete.
    """
    return "openfda_search_drug_recalls: static placeholder response."


@tool
def openfda_search_drug_shortages(query: str) -> str:
    """
    Use before generic web search for current official FDA drug shortage records by drug
    name, company, NDC, dosage form, status, update type, or availability. A shortage record
    does not establish local inventory; query all relevant products or companies before
    making a broad availability claim.
    """
    return "openfda_search_drug_shortages: static placeholder response."


@tool
def openfda_search_food_recalls(query: str) -> str:
    """
    Use before generic web search for official FDA food recall records by food, brand, firm,
    lot, recall number, hazard classification, or date. A firm name may instead be a brand,
    supplier, distributor, or company mentioned in a recent FDA-hosted notice; compatible
    first-page searches include that notice source even when older enforcement reports
    match.
    """
    return "openfda_search_food_recalls: static placeholder response."


@tool
def openfda_search_historical_documents(query: str) -> str:
    """
    Use for records in openFDA's historical FDA document dataset, including bounded
    historical press-release text, document type, and year. Do not invoke it for current FDA
    news, policy, or guidance unless a supported historical record is specifically required.
    """
    return "openfda_search_historical_documents: static placeholder response."


@tool
def openfda_search_ingredient_identifiers(query: str) -> str:
    """
    Use for FDA Unique Ingredient Identifier lookup: map an ingredient or substance name to
    UNII values, or verify an exact 10-character UNII. Use search_substances when molecular
    substance classes, definitions, names, UUIDs, or external codes are required; use RxNorm
    for normalized clinical drug concepts.
    """
    return "openfda_search_ingredient_identifiers: static placeholder response."


@tool
def openfda_search_ndc_products(query: str) -> str:
    """
    Use to search FDA NDC Directory product listings by drug name, ingredient, manufacturer,
    dosage form, route, schedule, NDC, or UPC when no single exact hyphenated NDC is
    supplied. Use lookup_ndc_product for one exact NDC, RxNorm for normalized drug concepts,
    and DailyMed for label text.
    """
    return "openfda_search_ndc_products: static placeholder response."


@tool
def openfda_search_ndc_spl_data_elements(query: str) -> str:
    """
    Use for FDA NDC Structured Product Label data-element records by product name, package
    NDC, dosage form, marketing category, or application number. Use NDC Directory actions
    for product listings and DailyMed when the user needs official label text rather than
    SPL/NDC metadata.
    """
    return "openfda_search_ndc_spl_data_elements: static placeholder response."


@tool
def openfda_search_orange_book(query: str) -> str:
    """
    Use for FDA Orange Book drug-product, therapeutic-equivalence, patent, and exclusivity
    records. Use search_drug_applications for Drugs@FDA submissions and approval history, or
    NDC actions for marketed product-listing metadata; Orange Book metadata alone does not
    establish current legal or marketing status.
    """
    return "openfda_search_orange_book: static placeholder response."


@tool
def openfda_search_substances(query: str) -> str:
    """
    Use for FDA molecular substance records by name, UNII, substance class, or external
    code, including UUID, definitions, bounded names, classes, and codes. Use
    search_ingredient_identifiers for simple UNII-name pairs; do not use this for RxCUI
    resolution or product-level NDC lookup.
    """
    return "openfda_search_substances: static placeholder response."


@tool
def openfda_search_tobacco_digital_ad_research(query: str) -> str:
    """
    Use for FDA digital tobacco-ad research by ad number, channel, format, or brand-
    recognition metric. Use prevention-ad research for exposure studies and smokefree
    research for campaign variables, definitions, or cessation metrics.
    """
    return "openfda_search_tobacco_digital_ad_research: static placeholder response."


@tool
def openfda_search_tobacco_prevention_ad_research(query: str) -> str:
    """
    Use for FDA tobacco-prevention advertisement study records by ad number, study name,
    tobacco product, or exposure type. Use the digital-ad action for channel, format, or
    brand-recognition metrics and the smokefree action for campaign variables or cessation-
    research metrics.
    """
    return "openfda_search_tobacco_prevention_ad_research: static placeholder response."


@tool
def openfda_search_tobacco_smokefree_research(query: str) -> str:
    """
    Use for FDA smokefree or vaping-cessation campaign research by study variable, variable
    definition, or reported metric. Use prevention-ad research for ad exposure studies and
    digital-ad research for channel, format, or brand-recognition records.
    """
    return "openfda_search_tobacco_smokefree_research: static placeholder response."


@tool
def openfda_summarize_adverse_event_reactions(query: str) -> str:
    """
    Use for aggregate FAERS reaction-term counts for a drug name or RxCUI. Do not treat
    report counts as incidence, causality, comparative risk, or expected side effects.
    """
    return "openfda_summarize_adverse_event_reactions: static placeholder response."


@tool
def openfda_summarize_animal_drug_adverse_events(query: str) -> str:
    """
    Use for aggregate FDA animal or veterinary-drug adverse-event report counts by reaction,
    species, outcome, or drug brand. Do not interpret report counts as incidence, causality,
    comparative risk, or veterinary treatment advice.
    """
    return "openfda_summarize_animal_drug_adverse_events: static placeholder response."


@tool
def openfda_summarize_cosmetic_adverse_events(query: str) -> str:
    """
    Use for aggregate FDA cosmetic adverse-event report counts grouped by reaction, product,
    report type, or gender. Do not interpret report counts as incidence, causality,
    comparative risk, or general product-safety evidence.
    """
    return "openfda_summarize_cosmetic_adverse_events: static placeholder response."


@tool
def openfda_summarize_device_adverse_events(query: str) -> str:
    """
    Use for aggregate MAUDE medical-device event-type counts by device, brand, manufacturer,
    or product code. Do not use the counts as incidence, causality, comparative-risk, or
    general device-safety evidence.
    """
    return "openfda_summarize_device_adverse_events: static placeholder response."


@tool
def openfda_summarize_drug_brand_names(query: str) -> str:
    """
    Use to count distinct brand names represented in FDA NDC Directory listings for a
    generic name, ingredient, or manufacturer. Use search_ndc_products when the user needs
    individual product records rather than a brand-name aggregation.
    """
    return "openfda_summarize_drug_brand_names: static placeholder response."


@tool
def openfda_summarize_food_adverse_events(query: str) -> str:
    """
    Use for aggregate FDA food or dietary-supplement adverse-event report counts grouped by
    reaction, outcome, product, or industry. Do not use these counts as incidence,
    causality, comparative-risk, or general food-safety evidence.
    """
    return "openfda_summarize_food_adverse_events: static placeholder response."


@tool
def openfda_summarize_tobacco_product_problems(query: str) -> str:
    """
    Use for aggregate FDA tobacco, e-cigarette, or vaping product-problem report counts by
    product problem, health problem, or product type. Do not interpret report counts as
    incidence, causality, comparative risk, or cessation advice.
    """
    return "openfda_summarize_tobacco_product_problems: static placeholder response."


@tool
def pubmed_convert_article_ids(query: str) -> str:
    """
    Use when the user asks to map known PMID, PMCID, DOI, or manuscript identifiers to their
    corresponding publication identifiers. Do not use for topic search.
    """
    return "pubmed_convert_article_ids: static placeholder response."


@tool
def pubmed_find_related_articles(query: str) -> str:
    """
    Use after the user supplies a PMID or a PubMed result and asks for similar publications
    or linked NCBI records. Use search_articles instead for a new topic-based literature
    search.
    """
    return "pubmed_find_related_articles: static placeholder response."


@tool
def pubmed_get_articles(query: str) -> str:
    """
    Use before generic web search when the user provides PMIDs or asks to retrieve specific
    PubMed citation metadata and abstracts. Use search_articles first when PMIDs are not
    available.
    """
    return "pubmed_get_articles: static placeholder response."


@tool
def pubmed_get_copyright_status(query: str) -> str:
    """
    Use when the user asks whether known PubMed articles are open access, what rights or
    licenses apply, or whether PubMed Central full text can be retrieved. Accepts at most 10
    PMIDs per call because rights checks can require separate PMC requests.
    """
    return "pubmed_get_copyright_status: static placeholder response."


@tool
def pubmed_get_full_text_articles(query: str) -> str:
    """
    Use before generic web search when the user provides PMCIDs or asks for rights-eligible
    PubMed Central full text. Use identifier conversion or article search first when PMCIDs
    are not available.
    """
    return "pubmed_get_full_text_articles: static placeholder response."


@tool
def pubmed_match_citations(query: str) -> str:
    """
    Use to resolve structured or incomplete journal citation fields to PMIDs. Use
    search_articles instead for free-text publication discovery.
    """
    return "pubmed_match_citations: static placeholder response."


@tool
def pubmed_search_articles(query: str) -> str:
    """
    Use to search the biomedical literature when no exact PMID is known: topic, author,
    title, journal, or date searches; literature or evidence reviews; named papers; or
    studies supporting, comparing, or challenging a claim. Prefer this before generic web
    search for publication discovery.
    """
    return "pubmed_search_articles: static placeholder response."


@tool
def rxnorm_get_concept(query: str) -> str:
    """
    Use when an RxCUI is explicitly identified or was selected from search_drugs. Never
    reinterpret a patient, account, or record number as an RxCUI.
    """
    return "rxnorm_get_concept: static placeholder response."


@tool
def rxnorm_get_related_concepts(query: str) -> str:
    """
    Use after selecting an RxCUI to verify ingredients and enumerate normalized generic,
    brand, product, strength, dose-form, or pack relationships. Use only an RxCUI explicitly
    identified by the user or returned by RxNorm; never reinterpret a patient, account, or
    record number as an RxCUI.
    """
    return "rxnorm_get_related_concepts: static placeholder response."


@tool
def rxnorm_resolve_ndc(query: str) -> str:
    """
    Use when the input is explicitly identified as an NDC medication-product identifier and
    the task needs its normalized RxNorm concept, current or obsolete mapping status, source
    vocabularies, or mapping history. Never reinterpret a patient, account, or record number
    as an NDC.
    """
    return "rxnorm_resolve_ndc: static placeholder response."


@tool
def rxnorm_search_drugs(query: str) -> str:
    """
    This is the required entry action for medication name equivalence, generic-brand or
    U.S.-equivalent-name mapping, and normalized formulation inventories, even when the user
    does not ask for an RxCUI. Do not answer those terminology mappings from memory when
    this action is available.
    """
    return "rxnorm_search_drugs: static placeholder response."


HEALTHCARE_TOOLS = [
    clinicaltrials_gov_analyze_endpoints,
    clinicaltrials_gov_get_trial_details,
    clinicaltrials_gov_get_trial_results_and_publications,
    clinicaltrials_gov_search_by_eligibility,
    clinicaltrials_gov_search_by_sponsor,
    clinicaltrials_gov_search_investigators,
    clinicaltrials_gov_search_trials,
    cms_coverage_get_coding_analysis_for_labs,
    cms_coverage_get_local_coverage_data_freshness,
    cms_coverage_get_national_coverage_analysis,
    cms_coverage_get_national_coverage_determination,
    cms_coverage_list_local_coverage_contractor_classifications,
    cms_coverage_list_local_coverage_contractors,
    cms_coverage_list_local_coverage_states,
    cms_coverage_list_national_coverage_determination_related_analyses,
    cms_coverage_list_national_coverage_determination_versions,
    cms_coverage_list_recent_local_coverage_updates,
    cms_coverage_list_recent_national_coverage_updates,
    cms_coverage_search_annual_national_coverage_documents,
    cms_coverage_search_coding_analyses_for_labs,
    cms_coverage_search_local_coverage_summaries,
    cms_coverage_search_national_coverage_analyses,
    cms_coverage_search_national_coverage_determinations,
    cms_coverage_search_national_coverage_reference_documents,
    cms_open_data_compare_part_d_prescriber_classes,
    cms_open_data_get_curated_dataset_schema,
    cms_open_data_get_geographic_service_utilization_trend,
    cms_open_data_get_part_d_geography_totals,
    cms_open_data_list_curated_datasets,
    cms_open_data_rank_physician_services,
    cms_open_data_search_geographic_service_utilization,
    cms_open_data_search_inpatient_hospital_payments,
    cms_open_data_search_part_d_prescribers_by_drug,
    cms_open_data_search_physician_payment_by_provider,
    cms_open_data_search_physician_payment_by_service,
    dailymed_get_label_history,
    dailymed_get_label_products,
    dailymed_get_label_sections,
    dailymed_search_labels,
    medicare_care_compare_compare_hospital_quality_measure,
    medicare_care_compare_find_home_health_agencies,
    medicare_care_compare_find_hospitals,
    medicare_care_compare_find_nursing_homes,
    medicare_care_compare_get_hospital_details,
    medicare_care_compare_get_hospital_outcomes,
    medicare_care_compare_get_hospital_patient_experience,
    medicare_care_compare_get_hospital_quality_measures,
    medicare_care_compare_get_measure_specifications,
    npi_registry_lookup_npi,
    npi_registry_search_providers,
    npi_registry_validate_npi,
    openfda_get_drug_label_sections,
    openfda_lookup_ndc_product,
    openfda_search_complete_response_letters,
    openfda_search_covid19_serology_evaluations,
    openfda_search_device_510k_clearances,
    openfda_search_device_classifications,
    openfda_search_device_identifiers,
    openfda_search_device_premarket_approvals,
    openfda_search_device_recall_enforcement,
    openfda_search_device_recalls,
    openfda_search_device_registrations,
    openfda_search_drug_applications,
    openfda_search_drug_labels,
    openfda_search_drug_recalls,
    openfda_search_drug_shortages,
    openfda_search_food_recalls,
    openfda_search_historical_documents,
    openfda_search_ingredient_identifiers,
    openfda_search_ndc_products,
    openfda_search_ndc_spl_data_elements,
    openfda_search_orange_book,
    openfda_search_substances,
    openfda_search_tobacco_digital_ad_research,
    openfda_search_tobacco_prevention_ad_research,
    openfda_search_tobacco_smokefree_research,
    openfda_summarize_adverse_event_reactions,
    openfda_summarize_animal_drug_adverse_events,
    openfda_summarize_cosmetic_adverse_events,
    openfda_summarize_device_adverse_events,
    openfda_summarize_drug_brand_names,
    openfda_summarize_food_adverse_events,
    openfda_summarize_tobacco_product_problems,
    pubmed_convert_article_ids,
    pubmed_find_related_articles,
    pubmed_get_articles,
    pubmed_get_copyright_status,
    pubmed_get_full_text_articles,
    pubmed_match_citations,
    pubmed_search_articles,
    rxnorm_get_concept,
    rxnorm_get_related_concepts,
    rxnorm_resolve_ndc,
    rxnorm_search_drugs,
]
