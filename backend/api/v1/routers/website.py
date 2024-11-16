from fastapi import APIRouter, status, Depends, Request,Query
from fastapi_pagination import LimitOffsetPage, paginate

from core.const import FILTERTYPE
from website.schema.website_schema import WebsiteViewResponse, WebsiteCreateSchema, WebsiteReadSchema, \
    WebsiteUpdateSchema
from website.service.website_service import WebsiteService
from core.utils import request_user

website_router = r = APIRouter()


@r.post(
    "",
    response_model=WebsiteViewResponse,
    status_code=status.HTTP_201_CREATED
)
async def create(
        website: WebsiteCreateSchema,
        current_user = Depends(request_user),
        service: WebsiteService = Depends(WebsiteService)
):
    website_data = website.copy(update={"user_id": current_user.id})
    created_website = await service.insert(website_data, current_user)
    return WebsiteViewResponse(detail="Website Created Successfully", data=created_website)


@r.get(
    "",
    response_model=LimitOffsetPage[WebsiteReadSchema],
    status_code = status.HTTP_200_OK
)
async def get_all(
        request:Request ,
        current_user=Depends(request_user),
        service: WebsiteService = Depends(WebsiteService)
):
    filters = {
        "user_id":current_user.id
    }

    websites = await service.all(query=request.query_params, filters=filters)
    return paginate(websites)

@r.get(
    "/{website_id}",
    response_model=WebsiteReadSchema,
    status_code=status.HTTP_200_OK
)
async def get(
        website_id:int,
        service: WebsiteService = Depends(WebsiteService)
):
    website = await service.get(website_id)
    return website

@r.put("/{website_id}", response_model=WebsiteViewResponse, status_code=status.HTTP_200_OK)
async def update(
        website_id:int,
        website: WebsiteUpdateSchema = WebsiteUpdateSchema,
        service: WebsiteService = Depends(WebsiteService),
        current_user = Depends(request_user)
):

    updated_website = await service.edit(website_id, website, current_user)
    return WebsiteViewResponse(detail="Website Updated Successfully", data=updated_website)


@r.delete("/{website_id}", response_model=dict())
async def delete(
        website_id: int,
        current_user=Depends(request_user),
        service: WebsiteService = Depends(WebsiteService),
):
    deleted_website = await service.delete(website_id, current_user)
    return  {
        "details": "Website deleted successfully"
    }

