from uuid import UUID

from pydantic import BaseModel

from src.domain.TaxDeclaration.TaxDeclaration import TaxDeclarationPayload
from src.domain.Shared.Status import Status


class TaxDeclarationCreateDto(BaseModel):
    payload: TaxDeclarationPayload
    user_id: UUID

    class Config:
        orm_mode = True


class TaxDeclarationDto(BaseModel):
    id: UUID
    status: Status
    payload: TaxDeclarationPayload
    user_id: UUID

    class Config:
        orm_mode = True


class TaxDeclarationValidateDto(BaseModel):
    payload: TaxDeclarationPayload
    user_id: UUID

    class Config:
        orm_mode = True