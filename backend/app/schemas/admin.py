from __future__ import annotations

from datetime import date, datetime
from typing import Literal
from urllib.parse import urlparse
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    ValidationInfo,
    field_validator,
    model_validator,
)

from app.models.content import PublicationState


class AdminModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class AdminLoginRequest(AdminModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=512)


class AdminUserResponse(AdminModel):
    id: UUID
    email: EmailStr


class AdminSessionResponse(AdminModel):
    administrator: AdminUserResponse
    csrf_token: str


class AdminDashboardResponse(AdminModel):
    projects: dict[str, int]
    journal_articles: dict[str, int]
    messages: dict[str, int]


class AdminTaxonomyResponse(AdminModel):
    id: UUID
    slug: str
    title_en: str
    title_fa: str
    display_order: int


class AdminTaxonomyWriteRequest(AdminModel):
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=80)
    title_en: str = Field(min_length=1, max_length=160)
    title_fa: str = Field(min_length=1, max_length=160)


class AdminTaxonomyListResponse(AdminModel):
    items: list[AdminTaxonomyResponse]


class TaxonomyReorderRequest(AdminModel):
    identifiers: list[UUID] = Field(min_length=1, max_length=250)

    @field_validator("identifiers")
    @classmethod
    def identifiers_must_be_unique(cls, value: list[UUID]) -> list[UUID]:
        if len(value) != len(set(value)):
            raise ValueError("taxonomy identifiers must be unique")
        return value


class AdminBilingualContentResponse(AdminModel):
    id: UUID
    publication_state: PublicationState
    display_order: int
    title_en: str
    title_fa: str
    summary_en: str
    summary_fa: str
    updated_at: datetime


class AdminBilingualContentWriteRequest(AdminModel):
    publication_state: PublicationState = PublicationState.DRAFT
    title_en: str = Field(default="", max_length=180)
    title_fa: str = Field(default="", max_length=180)
    summary_en: str = Field(default="", max_length=12_000)
    summary_fa: str = Field(default="", max_length=12_000)


class AdminBilingualContentListResponse(AdminModel):
    items: list[AdminBilingualContentResponse]


class BilingualContentReorderRequest(AdminModel):
    identifiers: list[UUID] = Field(min_length=1, max_length=250)

    @field_validator("identifiers")
    @classmethod
    def identifiers_must_be_unique(cls, value: list[UUID]) -> list[UUID]:
        if len(value) != len(set(value)):
            raise ValueError("content identifiers must be unique")
        return value


class AdminStudioMemberResponse(AdminModel):
    id: UUID
    publication_state: PublicationState
    display_order: int
    name: str
    role_en: str
    role_fa: str
    biography_en: str | None
    biography_fa: str | None
    updated_at: datetime


class AdminStudioMemberWriteRequest(AdminModel):
    publication_state: PublicationState = PublicationState.DRAFT
    name: str = Field(default="", max_length=180)
    role_en: str = Field(default="", max_length=180)
    role_fa: str = Field(default="", max_length=180)
    biography_en: str | None = Field(default=None, max_length=12_000)
    biography_fa: str | None = Field(default=None, max_length=12_000)


class AdminStudioMemberListResponse(AdminModel):
    items: list[AdminStudioMemberResponse]


class AdminRecognitionResponse(AdminModel):
    id: UUID
    publication_state: PublicationState
    display_order: int
    title_en: str
    title_fa: str
    updated_at: datetime


class AdminRecognitionWriteRequest(AdminModel):
    publication_state: PublicationState = PublicationState.DRAFT
    title_en: str = Field(default="", max_length=240)
    title_fa: str = Field(default="", max_length=240)


class AdminRecognitionListResponse(AdminModel):
    items: list[AdminRecognitionResponse]


class StudioContentReorderRequest(AdminModel):
    identifiers: list[UUID] = Field(min_length=1, max_length=250)

    @field_validator("identifiers")
    @classmethod
    def identifiers_must_be_unique(cls, value: list[UUID]) -> list[UUID]:
        if len(value) != len(set(value)):
            raise ValueError("studio content identifiers must be unique")
        return value


class TextBlockPayload(AdminModel):
    heading: str | None = Field(default=None, max_length=240)
    body: str = Field(min_length=1, max_length=12_000)


class QuoteBlockPayload(AdminModel):
    quote: str = Field(min_length=1, max_length=4_000)
    attribution: str | None = Field(default=None, max_length=240)


class SingleImageBlockPayload(AdminModel):
    media_id: UUID


class PairedImageBlockPayload(AdminModel):
    left_media_id: UUID
    right_media_id: UUID

    @model_validator(mode="after")
    def image_ids_must_differ(self) -> PairedImageBlockPayload:
        if self.left_media_id == self.right_media_id:
            raise ValueError("paired-image blocks require two distinct media assets")
        return self


class GalleryBlockPayload(AdminModel):
    media_ids: list[UUID] = Field(min_length=1, max_length=24)

    @field_validator("media_ids")
    @classmethod
    def media_ids_must_be_unique(cls, value: list[UUID]) -> list[UUID]:
        if len(value) != len(set(value)):
            raise ValueError("gallery media assets must be unique")
        return value


ProjectBlockType = Literal[
    "text", "quote", "single_image", "full_width_image", "paired_image", "gallery"
]

_BLOCK_PAYLOADS: dict[str, type[AdminModel]] = {
    "text": TextBlockPayload,
    "quote": QuoteBlockPayload,
    "single_image": SingleImageBlockPayload,
    "full_width_image": SingleImageBlockPayload,
    "paired_image": PairedImageBlockPayload,
    "gallery": GalleryBlockPayload,
}


class ProjectBlockWriteRequest(AdminModel):
    block_type: ProjectBlockType
    content_en: dict[str, object]
    content_fa: dict[str, object]

    @field_validator("content_en", "content_fa")
    @classmethod
    def content_must_match_block_type(
        cls, value: dict[str, object], info: ValidationInfo
    ) -> dict[str, object]:
        block_type = info.data.get("block_type")
        if not isinstance(block_type, str):
            raise ValueError("block type is required before block content")
        return _BLOCK_PAYLOADS[block_type].model_validate(value).model_dump(mode="json")


class AdminProjectBlockResponse(AdminModel):
    id: UUID
    block_type: ProjectBlockType
    content_en: dict[str, object]
    content_fa: dict[str, object]
    display_order: int


class ProjectEditableFields(AdminModel):
    publication_state: PublicationState = PublicationState.DRAFT
    published_at: datetime | None = None
    featured: bool = False
    title_en: str = Field(min_length=1, max_length=240)
    title_fa: str = Field(min_length=1, max_length=240)
    subtitle_en: str | None = Field(default=None, max_length=320)
    subtitle_fa: str | None = Field(default=None, max_length=320)
    summary_en: str = Field(min_length=1, max_length=12_000)
    summary_fa: str = Field(min_length=1, max_length=12_000)
    location_en: str = Field(min_length=1, max_length=160)
    location_fa: str = Field(min_length=1, max_length=160)
    completion_year: int | None = Field(default=None, ge=1000, le=9999)
    status_en: str | None = Field(default=None, max_length=100)
    status_fa: str | None = Field(default=None, max_length=100)
    area_en: str | None = Field(default=None, max_length=100)
    area_fa: str | None = Field(default=None, max_length=100)
    scope_en: str | None = Field(default=None, max_length=240)
    scope_fa: str | None = Field(default=None, max_length=240)
    client_en: str | None = Field(default=None, max_length=240)
    client_fa: str | None = Field(default=None, max_length=240)
    architect_en: str | None = Field(default=None, max_length=240)
    architect_fa: str | None = Field(default=None, max_length=240)
    collaborators_en: str | None = Field(default=None, max_length=4_000)
    collaborators_fa: str | None = Field(default=None, max_length=4_000)
    completion_date: date | None = None
    seo_title_en: str | None = Field(default=None, max_length=240)
    seo_title_fa: str | None = Field(default=None, max_length=240)
    seo_description_en: str | None = Field(default=None, max_length=320)
    seo_description_fa: str | None = Field(default=None, max_length=320)
    intro_title_en: str | None = Field(default=None, max_length=240)
    intro_title_fa: str | None = Field(default=None, max_length=240)
    intro_en: str | None = Field(default=None, max_length=12_000)
    intro_fa: str | None = Field(default=None, max_length=12_000)
    narrative_title_en: str | None = Field(default=None, max_length=240)
    narrative_title_fa: str | None = Field(default=None, max_length=240)
    narrative_en: str | None = Field(default=None, max_length=12_000)
    narrative_fa: str | None = Field(default=None, max_length=12_000)
    quote_en: str | None = Field(default=None, max_length=4_000)
    quote_fa: str | None = Field(default=None, max_length=4_000)
    material_title_en: str | None = Field(default=None, max_length=240)
    material_title_fa: str | None = Field(default=None, max_length=240)
    material_en: str | None = Field(default=None, max_length=12_000)
    material_fa: str | None = Field(default=None, max_length=12_000)
    discipline_ids: list[UUID] = Field(default_factory=list, max_length=24)
    typology_ids: list[UUID] = Field(default_factory=list, max_length=24)

    @field_validator(
        "subtitle_en",
        "subtitle_fa",
        "status_en",
        "status_fa",
        "area_en",
        "area_fa",
        "scope_en",
        "scope_fa",
        "client_en",
        "client_fa",
        "architect_en",
        "architect_fa",
        "collaborators_en",
        "collaborators_fa",
        "seo_title_en",
        "seo_title_fa",
        "seo_description_en",
        "seo_description_fa",
        "intro_title_en",
        "intro_title_fa",
        "intro_en",
        "intro_fa",
        "narrative_title_en",
        "narrative_title_fa",
        "narrative_en",
        "narrative_fa",
        "quote_en",
        "quote_fa",
        "material_title_en",
        "material_title_fa",
        "material_en",
        "material_fa",
    )
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @field_validator("discipline_ids", "typology_ids")
    @classmethod
    def taxonomy_ids_must_be_unique(cls, value: list[UUID]) -> list[UUID]:
        if len(value) != len(set(value)):
            raise ValueError("taxonomy identifiers must be unique")
        return value

    @model_validator(mode="after")
    def bilingual_sections_must_be_complete(self) -> ProjectEditableFields:
        fields = (
            ("subtitle_en", "subtitle_fa"),
            ("status_en", "status_fa"),
            ("area_en", "area_fa"),
            ("scope_en", "scope_fa"),
            ("client_en", "client_fa"),
            ("architect_en", "architect_fa"),
            ("collaborators_en", "collaborators_fa"),
            ("intro_title_en", "intro_title_fa"),
            ("intro_en", "intro_fa"),
            ("narrative_title_en", "narrative_title_fa"),
            ("narrative_en", "narrative_fa"),
            ("quote_en", "quote_fa"),
            ("material_title_en", "material_title_fa"),
            ("material_en", "material_fa"),
        )
        for english, persian in fields:
            if bool(getattr(self, english)) != bool(getattr(self, persian)):
                raise ValueError(f"{english} and {persian} must be provided together")
        return self


class ProjectCreateRequest(ProjectEditableFields):
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=120)


class ProjectUpdateRequest(ProjectEditableFields):
    """The immutable slug is intentionally absent from an update request."""


class ProjectBlocksReplaceRequest(AdminModel):
    blocks: list[ProjectBlockWriteRequest] = Field(default_factory=list, max_length=80)


class ProjectReorderRequest(AdminModel):
    project_ids: list[UUID] = Field(min_length=1, max_length=500)

    @field_validator("project_ids")
    @classmethod
    def project_ids_must_be_unique(cls, value: list[UUID]) -> list[UUID]:
        if len(value) != len(set(value)):
            raise ValueError("project identifiers must be unique")
        return value


class AdminProjectListItemResponse(AdminModel):
    id: UUID
    slug: str
    title_en: str
    title_fa: str
    publication_state: PublicationState
    published_at: datetime | None
    display_order: int
    featured: bool
    updated_at: datetime


class AdminProjectListResponse(AdminModel):
    items: list[AdminProjectListItemResponse]


class AdminProjectFormOptionsResponse(AdminModel):
    disciplines: list[AdminTaxonomyResponse]
    typologies: list[AdminTaxonomyResponse]


class AdminProjectResponse(AdminProjectListItemResponse):
    subtitle_en: str | None
    subtitle_fa: str | None
    summary_en: str
    summary_fa: str
    location_en: str
    location_fa: str
    completion_year: int | None
    status_en: str | None
    status_fa: str | None
    area_en: str | None
    area_fa: str | None
    scope_en: str | None
    scope_fa: str | None
    client_en: str | None
    client_fa: str | None
    architect_en: str | None
    architect_fa: str | None
    collaborators_en: str | None
    collaborators_fa: str | None
    completion_date: date | None
    seo_title_en: str | None
    seo_title_fa: str | None
    seo_description_en: str | None
    seo_description_fa: str | None
    intro_title_en: str | None
    intro_title_fa: str | None
    intro_en: str | None
    intro_fa: str | None
    narrative_title_en: str | None
    narrative_title_fa: str | None
    narrative_en: str | None
    narrative_fa: str | None
    quote_en: str | None
    quote_fa: str | None
    material_title_en: str | None
    material_title_fa: str | None
    material_en: str | None
    material_fa: str | None
    disciplines: list[AdminTaxonomyResponse]
    typologies: list[AdminTaxonomyResponse]
    blocks: list[AdminProjectBlockResponse]


class AdminJournalCategoryResponse(AdminModel):
    id: UUID
    slug: str
    title_en: str
    title_fa: str
    display_order: int


class AdminJournalCategoryWriteRequest(AdminModel):
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=80)
    title_en: str = Field(min_length=1, max_length=160)
    title_fa: str = Field(min_length=1, max_length=160)


class AdminJournalCategoryListResponse(AdminModel):
    items: list[AdminJournalCategoryResponse]


class JournalCategoryReorderRequest(AdminModel):
    identifiers: list[UUID] = Field(min_length=1, max_length=250)

    @field_validator("identifiers")
    @classmethod
    def identifiers_must_be_unique(cls, value: list[UUID]) -> list[UUID]:
        if len(value) != len(set(value)):
            raise ValueError("journal category identifiers must be unique")
        return value


JournalArticleBlockType = Literal["text", "quote"]


class JournalArticleBlockWriteRequest(AdminModel):
    block_type: JournalArticleBlockType
    content_en: dict[str, object]
    content_fa: dict[str, object]

    @field_validator("content_en", "content_fa")
    @classmethod
    def content_must_match_block_type(
        cls, value: dict[str, object], info: ValidationInfo
    ) -> dict[str, object]:
        block_type = info.data.get("block_type")
        if not isinstance(block_type, str):
            raise ValueError("block type is required before block content")
        return _BLOCK_PAYLOADS[block_type].model_validate(value).model_dump(mode="json")


class AdminJournalArticleBlockResponse(AdminModel):
    id: UUID
    block_type: JournalArticleBlockType
    content_en: dict[str, object]
    content_fa: dict[str, object]
    display_order: int


class JournalArticleEditableFields(AdminModel):
    publication_state: PublicationState = PublicationState.DRAFT
    published_at: datetime | None = None
    category_id: UUID
    title_en: str = Field(default="", max_length=240)
    title_fa: str = Field(default="", max_length=240)
    excerpt_en: str = Field(default="", max_length=12_000)
    excerpt_fa: str = Field(default="", max_length=12_000)
    reading_minutes: int = Field(default=1, ge=1, le=1_440)
    cover_image_url: str | None = Field(default=None, max_length=500)
    cover_alt_en: str | None = Field(default=None, max_length=500)
    cover_alt_fa: str | None = Field(default=None, max_length=500)
    seo_title_en: str | None = Field(default=None, max_length=240)
    seo_title_fa: str | None = Field(default=None, max_length=240)
    seo_description_en: str | None = Field(default=None, max_length=320)
    seo_description_fa: str | None = Field(default=None, max_length=320)
    blocks: list[JournalArticleBlockWriteRequest] = Field(default_factory=list, max_length=80)

    @field_validator(
        "cover_image_url",
        "cover_alt_en",
        "cover_alt_fa",
        "seo_title_en",
        "seo_title_fa",
        "seo_description_en",
        "seo_description_fa",
    )
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @model_validator(mode="after")
    def bilingual_optional_fields_must_be_complete(self) -> JournalArticleEditableFields:
        fields = (
            ("cover_alt_en", "cover_alt_fa"),
            ("seo_title_en", "seo_title_fa"),
            ("seo_description_en", "seo_description_fa"),
        )
        for english, persian in fields:
            if bool(getattr(self, english)) != bool(getattr(self, persian)):
                raise ValueError(f"{english} and {persian} must be provided together")
        return self


class JournalArticleCreateRequest(JournalArticleEditableFields):
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=120)


class JournalArticleUpdateRequest(JournalArticleEditableFields):
    """The immutable public slug is intentionally absent from updates."""


class AdminJournalArticleListItemResponse(AdminModel):
    id: UUID
    slug: str
    publication_state: PublicationState
    published_at: datetime | None
    category: AdminJournalCategoryResponse
    title_en: str
    title_fa: str
    updated_at: datetime


class AdminJournalArticleListResponse(AdminModel):
    items: list[AdminJournalArticleListItemResponse]


class AdminJournalArticleResponse(AdminJournalArticleListItemResponse):
    excerpt_en: str
    excerpt_fa: str
    reading_minutes: int
    cover_image_url: str | None
    cover_alt_en: str | None
    cover_alt_fa: str | None
    seo_title_en: str | None
    seo_title_fa: str | None
    seo_description_en: str | None
    seo_description_fa: str | None
    blocks: list[AdminJournalArticleBlockResponse]


ThemeMode = Literal["system", "light", "dark"]


class SiteSettingsSocialLink(AdminModel):
    label: str = Field(min_length=1, max_length=80)
    url: str = Field(min_length=1, max_length=500)

    @field_validator("label")
    @classmethod
    def normalize_label(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("social link label is required")
        return normalized

    @field_validator("url")
    @classmethod
    def require_https_url(cls, value: str) -> str:
        normalized = value.strip()
        parsed = urlparse(normalized)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError("social link URL must use HTTPS")
        return normalized


class SiteSettingsPrinciple(AdminModel):
    title_en: str = Field(min_length=1, max_length=160)
    title_fa: str = Field(min_length=1, max_length=160)
    body_en: str = Field(min_length=1, max_length=2_000)
    body_fa: str = Field(min_length=1, max_length=2_000)

    @field_validator("title_en", "title_fa", "body_en", "body_fa")
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("site principle text is required")
        return normalized


class SiteSettingsWriteRequest(AdminModel):
    studio_name: str = Field(min_length=1, max_length=120)
    logo_url: str | None = Field(default=None, max_length=500)
    favicon_url: str | None = Field(default=None, max_length=500)
    contact_email: EmailStr | None = None
    contact_phone: str | None = Field(default=None, max_length=64)
    contact_address_en: str | None = Field(default=None, max_length=1_000)
    contact_address_fa: str | None = Field(default=None, max_length=1_000)
    social_links: list[SiteSettingsSocialLink] = Field(default_factory=list, max_length=10)
    default_theme: ThemeMode = "system"
    default_seo_title_en: str | None = Field(default=None, max_length=240)
    default_seo_title_fa: str | None = Field(default=None, max_length=240)
    default_seo_description_en: str | None = Field(default=None, max_length=320)
    default_seo_description_fa: str | None = Field(default=None, max_length=320)
    home_title_en: str = Field(min_length=1, max_length=4_000)
    home_title_fa: str = Field(min_length=1, max_length=4_000)
    home_body_en: str = Field(min_length=1, max_length=12_000)
    home_body_fa: str = Field(min_length=1, max_length=12_000)
    home_hero_image_url: str | None = Field(default=None, max_length=500)
    home_hero_alt_en: str | None = Field(default=None, max_length=500)
    home_hero_alt_fa: str | None = Field(default=None, max_length=500)
    studio_intro_en: str = Field(min_length=1, max_length=12_000)
    studio_intro_fa: str = Field(min_length=1, max_length=12_000)
    studio_principles: list[SiteSettingsPrinciple] = Field(default_factory=list, max_length=12)
    privacy_en: str = Field(min_length=1, max_length=12_000)
    privacy_fa: str = Field(min_length=1, max_length=12_000)

    @field_validator(
        "studio_name",
        "home_title_en",
        "home_title_fa",
        "home_body_en",
        "home_body_fa",
        "studio_intro_en",
        "studio_intro_fa",
        "privacy_en",
        "privacy_fa",
    )
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("site settings text is required")
        return normalized

    @field_validator(
        "contact_phone",
        "contact_address_en",
        "contact_address_fa",
        "default_seo_title_en",
        "default_seo_title_fa",
        "default_seo_description_en",
        "default_seo_description_fa",
        "home_hero_alt_en",
        "home_hero_alt_fa",
    )
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @field_validator("logo_url", "favicon_url", "home_hero_image_url")
    @classmethod
    def require_public_media_path(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            return None
        if not normalized.startswith("/media/") or ".." in normalized:
            raise ValueError("public media must use an approved /media/ path")
        return normalized

    @model_validator(mode="after")
    def related_localized_settings_must_be_complete(self) -> SiteSettingsWriteRequest:
        paired_fields = (
            ("contact_address_en", "contact_address_fa"),
            ("default_seo_title_en", "default_seo_title_fa"),
            ("default_seo_description_en", "default_seo_description_fa"),
            ("home_hero_alt_en", "home_hero_alt_fa"),
        )
        for english, persian in paired_fields:
            if bool(getattr(self, english)) != bool(getattr(self, persian)):
                raise ValueError(f"{english} and {persian} must be provided together")
        if self.home_hero_image_url is None and any((self.home_hero_alt_en, self.home_hero_alt_fa)):
            raise ValueError("hero alt text requires a hero image")
        if self.home_hero_image_url is not None and not all(
            (self.home_hero_alt_en, self.home_hero_alt_fa)
        ):
            raise ValueError("hero image requires localized alt text")
        return self


class AdminSiteSettingsResponse(SiteSettingsWriteRequest):
    id: UUID | None
    updated_at: datetime | None
