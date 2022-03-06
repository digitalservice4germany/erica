import asyncio
import datetime
from uuid import UUID, uuid4

from opyoid import Injector, Module
from rq import Retry

from src.application.FreischaltCode.freischalt_code import FreischaltCodeCreateDto, FreischaltCodeDto
from src.application.FreischaltCode.Jobs.jobs import send_freischalt_code
from src.domain.FreischaltCode.freischalt_code import FreischaltCode
from src.infrastructure.rq.queue import dongle_queue
from src.infrastructure.sqlalchemy.repositories.RepositoriesModule import RepositoriesModule
from src.infrastructure.sqlalchemy.repositories.freischalt_code_repository import FreischaltCodeRepository

injector = Injector([RepositoriesModule()])


class FreischaltCodeService:
    freischaltcode_repository: FreischaltCodeRepository

    def __init__(self, repository: FreischaltCodeRepository = injector.inject(FreischaltCodeRepository)) -> None:
        super().__init__()
        self.freischaltcode_repository = repository

    async def send_scheduled_to_elster(self, freischaltcode_dto: FreischaltCodeCreateDto) -> FreischaltCodeDto:
        job_id = uuid4()
        freischaltcode = FreischaltCode(tax_ident=freischaltcode_dto.tax_ident,
                                        job_id=job_id,
                                        date_of_birth=freischaltcode_dto.date_of_birth,
                                        created_at=datetime.datetime.now().__str__(),
                                        updated_at=datetime.datetime.now().__str__(),
                                        creator_id="api"
                                        )

        created = self.freischaltcode_repository.create(freischaltcode)

        dongle_queue.enqueue(send_freischalt_code,
                             created.id,
                             retry=Retry(max=3, interval=60),
                             job_id=job_id.__str__()
                             )

        return created

    async def send_to_elster(self, freischaltcode_dto: FreischaltCodeCreateDto):
        await asyncio.sleep(1)
        pass

    def get_status(self, tax_ident: UUID):
        return self.freischaltcode_repository.get_by_id(tax_ident)


class ApplicationFreischaltCodeModule(Module):
    def configure(self) -> None:
        self.install(ApplicationFreischaltCodeModule())
        self.bind(FreischaltCodeService)
