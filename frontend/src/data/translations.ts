import type { LanguageCode } from "../types";

type TranslationKey =
  | "appName"
  | "tagline"
  | "newConsultation"
  | "history"
  | "topics"
  | "askPlaceholder"
  | "send"
  | "sourcesUsed"
  | "viewSource"
  | "regimeFilter"
  | "welcomeHeading"
  | "welcomeBody"
  | "confidenceHigh"
  | "confidenceMedium"
  | "confidenceLow"
  | "disclaimer";

type TranslationMap = Record<TranslationKey, string>;

export const TRANSLATIONS: Partial<Record<LanguageCode, TranslationMap>> = {
  en: {
    appName: "IP-SAKTI Sahayak",
    tagline: "IP & regulatory guidance for Ayurveda, with cited sources",
    newConsultation: "New consultation",
    history: "Past consultations",
    topics: "Common questions",
    askPlaceholder: "Ask about a patent, GI, trademark, or compliance question…",
    send: "Ask",
    sourcesUsed: "Sources",
    viewSource: "Open source",
    regimeFilter: "Filter by regime",
    welcomeHeading: "Ask a question grounded in law, not guesswork",
    welcomeBody:
      "IP-SAKTI Sahayak answers questions on patents, trademarks, geographical indications, and traditional-knowledge protection for Ayurveda, across Indian and international regimes — every answer cites the provision or registry it comes from.",
    confidenceHigh: "Well-supported",
    confidenceMedium: "Partially supported",
    confidenceLow: "Limited evidence",
    disclaimer:
      "Informational guidance only, not a substitute for advice from a registered patent or trademark agent.",
  },
  hi: {
    appName: "आईपी-शक्ति सहायक",
    tagline: "आयुर्वेद के लिए बौद्धिक संपदा और नियामक मार्गदर्शन, स्रोत-सहित",
    newConsultation: "नई परामर्श",
    history: "पिछली परामर्श",
    topics: "सामान्य प्रश्न",
    askPlaceholder: "पेटेंट, जीआई, ट्रेडमार्क या अनुपालन से जुड़ा प्रश्न पूछें…",
    send: "पूछें",
    sourcesUsed: "स्रोत",
    viewSource: "स्रोत खोलें",
    regimeFilter: "व्यवस्था द्वारा फ़िल्टर करें",
    welcomeHeading: "कानून पर आधारित प्रश्न पूछें, अटकल पर नहीं",
    welcomeBody:
      "आईपी-शक्ति सहायक आयुर्वेद से जुड़े पेटेंट, ट्रेडमार्क, भौगोलिक संकेत और पारंपरिक ज्ञान संरक्षण से जुड़े प्रश्नों के उत्तर भारतीय व अंतरराष्ट्रीय व्यवस्थाओं के अनुसार देता है — हर उत्तर अपने स्रोत के साथ।",
    confidenceHigh: "सुस्थापित",
    confidenceMedium: "आंशिक रूप से समर्थित",
    confidenceLow: "सीमित प्रमाण",
    disclaimer:
      "केवल सूचनात्मक मार्गदर्शन; पंजीकृत पेटेंट या ट्रेडमार्क एजेंट की सलाह का विकल्प नहीं।",
  },
};

export function t(lang: LanguageCode, key: TranslationKey): string {
  return TRANSLATIONS[lang]?.[key] ?? TRANSLATIONS.en![key];
}
