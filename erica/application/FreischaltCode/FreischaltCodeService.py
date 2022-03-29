from abc import ABCMeta, abstractmethod
from uuid import UUID

from opyoid import Module

from erica.application.EricaRequest.EricaRequestService import EricaRequestService
from erica.application.FreischaltCode.FreischaltCode import FreischaltcodeRequestAndActivationResponseDto, \
    ResultFreischaltcodeRequestAndActivation, FreischaltcodeRevocationResponseDto, TransferTicketAndIdnr
from erica.application.Shared.response_dto import JobState
from erica.application.Shared.response_state_mapper import map_status


class FreischaltCodeServiceInterface:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_response_freischaltcode_request_and_activation(self,
                                                           request_id: UUID) -> FreischaltcodeRequestAndActivationResponseDto:
        pass

    @abstractmethod
    def get_response_freischaltcode_revocation(self, request_id: UUID) -> FreischaltcodeRevocationResponseDto:
        pass


class FreischaltCodeService(FreischaltCodeServiceInterface):
    erica_request_service: EricaRequestService

    def __init__(self, service: EricaRequestService) -> None:
        super().__init__()
        self.erica_request_service = service

    def get_response_freischaltcode_request_and_activation(self, request_id: UUID):
        erica_request = self.erica_request_service.get_request_by_request_id(request_id)
        process_status = map_status(erica_request.status)
        if process_status == JobState.SUCCESS:
            result = ResultFreischaltcodeRequestAndActivation(
                elster_request_id=erica_request.result["elster_request_id"],
                transfer_ticket=erica_request.result["transfer_ticket"],
                idnr=erica_request.payload.get("idnr"))
            return FreischaltcodeRequestAndActivationResponseDto(
                processStatus=map_status(erica_request.status), result=result)
        elif process_status == JobState.FAILURE:
            return FreischaltcodeRequestAndActivationResponseDto(
                processStatus=map_status(erica_request.status), errorCode=erica_request.error_code,
                errorMessage=erica_request.error_message)
        else:
            return FreischaltcodeRequestAndActivationResponseDto(
                processStatus=map_status(erica_request.status))

    def get_response_freischaltcode_revocation(self, request_id: UUID):
        erica_request = self.erica_request_service.get_request_by_request_id(request_id)
        process_status = map_status(erica_request.status)
        if process_status == JobState.SUCCESS:
            result = TransferTicketAndIdnr(
                transfer_ticket=erica_request.result["transfer_ticket"],
                idnr=erica_request.payload.get("idnr"))
            return FreischaltcodeRevocationResponseDto(
                processStatus=map_status(erica_request.status), result=result)
        elif process_status == JobState.FAILURE:
            return FreischaltcodeRevocationResponseDto(
                processStatus=map_status(erica_request.status), errorCode=erica_request.error_code,
                errorMessage=erica_request.error_message)
        else:
            return FreischaltcodeRevocationResponseDto(
                processStatus=map_status(erica_request.status))


class FreischaltCodeServiceModule(Module):
    def configure(self) -> None:
        self.bind(FreischaltCodeServiceInterface, to_class=FreischaltCodeService)
