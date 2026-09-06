from __future__ import annotations

from typing import cast

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.admin import AdminUser
from app.models.content import SiteSettings
from app.schemas.admin import (
    AdminSiteSettingsResponse,
    SiteSettingsPrinciple,
    SiteSettingsSocialLink,
    SiteSettingsWriteRequest,
    ThemeMode,
)
from app.services.admin_auth import record_audit_event
from app.services.public_cache import TaggedPublicCache


class SiteSettingsConflictError(RuntimeError):
    """Raised when concurrent bootstraps violate the single-settings-row invariant."""


def _default_response() -> AdminSiteSettingsResponse:
    return AdminSiteSettingsResponse(
        id=None,
        updated_at=None,
        studio_name="VOLUMA",
        logo_url=None,
        favicon_url=None,
        contact_email=None,
        contact_phone=None,
        contact_address_en=None,
        contact_address_fa=None,
        social_links=[],
        default_theme="system",
        default_seo_title_en=None,
        default_seo_title_fa=None,
        default_seo_description_en=None,
        default_seo_description_fa=None,
        home_title_en="Architecture for the life between walls.",
        home_title_fa="معماری برای زندگی میان دیوارها.",
        home_body_en="Configure this site before publishing production content.",
        home_body_fa="پیش از انتشار محتوای تولید، این سایت را پیکربندی کنید.",
        home_hero_image_url=None,
        home_hero_alt_en=None,
        home_hero_alt_fa=None,
        studio_intro_en="Configure the bilingual studio introduction before publication.",
        studio_intro_fa="پیش از انتشار، معرفی دوزبانهٔ استودیو را پیکربندی کنید.",
        studio_principles=[],
        privacy_en=(
            "Operational placeholder: replace this text with owner-approved privacy wording."
        ),
        privacy_fa=(
            "متن عملیاتی موقت: این متن باید با متن حریم خصوصی تأییدشده توسط مالک جایگزین شود."
        ),
    )


class SiteSettingsAdministrationService:
    """Single-record settings workflow with an explicit public-cache boundary."""

    def __init__(self, session: Session, cache: TaggedPublicCache) -> None:
        self.session = session
        self.cache = cache

    def get(self) -> AdminSiteSettingsResponse:
        record = self.session.scalar(
            select(SiteSettings).order_by(SiteSettings.created_at).limit(1)
        )
        return _settings_response(record) if record is not None else _default_response()

    def update(
        self, payload: SiteSettingsWriteRequest, administrator: AdminUser
    ) -> AdminSiteSettingsResponse:
        record = self.session.scalar(
            select(SiteSettings).order_by(SiteSettings.created_at).limit(1).with_for_update()
        )
        if record is None:
            record = SiteSettings(singleton=True)
            self.session.add(record)
        self._apply(record, payload)
        self.session.flush()
        record_audit_event(
            self.session,
            actor_id=administrator.id,
            action="site_settings.updated",
            target_type="site_settings",
            target_id=record.id,
        )
        try:
            self.session.commit()
        except IntegrityError as error:
            self.session.rollback()
            raise SiteSettingsConflictError() from error
        self.session.refresh(record)
        self.cache.invalidate(
            {
                "site",
                "site:en",
                "site:fa",
                "home",
                "home:en",
                "home:fa",
                "studio",
                "studio:en",
                "studio:fa",
            }
        )
        return _settings_response(record)

    @staticmethod
    def _apply(record: SiteSettings, payload: SiteSettingsWriteRequest) -> None:
        record.singleton = True
        record.studio_name = payload.studio_name
        record.logo_url = payload.logo_url
        record.favicon_url = payload.favicon_url
        record.contact_email = (
            str(payload.contact_email) if payload.contact_email is not None else None
        )
        record.contact_phone = payload.contact_phone
        record.contact_address_en = payload.contact_address_en
        record.contact_address_fa = payload.contact_address_fa
        record.social_links = [link.model_dump() for link in payload.social_links]
        record.default_theme = payload.default_theme
        record.default_seo_title_en = payload.default_seo_title_en
        record.default_seo_title_fa = payload.default_seo_title_fa
        record.default_seo_description_en = payload.default_seo_description_en
        record.default_seo_description_fa = payload.default_seo_description_fa
        record.home_title_en = payload.home_title_en
        record.home_title_fa = payload.home_title_fa
        record.home_body_en = payload.home_body_en
        record.home_body_fa = payload.home_body_fa
        record.home_hero_image_url = payload.home_hero_image_url
        record.home_hero_alt_en = payload.home_hero_alt_en
        record.home_hero_alt_fa = payload.home_hero_alt_fa
        record.studio_intro_en = payload.studio_intro_en
        record.studio_intro_fa = payload.studio_intro_fa
        record.studio_principles_en = [
            {"title": principle.title_en, "body": principle.body_en}
            for principle in payload.studio_principles
        ]
        record.studio_principles_fa = [
            {"title": principle.title_fa, "body": principle.body_fa}
            for principle in payload.studio_principles
        ]
        record.privacy_en = payload.privacy_en
        record.privacy_fa = payload.privacy_fa


def _settings_response(record: SiteSettings) -> AdminSiteSettingsResponse:
    english_principles = record.studio_principles_en
    persian_principles = record.studio_principles_fa
    principles = [
        SiteSettingsPrinciple(
            title_en=english["title"],
            title_fa=persian["title"],
            body_en=english["body"],
            body_fa=persian["body"],
        )
        for english, persian in zip(english_principles, persian_principles, strict=True)
    ]
    return AdminSiteSettingsResponse(
        id=record.id,
        updated_at=record.updated_at,
        studio_name=record.studio_name,
        logo_url=record.logo_url,
        favicon_url=record.favicon_url,
        contact_email=record.contact_email,
        contact_phone=record.contact_phone,
        contact_address_en=record.contact_address_en,
        contact_address_fa=record.contact_address_fa,
        social_links=[SiteSettingsSocialLink.model_validate(link) for link in record.social_links],
        default_theme=cast(ThemeMode, record.default_theme),
        default_seo_title_en=record.default_seo_title_en,
        default_seo_title_fa=record.default_seo_title_fa,
        default_seo_description_en=record.default_seo_description_en,
        default_seo_description_fa=record.default_seo_description_fa,
        home_title_en=record.home_title_en,
        home_title_fa=record.home_title_fa,
        home_body_en=record.home_body_en,
        home_body_fa=record.home_body_fa,
        home_hero_image_url=record.home_hero_image_url,
        home_hero_alt_en=record.home_hero_alt_en,
        home_hero_alt_fa=record.home_hero_alt_fa,
        studio_intro_en=record.studio_intro_en,
        studio_intro_fa=record.studio_intro_fa,
        studio_principles=principles,
        privacy_en=record.privacy_en,
        privacy_fa=record.privacy_fa,
    )
