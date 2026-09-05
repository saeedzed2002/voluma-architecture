from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.content import (
    Discipline,
    Expertise,
    JournalArticle,
    JournalCategory,
    ProcessStep,
    Project,
    PublicationState,
    SiteSettings,
    Typology,
)


def seed_development_content(session: Session) -> bool:
    """Seed representative content once for a local development database only.

    The records intentionally retain the development-fixture disclaimer from the
    approved static frontend. This function is never called by application startup.
    """

    if session.scalar(select(SiteSettings.id).limit(1)) is not None:
        return False

    now = datetime.now(UTC)
    settings = SiteSettings(
        studio_name="VOLUMA",
        home_title_en="Architecture for the life between walls.",
        home_title_fa="معماری برای زندگی میان دیوارها.",
        home_body_en="We shape quiet, enduring places through light, material, and use.",
        home_body_fa="فضاهایی آرام و ماندگار را با نور، مصالح و شیوه‌ی زیستن شکل می‌دهیم.",
        home_hero_image_url="/media/voluma-mountain-house.png",
        home_hero_alt_en="Concrete and timber house overlooking mountains and a lake",
        home_hero_alt_fa="خانه‌ی بتنی و چوبی رو به کوهستان و دریاچه",
        studio_intro_en=(
            "VOLUMA is presented as a development fixture. Published studio people, collaborators, "
            "recognition, and contact details require owner approval."
        ),
        studio_intro_fa=(
            "ولوما به‌عنوان دادهٔ نمونهٔ توسعه ارائه می‌شود. اطلاعات افراد، همکاران، تقدیرها و "
            "تماسِ منتشرشده به تأیید مالک نیاز دارد."
        ),
        studio_principles_en=[
            {
                "title": "Place before image",
                "body": "Every proposal begins with the site's conditions.",
            },
            {
                "title": "Use gives form",
                "body": "Plans are tested against ordinary movement and change.",
            },
            {
                "title": "Detail carries the whole",
                "body": "Material decisions make spatial ideas tangible.",
            },
        ],
        studio_principles_fa=[
            {"title": "مکان پیش از تصویر", "body": "هر پیشنهاد از شرایط واقعی سایت آغاز می‌شود."},
            {
                "title": "کاربری فرم می‌دهد",
                "body": "پلان با حرکت روزمره و تغییر در زمان آزموده می‌شود.",
            },
            {
                "title": "جزئیات، کل را حمل می‌کند",
                "body": "تصمیم‌های مادی، ایدهٔ فضایی را ملموس می‌کنند.",
            },
        ],
        privacy_en=(
            "Development fixture only. Owner-approved privacy wording is required "
            "before contact data collection is enabled."
        ),
        privacy_fa=(
            "فقط دادهٔ نمونهٔ توسعه است. پیش از فعال‌شدن دریافت دادهٔ تماس، متن حریم خصوصی باید "
            "به تأیید مالک برسد."
        ),
    )
    disciplines = {
        "architecture": Discipline(
            slug="architecture", title_en="Architecture", title_fa="معماری", display_order=1
        ),
        "interior": Discipline(
            slug="interior",
            title_en="Interior architecture",
            title_fa="معماری داخلی",
            display_order=2,
        ),
        "adaptive-reuse": Discipline(
            slug="adaptive-reuse",
            title_en="Adaptive reuse",
            title_fa="باززنده‌سازی",
            display_order=3,
        ),
        "spatial-strategy": Discipline(
            slug="spatial-strategy",
            title_en="Spatial strategy",
            title_fa="راهبرد فضایی",
            display_order=4,
        ),
    }
    typologies = {
        "residential": Typology(
            slug="residential", title_en="Residential", title_fa="مسکونی", display_order=1
        ),
        "workspace": Typology(
            slug="workspace", title_en="Workspace", title_fa="فضای کار", display_order=2
        ),
        "cultural": Typology(
            slug="cultural", title_en="Cultural", title_fa="فرهنگی", display_order=3
        ),
        "adaptive-reuse": Typology(
            slug="adaptive-reuse",
            title_en="Adaptive reuse",
            title_fa="باززنده‌سازی",
            display_order=4,
        ),
    }
    session.add(settings)
    session.add_all([*disciplines.values(), *typologies.values()])
    session.flush()

    project_data: list[tuple[Any, ...]] = [
        (
            "courtyard-house",
            "Courtyard House",
            "خانه‌ی حیاط مرکزی",
            "A home organized around shade, filtered light, and a protected inner garden.",
            "خانه‌ای شکل‌گرفته پیرامون سایه، نور فیلترشده و باغی محفوظ در مرکز.",
            "Tehran",
            "تهران",
            2026,
            "Completed",
            "تکمیل‌شده",
            "420 m²",
            "۴۲۰ مترمربع",
            "Architecture · Interior",
            "معماری · معماری داخلی",
            "/media/courtyard-house.png",
            "Concrete courtyard house arranged around a mature shade tree",
            "خانه‌ای بتنی پیرامون یک درخت سایه‌انداز بالغ",
            "A calm center for daily life.",
            "مرکزی آرام برای زندگی روزمره.",
            "The house turns inward to make privacy, daylight, and seasonal change "
            "part of one domestic landscape.",
            "خانه به درون بازمی‌گردد تا خلوت، نور روز و تغییر فصل‌ها را در یک منظر خانگی جمع کند.",
            "Light, shade, and a room outside.",
            "نور، سایه و اتاقی در فضای باز.",
            "Deep thresholds soften the transition from street to courtyard.",
            "آستانه‌های عمیق، گذار از خیابان به حیاط را نرم می‌کنند.",
            "The garden is not an object at the center. It is the measure of every room around it.",
            "باغ شیئی در مرکز نیست؛ مقیاس هر اتاقی است که پیرامون آن شکل گرفته.",
            "Material restraint",
            "خویشتن‌داری در مصالح",
            "Concrete, local stone, oak, and lime plaster form a limited palette.",
            "بتن، سنگ بومی، چوب بلوط و اندود آهکی، پالتی محدود می‌سازند.",
            ["architecture", "interior"],
            "residential",
        ),
        (
            "northline-atelier",
            "Northline Atelier",
            "آتلیه‌ی خط شمالی",
            "A long shared room for making, looking, and working beside a pine grove.",
            "اتاقی کشیده و مشترک برای ساختن، دیدن و کارکردن در کنار بیشه‌ی کاج.",
            "Karaj",
            "کرج",
            2026,
            "Completed",
            "تکمیل‌شده",
            "610 m²",
            "۶۱۰ مترمربع",
            "Architecture · Interior",
            "معماری · معماری داخلی",
            "/media/northline-atelier.png",
            "Long concrete and oak architecture studio looking into a pine grove",
            "استودیوی کشیده‌ی بتنی و چوبی رو به بیشه‌ی کاج",
            "One room, many ways of working.",
            "یک اتاق، شیوه‌های گوناگون کار.",
            "A continuous table and measured structural bay support focused and collective work.",
            "میزی پیوسته و دهانه‌های سازه‌ای سنجیده، کار متمرکز و جمعی را پشتیبانی می‌کنند.",
            "A working edge in the trees.",
            "لبه‌ای برای کار میان درختان.",
            "North light and a deep timber wall hold tools, drawings, and models.",
            "نور شمال و دیواره‌ای عمیق از چوب، ابزار، نقشه و ماکت را نگه می‌دارند.",
            "The studio is most useful when the room can disappear behind the work.",
            "استودیو زمانی کارآمدتر است که اتاق بتواند پشت فرایند کار محو شود.",
            "A durable work surface",
            "سطح کاری ماندگار",
            "Concrete carries thermal mass while oak accepts the marks of repeated making.",
            "بتن جرم حرارتی را تأمین می‌کند و چوب بلوط رد ساختن‌های مکرر را می‌پذیرد.",
            ["architecture", "interior"],
            "workspace",
        ),
        (
            "house-of-shade",
            "House of Shade",
            "خانه‌ی سایه",
            "A compact house that treats shade as its primary building material.",
            "خانه‌ای فشرده که سایه را مهم‌ترین مصالح خود می‌داند.",
            "Tehran",
            "تهران",
            2025,
            "Study",
            "در حال مطالعه",
            "310 m²",
            "۳۱۰ مترمربع",
            "Architecture",
            "معماری",
            "/media/material-shadow.png",
            "Leaf shadows crossing concrete and oak",
            "سایه‌ی برگ‌ها روی بتن و چوب بلوط",
            "A section tuned to the sun.",
            "برشی هماهنگ با خورشید.",
            "Terraces, deep reveals, and planted edges temper the movement of heat and light.",
            "تراس‌ها، فرورفتگی‌های عمیق و لبه‌های کاشته‌شده، حرکت گرما و نور را تعدیل می‌کنند.",
            "Shade with depth.",
            "سایه‌ای دارای عمق.",
            "The envelope becomes a sequence of inhabited thresholds.",
            "پوسته به توالی آستانه‌های قابل سکونت تبدیل می‌شود.",
            "Comfort begins before the interior.",
            "آسایش پیش از فضای داخلی آغاز می‌شود.",
            "Mineral envelope",
            "پوسته‌ی معدنی",
            "Pigmented concrete and local stone carry the changing temperature of the day.",
            "بتن رنگ‌دانه‌دار و سنگ بومی، تغییر دمای روز را در خود نگه می‌دارند.",
            ["architecture"],
            "residential",
        ),
        (
            "archive-rooms",
            "Archive Rooms",
            "اتاق‌های آرشیو",
            "An industrial shell recast as rooms for reading and shared memory.",
            "پوسته‌ای صنعتی که به اتاق‌هایی برای خواندن و حافظه‌ی جمعی بدل شده است.",
            "Rasht",
            "رشت",
            2025,
            "Completed",
            "تکمیل‌شده",
            "780 m²",
            "۷۸۰ مترمربع",
            "Adaptive reuse · Interior",
            "باززنده‌سازی · معماری داخلی",
            "/media/northline-atelier.png",
            "Timber shelving in a deep shared work room",
            "قفسه‌های چوبی در اتاقی مشترک و عمیق",
            "New uses inside an old measure.",
            "کاربری تازه در مقیاسی قدیمی.",
            "Independent timber rooms preserve the original brick shell.",
            "اتاق‌های مستقل چوبی، پوسته‌ی آجری موجود را حفظ می‌کنند.",
            "Repair before replacement.",
            "ترمیم پیش از جایگزینی.",
            "Every intervention is reversible and leaves useful scars visible.",
            "هر مداخله برگشت‌پذیر است و ردهای معنادار سازه را آشکار نگه می‌دارد.",
            "The existing fabric is part of the collection.",
            "بافت موجود بخشی از مجموعه است.",
            "Old brick, new timber",
            "آجر قدیمی، چوب تازه",
            "A dry assembly keeps old and new distinct while allowing both to age together.",
            "اتصال خشک، قدیم و جدید را متمایز نگه می‌دارد.",
            ["adaptive-reuse", "interior"],
            "adaptive-reuse",
        ),
        (
            "cedar-passage",
            "Cedar Passage",
            "گذر سرو",
            "Shaded civic rooms join street, garden, and exhibition space.",
            "فضاهای عمومی سایه‌دار، خیابان، باغ و نمایشگاه را پیوند می‌دهند.",
            "Shiraz",
            "شیراز",
            2025,
            "Competition",
            "مسابقه",
            "1,240 m²",
            "۱٬۲۴۰ مترمربع",
            "Architecture · Landscape",
            "معماری · منظر",
            "/media/voluma-mountain-house.png",
            "Concrete threshold opening toward a distant landscape",
            "آستانه‌ی بتنی رو به چشم‌اندازی دور",
            "A building that begins as a path.",
            "ساختمانی که از مسیر آغاز می‌شود.",
            "The public route remains visible from every room.",
            "مسیر عمومی از هر اتاق دیده می‌شود.",
            "Rooms without a front door.",
            "اتاق‌هایی بدون در ورودی اصلی.",
            "Multiple thresholds let the institution open gradually across the day.",
            "آستانه‌های متعدد اجازه می‌دهند مجموعه در طول روز به‌تدریج گشوده شود.",
            "The path is the first public room.",
            "مسیر، نخستین اتاق عمومی است.",
            "Shade and brick",
            "سایه و آجر",
            "Deep brick screens filter sun while preserving a civic edge.",
            "مشبک‌های عمیق آجری، خورشید را فیلتر می‌کنند.",
            ["architecture"],
            "cultural",
        ),
        (
            "common-ground",
            "Common Ground",
            "زمین مشترک",
            "A workplace organized around shared thresholds rather than assigned desks.",
            "محیط کاری‌ای که به‌جای میزهای ثابت، پیرامون آستانه‌های مشترک سامان یافته است.",
            "Karaj",
            "کرج",
            2024,
            "Completed",
            "تکمیل‌شده",
            "940 m²",
            "۹۴۰ مترمربع",
            "Interior · Spatial strategy",
            "معماری داخلی · راهبرد فضایی",
            "/media/material-shadow.png",
            "Concrete bench and oak frame in afternoon light",
            "نیمکت بتنی و قاب چوب بلوط در نور عصر",
            "Work gathered around a shared middle.",
            "کار پیرامون مرکزی مشترک.",
            "A continuous interior street supports informal meetings and focused rooms.",
            "خیابانی داخلی و پیوسته، گفت‌وگوهای غیررسمی و اتاق‌های متمرکز را پشتیبانی می‌کند.",
            "Structure as wayfinding.",
            "سازه به‌مثابه‌ی مسیریابی.",
            "Repeated timber bays make orientation intuitive without visual noise.",
            "دهانه‌های تکرارشونده‌ی چوبی، جهت‌یابی را طبیعی می‌کنند.",
            "Shared space should invite use, not prescribe it.",
            "فضای مشترک باید دعوت‌کننده باشد، نه تجویزکننده.",
            "A frame that can change",
            "قابی که می‌تواند تغییر کند",
            "Demountable timber frames support new rooms as the organization evolves.",
            "قاب‌های چوبی بازشدنی، اتاق‌های تازه را ممکن می‌کنند.",
            ["interior", "spatial-strategy"],
            "workspace",
        ),
    ]
    for order, data in enumerate(project_data, start=1):
        (
            slug,
            title_en,
            title_fa,
            summary_en,
            summary_fa,
            location_en,
            location_fa,
            year,
            status_en,
            status_fa,
            area_en,
            area_fa,
            scope_en,
            scope_fa,
            image_url,
            alt_en,
            alt_fa,
            intro_title_en,
            intro_title_fa,
            intro_en,
            intro_fa,
            narrative_title_en,
            narrative_title_fa,
            narrative_en,
            narrative_fa,
            quote_en,
            quote_fa,
            material_title_en,
            material_title_fa,
            material_en,
            material_fa,
            discipline_slugs,
            typology_slug,
        ) = data
        session.add(
            Project(
                slug=slug,
                publication_state=PublicationState.PUBLISHED,
                published_at=now,
                display_order=order,
                featured=order <= 2,
                title_en=title_en,
                title_fa=title_fa,
                summary_en=summary_en,
                summary_fa=summary_fa,
                location_en=location_en,
                location_fa=location_fa,
                completion_year=year,
                status_en=status_en,
                status_fa=status_fa,
                area_en=area_en,
                area_fa=area_fa,
                scope_en=scope_en,
                scope_fa=scope_fa,
                cover_image_url=image_url,
                cover_alt_en=alt_en,
                cover_alt_fa=alt_fa,
                gallery_images=[
                    {"url": image_url, "alt_en": alt_en, "alt_fa": alt_fa},
                    {
                        "url": "/media/material-shadow.png",
                        "alt_en": "Leaf shadows crossing concrete and oak",
                        "alt_fa": "سایه‌ی برگ‌ها روی بتن و چوب بلوط",
                    },
                ],
                intro_title_en=intro_title_en,
                intro_title_fa=intro_title_fa,
                intro_en=intro_en,
                intro_fa=intro_fa,
                narrative_title_en=narrative_title_en,
                narrative_title_fa=narrative_title_fa,
                narrative_en=narrative_en,
                narrative_fa=narrative_fa,
                quote_en=quote_en,
                quote_fa=quote_fa,
                material_title_en=material_title_en,
                material_title_fa=material_title_fa,
                material_en=material_en,
                material_fa=material_fa,
                disciplines=[disciplines[key] for key in discipline_slugs],
                typologies=[typologies[typology_slug]],
            )
        )

    session.add_all(
        [
            Expertise(
                publication_state=PublicationState.PUBLISHED,
                display_order=1,
                title_en="Architecture",
                title_fa="معماری",
                summary_en="Spatial frameworks shaped by climate, use, and time.",
                summary_fa="چارچوب‌های فضایی شکل‌گرفته با اقلیم، کاربری و زمان.",
            ),
            Expertise(
                publication_state=PublicationState.PUBLISHED,
                display_order=2,
                title_en="Interior architecture",
                title_fa="معماری داخلی",
                summary_en="Material, light, and detail calibrated at the human scale.",
                summary_fa="مصالح، نور و جزئیات در مقیاس انسان تنظیم می‌شوند.",
            ),
            Expertise(
                publication_state=PublicationState.PUBLISHED,
                display_order=3,
                title_en="Adaptive reuse",
                title_fa="باززنده‌سازی",
                summary_en="Existing fabric is measured before replacement is considered.",
                summary_fa="بافت موجود پیش از تصمیم برای جایگزینی سنجیده می‌شود.",
            ),
            Expertise(
                publication_state=PublicationState.PUBLISHED,
                display_order=4,
                title_en="Spatial strategy",
                title_fa="راهبرد فضایی",
                summary_en="A clear brief connects future use with the available place.",
                summary_fa="صورت‌مسئله‌ای روشن، کاربری آینده را به مکان موجود پیوند می‌دهد.",
            ),
            ProcessStep(
                publication_state=PublicationState.PUBLISHED,
                display_order=1,
                title_en="Listen",
                title_fa="شنیدن",
                summary_en="Read the place, people, and constraints before proposing form.",
                summary_fa="پیش از پیشنهاد فرم، مکان، افراد و محدودیت‌ها را می‌خوانیم.",
            ),
            ProcessStep(
                publication_state=PublicationState.PUBLISHED,
                display_order=2,
                title_en="Frame",
                title_fa="چارچوب‌دادن",
                summary_en="Turn observations into a clear spatial question.",
                summary_fa="مشاهده‌ها را به پرسشی روشن دربارهٔ فضا تبدیل می‌کنیم.",
            ),
            ProcessStep(
                publication_state=PublicationState.PUBLISHED,
                display_order=3,
                title_en="Develop",
                title_fa="پرورش",
                summary_en="Test scale, material, and use through a coordinated proposal.",
                summary_fa="مقیاس، مصالح و کاربری را با پیشنهادی هماهنگ آزمون می‌کنیم.",
            ),
            ProcessStep(
                publication_state=PublicationState.PUBLISHED,
                display_order=4,
                title_en="Deliver",
                title_fa="تحویل",
                summary_en="Carry the design through detail and implementation decisions.",
                summary_fa="طراحی را تا جزئیات و تصمیم‌های اجرا ادامه می‌دهیم.",
            ),
        ]
    )

    categories = {
        "ideas": JournalCategory(
            slug="ideas", title_en="Ideas", title_fa="ایده‌ها", display_order=1
        ),
        "process": JournalCategory(
            slug="process", title_en="Process", title_fa="فرایند", display_order=2
        ),
        "architecture": JournalCategory(
            slug="architecture", title_en="Architecture", title_fa="معماری", display_order=3
        ),
    }
    session.add_all(categories.values())
    session.flush()
    session.add_all(
        [
            JournalArticle(
                slug="material-as-memory",
                publication_state=PublicationState.PUBLISHED,
                published_at=now,
                category=categories["ideas"],
                title_en="Material as a memory of place",
                title_fa="مصالح به‌مثابهٔ حافظهٔ مکان",
                excerpt_en="A limited material palette can record weather, repair, and use.",
                excerpt_fa="پالتی محدود از مصالح می‌تواند آب‌وهوا، ترمیم و استفاده را ثبت کند.",
                body_en=(
                    "Materials are not neutral. Their texture and capacity to age decide "
                    "how a room receives light.\n\n"
                    "The useful question is whether change can become part of the place."
                ),
                body_fa=(
                    "مصالح خنثی نیستند. بافت و توانایی آن‌ها برای پیرشدن تعیین می‌کند "
                    "اتاق چگونه نور را می‌پذیرد.\n\n"
                    "پرسش مفید این است که آیا تغییر می‌تواند بخشی از مکان شود."
                ),
                reading_minutes=5,
                cover_image_url="/media/material-shadow.png",
                cover_alt_en="Leaf shadows crossing a concrete and oak surface",
                cover_alt_fa="سایهٔ برگ‌ها بر سطح بتن و چوب بلوط",
            ),
            JournalArticle(
                slug="reading-existing-fabric",
                publication_state=PublicationState.PUBLISHED,
                published_at=now,
                category=categories["process"],
                title_en="Reading the existing fabric",
                title_fa="خواندن بافت موجود",
                excerpt_en=(
                    "Before replacement, a building asks to be measured for what it already holds."
                ),
                excerpt_fa=(
                    "پیش از جایگزینی، ساختمان موجود باید برای آنچه هم‌اکنون در خود دارد سنجیده شود."
                ),
                body_en=(
                    "Existing fabric contains evidence: dimensions, habits, repairs, and "
                    "traces of climate control.\n\n"
                    "Reuse begins with attention to what can remain useful."
                ),
                body_fa=(
                    "بافت موجود حامل شواهدی از ابعاد، عادت‌ها، ترمیم‌ها و اقلیم است.\n\n"
                    "باززنده‌سازی با توجه به آنچه می‌تواند مفید بماند آغاز می‌شود."
                ),
                reading_minutes=4,
                cover_image_url="/media/northline-atelier.png",
                cover_alt_en="An interior with existing concrete structure and timber worktables",
                cover_alt_fa="فضای داخلی با سازهٔ بتنی موجود و میزهای کار چوبی",
            ),
            JournalArticle(
                slug="the-room-after-noon",
                publication_state=PublicationState.PUBLISHED,
                published_at=now,
                category=categories["architecture"],
                title_en="The room after noon",
                title_fa="اتاق پس از نیمروز",
                excerpt_en="The most revealing hour is when light has stopped performing.",
                excerpt_fa="آشکارترین ساعت یک اتاق زمانی است که نور دیگر در حال نمایش نیست.",
                body_en=(
                    "Architecture is tested after dramatic light has passed.\n\n"
                    "A durable space gives ordinary activity enough calm to become visible."
                ),
                body_fa=(
                    "معماری پس از گذشتن نور نمایشی آزموده می‌شود.\n\n"
                    "فضای ماندگار به فعالیت عادی آن‌قدر آرامش می‌دهد که دیده شود."
                ),
                reading_minutes=6,
                cover_image_url="/media/courtyard-house.png",
                cover_alt_en="A quiet courtyard room in late afternoon light",
                cover_alt_fa="اتاقی آرام رو به حیاط در نور آخر بعدازظهر",
            ),
        ]
    )
    return True
