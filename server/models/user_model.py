from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

class AgentResponse(BaseModel):
    user_id: str
    user_name: str
    agent_name: str
    agent_email: str
    last_chat_time: datetime
    role: str

class AgentListResponse(BaseModel):
    total_agents: int
    agents: List[AgentResponse]

class ConversationResponse(BaseModel):
    user_id : str
    conversation_id : str
    conversation_title : str

class Agent(BaseModel):
    user_name: str
    email: str
    full_name: str
    role: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UpdateAdminRoleRequest(BaseModel):
    user_id: str
    role: str

class AdminResponse(BaseModel):
    user_id: str
    user_name: str
    email: str
    role: str
    created_at: datetime
    updated_at: datetime

class AdminListResponse(AdminResponse):
    total_admins: int
    admins: List[AdminResponse]