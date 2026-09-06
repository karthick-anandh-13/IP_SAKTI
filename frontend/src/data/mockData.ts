import type {
  Conversation,
  LanguageOption,
  RegimeMeta,
  TopicSuggestion,
} from "../types";

export const LANGUAGES: LanguageOption[] = [
  { code: "en", label: "English", nativeLabel: "English" },
  { code: "hi", label: "Hindi", nativeLabel: "हिन्दी" },
  { code: "sa", label: "Sanskrit", nativeLabel: "संस्कृतम्" },
  { code: "ta", label: "Tamil", nativeLabel: "தமிழ்" },
  { code: "te", label: "Telugu", nativeLabel: "తెలుగు" },
  { code: "kn", label: "Kannada", nativeLabel: "ಕನ್ನಡ" },
  { code: "ml", label: "Malayalam", nativeLabel: "മലയാളം" },
];

export const REGIMES: RegimeMeta[] = [
  { id: "patents", label: "Patents", shortLabel: "Patents" },
  { id: "trademarks", label: "Trademarks", shortLabel: "Marks" },
  {
    id: "geographical-indications",
    label: "Geographical Indications",
    shortLabel: "GI",
  },
  {
    id: "traditional-knowledge",
    label: "Traditional Knowledge (TKDL)",
    shortLabel: "TK",
  },
  {
    id: "international",
    label: "International Regimes",
    shortLabel: "Global",
  },
];

export const TOPIC_SUGGESTIONS: TopicSuggestion[] = [
  {
    id: "t1",
    label: "Can I patent a classical Ayurvedic formulation?",
    regime: "patents",
    prompt: "Can I patent a classical Ayurvedic formulation described in the Charaka Samhita?",
  },
  {
    id: "t2",
    label: "GI protection for a regional herbal product",
    regime: "geographical-indications",
    prompt: "What is the process to register a regional herbal product under India's GI Act?",
  },
  {
    id: "t3",
    label: "How does TKDL prevent biopiracy?",
    regime: "traditional-knowledge",
    prompt: "How does the Traditional Knowledge Digital Library prevent biopiracy of Ayurvedic knowledge?",
  },
  {
    id: "t4",
    label: "Trademarking an Ayurvedic brand name",
    regime: "trademarks",
    prompt: "What should I check before trademarking a Sanskrit-derived brand name for an Ayurvedic product?",
  },
  {
    id: "t5",
    label: "Nagoya Protocol & export compliance",
    regime: "international",
    prompt: "What Nagoya Protocol obligations apply when exporting a formulation derived from a wild Indian herb?",
  },
];

export const SAMPLE_CONVERSATION: Conversation = {
  id: "c1",
  title: "Patentability of a classical Ayurvedic formulation",
  updatedAt: new Date().toISOString(),
  messages: [
    {
      id: "m1",
      role: "user",
      language: "en",
      content:
        "Can I patent a classical Ayurvedic formulation described in the Charaka Samhita?",
      createdAt: new Date(Date.now() - 1000 * 60 * 4).toISOString(),
    },
    {
      id: "m2",
      role: "assistant",
      language: "en",
      confidence: "high",
      regimes: ["patents", "traditional-knowledge"],
      content:
        "Generally, no. Section 3(p) of the Indian Patents Act, 1970 excludes an invention that is, in effect, traditional knowledge, or an aggregation or duplication of known properties of traditionally known components [1]. A formulation drawn directly from the Charaka Samhita would typically be treated as prior art already in the public domain, and is also indexed in the Traditional Knowledge Digital Library, which patent examiners in India, the EPO, and the USPTO consult during prior-art search [2]. A patent may still be available for a genuinely novel and inventive step layered on top of the classical base — for example a new extraction process, a new delivery mechanism, or a synergistic combination with a non-traditional ingredient that produces an unexpected effect [3]. That inventive layer, not the classical formulation itself, would be the subject of the claim.",
      sources: [
        {
          id: "s1",
          title: "The Patents Act, 1970 — Section 3(p)",
          authority: "Office of the Controller General of Patents, Designs & Trade Marks",
          citation: "Patents Act 1970, s.3(p)",
          jurisdiction: "India",
          regime: "patents",
          url: "https://ipindia.gov.in/writereaddata/Portal/IPOAct/1_31_1_patent-act-1970-11march2015.pdf",
          excerpt:
            "An invention which, in effect, is traditional knowledge or which is an aggregation or duplication of known properties of traditionally known component or components is not patentable.",
        },
        {
          id: "s2",
          title: "Traditional Knowledge Digital Library — Access & Use Policy",
          authority: "CSIR & Ministry of AYUSH",
          citation: "TKDL Access Policy, cl. 4.2",
          jurisdiction: "India",
          regime: "traditional-knowledge",
          url: "https://www.tkdl.res.in/",
          excerpt:
            "TKDL is provided to patent offices under access agreements to serve as prior-art evidence during substantive examination of applications relating to traditional medicine systems.",
        },
        {
          id: "s3",
          title: "Guidelines for Examination of Patent Applications relating to Traditional Knowledge",
          authority: "Indian Patent Office",
          citation: "IPO TK Examination Guidelines, para 5.3",
          jurisdiction: "India",
          regime: "patents",
          excerpt:
            "Claims directed to a novel process of preparation, a new use, or a synergistic combination that yields a result not obvious from the traditional formulation may be considered for patentability on their own merits.",
        },
      ],
      createdAt: new Date(Date.now() - 1000 * 60 * 3).toISOString(),
    },
  ],
};
