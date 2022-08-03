import os
from datetime import date

from erica.application.freischaltcode.freischaltcode import FreischaltCodeRequestDto, FreischaltCodeActivateDto, \
    FreischaltCodeRevocateDto
from erica.application.tax_declaration.tax_declaration_dto import TaxDeclarationDto
from erica.application.tax_number_validation.tax_number_validation_dto import CheckTaxNumberDto
from erica.domain.freischaltcode.freischaltcode import FreischaltCodeRequestPayload, FreischaltCodeActivatePayload, \
    FreischaltCodeRevocatePayload
from erica.domain.tax_declaration.tax_declaration import TaxDeclarationPayload
from erica.domain.tax_number_validation.tax_number_validation import CheckTaxNumberPayload
from erica.application.grundsteuer.grundsteuer_dto import GrundsteuerDto
from tests.erica_legacy.samples.grundsteuer_sample_data import SampleGrundsteuerData
from tests.erica_legacy.utils import create_meta_data, create_form_data

samples_folder = os.path.join(os.path.dirname(__file__), 'erica_legacy/samples')


def read_text_from_sample(sample_name, read_type='r'):
    with open(os.path.join(samples_folder, sample_name), read_type) as sample_xml:
        return sample_xml.read()


def create_unlock_code_request(correct=True):
    if correct:
        payload = FreischaltCodeRequestPayload(tax_id_number="04531972802", date_of_birth=date(1957, 7, 14))
    else:
        payload = FreischaltCodeRequestPayload(tax_id_number="123456789", date_of_birth=date(1969, 7, 20))

    return FreischaltCodeRequestDto(payload=payload, client_identifier="steuerlotse")


def create_unlock_code_activation(correct=True):
    if correct:
        payload = FreischaltCodeActivatePayload(tax_id_number="09952417688", freischalt_code="42",
                                                elster_request_id="CORRECT")
    else:
        payload = FreischaltCodeActivatePayload(tax_id_number="123456789", freischalt_code="INCORRECT",
                                                elster_request_id="INCORRECT")

    return FreischaltCodeActivateDto(payload=payload, client_identifier="steuerlotse")


def create_unlock_code_revocation(correct=True):
    if correct:
        payload = FreischaltCodeRevocatePayload(tax_id_number="04531972802", elster_request_id="CORRECT")
    else:
        payload = FreischaltCodeRevocatePayload(tax_id_number="123456789", elster_request_id="INCORRECT")

    return FreischaltCodeRevocateDto(payload=payload, client_identifier="steuerlotse")


def create_tax_number_validity(correct=True):
    if correct:
        payload = CheckTaxNumberPayload(state_abbreviation="BY", tax_number="04531972802")
    else:
        payload = CheckTaxNumberPayload(state_abbreviation="BY", tax_number="123456789")

    return CheckTaxNumberDto(payload=payload, client_identifier="steuerlotse")


def create_send_est():
    payload = TaxDeclarationPayload(est_data=create_form_data(), meta_data=create_meta_data())
    return TaxDeclarationDto(payload=payload, client_identifier="steuerlotse")


def create_send_grundsteuer():
    return GrundsteuerDto(payload=SampleGrundsteuerData().parse(), client_identifier="grundsteuer")


def get_job_service_patch_string(endpoint):
    return "erica.erica_api.api.v2.endpoints." + endpoint + ".get_job_service"


def get_erica_request_patch_string(endpoint):
    return "erica.erica_api.api.v2.endpoints." + endpoint + ".get_erica_request"
