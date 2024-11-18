from datetime import datetime
from fastapi_utils.tasks import repeat_every
from fastapi import FastAPI , APIRouter
from repositories.statistics_repo import StatisticsRepo


cronjob = APIRouter()

@cronjob.on_event("startup")
@repeat_every(seconds=3600)
async def run_job():
    print("Running job")
    statistics_repo = StatisticsRepo()
    try:
        print("Heads up! Job started at", datetime.now())
    except Exception as e:
        print("Error in job", e)
