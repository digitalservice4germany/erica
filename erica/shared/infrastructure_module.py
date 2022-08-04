from opyoid import Module
from sqlalchemy.orm import Session

from erica.shared.domain_module import DomainModule
from erica.shared.repositories.base_repository_interface import BaseRepositoryInterface
from erica.shared.repositories.erica_request_repository_interface import EricaRequestRepositoryInterface
from erica.shared.sqlalchemy.erica_request_schema import EricaRequestSchema
from erica.shared.sqlalchemy.database import DatabaseSessionProvider
from erica.shared.sqlalchemy.repositories.erica_request_repository import EricaRequestRepository


class InfrastructureModule(Module):
    def configure(self) -> None:
        self.install(DomainModule())
        self.bind(Session, to_provider=DatabaseSessionProvider)
        self.bind(EricaRequestRepositoryInterface, to_class=EricaRequestRepository)
        self.bind(BaseRepositoryInterface[EricaRequestSchema], to_class=EricaRequestRepository)
