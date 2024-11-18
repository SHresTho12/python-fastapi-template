import http

from fastapi import APIRouter, Depends, HTTPException

from Token_verifier.auth import verify_access_token
from repositories.statistics_repo import StatisticsRepo

stats_router = APIRouter()

@stats_router.get(
    "/get",
    status_code=http.HTTPStatus.OK,
    dependencies=[Depends(verify_access_token)]
)
async def get_stats():
    statistics_repo = StatisticsRepo()
    stats = await statistics_repo.get_one()
    if not stats:
        raise HTTPException(status_code=404, detail="No statistics found")
    stats["_id"] = str(stats["_id"])
    return stats
