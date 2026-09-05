import type { LocalizedText } from "@/content/site";

export type ExpertiseEntry = {
  index: string;
  title: LocalizedText;
  summary: LocalizedText;
  image: string;
  alt: LocalizedText;
};

export type ProcessStep = {
  index: string;
  title: LocalizedText;
  summary: LocalizedText;
};

export type JournalArticle = {
  slug: string;
  category: LocalizedText;
  title: LocalizedText;
  excerpt: LocalizedText;
  published: LocalizedText;
  readingTime: LocalizedText;
  cover: string;
  alt: LocalizedText;
  body: LocalizedText[];
};

export const expertiseEntries: ExpertiseEntry[] = [
  {
    index: "01",
    title: { en: "Architecture", fa: "معماری" },
    summary: {
      en: "Buildings that give daily life a clear relation to climate, structure, and landscape.",
      fa: "ساختمان‌هایی که زندگی روزمره را با اقلیم، سازه و منظر در نسبتی روشن قرار می‌دهند.",
    },
    image: "/media/courtyard-house.png",
    alt: {
      en: "A shaded courtyard opening from a concrete house",
      fa: "حیاطی سایه‌دار در امتداد خانه‌ای بتنی",
    },
  },
  {
    index: "02",
    title: { en: "Interior architecture", fa: "معماری داخلی" },
    summary: {
      en: "Interiors shaped around movement, light, and the character of everyday materials.",
      fa: "فضاهای داخلی شکل‌گرفته پیرامون حرکت، نور و شخصیت مصالح روزمره.",
    },
    image: "/media/northline-atelier.png",
    alt: {
      en: "A long oak and concrete interior facing trees",
      fa: "فضای داخلی کشیده‌ای از بلوط و بتن رو به درختان",
    },
  },
  {
    index: "03",
    title: { en: "Adaptive reuse", fa: "باززنده‌سازی" },
    summary: {
      en: "Existing structures read closely before a new use is introduced with care.",
      fa: "سازه‌های موجود پیش از افزودن کاربری تازه، با دقت خوانده می‌شوند.",
    },
    image: "/media/material-shadow.png",
    alt: {
      en: "Light moving across a material junction",
      fa: "حرکت نور بر محل اتصال مصالح",
    },
  },
];

export const processSteps: ProcessStep[] = [
  {
    index: "01",
    title: { en: "Discover", fa: "شناخت" },
    summary: {
      en: "We begin with the site, the people who will use it, and the conditions already present.",
      fa: "از سایت، استفاده‌کنندگان و شرایطی که از پیش وجود دارند آغاز می‌کنیم.",
    },
  },
  {
    index: "02",
    title: { en: "Research", fa: "پژوهش" },
    summary: {
      en: "References, climate, materials, regulations, and budget become a shared frame for decisions.",
      fa: "مرجع‌ها، اقلیم، مصالح، ضوابط و بودجه به چارچوبی مشترک برای تصمیم‌ها بدل می‌شوند.",
    },
  },
  {
    index: "03",
    title: { en: "Concept", fa: "ایده" },
    summary: {
      en: "A spatial idea is tested until it can hold program, atmosphere, and construction together.",
      fa: "ایدهٔ فضایی تا جایی آزموده می‌شود که برنامه، کیفیت فضا و ساخت را کنار هم نگه دارد.",
    },
  },
  {
    index: "04",
    title: { en: "Develop", fa: "توسعه" },
    summary: {
      en: "Drawings and details make the design legible to everyone responsible for building it.",
      fa: "نقشه‌ها و جزئیات، طراحی را برای همهٔ مسئولان ساخت خوانا می‌کنند.",
    },
  },
  {
    index: "05",
    title: { en: "Deliver", fa: "تحویل" },
    summary: {
      en: "We remain attentive to the work on site, where material decisions become lived space.",
      fa: "در سایت همراه کار می‌مانیم؛ جایی که تصمیم‌های مادی به فضای زیسته بدل می‌شوند.",
    },
  },
];

export const studioCopy = {
  en: {
    eyebrow: "Studio",
    title: "A practice built around attentive looking.",
    intro:
      "VOLUMA is presented here as a development fixture for an architecture and design practice. The future content-managed studio page will introduce approved people, collaborators, recognition, and contact details without inventing claims.",
    principles: [
      [
        "Place before image",
        "Every proposal starts with the conditions that already give a site its character.",
      ],
      [
        "Use gives form",
        "Plans are tested against ordinary movement, maintenance, and change over time.",
      ],
      ["Detail carries the whole", "Material decisions make the larger spatial idea tangible."],
    ],
    recordsTitle: "Records to be published with approval.",
    recordsBody:
      "People, collaborators, selected numbers, and recognition are intentionally not represented as fictional content in this preview.",
  },
  fa: {
    eyebrow: "استودیو",
    title: "ممارستی بر پایهٔ نگاه دقیق.",
    intro:
      "ولوما در اینجا به‌عنوان دادهٔ نمونهٔ توسعه برای یک استودیوی معماری و طراحی ارائه شده است. صفحهٔ استودیوی آینده که با محتوا مدیریت می‌شود، افراد، همکاران، تقدیرها و اطلاعات تماس تأییدشده را بدون ساختن ادعاهای خیالی معرفی می‌کند.",
    principles: [
      ["مکان پیش از تصویر", "هر پیشنهاد از شرایطی آغاز می‌شود که از پیش به سایت شخصیت داده‌اند."],
      ["کاربری فرم می‌دهد", "پلان‌ها با حرکت روزمره، نگهداری و تغییر در طول زمان آزموده می‌شوند."],
      ["جزئیات، کل را حمل می‌کند", "تصمیم‌های مادی، ایدهٔ فضایی بزرگ‌تر را ملموس می‌کنند."],
    ],
    recordsTitle: "اطلاعاتی که با تأیید منتشر می‌شوند.",
    recordsBody:
      "افراد، همکاران، آمار منتخب و تقدیرها عمداً در این پیش‌نمایش با محتوای ساختگی نمایش داده نشده‌اند.",
  },
} as const;

export const journalArticles: JournalArticle[] = [
  {
    slug: "material-as-memory",
    category: { en: "Ideas", fa: "ایده‌ها" },
    title: { en: "Material as a memory of place", fa: "مصالح به‌مثابهٔ حافظهٔ مکان" },
    excerpt: {
      en: "A limited material palette can record weather, repair, and use without asking for attention.",
      fa: "پالتی محدود از مصالح می‌تواند آب‌وهوا، ترمیم و استفاده را ثبت کند، بی‌آنکه توجه بطلبد.",
    },
    published: { en: "Development fixture", fa: "دادهٔ نمونهٔ توسعه" },
    readingTime: { en: "5 min read", fa: "۵ دقیقه مطالعه" },
    cover: "/media/material-shadow.png",
    alt: {
      en: "Leaf shadows crossing a concrete and oak surface",
      fa: "سایهٔ برگ‌ها بر سطح بتن و چوب بلوط",
    },
    body: [
      {
        en: "Materials are not neutral. Their texture and capacity to age decide how a room receives light, touch, and repair.",
        fa: "مصالح خنثی نیستند. بافت و توانایی آن‌ها برای پیرشدن تعیین می‌کند یک اتاق چگونه نور، لمس و ترمیم را می‌پذیرد.",
      },
      {
        en: "The useful question is not whether a surface will remain unchanged, but whether its change can become part of the place.",
        fa: "پرسش مفید این نیست که آیا سطح بدون تغییر می‌ماند؛ پرسش این است که آیا تغییر آن می‌تواند بخشی از مکان شود.",
      },
    ],
  },
  {
    slug: "reading-existing-fabric",
    category: { en: "Process", fa: "فرایند" },
    title: { en: "Reading the existing fabric", fa: "خواندن بافت موجود" },
    excerpt: {
      en: "Before replacement, an existing building asks to be measured for what it already holds.",
      fa: "پیش از جایگزینی، ساختمان موجود باید برای آنچه هم‌اکنون در خود دارد سنجیده شود.",
    },
    published: { en: "Development fixture", fa: "دادهٔ نمونهٔ توسعه" },
    readingTime: { en: "4 min read", fa: "۴ دقیقه مطالعه" },
    cover: "/media/northline-atelier.png",
    alt: {
      en: "An interior with existing concrete structure and timber worktables",
      fa: "فضای داخلی با سازهٔ بتنی موجود و میزهای کار چوبی",
    },
    body: [
      {
        en: "Existing fabric contains evidence: dimensions, habits, repairs, and traces of prior climate control. That evidence can make a proposal more precise.",
        fa: "بافت موجود حامل شواهد است: ابعاد، عادت‌ها، ترمیم‌ها و ردهای کنترل پیشین اقلیم. این شواهد می‌توانند پیشنهاد را دقیق‌تر کنند.",
      },
      {
        en: "Reuse begins with attention to what can remain useful, not with an image of what must look new.",
        fa: "باززنده‌سازی با توجه به آنچه می‌تواند مفید بماند آغاز می‌شود، نه با تصویری از آنچه باید تازه به نظر برسد.",
      },
    ],
  },
  {
    slug: "the-room-after-noon",
    category: { en: "Architecture", fa: "معماری" },
    title: { en: "The room after noon", fa: "اتاق پس از نیمروز" },
    excerpt: {
      en: "The most revealing hour in a room is often the one when light has stopped performing.",
      fa: "آشکارترین ساعت یک اتاق اغلب زمانی است که نور دیگر در حال نمایش نیست.",
    },
    published: { en: "Development fixture", fa: "دادهٔ نمونهٔ توسعه" },
    readingTime: { en: "6 min read", fa: "۶ دقیقه مطالعه" },
    cover: "/media/courtyard-house.png",
    alt: {
      en: "A quiet courtyard room in late afternoon light",
      fa: "اتاقی آرام رو به حیاط در نور آخر بعدازظهر",
    },
    body: [
      {
        en: "Architecture is tested after the dramatic light has passed. What remains is proportion, temperature, and the room's willingness to be used.",
        fa: "معماری پس از گذشتن نور نمایشی آزموده می‌شود. آنچه می‌ماند تناسب، دما و آمادگی اتاق برای استفاده است.",
      },
      {
        en: "A durable space does not need to announce itself. It gives ordinary activity enough calm to become visible.",
        fa: "فضای ماندگار نیازی به اعلام خود ندارد. به فعالیت عادی آن‌قدر آرامش می‌دهد که دیده شود.",
      },
    ],
  },
];

export function getJournalArticle(slug: string) {
  return journalArticles.find((article) => article.slug === slug);
}

export const privacyCopy = {
  en: {
    title: "Privacy, in plain language.",
    intro:
      "This development preview describes the intended handling of contact-form data. It is not legal advice and must be replaced with owner-approved wording before commercial use.",
    sections: [
      [
        "What is collected",
        "A contact form is intended to collect the name, email address, optional phone, optional company, optional project type, and message provided by the sender.",
      ],
      [
        "Why it is collected",
        "The information is intended only to respond to an enquiry and to understand the context of a possible project.",
      ],
      [
        "How it is stored",
        "When the service is implemented, messages will be stored in the application's protected database for administrator triage. They are not intended for public display.",
      ],
      [
        "Retention and requests",
        "The owner must define a retention period before launch. A sender will be able to contact the site owner to request access, correction, or deletion where applicable.",
      ],
    ],
  },
  fa: {
    title: "حریم خصوصی، به زبان روشن.",
    intro:
      "این پیش‌نمایش توسعه، شیوهٔ موردنظر برای رسیدگی به داده‌های فرم تماس را توضیح می‌دهد. این متن مشاورهٔ حقوقی نیست و پیش از استفادهٔ تجاری باید با متن تأییدشدهٔ مالک جایگزین شود.",
    sections: [
      [
        "چه چیزی جمع‌آوری می‌شود",
        "فرم تماس برای دریافت نام، نشانی ایمیل، تلفن اختیاری، شرکت اختیاری، نوع پروژهٔ اختیاری و پیام فرستنده طراحی شده است.",
      ],
      [
        "چرا جمع‌آوری می‌شود",
        "این اطلاعات فقط برای پاسخ به درخواست و درک زمینهٔ یک پروژهٔ احتمالی در نظر گرفته شده‌اند.",
      ],
      [
        "چگونه نگهداری می‌شود",
        "پس از پیاده‌سازی سرویس، پیام‌ها برای رسیدگی مدیر در پایگاه‌دادهٔ محافظت‌شدهٔ برنامه نگهداری می‌شوند و برای نمایش عمومی در نظر گرفته نشده‌اند.",
      ],
      [
        "نگهداری و درخواست‌ها",
        "مالک باید پیش از راه‌اندازی، دورهٔ نگهداری را تعیین کند. فرستنده در صورت لزوم می‌تواند برای درخواست دسترسی، اصلاح یا حذف با مالک سایت ارتباط بگیرد.",
      ],
    ],
  },
} as const;
