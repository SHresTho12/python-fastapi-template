from dataclasses import dataclass

from core.enum.enum_json import PROJECT_ENUM


@dataclass
class ProjectType:
    id: int
    name: str
    title: str
    about: str

@dataclass
class TurnAroundTime:
    id: int
    title: str
    time: int
    scale: str
    credits: int

@dataclass
class AssetType:
    id: int
    name: str

@dataclass
class AgentBrandingTo:
    id: int
    name: str

@dataclass
class AgentLogoAnimationTo:
    id: int
    name: str

@dataclass
class ProjectPackageTypePhoto:
    id: int
    name: str
    credits: int

@dataclass
class ProjectPackageTypeVideo:
    id: int
    name: str
    credits: int

@dataclass
class VideoSequence:
    id: int
    name: str
    description: str

@dataclass
class ProjectStatus:
    id: int
    name: str

@dataclass
class FileType:
    id: int
    name: str

@dataclass
class MediaType:
    id: int
    name: str

# Create dictionaries with enum-like objects
project_type_enum = {entry["code"]: ProjectType(**entry) for entry in PROJECT_ENUM["project_type"]}
turn_around_time_enum = {entry["code"]: TurnAroundTime(**entry) for entry in PROJECT_ENUM["turn_around_time"]}
asset_type_enum = {entry["code"]: AssetType(**entry) for entry in PROJECT_ENUM["asset_type"]}
agent_branding_to_enum = {entry["code"]: AgentBrandingTo(**entry) for entry in PROJECT_ENUM["agent_branding_to"]}
agent_logo_animation_to_enum = {entry["code"]: AgentLogoAnimationTo(**entry) for entry in PROJECT_ENUM["agent_logo_animation_to"]}
project_package_type_photo_enum = {entry["code"]: ProjectPackageTypePhoto(**entry) for entry in PROJECT_ENUM["project_package_type_photo"]}
project_package_type_video_enum = {entry["code"]: ProjectPackageTypeVideo(**entry) for entry in PROJECT_ENUM["project_package_type_video"]}
video_sequence_enum = {entry["code"]: VideoSequence(**entry) for entry in PROJECT_ENUM["video_sequence"]}
project_status_enum = {entry["code"]: ProjectStatus(**entry) for entry in PROJECT_ENUM["project_status"]}
file_type_enum = {entry["code"]: FileType(**entry) for entry in PROJECT_ENUM["file_type"]}
media_type_enum = {entry["code"]: MediaType(**entry) for entry in PROJECT_ENUM["media_type"]}




