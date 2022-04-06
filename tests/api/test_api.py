import json
import uuid
from unittest.mock import MagicMock, Mock, patch

import pytest

from erica.api.v2.endpoints.est import send_est, get_send_est_job
from erica.api.v2.endpoints.fsc import request_fsc, get_fsc_request_job, activate_fsc, get_fsc_activation_job, \
    revocate_fsc, get_fsc_revocation_job
from erica.api.v2.endpoints.grundsteuer import send_grundsteuer, get_grundsteuer_job
from erica.api.v2.endpoints.tax import is_valid_tax_number, get_valid_tax_number_job
from erica.application.FreischaltCode.FreischaltCodeService import FreischaltCodeService
from erica.application.JobService.job_service import JobService
from erica.application.Shared.response_dto import JobState
from erica.application.erica_request.erica_request import EricaRequestDto
from erica.application.grundsteuer.GrundsteuerService import GrundsteuerService
from erica.application.tax_declaration.TaxDeclarationService import TaxDeclarationService
from erica.application.tax_number_validation.TaxNumberValidityService import TaxNumberValidityService
from erica.domain.Shared.EricaRequest import RequestType
from erica.domain.Shared.Status import Status
from erica.domain.erica_request.erica_request import EricaRequest
from erica.infrastructure.sqlalchemy.repositories.base_repository import EntityNotFoundError
from tests.application.job_service.test_job_service import MockEricaRequestRepository, MockRequestController, MockDto, \
    PickableMock
from tests.utils import create_unlock_code_request, \
    create_unlock_code_activation, create_unlock_code_revocation, create_tax_number_validity, create_send_est, \
    get_job_service_patch_string, create_send_grundsteuer


@pytest.mark.asyncio
@pytest.mark.parametrize("api_method, input_data, request_type, endpoint_to_patch, expected_location",
                         [(request_fsc, create_unlock_code_request(), RequestType.freischalt_code_request, "fsc",
                           "fsc/request/"),
                          (activate_fsc, create_unlock_code_activation(), RequestType.freischalt_code_activate, "fsc",
                           "fsc/activation/"),
                          (revocate_fsc, create_unlock_code_revocation(), RequestType.freischalt_code_revocate, "fsc",
                           "fsc/revocation/"),
                          (is_valid_tax_number, create_tax_number_validity(), RequestType.check_tax_number, "tax",
                           "tax_number_validity/"),
                          (send_est, create_send_est(), RequestType.send_est, "est", "ests/"),
                          (send_grundsteuer, create_send_grundsteuer(), RequestType.grundsteuer, "grundsteuer",
                           "grundsteuer/")],
                         ids=["request_fsc", "activate_fsc", "revocate_fsc", "is_valid_tax_number", "send_est",
                              "grundsteuer"])
async def test_if_post_job_returns_location_with_uuid(api_method, input_data, request_type, endpoint_to_patch,
                                                      expected_location):
    request_id = uuid.uuid4()
    job_service_mock = JobService(job_repository=MockEricaRequestRepository(), background_worker=MagicMock(),
                                  request_controller=MockRequestController, payload_type=MockDto,
                                  job_method=PickableMock())
    job_service_mock.add_to_queue = Mock(
        return_value=EricaRequestDto(type=request_type, status=Status.new, payload="{}",
                                     request_id=request_id))
    with patch(get_job_service_patch_string(endpoint_to_patch), MagicMock(return_value=job_service_mock)):
        response = await api_method(input_data)
        assert response.headers['Location'] == expected_location + str(request_id)


@pytest.mark.asyncio
@pytest.mark.parametrize("api_method, request_type", [(get_fsc_request_job, RequestType.freischalt_code_request),
                                                      (get_fsc_activation_job, RequestType.freischalt_code_activate)],
                         ids=["request_fsc", "activate_fsc"])
async def test_if_get_fsc_request_or_activation_job_returns_success_status_with_result(api_method, request_type):
    request_id = uuid.uuid4()
    idnr = "test_idnr"
    elster_request_id = "test_elster_request_id"
    transfer_ticket = "test_transfer_ticket"
    erica_request = EricaRequest(type=request_type, status=Status.success,
                                 payload={"idnr": idnr},
                                 result={"elster_request_id": elster_request_id,
                                         "transfer_ticket": transfer_ticket},
                                 request_id=request_id, creator_id="test")
    with patch("erica.api.v2.endpoints.fsc.get_service", MagicMock()) as get_service_mock:
        mock_service = MagicMock(get_request_by_request_id=MagicMock(return_value=erica_request))
        get_service_mock.return_value = FreischaltCodeService(service=mock_service)
        response = await api_method(request_id)
        assert response.processStatus == JobState.SUCCESS
        assert response.result.idnr == idnr
        assert response.result.elster_request_id == elster_request_id
        assert response.result.transfer_ticket == transfer_ticket
        assert response.errorCode is None
        assert response.errorMessage is None


@pytest.mark.asyncio
async def test_if_get_fsc_revocation_job_returns_success_status_with_result():
    request_id = uuid.uuid4()
    idnr = "test_idnr"
    transfer_ticket = "test_transfer_ticket"
    erica_request = EricaRequest(type=RequestType.freischalt_code_revocate, status=Status.success,
                                 payload={"idnr": idnr},
                                 result={"transfer_ticket": transfer_ticket, "idnr": idnr},
                                 request_id=request_id, creator_id="test")
    with patch("erica.api.v2.endpoints.fsc.get_service", MagicMock()) as get_service_mock:
        mock_service = MagicMock(get_request_by_request_id=MagicMock(return_value=erica_request))
        get_service_mock.return_value = FreischaltCodeService(service=mock_service)
        response = await get_fsc_revocation_job(request_id)
        assert response.processStatus == JobState.SUCCESS
        assert response.result.idnr == idnr
        assert response.result.transfer_ticket == transfer_ticket
        assert response.errorCode is None
        assert response.errorMessage is None


@pytest.mark.asyncio
async def test_if_get_tax_validity_job_returns_success_status_with_result():
    request_id = uuid.uuid4()
    is_valid = True
    erica_request = EricaRequest(type=RequestType.check_tax_number, status=Status.success,
                                 payload={},
                                 result={"is_valid": is_valid},
                                 request_id=request_id, creator_id="test")
    with patch("erica.api.v2.endpoints.tax.get_service", MagicMock()) as get_service_mock:
        mock_service = MagicMock(get_request_by_request_id=MagicMock(return_value=erica_request))
        get_service_mock.return_value = TaxNumberValidityService(service=mock_service)
        response = await get_valid_tax_number_job(request_id)
        assert response.processStatus == JobState.SUCCESS
        assert response.result.is_valid == is_valid
        assert response.errorCode is None
        assert response.errorMessage is None


@pytest.mark.asyncio
async def test_if_get_send_est_job_returns_success_status_with_result():
    request_id = uuid.uuid4()
    pdf = "test_pdf"
    transfer_ticket = "test_transfer_ticket"
    erica_request = EricaRequest(type=RequestType.send_est, status=Status.success,
                                 payload={},
                                 result={"transfer_ticket": transfer_ticket, "pdf": pdf},
                                 request_id=request_id, creator_id="test")
    with patch("erica.api.v2.endpoints.est.get_service", MagicMock()) as get_service_mock:
        mock_service = MagicMock(get_request_by_request_id=MagicMock(return_value=erica_request))
        get_service_mock.return_value = TaxDeclarationService(service=mock_service)
        response = await get_send_est_job(request_id)
        assert response.processStatus == JobState.SUCCESS
        assert response.result.pdf == pdf
        assert response.result.transfer_ticket == transfer_ticket
        assert response.errorCode is None
        assert response.errorMessage is None


@pytest.mark.asyncio
async def test_if_get_grundsteuer_job_returns_success_status_with_result():
    request_id = uuid.uuid4()
    pdf = "test_pdf"
    transfer_ticket = "test_transfer_ticket"
    erica_request = EricaRequest(type=RequestType.grundsteuer, status=Status.success,
                                 payload={},
                                 result={"transfer_ticket": transfer_ticket, "pdf": pdf},
                                 request_id=request_id, creator_id="test")
    with patch("erica.api.v2.endpoints.grundsteuer.get_service", MagicMock()) as get_service_mock:
        mock_service = MagicMock(get_request_by_request_id=MagicMock(return_value=erica_request))
        get_service_mock.return_value = GrundsteuerService(service=mock_service)
        response = await get_grundsteuer_job(request_id)
        assert response.processStatus == JobState.SUCCESS
        assert response.result.pdf == pdf
        assert response.result.transfer_ticket == transfer_ticket
        assert response.errorCode is None
        assert response.errorMessage is None


@pytest.mark.asyncio
@pytest.mark.parametrize("api_method, request_type",
                         [(get_fsc_request_job, RequestType.freischalt_code_request),
                          (get_fsc_activation_job, RequestType.freischalt_code_activate),
                          (get_fsc_revocation_job, RequestType.freischalt_code_revocate)],
                         ids=["request_fsc", "activate_fsc", "revocate_fsc"])
async def test_if_get_fsc_job_returns_failure_status(api_method, request_type):
    request_id = uuid.uuid4()
    error_code = "1"
    error_message = "wingardium leviosa"
    erica_request = EricaRequest(type=request_type, status=Status.failed,
                                 error_code=error_code,
                                 error_message=error_message,
                                 request_id=request_id, creator_id="test")
    with patch("erica.api.v2.endpoints.fsc.get_service", MagicMock()) as get_service_mock:
        mock_service = MagicMock(get_request_by_request_id=MagicMock(return_value=erica_request))
        get_service_mock.return_value = FreischaltCodeService(service=mock_service)
        response = await api_method(request_id)
        assert response.processStatus == JobState.FAILURE
        assert response.errorCode == error_code
        assert response.errorMessage == error_message
        assert response.result is None


@pytest.mark.asyncio
async def test_if_get_tax_validity_job_returns_failure_status():
    request_id = uuid.uuid4()
    error_code = "1"
    error_message = "wingardium leviosa"
    erica_request = EricaRequest(type=RequestType.check_tax_number, status=Status.failed,
                                 error_code=error_code,
                                 error_message=error_message,
                                 request_id=request_id, creator_id="test")
    with patch("erica.api.v2.endpoints.tax.get_service", MagicMock()) as get_service_mock:
        mock_service = MagicMock(get_request_by_request_id=MagicMock(return_value=erica_request))
        get_service_mock.return_value = TaxNumberValidityService(service=mock_service)
        response = await get_valid_tax_number_job(request_id)
        assert response.processStatus == JobState.FAILURE
        assert response.errorCode == error_code
        assert response.errorMessage == error_message
        assert response.result is None


@pytest.mark.asyncio
async def test_if_get_est_job_returns_failure_status():
    request_id = uuid.uuid4()
    error_code = "1"
    error_message = "wingardium leviosa"
    erica_request = EricaRequest(type=RequestType.send_est, status=Status.failed,
                                 error_code=error_code,
                                 error_message=error_message,
                                 request_id=request_id, creator_id="test")
    with patch("erica.api.v2.endpoints.est.get_service", MagicMock()) as get_service_mock:
        mock_service = MagicMock(get_request_by_request_id=MagicMock(return_value=erica_request))
        get_service_mock.return_value = TaxDeclarationService(service=mock_service)
        response = await get_send_est_job(request_id)
        assert response.processStatus == JobState.FAILURE
        assert response.errorCode == error_code
        assert response.errorMessage == error_message
        assert response.result is None


@pytest.mark.asyncio
async def test_if_get_grundsteuer_job_returns_failure_status():
    request_id = uuid.uuid4()
    error_code = "1"
    error_message = "wingardium leviosa"
    erica_request = EricaRequest(type=RequestType.grundsteuer, status=Status.failed,
                                 error_code=error_code,
                                 error_message=error_message,
                                 request_id=request_id, creator_id="test")
    with patch("erica.api.v2.endpoints.grundsteuer.get_service", MagicMock()) as get_service_mock:
        mock_service = MagicMock(get_request_by_request_id=MagicMock(return_value=erica_request))
        get_service_mock.return_value = GrundsteuerService(service=mock_service)
        response = await get_grundsteuer_job(request_id)
        assert response.processStatus == JobState.FAILURE
        assert response.errorCode == error_code
        assert response.errorMessage == error_message
        assert response.result is None


@pytest.mark.asyncio
@pytest.mark.parametrize("mock_job_state", [Status.new, Status.scheduled, Status.processing])
@pytest.mark.parametrize("api_method, request_type",
                         [(get_fsc_request_job, RequestType.freischalt_code_request),
                          (get_fsc_activation_job, RequestType.freischalt_code_activate),
                          (get_fsc_revocation_job, RequestType.freischalt_code_revocate)],
                         ids=["request_fsc", "activate_fsc", "revocate_fsc"])
async def test_if_get_fsc_job_returns_processing_status(mock_job_state, api_method, request_type):
    request_id = uuid.uuid4()
    erica_request = EricaRequest(type=request_type, status=mock_job_state,
                                 request_id=request_id, creator_id="test")
    with patch("erica.api.v2.endpoints.fsc.get_service", MagicMock()) as get_service_mock:
        mock_service = MagicMock(get_request_by_request_id=MagicMock(return_value=erica_request))
        get_service_mock.return_value = FreischaltCodeService(service=mock_service)
        response = await api_method(request_id)
        assert response.processStatus == JobState.PROCESSING
        assert response.result is None
        assert response.errorCode is None
        assert response.errorMessage is None


@pytest.mark.asyncio
@pytest.mark.parametrize("mock_job_state", [Status.new, Status.scheduled, Status.processing])
@pytest.mark.parametrize("api_method, request_type", [(get_valid_tax_number_job, RequestType.check_tax_number)])
async def test_if_get_tax_validity_job_returns_processing_status(mock_job_state, api_method, request_type):
    request_id = uuid.uuid4()
    erica_request = EricaRequest(type=request_type, status=mock_job_state,
                                 request_id=request_id, creator_id="test")
    with patch("erica.api.v2.endpoints.tax.get_service", MagicMock()) as get_service_mock:
        mock_service = MagicMock(get_request_by_request_id=MagicMock(return_value=erica_request))
        get_service_mock.return_value = TaxNumberValidityService(service=mock_service)
        response = await api_method(request_id)
        assert response.processStatus == JobState.PROCESSING
        assert response.result is None
        assert response.errorCode is None
        assert response.errorMessage is None


@pytest.mark.asyncio
@pytest.mark.parametrize("mock_job_state", [Status.new, Status.scheduled, Status.processing])
@pytest.mark.parametrize("api_method, request_type", [(get_send_est_job, RequestType.send_est)])
async def test_if_get_est_job_returns_processing_status(mock_job_state, api_method, request_type):
    request_id = uuid.uuid4()
    erica_request = EricaRequest(type=request_type, status=mock_job_state,
                                 request_id=request_id, creator_id="test")
    with patch("erica.api.v2.endpoints.est.get_service", MagicMock()) as get_service_mock:
        mock_service = MagicMock(get_request_by_request_id=MagicMock(return_value=erica_request))
        get_service_mock.return_value = TaxDeclarationService(service=mock_service)
        response = await api_method(request_id)
        assert response.processStatus == JobState.PROCESSING
        assert response.result is None
        assert response.errorCode is None
        assert response.errorMessage is None


@pytest.mark.asyncio
@pytest.mark.parametrize("mock_job_state", [Status.new, Status.scheduled, Status.processing])
@pytest.mark.parametrize("api_method, request_type", [(get_grundsteuer_job, RequestType.grundsteuer)])
async def test_if_get_grundsteuer_job_returns_processing_status(mock_job_state, api_method, request_type):
    request_id = uuid.uuid4()
    erica_request = EricaRequest(type=request_type, status=mock_job_state,
                                 request_id=request_id, creator_id="test")
    with patch("erica.api.v2.endpoints.grundsteuer.get_service", MagicMock()) as get_service_mock:
        mock_service = MagicMock(get_request_by_request_id=MagicMock(return_value=erica_request))
        get_service_mock.return_value = GrundsteuerService(service=mock_service)
        response = await api_method(request_id)
        assert response.processStatus == JobState.PROCESSING
        assert response.result is None
        assert response.errorCode is None
        assert response.errorMessage is None


@pytest.mark.asyncio
@pytest.mark.parametrize("api_method",
                         [get_fsc_request_job, get_fsc_activation_job, get_fsc_revocation_job],
                         ids=["request_fsc", "activate_fsc", "revocate_fsc"])
async def test_if_get_fsc_job_returns_not_found(api_method):
    request_id = uuid.uuid4()
    with patch("erica.api.v2.endpoints.fsc.get_service", MagicMock()) as get_service_mock:
        mock_service = MagicMock(get_request_by_request_id=MagicMock(side_effect=EntityNotFoundError))
        get_service_mock.return_value = FreischaltCodeService(service=mock_service)
        response = await api_method(request_id)
        body = json.loads(response.body)
        assert body['errorCode'] == -1
        assert body['errorMessage'] == "Raised in case an entity could not be found in the database"


@pytest.mark.asyncio
async def test_if_get_tax_validity_job_returns_not_found():
    request_id = uuid.uuid4()
    with patch("erica.api.v2.endpoints.tax.get_service", MagicMock()) as get_service_mock:
        mock_service = MagicMock(get_request_by_request_id=MagicMock(side_effect=EntityNotFoundError))
        get_service_mock.return_value = TaxNumberValidityService(service=mock_service)
        response = await get_valid_tax_number_job(request_id)
        body = json.loads(response.body)
        assert body['errorCode'] == -1
        assert body['errorMessage'] == "Raised in case an entity could not be found in the database"


@pytest.mark.asyncio
async def test_if_get_est_job_returns_not_found():
    request_id = uuid.uuid4()
    with patch("erica.api.v2.endpoints.est.get_service", MagicMock()) as get_service_mock:
        mock_service = MagicMock(get_request_by_request_id=MagicMock(side_effect=EntityNotFoundError))
        get_service_mock.return_value = TaxDeclarationService(service=mock_service)
        response = await get_send_est_job(request_id)
        body = json.loads(response.body)
        assert body['errorCode'] == -1
        assert body['errorMessage'] == "Raised in case an entity could not be found in the database"


@pytest.mark.asyncio
async def test_if_get_grundsteuer_job_returns_not_found():
    request_id = uuid.uuid4()
    with patch("erica.api.v2.endpoints.grundsteuer.get_service", MagicMock()) as get_service_mock:
        mock_service = MagicMock(get_request_by_request_id=MagicMock(side_effect=EntityNotFoundError))
        get_service_mock.return_value = GrundsteuerService(service=mock_service)
        response = await get_grundsteuer_job(request_id)
        body = json.loads(response.body)
        assert body['errorCode'] == -1
        assert body['errorMessage'] == "Raised in case an entity could not be found in the database"
