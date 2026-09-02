/**
 * Display language for the screens that show computed values.
 *
 * Two languages, not three. The chat has a third — Hinglish — because it is a
 * conversation and that is how these users talk; a table of tithis and degrees
 * has no Hinglish, only Devanagari or Latin.
 *
 * Every Sanskrit term the engine produces arrives from the backend in both
 * scripts (`rashi` / `rashi_hi`), so nothing here translates a *value*. This
 * file is the app's own words only, which is the line worth holding: a
 * translation table that starts guessing at nakshatra names is one that will
 * eventually disagree with the engine.
 */

export type DisplayLanguage = 'en' | 'hi';

/**
 * The app's destinations, as a key set rather than free strings.
 *
 * `src/destinations.ts` owns where each one goes; this owns what it is called.
 * A `Record` over this union is what makes a missing Hindi card a type error
 * rather than a card that quietly reads in English on a Hindi phone.
 */
export type HubKey =
  | 'today'
  | 'chart'
  | 'matching'
  | 'tarot'
  | 'chat'
  | 'history'
  | 'learn'
  | 'plans'
  | 'settings';

/**
 * The companion's name is shown as an attribution, never inside a sentence.
 *
 * "Priya says" has no neutral Hindi: कहती है is feminine, कहते हैं masculine,
 * and five of the fifteen companions are men. A label beside the portrait needs
 * no verb, so it needs no gender — and it reads better in English too.
 */

export const DISPLAY_LANGUAGES: { value: DisplayLanguage; label: string }[] = [
  { value: 'en', label: 'English' },
  { value: 'hi', label: 'हिंदी' },
];

type Strings = {
  // Shared
  tryAgain: string;
  unreachable: string;

  // Chart
  computing: string;
  chartFailed: string;
  yourChart: string;
  lagnaSuffix: (rashi: string) => string;
  moonLine: (rashi: string, nakshatra: string) => string;
  readInWords: string;
  currentPeriod: string;
  dashaLevels: [string, string, string];
  outsideCycle: string;
  grahas: string;
  houseLine: (house: number, nakshatra: string, pada: number) => string;
  retro: string;
  combust: string;
  panchangAtBirth: string;
  tithi: string;
  nakshatra: string;
  yoga: string;
  karana: string;
  vara: string;
  masa: string;
  samvat: string;
  samvatValue: (vikram: number, shaka: number) => string;
  sunriseSet: string;
  moonriseSet: string;
  absent: string;
  elapsed: (percent: string) => string;
  pada: (n: number) => string;
  ruledBy: (lord: string) => string;
  howComputed: string;
  ayanamsa: string;
  houseSystem: string;
  wholeSign: string;
  ephemeris: string;
  timezone: string;
  julianDay: string;
  determinismNote: string;

  // Messages left
  proNeeded: string;
  proNeededWhy: string;
  proNeededFree: string;
  upgrade: string;
  signInToAsk: string;
  signInToChat: string;
  signInToChatWhy: string;
  signInAction: string;
  crisisHeading: string;
  crisisHelplines: string;

  // Matching
  matching: string;
  matchingIntro: string;
  matchPartnerLabel: string;
  matchDate: string;
  matchTime: string;
  matchPlace: string;
  matchPlaceSearch: string;
  matchRun: string;
  matchAgain: string;
  matchScore: (total: string, maximum: number) => string;
  matchYou: string;
  matchThem: string;
  matchCaption: string;
  koots: Record<string, string>;

  // Tarot
  tarot: string;
  tarotIntro: string;
  tarotQuestionLabel: string;
  tarotQuestionPlaceholder: string;
  tarotDraw: string;
  tarotDrawAgain: string;
  tarotTurn: string;
  tarotUpright: string;
  tarotReversed: string;
  tarotRead: string;
  tarotReadCost: string;
  tarotReadingFailed: string;
  tarotUngrounded: string;
  tarotShuffle: (seed: string) => string;
  tarotSignIn: string;
  tarotSignInWhy: string;
  tarotDeckLink: string;
  tarotDeckTitle: string;
  tarotDeckIntro: string;
  tarotMajor: string;
  tarotAll: string;

  // Home
  today: string;
  cosmicVibe: string;
  greeting: (name: string) => string;
  greetingNoName: string;
  askAbout: (companion: string) => string;
  askAboutNoCompanion: string;
  tipUnavailable: string;
  tipAsk: string;
  panchangNow: string;
  sun: string;
  panchangPlaceNote: (place: string, timezone: string) => string;
  yourPeriod: string;
  againstBirth: string;
  moonThen: string;
  moonNow: string;
  janmaNakshatra: string;
  sharedSkyNote: string;
  yourBirthPlace: string;

  // Home — the welcome screen above the grid
  /**
   * The hero's own greeting, kept apart from `greeting` on purpose. Today
   * says hello because you have arrived on a particular day; the first
   * screenful welcomes you to the app itself, which is a different sentence
   * and would be wrong in either other place.
   */
  welcomeGreeting: (name: string) => string;
  welcomeGreetingNoName: string;
  welcomeTagline: string;
  welcomeScroll: string;

  // Home hub — the card grid the app opens on
  hubKicker: string;
  hub: Record<HubKey, { title: string; blurb: string }>;
  /**
   * What a card says once it knows something. Each one replaces the card's
   * blurb, and each one is allowed not to arrive: the blurb is what shows while
   * the chart is still loading, or when the phone is offline.
   *
   * `hubChatWith` names the companion the way the rest of the app does — beside
   * an imperative addressed to the reader, never as the subject of a verb, so
   * the Hindi needs no gender for a set of companions that is half men.
   */
  hubChartLagna: (rashi: string) => string;
  hubChatWith: (companion: string) => string;
  hubChapters: (done: number, total: number) => string;
};

const EN: Strings = {
  tryAgain: 'Try again',
  unreachable: 'Could not reach the server',

  computing: 'Computing positions…',
  chartFailed: 'Could not compute your chart',
  yourChart: 'Your chart',
  lagnaSuffix: (rashi) => `${rashi} lagna`,
  moonLine: (rashi, nakshatra) => `Moon in ${rashi} · ${nakshatra} nakshatra`,
  readInWords: 'Read my chart in words',
  currentPeriod: 'Current period',
  dashaLevels: ['Mahadasha', 'Antardasha', 'Pratyantardasha'],
  outsideCycle: 'Outside the computed 120-year cycle.',
  grahas: 'Grahas',
  houseLine: (house, nakshatra, pada) => `House ${house} · ${nakshatra} pada ${pada}`,
  retro: 'RETRO',
  combust: 'COMBUST',
  panchangAtBirth: 'Panchang at birth',
  tithi: 'Tithi',
  nakshatra: 'Nakshatra',
  yoga: 'Yoga',
  karana: 'Karana',
  vara: 'Vara',
  masa: 'Masa',
  samvat: 'Samvat',
  samvatValue: (vikram, shaka) => `Vikram ${vikram} · Shaka ${shaka}`,
  sunriseSet: 'Sunrise / set',
  moonriseSet: 'Moonrise / set',
  absent: '—',
  elapsed: (percent) => `${percent}% elapsed`,
  pada: (n) => `Pada ${n}`,
  ruledBy: (lord) => `Ruled by ${lord}`,
  howComputed: 'How this was computed',
  ayanamsa: 'Ayanamsa',
  houseSystem: 'House system',
  wholeSign: 'whole-sign',
  ephemeris: 'Ephemeris',
  timezone: 'Timezone',
  julianDay: 'Julian day (UT)',
  determinismNote:
    'Every value above is arithmetic from your birth moment. Same input, same output, always.',

  proNeeded: 'This part needs Enuma Sky Pro',
  proNeededWhy:
    'Pro covers every reading and every question, with no daily count to watch. Weekly, monthly or yearly \u2014 cancel whenever you like.',
  proNeededFree:
    'Your chart, your dashas, the panchang, matching and the card draw stay free, and always will.',
  upgrade: 'See plans',
  signInToAsk: 'Sign in again to keep asking.',
  signInToChat: 'Chat needs an account',
  signInToChatWhy:
    'Your conversations are kept in your account, and so is your subscription. Everything else in the app works without one.',
  signInAction: 'Sign in or create an account',
  crisisHeading: 'Please talk to someone who can help',
  crisisHelplines:
    'India, distress or thoughts of suicide: Tele-MANAS 14416 (free, 24\u00d77) or AASRA +91-9820466726.\nViolence at home: Women Helpline 181, or 112 if you are in danger now.',

  matching: 'Matching',
  matchingIntro:
    'Ashtakoot Milan scores two janma nakshatras across eight categories. The arithmetic is below in full, so you can check every point.',
  matchPartnerLabel: 'The other person\u2019s birth',
  matchDate: 'Date of birth',
  matchTime: 'Time of birth',
  matchPlace: 'Place of birth',
  matchPlaceSearch: 'Search a city',
  matchRun: 'Compute the eight koots',
  matchAgain: 'Change these details',
  matchScore: (total, maximum) => `${total} of ${maximum}`,
  matchYou: 'You',
  matchThem: 'Them',
  matchCaption:
    'A score out of 36 is not a fact about two people. It is what this procedure returns, shown in full so it cannot be used on you as a number you did not see the working for.',
  koots: {
    varna: 'Varna',
    vashya: 'Vashya',
    tara: 'Tara',
    yoni: 'Yoni',
    graha_maitri: 'Graha Maitri',
    gana: 'Gana',
    bhakoot: 'Bhakoot',
    nadi: 'Nadi',
  },

  tarot: 'Tarot',
  tarotIntro:
    'Three cards: where you are, what is in the way, and what you could do about it.',
  tarotQuestionLabel: 'What is on your mind?',
  tarotQuestionPlaceholder: 'Optional \u2014 the cards are dealt either way',
  tarotDraw: 'Shuffle and draw',
  tarotDrawAgain: 'Shuffle again',
  tarotTurn: 'Tap each card to turn it over',
  tarotUpright: 'UPRIGHT',
  tarotReversed: 'REVERSED',
  tarotRead: 'Read the three together',
  tarotReadCost: 'Reading the spread together needs Pro. Turning the cards over is free and stays that way.',
  tarotReadingFailed: 'The reading could not be written just now.',
  tarotUngrounded:
    'This reading named a card that was not dealt. Shown anyway, and flagged rather than quietly dropped.',
  tarotShuffle: (seed) => `Shuffle ${seed}`,
  tarotSignIn: 'A written reading needs an account',
  tarotSignInWhy:
    'The cards and their meanings are free and work signed out. Only having the three read together counts against your messages.',
  tarotDeckLink: 'All 78 cards',
  tarotDeckTitle: 'The deck',
  tarotDeckIntro:
    'Every card, upright and reversed, written out. Nothing here is generated \u2014 the same words for everyone, every day.',
  tarotMajor: 'Major arcana',
  tarotAll: 'All',

  today: 'Today',
  cosmicVibe: 'Cosmic vibe for today',
  greeting: (name) => `Hello, ${name}`,
  greetingNoName: 'Hello',
  askAbout: (companion) => `Ask ${companion} about today`,
  askAboutNoCompanion: 'Ask about today',
  tipUnavailable: "Today's line could not be written.",
  tipAsk: 'Write today\u2019s line',
  panchangNow: 'Panchang now',
  sun: 'Sun',
  panchangPlaceNote: (place, timezone) =>
    `Computed for ${place} (${timezone}). A panchang belongs to a moment and a place, not to a person.`,
  yourPeriod: 'Your period',
  againstBirth: 'Against your birth',
  moonThen: 'Moon then',
  moonNow: 'Moon now',
  janmaNakshatra: 'Janma nakshatra',
  sharedSkyNote:
    'The sky above is the same for everyone alive right now. Only the second column is yours.',
  yourBirthPlace: 'your birth place',

  // Says what the app does in the order it does it — the arithmetic first,
  // because that is the part that cannot be wrong, and the words second.
  welcomeGreeting: (name) => `Welcome, ${name}`,
  welcomeGreetingNoName: 'Welcome',
  welcomeTagline: 'Your sky at birth, worked out exactly. Then said plainly.',
  welcomeScroll: 'Scroll',

  hubKicker: 'Where to?',
  // Titles match the sidebar exactly — the sidebar reads them from here, so a
  // card and the row that leads to the same screen cannot end up named
  // differently. The blurb says what the screen gives you, not what it is.
  hub: {
    today: { title: 'Today', blurb: 'Panchang for this moment, and a line from your companion.' },
    chart: { title: 'Chart', blurb: 'Your kundli, the grahas and the dasha running now.' },
    matching: { title: 'Matching', blurb: 'Two charts, koot by koot.' },
    tarot: { title: 'Tarot', blurb: 'Three cards on your question.' },
    chat: { title: 'Chat', blurb: 'Ask anything about your chart.' },
    history: { title: 'History', blurb: 'Everything you have asked, kept with your account.' },
    learn: { title: 'Learn', blurb: 'Jyotisha, from the ground up.' },
    plans: { title: 'Pro', blurb: 'Readings, questions and tarot, uncounted.' },
    settings: { title: 'Settings', blurb: 'Birth details, language, account and sync.' },
  },
  hubChartLagna: (rashi) => `Your ${rashi} lagna`,
  hubChatWith: (companion) => `Talk to ${companion}`,
  hubChapters: (done, total) => `${done} of ${total} chapters`,
};

const HI: Strings = {
  tryAgain: 'फिर कोशिश करें',
  unreachable: 'सर्वर तक नहीं पहुँच सके',

  computing: 'स्थितियाँ गिनी जा रही हैं…',
  chartFailed: 'आपकी कुंडली नहीं बन सकी',
  yourChart: 'आपकी कुंडली',
  lagnaSuffix: (rashi) => `${rashi} लग्न`,
  moonLine: (rashi, nakshatra) => `चंद्रमा ${rashi} में · ${nakshatra} नक्षत्र`,
  readInWords: 'मेरी कुंडली शब्दों में पढ़िए',
  currentPeriod: 'चल रही दशा',
  dashaLevels: ['महादशा', 'अंतर्दशा', 'प्रत्यंतर्दशा'],
  outsideCycle: 'गणना किए गए 120 वर्ष के चक्र से बाहर।',
  grahas: 'ग्रह',
  houseLine: (house, nakshatra, pada) => `भाव ${house} · ${nakshatra} पाद ${pada}`,
  retro: 'वक्री',
  combust: 'अस्त',
  panchangAtBirth: 'जन्म का पंचांग',
  tithi: 'तिथि',
  nakshatra: 'नक्षत्र',
  yoga: 'योग',
  karana: 'करण',
  vara: 'वार',
  masa: 'मास',
  samvat: 'संवत',
  samvatValue: (vikram, shaka) => `विक्रम ${vikram} · शक ${shaka}`,
  sunriseSet: 'सूर्योदय / अस्त',
  moonriseSet: 'चंद्रोदय / अस्त',
  absent: '—',
  elapsed: (percent) => `${percent}% बीत चुकी`,
  pada: (n) => `पाद ${n}`,
  ruledBy: (lord) => `स्वामी ${lord}`,
  howComputed: 'यह कैसे गिना गया',
  ayanamsa: 'अयनांश',
  houseSystem: 'भाव पद्धति',
  wholeSign: 'पूर्ण राशि',
  ephemeris: 'ग्रहगणित',
  timezone: 'समय क्षेत्र',
  julianDay: 'जूलियन दिन (UT)',
  determinismNote:
    'ऊपर का हर मान आपके जन्म-क्षण से निकला गणित है। वही जानकारी, वही परिणाम, हर बार।',

  proNeeded: 'इसके लिए Enuma Sky Pro चाहिए',
  proNeededWhy:
    'Pro में हर पाठ और हर सवाल शामिल है, गिनती रखने की ज़रूरत नहीं। साप्ताहिक, मासिक या वार्षिक — जब चाहें बंद कर दीजिए।',
  proNeededFree:
    'आपकी कुंडली, दशाएँ, पंचांग, मिलान और कार्ड निकालना — ये मुफ़्त हैं और रहेंगे।',
  upgrade: 'योजनाएँ देखिए',
  signInToAsk: 'पूछते रहने के लिए दोबारा साइन इन कीजिए।',
  signInToChat: 'बातचीत के लिए खाता चाहिए',
  signInToChatWhy:
    'आपकी बातचीत आपके खाते में रहती है, और आपकी सदस्यता भी वहीं जुड़ी होती है। ऐप का बाक़ी सब बिना खाते के चलता है।',
  signInAction: 'साइन इन कीजिए या खाता बनाइए',
  crisisHeading: 'किसी से बात कीजिए जो मदद कर सके',
  crisisHelplines:
    'भारत — मन की परेशानी या आत्महत्या के विचार: टेली-मानस 14416 (मुफ़्त, 24×7) या आसरा +91-9820466726।\nघर में हिंसा: महिला हेल्पलाइन 181, या तुरंत ख़तरे में 112।',

  matching: 'मिलान',
  matchingIntro:
    'अष्टकूट मिलान दो जन्म नक्षत्रों को आठ कूटों में अंक देता है। पूरा गणित नीचे है, ताकि आप हर अंक ख़ुद जाँच सकें।',
  matchPartnerLabel: 'दूसरे व्यक्ति का जन्म',
  matchDate: 'जन्म तिथि',
  matchTime: 'जन्म समय',
  matchPlace: 'जन्म स्थान',
  matchPlaceSearch: 'शहर खोजिए',
  matchRun: 'आठों कूट गिनिए',
  matchAgain: 'ये विवरण बदलिए',
  matchScore: (total, maximum) => `${maximum} में से ${total}`,
  matchYou: 'आप',
  matchThem: 'वे',
  matchCaption:
    '36 में से मिला अंक दो व्यक्तियों के बारे में तथ्य नहीं है। यह बस इस विधि का परिणाम है, पूरा दिखाया हुआ — ताकि कोई इसे आप पर ऐसी संख्या की तरह न चला सके जिसका हिसाब आपने देखा ही न हो।',
  koots: {
    varna: 'वर्ण',
    vashya: 'वश्य',
    tara: 'तारा',
    yoni: 'योनि',
    graha_maitri: 'ग्रह मैत्री',
    gana: 'गण',
    bhakoot: 'भकूट',
    nadi: 'नाड़ी',
  },

  tarot: 'टैरो',
  tarotIntro: 'तीन कार्ड: आप कहाँ हैं, रास्ते में क्या है, और आप क्या कर सकते हैं।',
  tarotQuestionLabel: 'मन में क्या है?',
  tarotQuestionPlaceholder: 'ज़रूरी नहीं \u2014 कार्ड वैसे भी निकलेंगे',
  tarotDraw: 'फेंटिए और कार्ड निकालिए',
  tarotDrawAgain: 'दोबारा फेंटिए',
  tarotTurn: 'हर कार्ड को पलटने के लिए उस पर छुइए',
  tarotUpright: 'सीधा',
  tarotReversed: 'उल्टा',
  tarotRead: 'तीनों को एक साथ पढ़वाइए',
  tarotReadCost: 'तीनों कार्ड को साथ पढ़ने के लिए Pro चाहिए। कार्ड पलटना मुफ़्त है और रहेगा।',
  tarotReadingFailed: 'अभी पाठ नहीं लिखा जा सका।',
  tarotUngrounded:
    'इस पाठ में कोई ऐसा कार्ड आ गया जो निकला ही नहीं था। छुपाया नहीं गया — दिखाकर बता दिया गया है।',
  tarotShuffle: (seed) => `फेंट ${seed}`,
  tarotSignIn: 'लिखा हुआ पाठ पाने के लिए खाता चाहिए',
  tarotSignInWhy:
    'कार्ड और उनके अर्थ मुफ़्त हैं, बिना खाते के भी चलते हैं। सिर्फ़ तीनों को एक साथ पढ़वाना आपके संदेशों में गिना जाता है।',
  tarotDeckLink: 'सभी 78 कार्ड',
  tarotDeckTitle: 'पूरी गड्डी',
  tarotDeckIntro:
    'हर कार्ड, सीधा और उल्टा, लिखा हुआ। यहाँ कुछ भी बनाया नहीं जाता — सबके लिए वही शब्द, हर दिन।',
  tarotMajor: 'महा अर्चना',
  tarotAll: 'सभी',

  today: 'आज',
  cosmicVibe: 'आज का मिज़ाज',
  greeting: (name) => `नमस्ते, ${name}`,
  greetingNoName: 'नमस्ते',
  askAbout: (companion) => `${companion} से आज के बारे में पूछिए`,
  askAboutNoCompanion: 'आज के बारे में पूछिए',
  tipUnavailable: 'आज की बात नहीं लिखी जा सकी।',
  tipAsk: 'आज की बात लिखवाइए',
  panchangNow: 'अभी का पंचांग',
  sun: 'सूर्य',
  panchangPlaceNote: (place, timezone) =>
    `${place} (${timezone}) के लिए गिना गया। पंचांग किसी क्षण और स्थान का होता है, व्यक्ति का नहीं।`,
  yourPeriod: 'आपकी दशा',
  againstBirth: 'जन्म से मिलान',
  moonThen: 'जन्म का चंद्रमा',
  moonNow: 'अभी का चंद्रमा',
  janmaNakshatra: 'जन्म नक्षत्र',
  sharedSkyNote:
    'ऊपर का आकाश इस समय जीवित हर व्यक्ति के लिए एक ही है। सिर्फ़ दूसरी पंक्ति आपकी है।',
  yourBirthPlace: 'आपके जन्मस्थान',

  welcomeGreeting: (name) => `स्वागत है, ${name}`,
  welcomeGreetingNoName: 'स्वागत है',
  welcomeTagline: 'जन्म का आपका आकाश, ठीक-ठीक गिना हुआ। फिर सरल भाषा में कहा हुआ।',
  welcomeScroll: 'नीचे चलिए',

  hubKicker: 'कहाँ चलें?',
  hub: {
    today: { title: 'आज', blurb: 'इस समय का पंचांग, और आपके साथी की एक पंक्ति।' },
    chart: { title: 'कुंडली', blurb: 'आपकी कुंडली, ग्रह और चल रही दशा।' },
    matching: { title: 'मिलान', blurb: 'दो कुंडलियाँ, कूट दर कूट।' },
    tarot: { title: 'टैरो', blurb: 'आपके सवाल पर तीन पत्ते।' },
    chat: { title: 'बातचीत', blurb: 'कुंडली के बारे में कुछ भी पूछिए।' },
    history: { title: 'इतिहास', blurb: 'आपके पूछे हुए सब सवाल, खाते के साथ सुरक्षित।' },
    learn: { title: 'सीखिए', blurb: 'ज्योतिष, बिलकुल शुरू से।' },
    plans: { title: 'प्रो', blurb: 'रीडिंग, सवाल और टैरो — बिना गिनती के।' },
    settings: { title: 'सेटिंग', blurb: 'जन्म विवरण, भाषा, खाता और सिंक।' },
  },
  hubChartLagna: (rashi) => `आपकी ${rashi} लग्न`,
  hubChatWith: (companion) => `${companion} से बात कीजिए`,
  hubChapters: (done, total) => `${total} में से ${done} अध्याय`,
};

export function strings(language: DisplayLanguage): Strings {
  return language === 'hi' ? HI : EN;
}

/**
 * The chat's three languages folded into the two these strings come in.
 *
 * Hinglish takes the English set. It is written in Roman script by people who
 * read English chrome without noticing it — and a third set of UI strings that
 * differed from the English one only in tone would be three things to keep in
 * step for no gain. The *conversation* stays Hinglish; only the labels around
 * it are English.
 */
export function chromeFor(language: 'en' | 'hi' | 'hinglish'): Strings {
  return strings(language === 'hi' ? 'hi' : 'en');
}

/**
 * A rise or set instant as a wall clock, or a dash when there was none.
 *
 * The dash is the point. A body that does not rise on a given day has no time,
 * and printing a plausible one instead would be exactly the invented number
 * this app exists not to print.
 */
export function clockTime(
  iso: string | null,
  language: DisplayLanguage,
  absent: string,
  timeZone?: string,
): string {
  if (!iso) return absent;

  // 24-hour, deliberately. Hermes on Android has no Hindi am/pm, so a 12-hour
  // clock printed "6:36 am" in Latin inside an otherwise Devanagari card — and
  // an almanac is a table of times, where 17:19 is what belongs anyway.
  const clock: Intl.DateTimeFormatOptions = {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  };

  // The zone is the *place's*, not the phone's. These instants are sunrise and
  // sunset at a set of coordinates, and the device's own zone is only the same
  // one while the reader is standing there. Someone in Toronto reading a chart
  // cast for Patna was shown a sunrise ten and a half hours out — a number this
  // app computed exactly and then printed against the wrong clock.
  //
  // Guarded because the zone comes off the wire and `Intl` throws on one it
  // does not know; the device's clock is a worse answer than the right one and
  // a better one than a blank screen.
  if (timeZone) {
    try {
      return new Date(iso).toLocaleTimeString(localeFor(language), { ...clock, timeZone });
    } catch {
      // Falls through to the device's zone.
    }
  }

  return new Date(iso).toLocaleTimeString(localeFor(language), clock);
}

/**
 * A rise and a set, as two facts about one day rather than one span.
 *
 * The arrow this started as was quietly wrong. Rise and set are found inside
 * one local day independently, and the Moon's set usually belongs to the rise
 * *before* it — a Moon that rose at 14:54 sets at 00:05 the following morning,
 * so the set listed against today is the tail of yesterday's rise. An arrow
 * claims a span that never happened. The row's label carries the order instead,
 * and the two times sit side by side as what they are: two separate events that
 * both fell on this date.
 */
export function riseSet(
  rise: string | null,
  set: string | null,
  language: DisplayLanguage,
  absent: string,
  timeZone?: string,
): string {
  return (
    `${clockTime(rise, language, absent, timeZone)}` +
    `  ·  ${clockTime(set, language, absent, timeZone)}`
  );
}

/**
 * The date, in the reader's script.
 *
 * `hi-IN` rather than the device locale: someone reading the app in Hindi asked
 * for Hindi, and their phone may well be set to English.
 */
export function localeFor(language: DisplayLanguage): string {
  return language === 'hi' ? 'hi-IN' : 'en-IN';
}
