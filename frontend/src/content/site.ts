import type { Locale } from "@/i18n/routing";

export type LocalizedText = Record<Locale, string>;
export type ProjectCategory = "residential" | "workspace" | "cultural" | "adaptive-reuse";

export type Project = {
  slug: string;
  title: LocalizedText;
  category: ProjectCategory;
  categoryLabel: LocalizedText;
  location: LocalizedText;
  year: string;
  status: LocalizedText;
  area: LocalizedText;
  scope: LocalizedText;
  summary: LocalizedText;
  introTitle: LocalizedText;
  intro: LocalizedText;
  narrativeTitle: LocalizedText;
  narrative: LocalizedText;
  quote: LocalizedText;
  materialTitle: LocalizedText;
  material: LocalizedText;
  image: string;
  alt: LocalizedText;
  imagePosition?: string;
};

export const navItems = [
  { href: "/projects", label: { en: "Projects", fa: "پروژه‌ها" } },
  { href: "/expertise", label: { en: "Expertise", fa: "تخصص‌ها" } },
  { href: "/process", label: { en: "Process", fa: "فرایند" } },
  { href: "/studio", label: { en: "Studio", fa: "استودیو" } },
  { href: "/journal", label: { en: "Journal", fa: "یادداشت‌ها" } },
  { href: "/contact", label: { en: "Contact", fa: "تماس" } },
] as const;

export const categoryLabels: Record<"all" | ProjectCategory, LocalizedText> = {
  all: { en: "All", fa: "همه" },
  residential: { en: "Residential", fa: "مسکونی" },
  workspace: { en: "Workspace", fa: "فضای کار" },
  cultural: { en: "Cultural", fa: "فرهنگی" },
  "adaptive-reuse": { en: "Adaptive reuse", fa: "باززنده‌سازی" },
};

export const projects: Project[] = [
  {
    slug: "courtyard-house",
    title: { en: "Courtyard House", fa: "خانه‌ی حیاط مرکزی" },
    category: "residential",
    categoryLabel: categoryLabels.residential,
    location: { en: "Tehran", fa: "تهران" },
    year: "2026",
    status: { en: "Completed", fa: "تکمیل‌شده" },
    area: { en: "420 m²", fa: "۴۲۰ مترمربع" },
    scope: { en: "Architecture · Interior", fa: "معماری · معماری داخلی" },
    summary: {
      en: "A home organized around shade, filtered light, and a protected inner garden.",
      fa: "خانه‌ای شکل‌گرفته پیرامون سایه، نور فیلترشده و باغی محفوظ در مرکز.",
    },
    introTitle: { en: "A calm center for daily life.", fa: "مرکزی آرام برای زندگی روزمره." },
    intro: {
      en: "The house turns inward to make privacy, daylight, and seasonal change part of one continuous domestic landscape.",
      fa: "خانه به درون بازمی‌گردد تا خلوت، نور روز و تغییر فصل‌ها را در یک منظر پیوسته‌ی خانگی جمع کند.",
    },
    narrativeTitle: {
      en: "Light, shade, and a room outside.",
      fa: "نور، سایه و اتاقی در فضای باز.",
    },
    narrative: {
      en: "Deep thresholds soften the transition from street to courtyard. Openings are placed to frame movement rather than objects.",
      fa: "آستانه‌های عمیق، گذار از خیابان به حیاط را نرم می‌کنند. بازشوها به‌جای قاب‌کردن اشیا، حرکت را قاب می‌گیرند.",
    },
    quote: {
      en: "The garden is not an object at the center. It is the measure of every room around it.",
      fa: "باغ شیئی در مرکز نیست؛ مقیاس هر اتاقی است که پیرامون آن شکل گرفته.",
    },
    materialTitle: { en: "Material restraint", fa: "خویشتن‌داری در مصالح" },
    material: {
      en: "Board-marked concrete, local stone, oak, and lime plaster form a limited palette that records light and use.",
      fa: "بتن قالب‌تخته‌ای، سنگ بومی، چوب بلوط و اندود آهکی، پالت محدودی می‌سازند که نور و استفاده را ثبت می‌کند.",
    },
    image: "/media/courtyard-house.png",
    alt: {
      en: "Concrete courtyard house arranged around a mature shade tree",
      fa: "خانه‌ای بتنی پیرامون یک درخت سایه‌انداز بالغ",
    },
  },
  {
    slug: "northline-atelier",
    title: { en: "Northline Atelier", fa: "آتلیه‌ی خط شمالی" },
    category: "workspace",
    categoryLabel: categoryLabels.workspace,
    location: { en: "Karaj", fa: "کرج" },
    year: "2026",
    status: { en: "Completed", fa: "تکمیل‌شده" },
    area: { en: "610 m²", fa: "۶۱۰ مترمربع" },
    scope: { en: "Architecture · Interior", fa: "معماری · معماری داخلی" },
    summary: {
      en: "A long shared room for making, looking, and working beside a pine grove.",
      fa: "اتاقی کشیده و مشترک برای ساختن، دیدن و کارکردن در کنار بیشه‌ی کاج.",
    },
    introTitle: { en: "One room, many ways of working.", fa: "یک اتاق، شیوه‌های گوناگون کار." },
    intro: {
      en: "A continuous table and a measured structural bay let the studio shift between focused work, reviews, and collective making.",
      fa: "میزی پیوسته و دهانه‌های سازه‌ای سنجیده، استودیو را میان تمرکز فردی، نقد و ساخت جمعی تغییر می‌دهند.",
    },
    narrativeTitle: { en: "A working edge in the trees.", fa: "لبه‌ای برای کار میان درختان." },
    narrative: {
      en: "North light and a deep timber wall hold tools, drawings, and models without turning the room into storage.",
      fa: "نور شمال و دیواره‌ای عمیق از چوب، ابزار، نقشه و ماکت را نگه می‌دارند بی‌آنکه اتاق به انبار تبدیل شود.",
    },
    quote: {
      en: "The studio is most useful when the room can disappear behind the work.",
      fa: "استودیو زمانی کارآمدتر است که اتاق بتواند پشت فرایند کار محو شود.",
    },
    materialTitle: { en: "A durable work surface", fa: "سطح کاری ماندگار" },
    material: {
      en: "Concrete carries thermal mass while oak absorbs the marks of repeated making.",
      fa: "بتن جرم حرارتی را تأمین می‌کند و چوب بلوط رد ساختن‌های مکرر را می‌پذیرد.",
    },
    image: "/media/northline-atelier.png",
    alt: {
      en: "Long concrete and oak architecture studio looking into a pine grove",
      fa: "استودیوی کشیده‌ی بتنی و چوبی رو به بیشه‌ی کاج",
    },
  },
  {
    slug: "house-of-shade",
    title: { en: "House of Shade", fa: "خانه‌ی سایه" },
    category: "residential",
    categoryLabel: categoryLabels.residential,
    location: { en: "Tehran", fa: "تهران" },
    year: "2025",
    status: { en: "Study", fa: "در حال مطالعه" },
    area: { en: "310 m²", fa: "۳۱۰ مترمربع" },
    scope: { en: "Architecture", fa: "معماری" },
    summary: {
      en: "A compact house that treats shade as its primary building material.",
      fa: "خانه‌ای فشرده که سایه را مهم‌ترین مصالح خود می‌داند.",
    },
    introTitle: { en: "A section tuned to the sun.", fa: "برشی هماهنگ با خورشید." },
    intro: {
      en: "Terraces, deep reveals, and planted edges temper the daily movement of heat and light.",
      fa: "تراس‌ها، فرورفتگی‌های عمیق و لبه‌های کاشته‌شده، حرکت روزانه‌ی گرما و نور را تعدیل می‌کنند.",
    },
    narrativeTitle: { en: "Shade with depth.", fa: "سایه‌ای دارای عمق." },
    narrative: {
      en: "The envelope becomes a sequence of inhabited thresholds rather than a flat boundary.",
      fa: "پوسته به‌جای مرزی تخت، به توالی آستانه‌های قابل سکونت تبدیل می‌شود.",
    },
    quote: {
      en: "Comfort begins before the interior.",
      fa: "آسایش پیش از فضای داخلی آغاز می‌شود.",
    },
    materialTitle: { en: "Mineral envelope", fa: "پوسته‌ی معدنی" },
    material: {
      en: "Pigmented concrete and local stone carry the changing temperature of the day.",
      fa: "بتن رنگ‌دانه‌دار و سنگ بومی، تغییر دمای روز را در خود نگه می‌دارند.",
    },
    image: "/media/material-shadow.png",
    imagePosition: "center",
    alt: { en: "Leaf shadows crossing concrete and oak", fa: "سایه‌ی برگ‌ها روی بتن و چوب بلوط" },
  },
  {
    slug: "archive-rooms",
    title: { en: "Archive Rooms", fa: "اتاق‌های آرشیو" },
    category: "adaptive-reuse",
    categoryLabel: categoryLabels["adaptive-reuse"],
    location: { en: "Rasht", fa: "رشت" },
    year: "2025",
    status: { en: "Completed", fa: "تکمیل‌شده" },
    area: { en: "780 m²", fa: "۷۸۰ مترمربع" },
    scope: { en: "Adaptive reuse · Interior", fa: "باززنده‌سازی · معماری داخلی" },
    summary: {
      en: "An existing industrial shell recast as rooms for reading and shared memory.",
      fa: "پوسته‌ای صنعتی که به اتاق‌هایی برای خواندن و حافظه‌ی جمعی بدل شده است.",
    },
    introTitle: { en: "New uses inside an old measure.", fa: "کاربری تازه در مقیاسی قدیمی." },
    intro: {
      en: "Independent timber rooms preserve the legibility of the original brick shell.",
      fa: "اتاق‌های مستقل چوبی، خوانایی پوسته‌ی آجری موجود را حفظ می‌کنند.",
    },
    narrativeTitle: { en: "Repair before replacement.", fa: "ترمیم پیش از جایگزینی." },
    narrative: {
      en: "Every intervention is reversible and leaves the useful scars of the structure visible.",
      fa: "هر مداخله برگشت‌پذیر است و ردهای معنادار سازه را آشکار نگه می‌دارد.",
    },
    quote: {
      en: "The existing fabric is part of the collection.",
      fa: "بافت موجود بخشی از مجموعه است.",
    },
    materialTitle: { en: "Old brick, new timber", fa: "آجر قدیمی، چوب تازه" },
    material: {
      en: "A dry assembly keeps old and new distinct while allowing both to age together.",
      fa: "اتصال خشک، قدیم و جدید را متمایز نگه می‌دارد و در عین حال امکان پیرشدن مشترک را فراهم می‌کند.",
    },
    image: "/media/northline-atelier.png",
    imagePosition: "center",
    alt: {
      en: "Timber shelving in a deep shared work room",
      fa: "قفسه‌های چوبی در اتاقی مشترک و عمیق",
    },
  },
  {
    slug: "cedar-passage",
    title: { en: "Cedar Passage", fa: "گذر سرو" },
    category: "cultural",
    categoryLabel: categoryLabels.cultural,
    location: { en: "Shiraz", fa: "شیراز" },
    year: "2025",
    status: { en: "Competition", fa: "مسابقه" },
    area: { en: "1,240 m²", fa: "۱٬۲۴۰ مترمربع" },
    scope: { en: "Architecture · Landscape", fa: "معماری · منظر" },
    summary: {
      en: "A sequence of shaded civic rooms joining street, garden, and exhibition space.",
      fa: "توالی فضاهای عمومی سایه‌دار که خیابان، باغ و نمایشگاه را پیوند می‌دهد.",
    },
    introTitle: { en: "A building that begins as a path.", fa: "ساختمانی که از مسیر آغاز می‌شود." },
    intro: {
      en: "The public route remains visible from every room and extends the garden through the building.",
      fa: "مسیر عمومی از هر اتاق دیده می‌شود و باغ را درون ساختمان امتداد می‌دهد.",
    },
    narrativeTitle: { en: "Rooms without a front door.", fa: "اتاق‌هایی بدون در ورودی اصلی." },
    narrative: {
      en: "Multiple thresholds let the institution open gradually across the day.",
      fa: "آستانه‌های متعدد اجازه می‌دهند مجموعه در طول روز به‌تدریج گشوده شود.",
    },
    quote: { en: "The path is the first public room.", fa: "مسیر، نخستین اتاق عمومی است." },
    materialTitle: { en: "Shade and brick", fa: "سایه و آجر" },
    material: {
      en: "Deep brick screens filter sun while preserving a continuous civic edge.",
      fa: "مشبک‌های عمیق آجری، خورشید را فیلتر می‌کنند و لبه‌ای عمومی و پیوسته می‌سازند.",
    },
    image: "/media/voluma-mountain-house.png",
    imagePosition: "center",
    alt: {
      en: "Concrete threshold opening toward a distant landscape",
      fa: "آستانه‌ی بتنی رو به چشم‌اندازی دور",
    },
  },
  {
    slug: "common-ground",
    title: { en: "Common Ground", fa: "زمین مشترک" },
    category: "workspace",
    categoryLabel: categoryLabels.workspace,
    location: { en: "Karaj", fa: "کرج" },
    year: "2024",
    status: { en: "Completed", fa: "تکمیل‌شده" },
    area: { en: "940 m²", fa: "۹۴۰ مترمربع" },
    scope: { en: "Interior · Spatial strategy", fa: "معماری داخلی · راهبرد فضایی" },
    summary: {
      en: "A workplace organized around shared thresholds rather than assigned desks.",
      fa: "محیط کاری‌ای که به‌جای میزهای ثابت، پیرامون آستانه‌های مشترک سامان یافته است.",
    },
    introTitle: { en: "Work gathered around a shared middle.", fa: "کار پیرامون مرکزی مشترک." },
    intro: {
      en: "A continuous interior street supports informal meetings, focused rooms, and changing teams.",
      fa: "خیابانی داخلی و پیوسته، گفت‌وگوهای غیررسمی، اتاق‌های متمرکز و تیم‌های متغیر را پشتیبانی می‌کند.",
    },
    narrativeTitle: { en: "Structure as wayfinding.", fa: "سازه به‌مثابه‌ی مسیریابی." },
    narrative: {
      en: "Repeated timber bays make orientation intuitive without added visual noise.",
      fa: "دهانه‌های تکرارشونده‌ی چوبی، بدون افزودن اغتشاش بصری، جهت‌یابی را طبیعی می‌کنند.",
    },
    quote: {
      en: "Shared space should invite use, not prescribe it.",
      fa: "فضای مشترک باید دعوت‌کننده باشد، نه تجویزکننده.",
    },
    materialTitle: { en: "A frame that can change", fa: "قابی که می‌تواند تغییر کند" },
    material: {
      en: "Demountable timber frames support new rooms as the organization evolves.",
      fa: "قاب‌های چوبی بازشدنی، هم‌زمان با تغییر سازمان، اتاق‌های تازه را ممکن می‌کنند.",
    },
    image: "/media/material-shadow.png",
    imagePosition: "center",
    alt: {
      en: "Concrete bench and oak frame in afternoon light",
      fa: "نیمکت بتنی و قاب چوب بلوط در نور عصر",
    },
  },
];

export const siteCopy = {
  en: {
    menu: "Menu",
    closeMenu: "Close menu",
    switchLocale: "View this page in Persian",
    theme: { system: "System theme", light: "Light theme", dark: "Dark theme" },
    heroTitle: "Architecture for the life between walls.",
    heroBody: "We shape quiet, enduring places through light, material, and use.",
    heroCta: "Explore selected work",
    selectedProjects: "Selected projects",
    statementTitle: "We design for atmosphere, use, and time.",
    statementBody:
      "VOLUMA is an architecture and design practice working across homes, workplaces, and cultural spaces.",
    statementCta: "Discover the studio",
    expertiseTitle: "What we shape",
    expertise: ["Architecture", "Interior architecture", "Adaptive reuse", "Spatial strategy"],
    storyLabel: "Journal · Field notes",
    storyTitle: "Material as a memory of place",
    processTitle: "A clear path from first question to built form.",
    process: ["Listen", "Frame", "Develop", "Deliver"],
    journalTitle: "Latest from the journal",
    journal: [
      { title: "The room after noon", meta: "Essay · 6 min read" },
      { title: "Reading the existing fabric", meta: "Field notes · 4 min read" },
    ],
    ctaTitle: "Begin with a place, a question, or a possibility.",
    cta: "Start a conversation",
    descriptor: "Architecture & Design",
    location: "Tehran · Working internationally",
    privacy: "Privacy",
    copyright: "© 2026 VOLUMA",
    fixture:
      "Development preview: all project names, dates, locations, text, and imagery are representative fixtures and not published content.",
    archiveTitle: "Projects",
    archiveIntro: "Built work, interiors, and ongoing studies shaped by place and use.",
    searchPlaceholder: "Search projects",
    grid: "Grid",
    list: "List",
    result: "project",
    results: "projects",
    noResults: "No projects match this view.",
    clearFilters: "Clear filters",
    facts: {
      type: "Type",
      location: "Location",
      status: "Status",
      year: "Year",
      area: "Area",
      scope: "Scope",
    },
    backToProjects: "Back to projects",
    detailCaption: "Courtyard threshold · afternoon",
    materialCaption: "Board-marked concrete · detail",
    interiorCaption: "Oak frame · interior view",
    continueExploring: "Continue exploring",
    previousProject: "Previous project",
    nextProject: "Next project",
    openImage: "Open image in gallery",
    closeGallery: "Close gallery",
  },
  fa: {
    menu: "فهرست",
    closeMenu: "بستن فهرست",
    switchLocale: "مشاهده‌ی این صفحه به انگلیسی",
    theme: { system: "پوسته‌ی سیستم", light: "پوسته‌ی روشن", dark: "پوسته‌ی تیره" },
    heroTitle: "معماری برای زندگی میان دیوارها.",
    heroBody: "فضاهایی آرام و ماندگار را با نور، مصالح و شیوه‌ی زیستن شکل می‌دهیم.",
    heroCta: "مشاهده‌ی پروژه‌های منتخب",
    selectedProjects: "پروژه‌های منتخب",
    statementTitle: "برای کیفیت فضا، شیوه‌ی استفاده و گذر زمان طراحی می‌کنیم.",
    statementBody:
      "ولوما استودیوی معماری و طراحی است که روی خانه، محیط کار و فضاهای فرهنگی کار می‌کند.",
    statementCta: "آشنایی با استودیو",
    expertiseTitle: "آنچه شکل می‌دهیم",
    expertise: ["معماری", "معماری داخلی", "باززنده‌سازی", "راهبرد فضایی"],
    storyLabel: "یادداشت‌ها · از میدان",
    storyTitle: "مصالح به‌مثابه‌ی حافظه‌ی مکان",
    processTitle: "مسیری روشن از نخستین پرسش تا فضای ساخته‌شده.",
    process: ["شنیدن", "صورت‌بندی", "توسعه", "تحویل"],
    journalTitle: "تازه‌ترین یادداشت‌ها",
    journal: [
      { title: "اتاق پس از نیمروز", meta: "جستار · ۶ دقیقه" },
      { title: "خواندن بافت موجود", meta: "یادداشت میدانی · ۴ دقیقه" },
    ],
    ctaTitle: "با یک مکان، یک پرسش یا یک امکان آغاز کنیم.",
    cta: "گفت‌وگو را آغاز کنید",
    descriptor: "معماری و طراحی",
    location: "تهران · فعالیت بین‌المللی",
    privacy: "حریم خصوصی",
    copyright: "© ۲۰۲۶ VOLUMA",
    fixture:
      "پیش‌نمایش توسعه: همه‌ی نام‌ها، تاریخ‌ها، مکان‌ها، متن‌ها و تصاویر، داده‌های نمونه هستند و محتوای منتشرشده نیستند.",
    archiveTitle: "پروژه‌ها",
    archiveIntro:
      "آثار ساخته‌شده، فضاهای داخلی و مطالعات جاری؛ شکل‌گرفته با مکان و شیوه‌ی استفاده.",
    searchPlaceholder: "جست‌وجوی پروژه‌ها",
    grid: "شبکه",
    list: "فهرست",
    result: "پروژه",
    results: "پروژه",
    noResults: "پروژه‌ای با این مشخصات پیدا نشد.",
    clearFilters: "پاک‌کردن فیلترها",
    facts: {
      type: "نوع",
      location: "مکان",
      status: "وضعیت",
      year: "سال",
      area: "مساحت",
      scope: "دامنه",
    },
    backToProjects: "بازگشت به پروژه‌ها",
    detailCaption: "آستانه‌ی حیاط · بعدازظهر",
    materialCaption: "بتن قالب‌تخته‌ای · جزئیات",
    interiorCaption: "قاب بلوط · نمای داخلی",
    continueExploring: "ادامه‌ی مرور",
    previousProject: "پروژه‌ی قبلی",
    nextProject: "پروژه‌ی بعدی",
    openImage: "بازکردن تصویر در گالری",
    closeGallery: "بستن گالری",
  },
} as const;

export function getProject(slug: string): Project | undefined {
  return projects.find((project) => project.slug === slug);
}

export function localize(text: LocalizedText, locale: Locale): string {
  return text[locale];
}
