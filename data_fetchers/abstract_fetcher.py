from abc import ABC, abstractmethod
from typing import List
from models.job_report import JobReportRow
from models.cpi_report_row import CpiReportRow
from models.fed_rate_row import FedRateRow

class AbstractFetcher(ABC):

    @abstractmethod
    def get_jobs_data(self) -> List[JobReportRow]:
        pass

    @abstractmethod
    def get_cpi_data(self) -> List[CpiReportRow]:
        pass

    @abstractmethod
    def get_fed_rate_data(self) -> List[FedRateRow]:
        pass
