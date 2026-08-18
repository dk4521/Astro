"""The course: thirty chapters, in English and Hindi.

Prose, not code. It lives here rather than in the mobile bundle for three
reasons: the app stays small, a correction ships without an app release, and the
personalised line at the end of each chapter is computed by the same engine that
draws the chart — see `personalise.py`.

House style, worth keeping:

- **Positions are measurements.** Nothing here predicts, ranks a chart, or warns.
- **Say what the app actually does.** The conventions taught are this engine's —
  whole-sign houses, Lahiri, the mean node, a 365.25-day Vimshottari year — so a
  reader who finishes can check the arithmetic themselves.
- **Hindi is not a translation afterthought.** It is written, not rendered, and
  it is the version most of this market will read.
"""

from __future__ import annotations

from . import personalise as P
from .models import Chapter, Section

PART_FOUNDATIONS = {"en": "Foundations", "hi": "बुनियाद"}
PART_GRAHAS = {"en": "The grahas", "hi": "ग्रह"}
PART_HOUSES = {"en": "Houses", "hi": "भाव"}
PART_NAKSHATRAS = {"en": "Nakshatras", "hi": "नक्षत्र"}
PART_TIME = {"en": "Time", "hi": "काल"}
PART_PRACTICE = {"en": "Practice", "hi": "व्यवहार"}

_FOUNDATIONS: tuple[Chapter, ...] = (
    Chapter(
        slug="what-a-chart-is",
        part=PART_FOUNDATIONS,
        title={"en": "What a chart actually is", "hi": "कुंडली असल में है क्या"},
        summary={
            "en": "A record of the sky, from one spot on Earth, at one second.",
            "hi": "एक क्षण का आकाश, पृथ्वी की एक जगह से देखा हुआ।",
        },
        minutes=4,
        level="basic",
        sections=(
            Section(
                heading={"en": "A position, not a prophecy", "hi": "स्थिति, भविष्यवाणी नहीं"},
                body=(
                    {
                        "en": "A birth chart records where the Sun, Moon and planets were at a particular moment, seen from a particular place. That is the entire raw material. Everything else — the meanings, the traditions, the disagreements between schools — is interpretation laid on top of that measurement.",
                        "hi": "जन्म कुंडली इतना भर दर्ज करती है कि एक ख़ास क्षण में, एक ख़ास जगह से देखने पर सूर्य, चंद्रमा और ग्रह कहाँ थे। कच्चा माल बस यही है। बाक़ी सब — अर्थ, परंपराएँ, अलग-अलग मतों के झगड़े — उसी माप के ऊपर रखी गई व्याख्या है।",
                    },
                    {
                        "en": "This distinction is why this app exists. The positions are astronomy and can be checked against an observatory. The meanings are a tradition, and traditions can be argued with. An app that blurs the two can tell you anything and call it fact.",
                        "hi": "यही फ़र्क़ इस ऐप की वजह है। स्थितियाँ खगोल विज्ञान हैं और वेधशाला से मिलाई जा सकती हैं। अर्थ परंपरा हैं, और परंपरा से बहस हो सकती है। जो ऐप दोनों को घोल देती है वह कुछ भी कहकर उसे तथ्य कह सकती है।",
                    },
                ),
            ),
            Section(
                heading={"en": "What the tradition adds", "hi": "परंपरा क्या जोड़ती है"},
                body=(
                    {
                        "en": "Jyotisha takes those positions and reads them as a vocabulary: this graha in that sign, in that house, during that period. The vocabulary is old, internally consistent, and useful to many people as a mirror. None of that makes it a mechanism of cause.",
                        "hi": "ज्योतिष उन स्थितियों को एक शब्दावली की तरह पढ़ता है: यह ग्रह उस राशि में, उस भाव में, उस काल में। यह शब्दावली पुरानी है, अपने भीतर संगत है, और बहुतों को आईने की तरह काम आती है। इससे वह कारण-तंत्र नहीं बन जाती।",
                    },
                    {
                        "en": "Keeping the two layers separate is what lets you use the tradition without being ruled by it. You can find a reading useful and still know it is a reading.",
                        "hi": "दोनों परतों को अलग रखना ही आपको परंपरा का उपयोग करने देता है, उसके अधीन हुए बिना। कोई व्याख्या उपयोगी लग सकती है, और फिर भी यह जानना बना रह सकता है कि वह व्याख्या ही है।",
                    },
                ),
            ),
        ),
        personalise=P.birth_moment,
    ),
    Chapter(
        slug="twelve-rashis",
        part=PART_FOUNDATIONS,
        title={"en": "The twelve rashis", "hi": "बारह राशियाँ"},
        summary={
            "en": "Twelve equal 30° slices — a coordinate system, not twelve personality types.",
            "hi": "तीस-तीस अंश के बारह बराबर हिस्से — एक निर्देशांक व्यवस्था, बारह स्वभाव नहीं।",
        },
        minutes=5,
        level="basic",
        sections=(
            Section(
                heading={"en": "Twelve equal slices", "hi": "बारह बराबर हिस्से"},
                body=(
                    {
                        "en": "The band of sky the planets travel through is divided into twelve equal parts of 30 degrees. In order: Mesha, Vrishabha, Mithuna, Karka, Simha, Kanya, Tula, Vrishchika, Dhanu, Makara, Kumbha, Meena.",
                        "hi": "जिस पट्टी में ग्रह चलते हैं उसे तीस-तीस अंश के बारह बराबर हिस्सों में बाँटा गया है। क्रम से: मेष, वृषभ, मिथुन, कर्क, सिंह, कन्या, तुला, वृश्चिक, धनु, मकर, कुंभ, मीन।",
                    },
                    {
                        "en": "Saying \"the Moon is in Karka\" means the Moon fell somewhere in the fourth slice. That is a coordinate, in the same sense as a latitude — and like a latitude, it is either right or wrong, not a matter of opinion.",
                        "hi": "\"चंद्रमा कर्क में है\" का अर्थ है कि चंद्रमा चौथे हिस्से में कहीं पड़ा। यह एक निर्देशांक है, ठीक वैसे जैसे अक्षांश — और अक्षांश की तरह यह या तो सही होता है या ग़लत, राय का विषय नहीं।",
                    },
                ),
            ),
            Section(
                heading={"en": "What a rashi is said to carry", "hi": "राशि किसका संकेत मानी जाती है"},
                body=(
                    {
                        "en": "Each rashi has a ruling graha, an element (fire, earth, air, water) and a modality (movable, fixed, dual). Tula is ruled by Venus, is an air sign, and is movable. These are the tradition's words for an emphasis, a texture.",
                        "hi": "हर राशि का एक स्वामी ग्रह है, एक तत्व (अग्नि, पृथ्वी, वायु, जल) और एक स्वभाव (चर, स्थिर, द्विस्वभाव)। तुला का स्वामी शुक्र है, वह वायु राशि है और चर है। ये परंपरा के शब्द हैं किसी झुकाव या बनावट के लिए।",
                    },
                    {
                        "en": "They are not a diagnosis. Nobody is \"a Taurus\" the way they are left-handed. A rashi says where a body was, and what the tradition reads into that.",
                        "hi": "यह निदान नहीं है। कोई \"वृषभ का\" उस तरह नहीं होता जैसे कोई बाएँ हाथ का होता है। राशि बताती है कि पिंड कहाँ था, और परंपरा उसमें क्या पढ़ती है।",
                    },
                ),
            ),
        ),
        personalise=P.moon_rashi,
    ),
    Chapter(
        slug="ayanamsa",
        part=PART_FOUNDATIONS,
        title={"en": "Sidereal and tropical", "hi": "निरयन और सायन"},
        summary={
            "en": "Why your Indian sign is usually one earlier than the magazine's.",
            "hi": "आपकी भारतीय राशि पत्रिका वाली से एक पीछे क्यों होती है।",
        },
        minutes=5,
        level="basic",
        sections=(
            Section(
                heading={"en": "Two zero points", "hi": "दो शून्य-बिंदु"},
                body=(
                    {
                        "en": "Western astrology measures from the spring equinox. Vedic astrology measures against the fixed stars. The two agreed around the fifth century CE and have drifted apart ever since, because the Earth wobbles slowly on its axis — one full wobble takes about 26,000 years.",
                        "hi": "पाश्चात्य ज्योतिष वसंत विषुव से नापता है। वैदिक ज्योतिष स्थिर तारों से। दोनों लगभग पाँचवीं सदी में एक थे और तब से अलग होते जा रहे हैं, क्योंकि पृथ्वी अपनी धुरी पर धीरे-धीरे डोलती है — एक पूरा चक्कर क़रीब 26,000 वर्ष का।",
                    },
                    {
                        "en": "That drift is now about 24 degrees, which is most of a sign. It is why your sign in an Indian panchang is usually one earlier than in a Western magazine. Neither is wrong; they measure from different zeros.",
                        "hi": "यह अंतर अब क़रीब 24 अंश है, यानी लगभग पूरी एक राशि। इसी से भारतीय पंचांग में आपकी राशि पाश्चात्य पत्रिका से प्रायः एक पीछे होती है। दोनों में कोई ग़लत नहीं; दोनों अलग शून्य से नापते हैं।",
                    },
                ),
                aside={
                    "en": "The correction is called the ayanamsa. This app uses Lahiri (Chitrapaksha), the Government of India standard, and reports the exact value it used with every chart.",
                    "hi": "इस सुधार को अयनांश कहते हैं। यह ऐप लाहिड़ी (चित्रपक्ष) इस्तेमाल करती है, जो भारत सरकार का मानक है, और हर कुंडली के साथ उसका ठीक मान बताती है।",
                },
            ),
        ),
        personalise=P.ayanamsa,
    ),
    Chapter(
        slug="the-lagna",
        part=PART_FOUNDATIONS,
        title={"en": "The lagna", "hi": "लग्न"},
        summary={
            "en": "The anchor. Every house in your chart is counted from it.",
            "hi": "आधार। कुंडली का हर भाव इसी से गिना जाता है।",
        },
        minutes=6,
        level="basic",
        sections=(
            Section(
                heading={"en": "The rising point", "hi": "उदय होता बिंदु"},
                body=(
                    {
                        "en": "The lagna, or ascendant, is the degree of the zodiac climbing over the eastern horizon at the moment of birth. It is not a planet. It is where two things intersect: the path of the planets, and the horizon of your birth place.",
                        "hi": "लग्न, या उदय-बिंदु, राशिचक्र का वह अंश है जो जन्म के क्षण पूर्वी क्षितिज पर चढ़ रहा होता है। यह ग्रह नहीं है। यह दो चीज़ों का कटान है: ग्रहों का मार्ग, और आपके जन्मस्थान का क्षितिज।",
                    },
                ),
            ),
            Section(
                heading={"en": "The same instant, two horizons", "hi": "एक ही क्षण, दो क्षितिज"},
                body=(
                    {
                        "en": "Two children born at the same instant in Chennai and Delhi have identical planetary positions — the planets do not care where you stand. Their lagnas differ, because the horizon they were born under is tilted differently. The place also fixes the timezone, including the historical offsets countries have changed over the decades.",
                        "hi": "एक ही क्षण में चेन्नई और दिल्ली में जन्मे दो बच्चों की ग्रह-स्थितियाँ बिल्कुल एक होंगी — ग्रहों को इससे मतलब नहीं कि आप कहाँ खड़े हैं। पर लग्न अलग होगा, क्योंकि जिस क्षितिज के नीचे वे जन्मे उसका झुकाव अलग है। स्थान से समय-क्षेत्र भी तय होता है, उन पुराने बदलावों समेत जो देश दशकों में करते रहे हैं।",
                    },
                    {
                        "en": "The Earth turns a full circle every day, so the rising point moves a whole sign roughly every two hours. Get the birth time wrong by two hours and every house in the chart shifts by one. Nothing computed afterwards survives that.",
                        "hi": "पृथ्वी रोज़ पूरा चक्कर लगाती है, इसलिए उदय-बिंदु लगभग हर दो घंटे में एक पूरी राशि सरक जाता है। जन्म समय दो घंटे ग़लत हुआ तो कुंडली का हर भाव एक खिसक जाता है। उसके बाद की कोई गणना नहीं बचती।",
                    },
                ),
                aside={
                    "en": "This is why the app asks for exact clock time and a city, and refuses to guess either.",
                    "hi": "इसीलिए ऐप घड़ी का सही समय और शहर माँगती है, और दोनों में से किसी का अंदाज़ा नहीं लगाती।",
                },
            ),
            Section(
                heading={"en": "Why it is the anchor", "hi": "यह आधार क्यों है"},
                body=(
                    {
                        "en": "Houses are counted from the lagna, so the lagna decides which area of life every graha lands in. Two people born the same day with different lagnas have the same planets in the same signs and completely different charts.",
                        "hi": "भाव लग्न से गिने जाते हैं, इसलिए लग्न ही तय करता है कि हर ग्रह जीवन के किस क्षेत्र में पड़ेगा। एक ही दिन जन्मे दो लोग, लग्न अलग हों तो ग्रह वही राशियों में वही — और कुंडलियाँ बिल्कुल अलग।",
                    },
                    {
                        "en": "This is also why the lagna is the first thing any reading states. Change it and everything downstream changes with it.",
                        "hi": "इसीलिए कोई भी व्याख्या सबसे पहले लग्न बताती है। वह बदले तो उसके बाद का सब कुछ बदल जाता है।",
                    },
                ),
                aside={
                    "en": "A birth time recalled as \"around 7\" is the largest single source of wrong charts. If yours is uncertain, treat house-based statements with more caution than sign-based ones.",
                    "hi": "\"क़रीब सात बजे\" जैसा याद किया हुआ समय ग़लत कुंडलियों का सबसे बड़ा कारण है। आपका समय अनिश्चित हो तो भाव पर टिकी बातों को राशि पर टिकी बातों से ज़्यादा सावधानी से लें।",
                },
            ),
        ),
        personalise=P.lagna_speed,
    ),
    Chapter(
        slug="reading-the-diagram",
        part=PART_FOUNDATIONS,
        title={"en": "Reading a North Indian chart", "hi": "उत्तर भारतीय कुंडली पढ़ना"},
        summary={
            "en": "The numbers in the boxes are rashis, not houses. Everyone trips on this once.",
            "hi": "खानों में लिखे अंक राशियाँ हैं, भाव नहीं। यहाँ हर कोई एक बार ठोकर खाता है।",
        },
        minutes=4,
        level="basic",
        sections=(
            Section(
                heading={"en": "Fixed houses, moving signs", "hi": "भाव स्थिर, राशियाँ चलती"},
                body=(
                    {
                        "en": "In the diamond-shaped North Indian chart, the house positions are fixed on the page. The top-centre diamond is always the 1st house, and the number written inside it tells you which rashi occupies it.",
                        "hi": "हीरे जैसी उत्तर भारतीय कुंडली में भाव कागज़ पर स्थिर रहते हैं। ऊपर बीच का खाना हमेशा पहला भाव होता है, और उसमें लिखा अंक बताता है कि उसमें कौन सी राशि है।",
                    },
                    {
                        "en": "So the numbers move from chart to chart while the boxes stay put. The South Indian chart does the opposite: signs are fixed on the page and the lagna is marked.",
                        "hi": "यानी अंक हर कुंडली में बदलते हैं, खाने वहीं रहते हैं। दक्षिण भारतीय कुंडली उल्टा करती है: राशियाँ कागज़ पर स्थिर रहती हैं और लग्न पर निशान लगता है।",
                    },
                ),
            ),
        ),
        personalise=P.graha_positions,
    ),
)


_GRAHAS: tuple[Chapter, ...] = (
    Chapter(
        slug="nine-grahas",
        part=PART_GRAHAS,
        title={"en": 'The nine grahas', "hi": 'नौ ग्रह'},
        summary={"en": 'Seven visible bodies and two points where orbits cross.', "hi": 'सात दिखने वाले पिंड और दो बिंदु जहाँ कक्षाएँ कटती हैं।'},
        minutes=5,
        level="basic",
        sections=(
            Section(
                heading={"en": 'Why the list stops at Saturn', "hi": 'सूची शनि पर क्यों रुकती है'},
                body=(
                    {"en": 'Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn. These are the bodies visible to the naked eye, which is exactly why the list ends where it does — the tradition was built by people watching the sky without lenses.', "hi": 'सूर्य, चंद्र, मंगल, बुध, गुरु, शुक्र, शनि। ये नंगी आँख से दिखने वाले पिंड हैं, और सूची यहीं ख़त्म होने का कारण भी यही है — यह परंपरा बिना दूरबीन के आकाश देखने वालों ने बनाई थी।'},
                    {"en": 'Uranus, Neptune and Pluto are not used in classical Vedic astrology. They were found after the system was complete, and it has no slot for them.', "hi": 'शास्त्रीय वैदिक ज्योतिष में यूरेनस, नेपच्यून और प्लूटो का उपयोग नहीं होता। वे व्यवस्था बन जाने के बाद खोजे गए, और उसमें उनके लिए जगह नहीं है।'},
                ),
            ),
            Section(
                heading={"en": 'What “graha” means', "hi": '“ग्रह” का अर्थ'},
                body=(
                    {"en": 'The Sanskrit word means “one that seizes” or “holds”, not “planet”. That is why the Sun and Moon, which are not planets, and Rahu and Ketu, which are not objects at all, sit comfortably in the same list. The category is about what the tradition watches.', "hi": 'संस्कृत शब्द का अर्थ है “जो पकड़ता है”, “ग्रह” यानी planet नहीं। इसीलिए सूर्य और चंद्र, जो ग्रह नहीं हैं, और राहु-केतु, जो पिंड ही नहीं हैं, एक ही सूची में सहज बैठ जाते हैं। यह श्रेणी इस बारे में है कि परंपरा किसे देखती है।'},
                ),
            ),
        ),
        personalise=P.graha_positions,
    ),
    Chapter(
        slug="sun-and-moon",
        part=PART_GRAHAS,
        title={"en": 'Sun and Moon', "hi": 'सूर्य और चंद्र'},
        summary={"en": 'The two lights, and the distance between them that names the day.', "hi": 'दो प्रकाश, और उनके बीच की दूरी जो दिन का नाम रखती है।'},
        minutes=5,
        level="basic",
        sections=(
            Section(
                heading={"en": 'The two lights', "hi": 'दो प्रकाश'},
                body=(
                    {"en": 'The Sun and Moon are called the luminaries. The tradition reads the Sun as the steady self and the Moon as the moving mind — the part of you that changes with the week. In Indian practice the Moon matters more than the Sun, which is why you are asked for your rashi and not your sun sign.', "hi": 'सूर्य और चंद्र को ज्योतिर्पिंड कहा जाता है। परंपरा सूर्य को स्थिर आत्म और चंद्र को चलायमान मन की तरह पढ़ती है — वह हिस्सा जो हफ़्ते के साथ बदलता है। भारतीय व्यवहार में चंद्रमा सूर्य से ज़्यादा मायने रखता है, इसीलिए आपसे राशि पूछी जाती है, सूर्य-राशि नहीं।'},
                ),
            ),
            Section(
                heading={"en": 'The gap between them', "hi": 'उनके बीच की दूरी'},
                body=(
                    {"en": 'The angle between Sun and Moon is the single most used number in the Indian calendar. Every 12 degrees of it is one tithi; 180 degrees is a full moon; zero is a new moon. The whole festival calendar rests on that one measurement.', "hi": 'सूर्य और चंद्र के बीच का कोण भारतीय पंचांग की सबसे ज़्यादा इस्तेमाल होने वाली संख्या है। उसके हर 12 अंश की एक तिथि; 180 अंश पर पूर्णिमा; शून्य पर अमावस्या। पूरा त्योहार-पंचांग इसी एक माप पर टिका है।'},
                ),
            ),
        ),
        personalise=P.luminaries,
    ),
    Chapter(
        slug="mars-and-mercury",
        part=PART_GRAHAS,
        title={"en": 'Mars and Mercury', "hi": 'मंगल और बुध'},
        summary={"en": 'The fast inner pair, and the manglik business.', "hi": 'तेज़ चलने वाली भीतरी जोड़ी, और मांगलिक का धंधा।'},
        minutes=5,
        level="basic",
        sections=(
            Section(
                heading={"en": 'Mars', "hi": 'मंगल'},
                body=(
                    {"en": 'Mars is read as drive, edge and the will to act. It is also the graha with the worst reputation in popular practice, because of manglik dosha — a configuration that has become a product sold to frighten families, particularly about women and marriage.', "hi": 'मंगल को गति, धार और करने की इच्छा के रूप में पढ़ा जाता है। लोकप्रिय व्यवहार में सबसे बदनाम ग्रह भी यही है, मांगलिक दोष की वजह से — एक स्थिति जो अब परिवारों को डराने का सामान बन चुकी है, ख़ासकर स्त्रियों और विवाह को लेकर।'},
                    {"en": 'The configuration is computable and real. The claim that it causes a specific misfortune, and that a payment removes it, is neither.', "hi": 'वह स्थिति गणनीय है और असली है। यह दावा कि उससे कोई ख़ास दुर्भाग्य आता है, और कि पैसा देकर वह हट जाता है — वह न गणनीय है न असली।'},
                ),
                aside={"en": 'Chapter 30 returns to this. It is the clearest example of a real measurement turned into a lever.', "hi": 'अध्याय 30 इस पर लौटता है। असली माप को दबाव के औज़ार में बदलने का यह सबसे साफ़ उदाहरण है।'},
            ),
            Section(
                heading={"en": 'Mercury', "hi": 'बुध'},
                body=(
                    {"en": 'Mercury never strays far from the Sun — it is the innermost planet, so from Earth it always appears close to it. That is why Mercury is combust more often than any other graha, and why the tradition ties it to speech, exchange and calculation.', "hi": 'बुध सूर्य से कभी दूर नहीं जाता — वह सबसे भीतरी ग्रह है, इसलिए पृथ्वी से हमेशा सूर्य के पास ही दिखता है। इसी से बुध बाक़ी सब ग्रहों से ज़्यादा बार अस्त होता है, और इसी से परंपरा उसे वाणी, विनिमय और गणना से जोड़ती है।'},
                ),
            ),
        ),
        personalise=P.mars_mercury,
    ),
    Chapter(
        slug="jupiter-and-venus",
        part=PART_GRAHAS,
        title={"en": 'Jupiter and Venus', "hi": 'गुरु और शुक्र'},
        summary={"en": 'The two the tradition calls benefics — and what that word does not mean.', "hi": 'परंपरा जिन्हें शुभ कहती है — और उस शब्द का अर्थ क्या नहीं है।'},
        minutes=5,
        level="basic",
        sections=(
            Section(
                heading={"en": 'Benefic is not a promise', "hi": 'शुभ का अर्थ आश्वासन नहीं'},
                body=(
                    {"en": 'Jupiter and Venus are classed as benefics: Jupiter as expansion and counsel, Venus as pleasure, art and partnership. The word means the tradition reads their emphasis as easy rather than abrasive. It does not mean their periods are pleasant or their placements lucky.', "hi": 'गुरु और शुक्र शुभ ग्रह माने जाते हैं: गुरु विस्तार और परामर्श, शुक्र सुख, कला और साहचर्य। इस शब्द का अर्थ इतना है कि परंपरा उनके ज़ोर को कठोर के बजाय सहज पढ़ती है। इसका अर्थ यह नहीं कि उनकी दशाएँ सुखद होती हैं या उनका स्थान भाग्यशाली।'},
                ),
            ),
            Section(
                heading={"en": "Jupiter's twelve years", "hi": 'गुरु के बारह वर्ष'},
                body=(
                    {"en": 'Jupiter takes about twelve years to go round the zodiac, so it spends roughly a year in each sign. That is slow enough that a whole generation shares a placement, which is a useful reminder of what a chart can and cannot single you out for.', "hi": 'गुरु राशिचक्र का चक्कर क़रीब बारह वर्ष में पूरा करता है, यानी हर राशि में लगभग एक वर्ष। यह इतना धीमा है कि एक पूरी पीढ़ी एक ही स्थिति साझा करती है — यह याद दिलाने के लिए उपयोगी बात है कि कुंडली किस चीज़ में आपको अलग कर सकती है और किसमें नहीं।'},
                ),
            ),
        ),
        personalise=P.jupiter_venus,
    ),
    Chapter(
        slug="saturn",
        part=PART_GRAHAS,
        title={"en": 'Saturn', "hi": 'शनि'},
        summary={"en": 'The slowest visible graha, and the most feared — mostly by marketing.', "hi": 'दिखने वालों में सबसे धीमा, और सबसे डरा हुआ नाम — ज़्यादातर विज्ञापन की वजह से।'},
        minutes=5,
        level="basic",
        sections=(
            Section(
                heading={"en": 'Thirty years, two and a half per sign', "hi": 'तीस वर्ष, ढाई प्रति राशि'},
                body=(
                    {"en": 'Saturn takes about 29.5 years to circle the zodiac, so it sits in each sign for roughly two and a half years. Sade sati — the famous seven-and-a-half-year stretch — is simply Saturn transiting the sign before your Moon, the sign of your Moon, and the one after.', "hi": 'शनि राशिचक्र लगभग 29.5 वर्ष में पूरा करता है, यानी हर राशि में क़रीब ढाई वर्ष। साढ़ेसाती — वह प्रसिद्ध साढ़े सात वर्ष — बस इतना है कि शनि आपकी चंद्र-राशि से पहले वाली, चंद्र-राशि, और उसके बाद वाली राशि से गुज़रता है।'},
                    {"en": 'It happens to everyone, roughly three times in a long life, on a fixed schedule anyone can compute. Nothing about it is a personal judgement, and nothing about it needs to be bought off.', "hi": 'यह सबके साथ होता है, लंबे जीवन में क़रीब तीन बार, एक तय समय-सारणी पर जिसे कोई भी गिन सकता है। इसमें कुछ भी व्यक्तिगत फ़ैसला नहीं है, और कुछ भी ऐसा नहीं जिसे पैसे से टाला जाना हो।'},
                ),
                aside={"en": 'If an app or an astrologer introduces sade sati with a countdown and a remedy price, you are being sold something. The dates are arithmetic; they are free.', "hi": 'अगर कोई ऐप या ज्योतिषी साढ़ेसाती के साथ उलटी गिनती और उपाय का दाम लेकर आए, तो आपको कुछ बेचा जा रहा है। तिथियाँ गणित हैं; वे मुफ़्त हैं।'},
            ),
        ),
        personalise=P.saturn,
    ),
    Chapter(
        slug="rahu-and-ketu",
        part=PART_GRAHAS,
        title={"en": 'Rahu and Ketu', "hi": 'राहु और केतु'},
        summary={"en": 'Two points where orbits cross — not objects, and always exactly opposite.', "hi": 'दो बिंदु जहाँ कक्षाएँ कटती हैं — पिंड नहीं, और सदा ठीक आमने-सामने।'},
        minutes=6,
        level="intermediate",
        sections=(
            Section(
                heading={"en": 'Where the eclipse comes from', "hi": 'ग्रहण कहाँ से आता है'},
                body=(
                    {"en": "The Moon's orbit is tilted about five degrees against the Sun's apparent path. The two points where they cross are Rahu and Ketu. There is nothing there to see. When the Moon happens to be at one of them at new or full moon, you get an eclipse — which is why the tradition describes them as swallowing the lights.", "hi": 'चंद्रमा की कक्षा सूर्य के आभासी मार्ग से क़रीब पाँच अंश झुकी है। जहाँ दोनों कटते हैं, वे दो बिंदु राहु और केतु हैं। वहाँ देखने को कुछ नहीं है। जब अमावस्या या पूर्णिमा पर चंद्रमा उन्हीं में से किसी बिंदु पर हो, तब ग्रहण होता है — इसीलिए परंपरा कहती है कि वे प्रकाश को निगल लेते हैं।'},
                    {"en": 'They are always exactly 180 degrees apart, because they are two ends of one line. This engine computes Rahu and derives Ketu as its exact opposite; it never calculates them separately, because they cannot disagree.', "hi": 'वे हमेशा ठीक 180 अंश दूर रहते हैं, क्योंकि वे एक ही रेखा के दो सिरे हैं। यह engine राहु गिनता है और केतु उसका ठीक उल्टा निकालता है; उन्हें अलग-अलग कभी नहीं गिनता, क्योंकि उनमें मतभेद हो ही नहीं सकता।'},
                ),
                aside={"en": 'They always move backwards through the zodiac, so your chart marks them retrograde. That is their normal state, not an anomaly.', "hi": 'वे राशिचक्र में सदा पीछे की ओर चलते हैं, इसलिए कुंडली उन्हें वक्री दिखाती है। यह उनकी सामान्य दशा है, कोई विचलन नहीं।'},
            ),
            Section(
                heading={"en": 'Mean and true', "hi": 'मध्यम और स्पष्ट'},
                body=(
                    {"en": 'There are two conventions: the mean node, a smooth average, and the true node, which wobbles. They differ by a few arc-minutes. This engine uses the mean node, the mainstream Indian convention — and states so, because two apps using different conventions will disagree slightly and neither is lying.', "hi": 'दो परिपाटियाँ हैं: मध्यम राहु, जो सहज औसत है, और स्पष्ट राहु, जो डोलता है। दोनों में कुछ कला का अंतर होता है। यह engine मध्यम राहु इस्तेमाल करता है, जो मुख्यधारा की भारतीय परिपाटी है — और यह बताता भी है, क्योंकि अलग परिपाटी वाली दो ऐप्स में थोड़ा अंतर आएगा और उनमें से कोई झूठ नहीं बोल रहा।'},
                ),
            ),
        ),
        personalise=P.nodes,
    ),
    Chapter(
        slug="retrograde-combust",
        part=PART_GRAHAS,
        title={"en": 'Retrograde and combustion', "hi": 'वक्री और अस्त'},
        summary={"en": 'Two states with real astronomy behind them, and a lot of fear attached.', "hi": 'दो स्थितियाँ, जिनके पीछे असली खगोल है और ऊपर बहुत सारा डर।'},
        minutes=5,
        level="intermediate",
        sections=(
            Section(
                heading={"en": 'Retrograde is a trick of perspective', "hi": 'वक्री होना नज़र का खेल है'},
                body=(
                    {"en": 'A retrograde planet is not moving backwards. We watch from a moving platform: as Earth overtakes an outer planet on the inside track, that planet appears to loop backwards against the stars for a few weeks, then resume. It is the same illusion as a slower car sliding backwards as you pass it.', "hi": 'वक्री ग्रह पीछे नहीं चल रहा होता। हम एक चलते मंच से देख रहे हैं: जब पृथ्वी भीतरी रास्ते से किसी बाहरी ग्रह को पार करती है, तो वह ग्रह कुछ हफ़्तों के लिए तारों के सापेक्ष पीछे लौटता दिखता है, फिर आगे बढ़ जाता है। यह वही भ्रम है जो धीमी गाड़ी को पार करते समय उसके पीछे खिसकने का होता है।'},
                    {"en": 'Nothing about the planet changes. What changes is our viewing angle.', "hi": 'ग्रह में कुछ नहीं बदलता। बदलता है हमारा देखने का कोण।'},
                ),
            ),
            Section(
                heading={"en": 'Combustion is proximity', "hi": 'अस्त होना निकटता है'},
                body=(
                    {"en": 'A graha is combust when it sits close enough to the Sun to be lost in its glare — invisible to an observer. The threshold differs by graha and by school; it is a statement about visibility, not damage.', "hi": 'ग्रह तब अस्त कहलाता है जब वह सूर्य के इतने पास हो कि उसकी चमक में खो जाए — देखने वाले को दिखे नहीं। सीमा हर ग्रह और हर मत में अलग है; यह दिखाई देने की बात है, हानि की नहीं।'},
                ),
                aside={"en": 'The tradition does read these as an emphasis turned inward, working out of sight. That is a long way from harm, and this app will not frame it as harm.', "hi": 'परंपरा इन्हें भीतर की ओर मुड़े ज़ोर की तरह ज़रूर पढ़ती है — कुछ जो नज़र से दूर चल रहा है। यह हानि से बहुत दूर है, और यह ऐप इसे हानि की तरह नहीं कहेगी।'},
            ),
        ),
        personalise=P.marked_grahas,
    ),
)


_HOUSES_AND_NAKSHATRAS: tuple[Chapter, ...] = (
    Chapter(
        slug="what-houses-are",
        part=PART_HOUSES,
        title={"en": 'What houses are', "hi": 'भाव क्या हैं'},
        summary={"en": 'Rashis divide the sky. Houses divide life.', "hi": 'राशियाँ आकाश बाँटती हैं। भाव जीवन बाँटते हैं।'},
        minutes=5,
        level="intermediate",
        sections=(
            Section(
                heading={"en": 'Counted from the lagna', "hi": 'लग्न से गिने हुए'},
                body=(
                    {"en": 'The 1st house is you — body, temperament, how you arrive in a room. The 4th is home and inner ground, the 7th partnership, the 10th work and public role. The others fill in the rest of a life.', "hi": 'पहला भाव आप हैं — देह, स्वभाव, कमरे में आपके आने का ढंग। चौथा घर और भीतरी ज़मीन, सातवाँ साथ, दसवाँ काम और सार्वजनिक भूमिका। बाक़ी भाव जीवन का शेष भरते हैं।'},
                    {"en": 'They are counted from the lagna. If your lagna is Vrishabha, then Vrishabha is your 1st house, Mithuna your 2nd, and so on around the circle.', "hi": 'ये लग्न से गिने जाते हैं। लग्न वृषभ है तो वृषभ आपका पहला भाव, मिथुन दूसरा, और इसी क्रम में पूरा चक्र।'},
                ),
            ),
        ),
        personalise=P.houses_from_lagna,
    ),
    Chapter(
        slug="whole-sign",
        part=PART_HOUSES,
        title={"en": 'Whole-sign houses', "hi": 'पूर्ण-राशि भाव'},
        summary={"en": 'One house is exactly one rashi. Why this app uses the oldest system.', "hi": 'एक भाव यानी ठीक एक राशि। यह ऐप सबसे पुरानी पद्धति क्यों इस्तेमाल करती है।'},
        minutes=5,
        level="intermediate",
        sections=(
            Section(
                heading={"en": 'Systems that disagree', "hi": 'आपस में असहमत पद्धतियाँ'},
                body=(
                    {"en": 'There are several ways to draw house boundaries, and they give different answers. This app uses whole-sign houses: one house is exactly one rashi, no more and no less. It is the oldest system and the standard in both North and South Indian practice.', "hi": 'भाव की सीमाएँ खींचने के कई तरीक़े हैं, और वे अलग-अलग उत्तर देते हैं। यह ऐप पूर्ण-राशि भाव इस्तेमाल करती है: एक भाव ठीक एक राशि, न कम न ज़्यादा। यह सबसे पुरानी पद्धति है और उत्तर व दक्षिण, दोनों भारतीय परंपराओं का मानक।'},
                    {"en": 'The practical effect is that a graha never straddles two houses. Systems that split houses by degree can put the same graha in a different house — one reason two apps can disagree about the same birth.', "hi": 'इसका व्यावहारिक असर यह है कि कोई ग्रह दो भावों में नहीं बँटता। अंश से भाव काटने वाली पद्धतियाँ उसी ग्रह को दूसरे भाव में डाल सकती हैं — दो ऐप्स एक ही जन्म पर असहमत क्यों होती हैं, यह उसका एक कारण है।'},
                ),
                aside={"en": 'When an app shows a house number without saying which system produced it, the number is not checkable. Yours reports whole-sign, every time.', "hi": 'जब कोई ऐप भाव-क्रमांक दिखाए पर यह न बताए कि किस पद्धति से, तो वह अंक जाँचा नहीं जा सकता। आपकी ऐप हर बार पूर्ण-राशि बताती है।'},
            ),
        ),
        personalise=P.houses_from_lagna,
    ),
    Chapter(
        slug="kendra-trikona",
        part=PART_HOUSES,
        title={"en": 'Kendras and trikonas', "hi": 'केंद्र और त्रिकोण'},
        summary={"en": "The two groupings that carry most of the tradition's weight.", "hi": 'दो समूह जिन पर परंपरा का अधिकांश भार टिका है।'},
        minutes=5,
        level="intermediate",
        sections=(
            Section(
                heading={"en": 'Angles and trines', "hi": 'केंद्र और त्रिकोण'},
                body=(
                    {"en": 'Houses 1, 4, 7 and 10 are the kendras — the angles, read as the structure of a life. Houses 1, 5 and 9 are the trikonas, read as its sustaining thread. The 1st belongs to both, which is why it carries so much.', "hi": 'पहला, चौथा, सातवाँ और दसवाँ भाव केंद्र हैं — जीवन का ढाँचा माने जाते हैं। पहला, पाँचवाँ और नवाँ त्रिकोण हैं, जिन्हें उसका सहारा माना जाता है। पहला भाव दोनों में आता है, इसीलिए उस पर सबसे ज़्यादा भार है।'},
                    {"en": 'Houses 6, 8 and 12 are called dusthanas, the difficult ones. It is worth saying plainly: that label describes friction, effort and things worked out privately. It is not a sentence, and grahas there are not damaged.', "hi": 'छठा, आठवाँ और बारहवाँ दुःस्थान कहलाते हैं, कठिन भाव। साफ़ कहना ज़रूरी है: यह नाम घर्षण, श्रम और एकांत में सुलझने वाली बातों का वर्णन है। यह दंड नहीं है, और वहाँ बैठे ग्रह क्षतिग्रस्त नहीं होते।'},
                ),
            ),
        ),
        personalise=P.kendra_trikona,
    ),
    Chapter(
        slug="houses-one-to-six",
        part=PART_HOUSES,
        title={"en": 'Houses 1 to 6', "hi": 'पहला से छठा भाव'},
        summary={"en": 'Body, resources, effort, roots, mind, friction.', "hi": 'देह, संसाधन, प्रयास, जड़ें, मन, घर्षण।'},
        minutes=6,
        level="intermediate",
        sections=(
            Section(
                heading={"en": 'The first six', "hi": 'पहले छह'},
                body=(
                    {"en": '1st: the body and the self as it appears. 2nd: what you hold — money, family, speech. 3rd: effort, hands, siblings, short journeys. 4th: home, mother, the ground under you. 5th: mind, creativity, children, what you make. 6th: work, service, illness, conflict — the friction of daily life.', "hi": 'पहला: देह और जैसा आप दिखते हैं। दूसरा: जो आप संजोते हैं — धन, कुटुंब, वाणी। तीसरा: प्रयास, हाथ, भाई-बहन, छोटी यात्राएँ। चौथा: घर, माता, आपके नीचे की ज़मीन। पाँचवाँ: मन, सृजन, संतान, जो आप रचते हैं। छठा: काम, सेवा, रोग, संघर्ष — रोज़मर्रा का घर्षण।'},
                    {"en": "These are areas, not outcomes. A graha in the 6th does not mean illness; it means the tradition reads that graha's emphasis as playing out in the region of work, service and friction.", "hi": 'ये क्षेत्र हैं, परिणाम नहीं। छठे में बैठा ग्रह रोग नहीं बताता; वह इतना बताता है कि परंपरा उस ग्रह के ज़ोर को काम, सेवा और घर्षण के इलाक़े में पढ़ती है।'},
                ),
            ),
        ),
        personalise=P.busiest_house,
    ),
    Chapter(
        slug="houses-seven-to-twelve",
        part=PART_HOUSES,
        title={"en": 'Houses 7 to 12', "hi": 'सातवाँ से बारहवाँ भाव'},
        summary={"en": 'Partnership, change, meaning, work, gain, retreat.', "hi": 'साथ, परिवर्तन, अर्थ, कर्म, लाभ, एकांत।'},
        minutes=6,
        level="intermediate",
        sections=(
            Section(
                heading={"en": 'The second six', "hi": 'अगले छह'},
                body=(
                    {"en": '7th: partnership, contracts, the other person. 8th: change, inheritance, what is hidden. 9th: meaning, teachers, long journeys, belief. 10th: work and public role. 11th: gains, networks, what comes back. 12th: retreat, sleep, foreign places, expense.', "hi": 'सातवाँ: साथ, अनुबंध, दूसरा व्यक्ति। आठवाँ: परिवर्तन, उत्तराधिकार, जो छिपा है। नवाँ: अर्थ, गुरु, लंबी यात्राएँ, आस्था। दसवाँ: कर्म और सार्वजनिक भूमिका। ग्यारहवाँ: लाभ, संपर्क, जो लौटकर आता है। बारहवाँ: एकांत, निद्रा, विदेश, व्यय।'},
                    {"en": 'Notice how the pairs sit opposite: 1 and 7 (self and other), 4 and 10 (private ground and public role), 6 and 12 (daily friction and withdrawal). The circle is built from those tensions.', "hi": 'ध्यान दें कि जोड़े आमने-सामने बैठते हैं: 1 और 7 (स्वयं और अन्य), 4 और 10 (निजी ज़मीन और सार्वजनिक भूमिका), 6 और 12 (रोज़ का घर्षण और विरति)। चक्र इन्हीं तनावों से बना है।'},
                ),
            ),
        ),
        personalise=P.busiest_house,
    ),
    Chapter(
        slug="house-lords",
        part=PART_HOUSES,
        title={"en": 'House lords', "hi": 'भावेश'},
        summary={"en": 'How an empty house still gets read.', "hi": 'खाली भाव भी कैसे पढ़ा जाता है।'},
        minutes=5,
        level="intermediate",
        sections=(
            Section(
                heading={"en": 'Nine grahas, twelve houses', "hi": 'नौ ग्रह, बारह भाव'},
                body=(
                    {"en": 'Most houses in most charts are empty — nine grahas cannot fill twelve houses. An empty house is not a blank. It is read through its lord: the graha that rules the sign occupying it, and wherever that graha happens to sit.', "hi": 'ज़्यादातर कुंडलियों में ज़्यादातर भाव खाली होते हैं — नौ ग्रह बारह भाव नहीं भर सकते। खाली भाव कोरा नहीं होता। उसे उसके स्वामी से पढ़ा जाता है: वह ग्रह जो उस भाव में पड़ी राशि का स्वामी है, और वह जहाँ भी बैठा हो।'},
                    {"en": "This is why a reading can say something about your 7th house when nothing is in it. The link runs: house → its sign → that sign's lord → where the lord sits.", "hi": 'इसीलिए कोई व्याख्या आपके सातवें भाव पर कुछ कह पाती है जबकि उसमें कुछ है ही नहीं। कड़ी ऐसे चलती है: भाव → उसकी राशि → उस राशि का स्वामी → वह स्वामी कहाँ बैठा है।'},
                ),
            ),
        ),
        personalise=P.house_lords,
    ),
    Chapter(
        slug="twenty-seven-nakshatras",
        part=PART_NAKSHATRAS,
        title={"en": 'The 27 nakshatras', "hi": 'सत्ताईस नक्षत्र'},
        summary={"en": 'The older layer, and the more distinctively Indian one.', "hi": 'पुरानी परत, और ज़्यादा भारतीय भी।'},
        minutes=5,
        level="intermediate",
        sections=(
            Section(
                heading={"en": 'One for each day of the Moon', "hi": 'चंद्रमा के हर दिन के लिए एक'},
                body=(
                    {"en": 'Before the twelve rashis were adopted, Indian astronomy tracked the Moon through 27 nakshatras — roughly one for each day of its journey round the sky. Each is 13 degrees and 20 minutes wide, and 27 of them make exactly 360.', "hi": 'बारह राशियाँ अपनाए जाने से पहले भारतीय खगोल चंद्रमा को 27 नक्षत्रों से होकर देखता था — मोटे तौर पर उसकी आकाश-यात्रा के हर दिन के लिए एक। हर नक्षत्र 13 अंश 20 कला चौड़ा है, और 27 मिलकर ठीक 360 बनाते हैं।'},
                    {"en": 'They are the older layer, and in daily Indian practice the more used one. A temple asks for your nakshatra, not your sign.', "hi": 'यह पुरानी परत है, और रोज़मर्रा के भारतीय व्यवहार में ज़्यादा इस्तेमाल होने वाली। मंदिर आपकी राशि नहीं, नक्षत्र पूछता है।'},
                ),
            ),
        ),
        personalise=P.janma_nakshatra,
    ),
    Chapter(
        slug="padas",
        part=PART_NAKSHATRAS,
        title={"en": 'Padas and the 108', "hi": 'पाद और 108'},
        summary={"en": 'Four quarters to a nakshatra, and where that famous number comes from.', "hi": 'हर नक्षत्र के चार पाद, और वह प्रसिद्ध संख्या कहाँ से आती है।'},
        minutes=5,
        level="intermediate",
        sections=(
            Section(
                heading={"en": 'Three degrees twenty', "hi": 'तीन अंश बीस कला'},
                body=(
                    {"en": 'Each nakshatra divides into four padas of 3 degrees 20 minutes. That gives 108 padas in the circle — the same 108 that recurs throughout Indian tradition, and not by coincidence.', "hi": 'हर नक्षत्र चार पादों में बँटता है, हर पाद 3 अंश 20 कला का। इससे पूरे चक्र में 108 पाद बनते हैं — वही 108 जो भारतीय परंपरा में बार-बार लौटता है, और संयोग से नहीं।'},
                    {"en": 'The pada decides the syllable a child is traditionally named with, and it feeds the navamsa — the divisional chart read for marriage.', "hi": 'पाद से ही वह अक्षर तय होता है जिससे परंपरा में बच्चे का नाम रखा जाता है, और यही नवांश बनाता है — विवाह के लिए देखी जाने वाली विभाग-कुंडली।'},
                ),
                aside={"en": 'Because 360/27 cannot be written exactly in binary, naive code puts longitudes landing on a boundary in the wrong nakshatra. This engine derives every subdivision from one snapped index — a bug that produces a plausible wrong chart rather than an error.', "hi": 'चूँकि 360/27 को द्विआधारी में ठीक-ठीक नहीं लिखा जा सकता, लापरवाह कोड सीमा पर पड़े देशांतर को ग़लत नक्षत्र में डाल देता है। यह engine हर उपविभाजन एक ही संरेखित सूचकांक से निकालता है — यह वह दोष है जो त्रुटि नहीं, बल्कि विश्वसनीय दिखने वाली ग़लत कुंडली बनाता है।'},
            ),
        ),
        personalise=P.pada_navamsa,
    ),
    Chapter(
        slug="nakshatra-lords",
        part=PART_NAKSHATRAS,
        title={"en": 'Nakshatra lords', "hi": 'नक्षत्र स्वामी'},
        summary={"en": 'A nine-graha cycle repeating three times — the hinge the dasha system turns on.', "hi": 'नौ ग्रहों का चक्र, तीन बार दोहराया — दशा व्यवस्था इसी कब्ज़े पर घूमती है।'},
        minutes=4,
        level="intermediate",
        sections=(
            Section(
                heading={"en": 'Ketu, Venus, Sun, Moon…', "hi": 'केतु, शुक्र, सूर्य, चंद्र…'},
                body=(
                    {"en": "The 27 nakshatras are assigned lords in a fixed nine-graha cycle: Ketu, Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury — repeated three times. Ashwini is Ketu's, Bharani is Venus's, and so on.", "hi": '27 नक्षत्रों को नौ ग्रहों के एक तय चक्र में स्वामी दिए गए हैं: केतु, शुक्र, सूर्य, चंद्र, मंगल, राहु, गुरु, शनि, बुध — तीन बार दोहराया हुआ। अश्विनी केतु की, भरणी शुक्र की, और इसी क्रम में।'},
                    {"en": 'This ordering is not decoration. It is what makes the Vimshottari dasha work, and you will meet it again in chapter 23.', "hi": 'यह क्रम सजावट नहीं है। विंशोत्तरी दशा इसी से चलती है, और अध्याय 23 में यह फिर मिलेगा।'},
                ),
            ),
        ),
        personalise=P.janma_nakshatra,
    ),
    Chapter(
        slug="janma-nakshatra",
        part=PART_NAKSHATRAS,
        title={"en": 'The janma nakshatra', "hi": 'जन्म नक्षत्र'},
        summary={"en": 'The single measurement your whole timeline unfolds from.', "hi": 'वह एक माप जिससे आपकी पूरी काल-श्रृंखला खुलती है।'},
        minutes=4,
        level="intermediate",
        sections=(
            Section(
                heading={"en": 'Where the Moon stood', "hi": 'चंद्रमा कहाँ खड़ा था'},
                body=(
                    {"en": 'The nakshatra the Moon occupied at birth is the janma nakshatra. In daily practice it is the most used fact in the chart: it names you at a temple, and it sets the starting point of your dasha timeline.', "hi": 'जन्म के समय चंद्रमा जिस नक्षत्र में था, वही जन्म नक्षत्र है। रोज़मर्रा में यह कुंडली का सबसे ज़्यादा काम आने वाला तथ्य है: मंदिर में यही आपका नाम है, और यही आपकी दशा-श्रृंखला का आरंभ तय करता है।'},
                    {"en": 'How far the Moon had already travelled into it decides how much of your first dasha was already spent when you were born. One measurement, and the next hundred and twenty years of the timeline follow from it.', "hi": 'चंद्रमा उसमें कितना आगे बढ़ चुका था, इसी से तय होता है कि जन्म के समय आपकी पहली दशा कितनी बीत चुकी थी। एक माप, और उसके बाद की एक सौ बीस वर्ष की श्रृंखला उसी से निकलती है।'},
                ),
            ),
        ),
        personalise=P.janma_nakshatra,
    ),
)


_TIME_AND_PRACTICE: tuple[Chapter, ...] = (
    Chapter(
        slug="vimshottari-idea",
        part=PART_TIME,
        title={"en": 'Vimshottari: the idea', "hi": 'विंशोत्तरी: विचार'},
        summary={"en": 'A 120-year clock, in a fixed order that never changes.', "hi": 'एक सौ बीस वर्ष की घड़ी, एक तय क्रम में जो कभी नहीं बदलता।'},
        minutes=6,
        level="intermediate",
        sections=(
            Section(
                heading={"en": 'One hundred and twenty years', "hi": 'एक सौ बीस वर्ष'},
                body=(
                    {"en": 'Vimshottari is a sequence of periods, each ruled by one graha, running in a fixed order: Ketu 7 years, Venus 20, Sun 6, Moon 10, Mars 7, Rahu 18, Jupiter 16, Saturn 19, Mercury 17. Add them and you get 120.', "hi": 'विंशोत्तरी कालखंडों की एक श्रृंखला है, हर खंड का एक स्वामी ग्रह, और क्रम तय: केतु 7 वर्ष, शुक्र 20, सूर्य 6, चंद्र 10, मंगल 7, राहु 18, गुरु 16, शनि 19, बुध 17। जोड़ें तो 120।'},
                    {"en": 'The order never changes for anyone. What differs is where in the sequence you start, and how much of that first period had already run when you were born.', "hi": 'क्रम किसी के लिए नहीं बदलता। अंतर बस इतना है कि आप श्रृंखला में कहाँ से शुरू होते हैं, और जन्म के समय उस पहली दशा का कितना बीत चुका था।'},
                ),
            ),
            Section(
                heading={"en": 'A marker, not a schedule', "hi": 'संकेत, समय-सारणी नहीं'},
                body=(
                    {"en": 'A dasha marks which theme the tradition considers foreground at a given time. It is not a calendar of events, and no honest reading will tell you what will happen during one.', "hi": 'दशा इतना बताती है कि परंपरा किसी समय किस विषय को आगे मानती है। यह घटनाओं का पंचांग नहीं है, और कोई ईमानदार व्याख्या यह नहीं बताएगी कि उसमें क्या होगा।'},
                ),
                aside={"en": 'This engine uses a 365.25-day year, matching mainstream implementations. Texts using a 360-day year produce dates that drift — one reason two panchangs disagree about when a period turns.', "hi": 'यह engine 365.25 दिन का वर्ष लेता है, जो मुख्यधारा की गणनाओं से मेल खाता है। 360 दिन का वर्ष लेने वाले ग्रंथों की तिथियाँ खिसक जाती हैं — दो पंचांग दशा-परिवर्तन पर असहमत क्यों होते हैं, यह उसका एक कारण है।'},
            ),
        ),
        personalise=P.dasha_now,
    ),
    Chapter(
        slug="dasha-balance",
        part=PART_TIME,
        title={"en": 'Where your timeline starts', "hi": 'आपकी श्रृंखला कहाँ से शुरू होती है'},
        summary={"en": 'The balance at birth, and why nobody starts at the beginning.', "hi": 'जन्म के समय बचा हुआ भाग, और कोई भी शुरुआत से क्यों नहीं शुरू करता।'},
        minutes=5,
        level="intermediate",
        sections=(
            Section(
                heading={"en": 'The unfinished first period', "hi": 'अधूरी पहली दशा'},
                body=(
                    {"en": 'Your first mahadasha is ruled by the lord of your janma nakshatra. But you were not born at the instant that nakshatra began — the Moon was already some way into it. That fraction is the part of the period that had already elapsed.', "hi": 'आपकी पहली महादशा का स्वामी वही है जो आपके जन्म नक्षत्र का स्वामी है। पर आपका जन्म उस नक्षत्र के शुरू होते ही नहीं हुआ — चंद्रमा उसमें कुछ आगे बढ़ चुका था। वही अंश उस दशा का बीता हुआ हिस्सा है।'},
                    {"en": 'So almost nobody starts life at the beginning of a dasha. The remainder is called the balance, and everything after it follows in strict order.', "hi": 'इसलिए लगभग कोई भी जीवन किसी दशा के आरंभ से नहीं शुरू करता। जो बचता है उसे शेष या बलेंस कहते हैं, और उसके बाद सब कुछ कड़े क्रम में चलता है।'},
                ),
            ),
        ),
        personalise=P.dasha_balance,
    ),
    Chapter(
        slug="sub-periods",
        part=PART_TIME,
        title={"en": 'Periods inside periods', "hi": 'दशा के भीतर दशा'},
        summary={"en": 'Antardasha, pratyantardasha, and how deep is useful.', "hi": 'अंतर्दशा, प्रत्यंतर्दशा, और कितनी गहराई काम की है।'},
        minutes=5,
        level="intermediate",
        sections=(
            Section(
                heading={"en": 'The same order, nested', "hi": 'वही क्रम, भीतर दोहराया'},
                body=(
                    {"en": 'Each mahadasha divides into antardashas in the same nine-graha order, proportional to their years. Those divide again into pratyantardashas, and so on as deep as you like.', "hi": 'हर महादशा उसी नौ-ग्रही क्रम में अंतर्दशाओं में बँटती है, उनके वर्षों के अनुपात में। वे फिर प्रत्यंतर्दशाओं में बँटती हैं, और जितना चाहें उतना गहरा।'},
                    {"en": 'This app computes three levels, which is enough to name a period of a few months. Going deeper is arithmetically easy and interpretively meaningless — precision past the point where anything can be checked is just decoration.', "hi": 'यह ऐप तीन स्तर गिनती है, जो कुछ महीनों का काल बताने के लिए काफ़ी है। इससे गहरा जाना गणित में आसान है और व्याख्या में निरर्थक — जाँच की सीमा के आगे की सूक्ष्मता महज़ सजावट है।'},
                ),
            ),
        ),
        personalise=P.sub_periods,
    ),
    Chapter(
        slug="gochara",
        part=PART_TIME,
        title={"en": 'Transits', "hi": 'गोचर'},
        summary={"en": 'Where the planets are now, against where they were when you were born.', "hi": 'ग्रह अभी कहाँ हैं, बनाम जन्म के समय कहाँ थे।'},
        minutes=4,
        level="intermediate",
        sections=(
            Section(
                heading={"en": 'Two clocks at once', "hi": 'एक साथ दो घड़ियाँ'},
                body=(
                    {"en": 'The birth chart is frozen. Gochara — transit — is the live sky, read against that frozen picture. Saturn taking two and a half years per sign, Jupiter one year, the Moon two and a quarter days: each is a different tempo laid over the same chart.', "hi": 'जन्म कुंडली जमी हुई है। गोचर चलता हुआ आकाश है, जिसे उसी जमी तस्वीर के सामने रखकर पढ़ा जाता है। शनि हर राशि में ढाई वर्ष, गुरु एक वर्ष, चंद्रमा सवा दो दिन: हर एक अलग लय, उसी कुंडली पर।'},
                    {"en": 'Sade sati, from chapter 11, is a transit. So is every "Mercury retrograde" post you have seen — and since the transiting sky is the same for everyone alive, anything read from transits alone is by definition not about you specifically.', "hi": 'अध्याय 11 वाली साढ़ेसाती गोचर है। हर "बुध वक्री" वाली पोस्ट भी। और चूँकि गोचर का आकाश इस समय जीवित सबके लिए एक ही है, केवल गोचर से पढ़ी गई कोई बात परिभाषा से ही ख़ास आपके बारे में नहीं होती।'},
                ),
            ),
        ),
        personalise=P.dasha_now,
    ),
    Chapter(
        slug="panchang-five-limbs",
        part=PART_TIME,
        title={"en": 'Panchang: the five limbs', "hi": 'पंचांग: पाँच अंग'},
        summary={"en": 'The part of this tradition people actually use every day.', "hi": 'इस परंपरा का वह हिस्सा जो लोग सचमुच रोज़ इस्तेमाल करते हैं।'},
        minutes=6,
        level="intermediate",
        sections=(
            Section(
                heading={"en": 'Tithi, vara, nakshatra, yoga, karana', "hi": 'तिथि, वार, नक्षत्र, योग, करण'},
                body=(
                    {"en": 'Panchang means "five limbs". A tithi is the time the Moon takes to gain 12 degrees on the Sun; thirty make a lunar month, split into shukla (brightening) and krishna (darkening) paksha.', "hi": 'पंचांग यानी "पाँच अंग"। तिथि वह समय है जिसमें चंद्रमा सूर्य से 12 अंश आगे बढ़ता है; तीस तिथियाँ एक चांद्र मास बनाती हैं, जो शुक्ल (बढ़ता) और कृष्ण (घटता) पक्ष में बँटा है।'},
                    {"en": 'Vara is the weekday, each ruled by a graha — the same rulerships that named the days in most languages. Yoga is derived from Sun and Moon together, and karana is half a tithi. All five are arithmetic on two longitudes.', "hi": 'वार सप्ताह का दिन है, हर दिन का एक ग्रह स्वामी — वही स्वामित्व जिससे अधिकांश भाषाओं में दिनों के नाम पड़े। योग सूर्य और चंद्र से मिलकर निकलता है, और करण आधी तिथि है। पाँचों दो देशांतरों का गणित हैं।'},
                ),
            ),
            Section(
                heading={"en": 'Why a tithi can skip a day', "hi": 'तिथि एक दिन क्यों छोड़ सकती है'},
                body=(
                    {"en": "The Moon's speed varies, so a tithi is not a fixed number of hours — it runs from about 19 to 26. That is why a tithi can cover two sunrises or none, and why festival dates sometimes shift by a day between panchangs.", "hi": 'चंद्रमा की चाल बदलती रहती है, इसलिए तिथि घंटों की तय संख्या नहीं होती — वह क़रीब 19 से 26 घंटे तक चलती है। इसीलिए कोई तिथि दो सूर्योदय ढक सकती है या एक भी नहीं, और इसीलिए अलग-अलग पंचांगों में त्योहार की तारीख़ कभी एक दिन खिसक जाती है।'},
                ),
            ),
        ),
        personalise=P.birth_panchang,
    ),
    Chapter(
        slug="navamsa",
        part=PART_PRACTICE,
        title={"en": 'Divisional charts', "hi": 'विभाग कुंडली'},
        summary={"en": 'The navamsa: a magnification, not a second opinion.', "hi": 'नवांश: आवर्धन, दूसरी राय नहीं।'},
        minutes=5,
        level="intermediate",
        sections=(
            Section(
                heading={"en": 'Dividing a sign by nine', "hi": 'राशि को नौ से बाँटना'},
                body=(
                    {"en": 'Divide each 30-degree sign into nine parts of 3 degrees 20 minutes and you get the navamsa — the same width as a pada, which is not a coincidence. Each part maps to a sign, producing a second chart from the same longitudes.', "hi": 'हर 30 अंश की राशि को 3 अंश 20 कला के नौ हिस्सों में बाँटिए और नवांश मिलता है — पाद के बराबर चौड़ाई, और यह संयोग नहीं है। हर हिस्सा एक राशि से जुड़ता है, जिससे उन्हीं देशांतरों से दूसरी कुंडली बनती है।'},
                    {"en": 'The navamsa is traditionally read for marriage and for the strength of a placement. It is not independent evidence: it is the same measurement viewed at higher magnification, so a shaky birth time makes it shakier, not steadier.', "hi": 'नवांश परंपरा में विवाह और स्थिति के बल के लिए देखा जाता है। यह स्वतंत्र प्रमाण नहीं है: वही माप अधिक आवर्धन पर है, इसलिए डगमगाता जन्म-समय उसे और डगमगाता करता है, स्थिर नहीं।'},
                ),
                aside={"en": 'This app computes D9. Higher divisions (D10 and friends) need per-sign starting rules the engine deliberately does not encode yet, rather than guess.', "hi": 'यह ऐप D9 गिनती है। इससे ऊँचे विभाग (D10 आदि) के लिए हर राशि के अलग आरंभ-नियम चाहिए, जिन्हें engine ने जानबूझकर अभी नहीं भरा — अंदाज़े से भरने के बजाय।'},
            ),
        ),
        personalise=P.navamsa_lagna,
    ),
    Chapter(
        slug="what-it-cannot-say",
        part=PART_PRACTICE,
        title={"en": 'What astrology cannot say', "hi": 'ज्योतिष क्या नहीं कह सकता'},
        summary={"en": 'The honest boundary, drawn from the inside.', "hi": 'ईमानदार सीमा, भीतर से खींची हुई।'},
        minutes=5,
        level="intermediate",
        sections=(
            Section(
                heading={"en": 'Shared skies', "hi": 'साझा आकाश'},
                body=(
                    {"en": 'Everyone born in your city that hour shares your lagna. Everyone born that month shares your Sun. A chart cannot pick you out of that crowd, and any reading that claims to name a specific event is claiming more than the method supports.', "hi": 'उस घंटे आपके शहर में जन्मा हर व्यक्ति आपका लग्न साझा करता है। उस महीने जन्मा हर व्यक्ति आपका सूर्य। कुंडली आपको उस भीड़ से अलग नहीं कर सकती, और जो व्याख्या किसी ख़ास घटना का नाम लेने का दावा करे, वह पद्धति से ज़्यादा का दावा कर रही है।'},
                    {"en": 'What it can offer is a vocabulary for describing a period, and a mirror many people find useful. That is a real thing. It is also a smaller thing than what is usually sold.', "hi": 'जो वह दे सकता है वह है किसी काल का वर्णन करने की शब्दावली, और एक आईना जो बहुतों को काम आता है। यह असली चीज़ है। और यह उससे छोटी चीज़ भी है जो आमतौर पर बेची जाती है।'},
                ),
            ),
        ),
        personalise=P.nothing_is_a_verdict,
    ),
    Chapter(
        slug="reading-responsibly",
        part=PART_PRACTICE,
        title={"en": 'Reading responsibly', "hi": 'ज़िम्मेदारी से पढ़ना'},
        summary={"en": 'The dosha business, and what to do when a chart is being used against someone.', "hi": 'दोष का धंधा, और जब कुंडली किसी के ख़िलाफ़ इस्तेमाल हो रही हो तब क्या करें।'},
        minutes=6,
        level="basic",
        sections=(
            Section(
                heading={"en": 'A measurement turned into a lever', "hi": 'माप, जो दबाव का औज़ार बना'},
                body=(
                    {"en": 'Manglik dosha, kaal sarp, sade sati. Each names a real, computable configuration. Each has also become a product: a diagnosis to frighten someone with, and a payment offered as the cure.', "hi": 'मांगलिक दोष, कालसर्प, साढ़ेसाती। हर एक किसी असली, गणनीय स्थिति का नाम है। और हर एक अब सामान भी बन चुका है: डराने के लिए एक निदान, और इलाज के नाम पर एक भुगतान।'},
                    {"en": 'The configuration is a fact about where planets were. The claim that it causes a specific misfortune, and the claim that money removes it, are neither of those things.', "hi": 'वह स्थिति इस बात का तथ्य है कि ग्रह कहाँ थे। यह दावा कि उससे कोई ख़ास दुर्भाग्य आता है, और यह कि पैसा उसे हटा देता है — इनमें से कोई तथ्य नहीं है।'},
                ),
            ),
            Section(
                heading={"en": 'When a chart is used as an excuse', "hi": 'जब कुंडली बहाना बन जाए'},
                body=(
                    {"en": 'The most common harm this tradition is put to is not a wrong prediction. It is an explanation offered where a different response was needed — a marriage blamed on a dosha rather than on violence, a depression treated as a planetary period rather than an illness.', "hi": 'इस परंपरा से होने वाली सबसे आम हानि ग़लत भविष्यवाणी नहीं है। वह है ऐसी जगह व्याख्या देना जहाँ कुछ और चाहिए था — किसी विवाह का दोष हिंसा के बजाय कुंडली पर, किसी अवसाद को रोग के बजाय दशा मान लेना।'},
                    {"en": 'No chart can make anyone hit you. If someone is being harmed, the answer is help, not a remedy.', "hi": 'कोई कुंडली किसी से मारपीट नहीं करवाती। अगर किसी को नुक़सान पहुँचाया जा रहा है, तो उत्तर मदद है, उपाय नहीं।'},
                ),
                aside={"en": 'This app stops reading charts entirely for someone in crisis and offers real help instead: Tele-MANAS 14416, AASRA +91-9820466726, Women Helpline 181, or 112 for immediate danger.', "hi": 'संकट में होने पर यह ऐप कुंडली पढ़ना पूरी तरह रोक देती है और असली मदद सामने रखती है: टेली-मानस 14416, AASRA +91-9820466726, महिला हेल्पलाइन 181, या तुरंत ख़तरे में 112।'},
            ),
            Section(
                heading={"en": 'A working standard', "hi": 'एक काम का मानक'},
                body=(
                    {"en": 'A reading that frightens you, ranks your chart as weak, or ends in something for sale has stopped describing the sky. You are allowed to walk away from it — including from this app.', "hi": 'जो व्याख्या आपको डराए, आपकी कुंडली को कमज़ोर ठहराए, या किसी बिकाऊ चीज़ पर ख़त्म हो — वह आकाश का वर्णन करना बंद कर चुकी है। उससे हट जाना आपका अधिकार है — इस ऐप से भी।'},
                ),
            ),
        ),
        personalise=P.nothing_is_a_verdict,
    ),
)

CHAPTERS: tuple[Chapter, ...] = (
    _FOUNDATIONS + _GRAHAS + _HOUSES_AND_NAKSHATRAS + _TIME_AND_PRACTICE
)

CHAPTERS_BY_SLUG = {c.slug: c for c in CHAPTERS}
