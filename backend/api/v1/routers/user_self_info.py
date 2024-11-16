from fastapi import APIRouter, Depends, Form, UploadFile, File

from core.enum.enum_json import PROJECT_ENUM
from auth import AuthRepo
from core.utils import request_user, get_all_status, phone_number_validation_check
from user_info.schema.user_information import PersonalUserInfoEdit, PersonalUserInfoView
from user_info.service.user_information import UserInformationService

user_router = r = APIRouter()


class UserRouter:
    def __init__(self):
        self.router = APIRouter()

        self.router.get(
            "/self_profile",
            response_model=PersonalUserInfoView,
        )(self.get_self_profile)

        self.router.patch(
            "/update_profile",
            response_model=str,
        )(self.update_self_profile)

        self.router.patch(
            "/upload_profile_picture",
            response_model=dict,
        )(self.upload_api)

    async def get_self_profile(self, current_user=Depends(request_user)):
        user_data = current_user.__dict__
        user_info = UserInformationService()
        user_info_data = await user_info.get_user_info(current_user.id)
        if user_info_data:
            user_info_response = user_info_data.__dict__
            if user_info_data.date_of_birth:
                user_info_response['date_of_birth'] = user_info_data.date_of_birth.strftime("%B %d, %Y")
            user_data.update(user_info_response)
        user_data['full_name'] = current_user.full_name
        return PersonalUserInfoView(**user_data)

    async def update_self_profile(
            self,
            self_profile_data: PersonalUserInfoEdit,
            current_user=Depends(request_user)
    ):
        user_repo = AuthRepo()
        await phone_number_validation_check(self_profile_data)
        async with user_repo:
            await user_repo.update(
                current_user,
                {
                    "first_name": self_profile_data.first_name,
                    "last_name": self_profile_data.last_name,
                    "phone": self_profile_data.phone
                }
            )
        user_info_service = UserInformationService()
        await user_info_service.update_user_info(
            current_user.id,
            {
                "company_website": self_profile_data.company_website,
                "address": self_profile_data.address,
                "updated_by_id": current_user.id,
                "contact_information": self_profile_data.contact_information,
                "personal_information": self_profile_data.contact_information,
                "date_of_birth": self_profile_data.date_of_birth,
                "gender": self_profile_data.gender,
            }
        )
        return "Successfully updated self profile."

    async def upload_api(
            self,
            file: UploadFile = File(...),
            current_user=Depends(request_user),
            service: UserInformationService = Depends(UserInformationService)
    ):
        uploaded_file = await service.profile_picture_upload(current_user, file)
        return uploaded_file


user_info_router = UserRouter().router
