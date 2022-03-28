from fastapi import APIRouter
from opyoid import Injector

from erica.api.ApiModule import ApiModule
from erica.application.EricaRequest.EricaRequestService import EricaRequestServiceInterface

router = APIRouter()

injector = Injector([
    ApiModule(),
])


@router.get("/erica_requests")
async def get_erica_request_status_list(skip: int, limit: int):
    freischalt_code_service: EricaRequestServiceInterface = injector.inject(EricaRequestServiceInterface)
    return freischalt_code_service.get_all_by_skip_and_limit(skip, limit)
