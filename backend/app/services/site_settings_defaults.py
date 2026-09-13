from __future__ import annotations

from typing import Any

from app.models.content import SiteSettings


def default_site_settings_values() -> dict[str, Any]:
    """Return the owner-editable settings used for a new VOLUMA installation."""

    return {
        "studio_name": "VOLUMA",
        "logo_media_id": None,
        "favicon_media_id": None,
        "contact_email": None,
        "contact_phone": None,
        "contact_address_en": None,
        "contact_address_fa": None,
        "social_links": [],
        "default_theme": "system",
        "default_seo_title_en": None,
        "default_seo_title_fa": None,
        "default_seo_description_en": None,
        "default_seo_description_fa": None,
        "home_title_en": "Architecture for the life between walls.",
        "home_title_fa": "معماری برای زندگی میان دیوارها.",
        "home_body_en": "Configure this site before publishing production content.",
        "home_body_fa": "پیش از انتشار محتوای تولید، این سایت را پیکربندی کنید.",
        "home_hero_media_id": None,
        "home_selected_projects_heading_en": "Selected projects",
        "home_selected_projects_heading_fa": "پروژه‌های منتخب",
        "home_studio_heading_en": "We design for atmosphere, use, and time.",
        "home_studio_heading_fa": "برای کیفیت فضا، شیوه‌ی استفاده و گذر زمان طراحی می‌کنیم.",
        "home_studio_body_en": "Configure the studio introduction shown on the home page.",
        "home_studio_body_fa": "معرفی استودیو که در صفحهٔ اصلی نمایش داده می‌شود را پیکربندی کنید.",
        "home_studio_media_id": None,
        "home_expertise_heading_en": "What we shape",
        "home_expertise_heading_fa": "آنچه شکل می‌دهیم",
        "home_expertise_media_id": None,
        "home_process_heading_en": "A clear path from first question to built form.",
        "home_process_heading_fa": "مسیری روشن از نخستین پرسش تا فضای ساخته‌شده.",
        "home_journal_heading_en": "Latest from the journal",
        "home_journal_heading_fa": "تازه‌ترین یادداشت‌ها",
        "home_contact_heading_en": "Begin with a place, a question, or a possibility.",
        "home_contact_heading_fa": "با یک مکان، یک پرسش یا یک امکان آغاز کنیم.",
        "studio_intro_en": "Configure the bilingual studio introduction before publication.",
        "studio_intro_fa": "پیش از انتشار، معرفی دوزبانهٔ استودیو را پیکربندی کنید.",
        "studio_principles_en": [],
        "studio_principles_fa": [],
        "privacy_en": (
            "Operational placeholder: replace this text with owner-approved privacy wording."
        ),
        "privacy_fa": (
            "متن عملیاتی موقت: این متن باید با متن حریم خصوصی تأییدشده توسط مالک جایگزین شود."
        ),
    }


def create_default_site_settings() -> SiteSettings:
    """Create the singleton record required by public routes on a fresh deployment."""

    return SiteSettings(**default_site_settings_values())
