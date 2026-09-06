from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Locale = Literal["en", "fa"]


class PublicModel(BaseModel):
    """A response model that rejects accidental ORM/admin fields."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class ImageResponse(PublicModel):
    url: str
    alt: str


class TaxonomyResponse(PublicModel):
    slug: str
    title: str


class ProjectCardResponse(PublicModel):
    slug: str
    title: str
    subtitle: str | None = None
    summary: str
    location: str
    completion_year: int | None = None
    status: str | None = None
    cover_image: ImageResponse | None = None
    disciplines: list[TaxonomyResponse]
    typologies: list[TaxonomyResponse]


class EditorialSectionResponse(PublicModel):
    title: str
    body: str


class TextEditorialBlockResponse(PublicModel):
    block_type: Literal["text"]
    heading: str | None = None
    body: str


class QuoteEditorialBlockResponse(PublicModel):
    block_type: Literal["quote"]
    quote: str
    attribution: str | None = None


ProjectEditorialBlockResponse = TextEditorialBlockResponse | QuoteEditorialBlockResponse


class ProjectDetailResponse(ProjectCardResponse):
    area: str | None = None
    scope: str | None = None
    introduction: EditorialSectionResponse | None = None
    narrative: EditorialSectionResponse | None = None
    quote: str | None = None
    material: EditorialSectionResponse | None = None
    gallery: list[ImageResponse]
    blocks: list[ProjectEditorialBlockResponse]
    seo_title: str
    seo_description: str


class PaginationResponse(PublicModel):
    limit: int
    offset: int
    total: int


class ProjectListResponse(PublicModel):
    items: list[ProjectCardResponse]
    pagination: PaginationResponse


class ExpertiseResponse(PublicModel):
    title: str
    summary: str
    display_order: int


class ProcessStepResponse(PublicModel):
    title: str
    summary: str
    display_order: int


class SiteResponse(PublicModel):
    studio_name: str
    privacy: str


class StudioPrincipleResponse(PublicModel):
    title: str
    body: str


class StudioMemberResponse(PublicModel):
    name: str
    role: str
    biography: str | None = None


class StudioResponse(PublicModel):
    intro: str
    principles: list[StudioPrincipleResponse]
    members: list[StudioMemberResponse]
    recognitions: list[str]


class JournalCategoryResponse(PublicModel):
    slug: str
    title: str


class JournalCardResponse(PublicModel):
    slug: str
    title: str
    excerpt: str
    category: JournalCategoryResponse
    published_at: datetime
    reading_minutes: int = Field(ge=1)
    cover_image: ImageResponse | None = None


class HomeResponse(PublicModel):
    studio_name: str
    hero_title: str
    hero_body: str
    hero_image: ImageResponse | None = None
    selected_projects: list[ProjectCardResponse]
    expertise: list[ExpertiseResponse]
    process: list[ProcessStepResponse]
    journal: list[JournalCardResponse]


class JournalArticleResponse(JournalCardResponse):
    body: list[str]
    blocks: list[ProjectEditorialBlockResponse]
    seo_title: str
    seo_description: str


class JournalListResponse(PublicModel):
    items: list[JournalCardResponse]
    pagination: PaginationResponse


class SearchResultResponse(PublicModel):
    kind: Literal["project", "journal"]
    slug: str
    title: str
    summary: str


class SearchResponse(PublicModel):
    query: str
    items: list[SearchResultResponse]
