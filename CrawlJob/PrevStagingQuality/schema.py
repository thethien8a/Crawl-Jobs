from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

class PrevStagingQualitySchema(BaseModel):
    job_title: str
    company_name: str
    location: str
    job_description: str
    source_site: str
    job_url: str
    
    salary: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    job_deadline: Optional[str] = None
    search_keyword: Optional[str] = None
    job_type: Optional[str] = None
    job_industry: Optional[str] = None
    experience_level: Optional[str] = None
    education_level: Optional[str] = None
    job_position: Optional[str] = None
    scraped_at: Optional[datetime] = None

    @field_validator('job_title', 'company_name', 'location', 'job_description', 'source_site')
    @classmethod
    def must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError(f'Không được để {v} trống hoặc chỉ chứa khoảng trắng')
        return v.strip()
    
    @field_validator('company_name', 'salary', 'location', 'job_type', 'job_industry', 'experience_level', 'education_level', 'job_position')
    @classmethod
    def limit_string_length(cls, v: str) -> str:
        max_length = 500
        if len(v) > max_length:
            return v[:max_length]
        return v.strip()
