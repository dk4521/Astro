"""Part one: what a chart is, and what has to be true before anything else is.

These five chapters carry more weight than their length suggests. Almost every
mistake a reader can make later — treating a sign as a personality, trusting a
house when the birth time is a guess, arguing with an app that uses a different
ayanamsa — is a foundation that was skipped.
"""

from __future__ import annotations

from .. import personalise as P
from ..models import Chapter, Section
from . import PART_FOUNDATIONS

CHAPTERS: tuple[Chapter, ...] = (
    Chapter(
        slug="what-a-chart-is",
        part=PART_FOUNDATIONS,
        title={"en": "What a chart actually is", "hi": "कुंडली असल में है क्या"},
        summary={
            "en": "A record of the sky, from one spot on Earth, at one second — and the line between that record and everything read into it.",
            "hi": "एक क्षण का आकाश, पृथ्वी की एक जगह से देखा हुआ — और उस अभिलेख तथा उसमें पढ़ी गई हर बात के बीच की रेखा।",
        },
        minutes=7,
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
                    {
                        "en": "Hold on to the word “record”. A chart does not act on you, does not know your name, and does not contain your future. It is a photograph of the sky with a timestamp, and the whole of Jyotisha is a way of talking about that photograph.",
                        "hi": "“अभिलेख” शब्द याद रखिए। कुंडली आप पर कुछ करती नहीं, आपका नाम जानती नहीं, और आपका भविष्य उसमें रखा नहीं है। वह समय-मुहर लगी आकाश की एक तस्वीर है, और पूरा ज्योतिष उसी तस्वीर पर बात करने का एक तरीक़ा है।",
                    },
                ),
            ),
            Section(
                heading={"en": "Three inputs, and nothing else", "hi": "तीन इनपुट, और कुछ नहीं"},
                body=(
                    {
                        "en": "Everything in your chart is computed from exactly three things: the calendar date, the clock time, and the place. The date fixes where the slow planets are. The time fixes the Moon and, far more sharply, the rising point. The place fixes the horizon you are looking from, and with it the timezone that turns your local clock into a universal instant.",
                        "hi": "आपकी कुंडली की हर चीज़ ठीक तीन बातों से निकलती है: तारीख़, घड़ी का समय, और स्थान। तारीख़ से धीमे ग्रहों की जगह तय होती है। समय से चंद्रमा तय होता है और उससे कहीं ज़्यादा तीखेपन से लग्न। स्थान से वह क्षितिज तय होता है जहाँ से आप देख रहे हैं, और उसी के साथ वह समय-क्षेत्र जो आपकी स्थानीय घड़ी को एक वैश्विक क्षण में बदलता है।",
                    },
                    {
                        "en": "No name, no photograph, no question you asked, no history you typed. If a reading appears to know something that could not have come out of a date, a minute and a pair of coordinates, it came from somewhere else — usually from you, in the question you asked.",
                        "hi": "न नाम, न तस्वीर, न आपका पूछा सवाल, न लिखा हुआ इतिहास। अगर कोई व्याख्या ऐसा कुछ जानती दिखे जो तारीख़, मिनट और दो निर्देशांकों से निकल ही नहीं सकता, तो वह कहीं और से आया है — प्रायः आपके ही पूछे सवाल से।",
                    },
                ),
                aside={
                    "en": "This is a useful test to keep for later chapters: for any statement, ask which of the three inputs it could possibly have come from.",
                    "hi": "आगे के अध्यायों के लिए यह जाँच काम की है: किसी भी बात पर पूछिए कि वह इन तीन इनपुट में से किससे निकल सकती थी।",
                },
            ),
            Section(
                heading={"en": "What the tradition adds", "hi": "परंपरा क्या जोड़ती है"},
                body=(
                    {
                        "en": "Jyotisha takes those positions and reads them as a vocabulary: this graha in that sign, in that house, during that period. The vocabulary is old, internally consistent, and useful to many people as a mirror. None of that makes it a mechanism of cause.",
                        "hi": "ज्योतिष उन स्थितियों को एक शब्दावली की तरह पढ़ता है: यह ग्रह उस राशि में, उस भाव में, उस काल में। यह शब्दावली पुरानी है, अपने भीतर संगत है, और बहुतों को आईने की तरह काम आती है। इससे वह कारण-तंत्र नहीं बन जाती।",
                    },
                    {
                        "en": "Internally consistent is worth pausing on. Given the same positions, two competent readers trained in the same school will describe them in recognisably similar words. That is a real property, and it is what makes the tradition teachable at all. It is also exactly what a well-built vocabulary does, and not evidence that planets cause anything.",
                        "hi": "“अपने भीतर संगत” पर एक क्षण रुकिए। एक ही स्थिति दी जाए तो एक ही परंपरा में सधे दो पढ़ने वाले उसे लगभग एक जैसे शब्दों में कहेंगे। यह असली गुण है, और इसी से यह विद्या सिखाई जा सकती है। और यही वह काम है जो कोई भी सुगठित शब्दावली करती है — इससे यह सिद्ध नहीं होता कि ग्रह कुछ करते हैं।",
                    },
                    {
                        "en": "Keeping the two layers separate is what lets you use the tradition without being ruled by it. You can find a reading useful and still know it is a reading.",
                        "hi": "दोनों परतों को अलग रखना ही आपको परंपरा का उपयोग करने देता है, उसके अधीन हुए बिना। कोई व्याख्या उपयोगी लग सकती है, और फिर भी यह जानना बना रह सकता है कि वह व्याख्या ही है।",
                    },
                ),
            ),
            Section(
                heading={"en": "Where this app draws the line", "hi": "यह ऐप रेखा कहाँ खींचती है"},
                body=(
                    {
                        "en": "The chart screen, the panchang, the dasha timeline and the personalised block at the foot of every chapter are arithmetic. They are computed by the same engine, they can be checked against any ephemeris, and they will return the same answer forever for the same birth details.",
                        "hi": "कुंडली की स्क्रीन, पंचांग, दशा की समय-रेखा, और हर अध्याय के नीचे आपकी कुंडली वाला हिस्सा — ये सब गणित हैं। इन्हें वही इंजन निकालता है, इन्हें किसी भी पंचांग-सारणी से मिलाया जा सकता है, और एक ही जन्म-विवरण पर ये हमेशा वही उत्तर देंगे।",
                    },
                    {
                        "en": "The written reading and the chat are the other layer, and they are labelled as such. When you cannot tell which layer you are reading, that is the app's failure and not yours — and it is the failure this course is written to make impossible.",
                        "hi": "लिखी हुई व्याख्या और बातचीत दूसरी परत हैं, और उन्हें वैसा ही चिह्नित किया गया है। अगर कभी पता न चले कि आप कौन सी परत पढ़ रहे हैं, तो यह ऐप की चूक है, आपकी नहीं — और यही वह चूक है जिसे असंभव बनाने के लिए यह पाठ्यक्रम लिखा गया है।",
                    },
                ),
                aside={
                    "en": "Nothing in these thirty chapters is generated. Every sentence was written by a person; the block at the foot of each chapter is computed by the engine. This is the one part of the app that cannot invent anything.",
                    "hi": "इन तीस अध्यायों में कुछ भी मशीन-रचित नहीं है। हर वाक्य किसी व्यक्ति ने लिखा है; हर अध्याय के नीचे का हिस्सा इंजन गिनता है। ऐप का यही एक हिस्सा है जो कुछ गढ़ ही नहीं सकता।",
                },
            ),
            Section(
                heading={"en": "How this course is built", "hi": "यह पाठ्यक्रम कैसे बना है"},
                body=(
                    {
                        "en": "Thirty chapters in six parts. Foundations first, because nothing later is safe without them. Then the nine grahas, the twelve houses, the twenty-seven nakshatras, the machinery of time — dashas, transits and the panchang — and finally practice: what this method cannot do, and how it is misused.",
                        "hi": "छह भागों में तीस अध्याय। पहले बुनियाद, क्योंकि उसके बिना आगे कुछ भी सुरक्षित नहीं। फिर नौ ग्रह, बारह भाव, सत्ताईस नक्षत्र, काल का तंत्र — दशा, गोचर और पंचांग — और अंत में व्यवहार: यह पद्धति क्या नहीं कर सकती, और इसका दुरुपयोग कैसे होता है।",
                    },
                    {
                        "en": "Read them in order the first time. Each part assumes the one before it, and the later chapters name earlier ones by number. Once through, they work as reference: come back to a single chapter when a word in a reading is unfamiliar.",
                        "hi": "पहली बार क्रम से पढ़िए। हर भाग अपने पिछले भाग को मान कर चलता है, और बाद के अध्याय पहले वालों को क्रमांक से पुकारते हैं। एक बार पढ़ लेने के बाद ये संदर्भ की तरह काम आते हैं: किसी व्याख्या में कोई शब्द अनजाना लगे तो उसी अध्याय पर लौट आइए।",
                    },
                    {
                        "en": "By the end you should be able to open your own chart, say what every number on it means, check the important ones by hand, and recognise the difference between a description and a sales pitch. That is the whole ambition.",
                        "hi": "अंत तक आप अपनी कुंडली खोलकर उसकी हर संख्या का अर्थ बता सकें, ज़रूरी संख्याएँ ख़ुद जाँच सकें, और वर्णन तथा बिक्री की बात में फ़र्क़ पहचान सकें — बस यही पूरा लक्ष्य है।",
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
                        "en": "Saying “the Moon is in Karka” means the Moon fell somewhere in the fourth slice. That is a coordinate, in the same sense as a latitude — and like a latitude, it is either right or wrong, not a matter of opinion.",
                        "hi": "“चंद्रमा कर्क में है” का अर्थ है कि चंद्रमा चौथे हिस्से में कहीं पड़ा। यह एक निर्देशांक है, ठीक वैसे जैसे अक्षांश — और अक्षांश की तरह यह या तो सही होता है या ग़लत, राय का विषय नहीं।",
                    },
                    {
                        "en": "The slices are equal by construction, so the arithmetic is trivial: divide a sidereal longitude by 30 and the quotient names the rashi, the remainder is the degree within it. Your chart screen shows both, which means every sign statement in this app can be checked in one division.",
                        "hi": "ये हिस्से बनावट से ही बराबर हैं, इसलिए गणित मामूली है: निरयन देशांतर को 30 से भाग दीजिए — भागफल राशि बताएगा, शेषफल उस राशि में अंश। आपकी कुंडली की स्क्रीन दोनों दिखाती है, यानी इस ऐप की हर राशि-संबंधी बात एक भाग से जाँची जा सकती है।",
                    },
                ),
            ),
            Section(
                heading={"en": "Ruler, element, modality", "hi": "स्वामी, तत्व, स्वभाव"},
                body=(
                    {
                        "en": "Each rashi carries three standard labels. Its ruling graha: Mesha and Vrishchika belong to Mars, Vrishabha and Tula to Venus, Mithuna and Kanya to Mercury, Dhanu and Meena to Jupiter, Makara and Kumbha to Saturn, and the two lights take one each — Karka the Moon, Simha the Sun.",
                        "hi": "हर राशि पर तीन मानक लेबल लगते हैं। पहला उसका स्वामी ग्रह: मेष और वृश्चिक मंगल के, वृषभ और तुला शुक्र के, मिथुन और कन्या बुध के, धनु और मीन गुरु के, मकर और कुंभ शनि के, और दोनों प्रकाश एक-एक लेते हैं — कर्क चंद्रमा का, सिंह सूर्य का।",
                    },
                    {
                        "en": "Then an element, repeating in fours: fire (Mesha, Simha, Dhanu), earth (Vrishabha, Kanya, Makara), air (Mithuna, Tula, Kumbha), water (Karka, Vrishchika, Meena). Then a modality, repeating in threes: movable or chara (Mesha, Karka, Tula, Makara), fixed or sthira (Vrishabha, Simha, Vrishchika, Kumbha), dual or dvisvabhava (Mithuna, Kanya, Dhanu, Meena).",
                        "hi": "फिर तत्व, जो चार-चार के क्रम में लौटता है: अग्नि (मेष, सिंह, धनु), पृथ्वी (वृषभ, कन्या, मकर), वायु (मिथुन, तुला, कुंभ), जल (कर्क, वृश्चिक, मीन)। फिर स्वभाव, जो तीन-तीन के क्रम में लौटता है: चर (मेष, कर्क, तुला, मकर), स्थिर (वृषभ, सिंह, वृश्चिक, कुंभ), द्विस्वभाव (मिथुन, कन्या, धनु, मीन)।",
                    },
                    {
                        "en": "Nothing here needs memorising in one sitting. The pattern is regular enough that you can rebuild any of it from the order of the signs, and the ruler is the only one of the three you will use constantly — chapter 18 turns on it.",
                        "hi": "यहाँ कुछ भी एक बैठक में रटने की ज़रूरत नहीं। क्रम इतना नियमित है कि राशियों की तरतीब से आप कोई भी लेबल फिर से बना लेंगे, और तीनों में से केवल स्वामी बार-बार काम आएगा — अध्याय 18 उसी पर घूमता है।",
                    },
                ),
            ),
            Section(
                heading={"en": "What a rashi is said to carry", "hi": "राशि किसका संकेत मानी जाती है"},
                body=(
                    {
                        "en": "Put together, those labels describe an emphasis rather than a person. Tula is ruled by Venus, is an air sign, and is movable — the tradition reads that combination as weighing, comparing, initiating through relationship. A graha sitting there is being described as working in that manner, not as having that character.",
                        "hi": "इन लेबलों को जोड़िए तो वे किसी व्यक्ति का नहीं, किसी झुकाव का वर्णन करते हैं। तुला का स्वामी शुक्र है, वह वायु राशि है और चर है — परंपरा इस मेल को तौलने, तुलना करने, संबंध के रास्ते पहल करने की तरह पढ़ती है। वहाँ बैठा ग्रह उस ढंग से काम करता कहा जा रहा है, उसका स्वभाव वैसा है — यह नहीं।",
                    },
                    {
                        "en": "They are not a diagnosis. Nobody is “a Taurus” the way they are left-handed. A rashi says where a body was, and what the tradition reads into that.",
                        "hi": "यह निदान नहीं है। कोई “वृषभ का” उस तरह नहीं होता जैसे कोई बाएँ हाथ का होता है। राशि बताती है कि पिंड कहाँ था, और परंपरा उसमें क्या पढ़ती है।",
                    },
                ),
            ),
            Section(
                heading={"en": "Which sign people mean by “your rashi”", "hi": "“आपकी राशि” से मतलब किस राशि से होता है"},
                body=(
                    {
                        "en": "In India, asking for your rashi almost always means the sign the Moon occupied at birth, not the Sun. A temple, a priest, a matchmaker and a panchang all mean the Moon. A Western magazine column means the Sun. The two are different signs for most people, and neither party usually says which they mean.",
                        "hi": "भारत में “आपकी राशि क्या है” का अर्थ लगभग हमेशा जन्म के समय चंद्रमा की राशि होता है, सूर्य की नहीं। मंदिर, पुरोहित, विवाह मिलाने वाले और पंचांग — सब चंद्र-राशि की बात करते हैं। पाश्चात्य पत्रिका का स्तंभ सूर्य-राशि की। अधिकांश लोगों के लिए दोनों अलग होती हैं, और कोई भी पक्ष प्रायः यह बताता नहीं कि वह किसकी बात कर रहा है।",
                    },
                    {
                        "en": "Your chart screen labels both, so you never have to guess. When someone tells you your sign and it does not match, the first question is not who is wrong — it is which body, and which zero point, they measured from. The next chapter is about that second question.",
                        "hi": "आपकी कुंडली की स्क्रीन दोनों को नाम देकर दिखाती है, इसलिए अंदाज़ा लगाने की ज़रूरत नहीं। कोई आपकी राशि बताए और वह मेल न खाए, तो पहला सवाल यह नहीं कि ग़लत कौन है — सवाल यह है कि किस पिंड से, और किस शून्य-बिंदु से नापा गया। अगला अध्याय इसी दूसरे सवाल पर है।",
                    },
                ),
                aside={
                    "en": "Both are on your chart screen: the Moon's rashi is the one Indian practice calls yours, and the Sun's is the one most people abroad mean.",
                    "hi": "दोनों आपकी कुंडली की स्क्रीन पर हैं: चंद्रमा वाली वह है जिसे भारतीय परंपरा आपकी राशि कहती है, और सूर्य वाली वह जो विदेश में प्रायः मानी जाती है।",
                },
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
            ),
            Section(
                heading={"en": "Why the sky slips", "hi": "आकाश खिसकता क्यों है"},
                body=(
                    {
                        "en": "The Earth spins like a top that is very slightly tilted, and like a top it also traces a slow cone. That cone is precession. It moves the equinox — the point where the Sun crosses the celestial equator in March — backwards through the stars at about 50 arc-seconds a year, roughly one degree every 72 years.",
                        "hi": "पृथ्वी लट्टू की तरह घूमती है और थोड़ी झुकी हुई है, और लट्टू की ही तरह वह एक धीमा शंकु भी बनाती है। यही शंकु अयन-चलन है। इससे विषुव — वह बिंदु जहाँ मार्च में सूर्य खगोलीय भूमध्य रेखा पार करता है — तारों के बीच पीछे की ओर सरकता है, लगभग 50 विकला प्रति वर्ष, यानी हर 72 वर्ष में क़रीब एक अंश।",
                    },
                    {
                        "en": "A tropical zodiac is pinned to that moving equinox, so it stays aligned with the seasons and slides against the stars. A sidereal zodiac is pinned to the stars, so it stays aligned with the constellations and slides against the seasons. Both are coherent; they simply answer different questions.",
                        "hi": "सायन राशिचक्र उसी चलते विषुव से बँधा है, इसलिए वह ऋतुओं के साथ बना रहता है और तारों के सापेक्ष खिसकता है। निरयन राशिचक्र तारों से बँधा है, इसलिए वह नक्षत्रों के साथ बना रहता है और ऋतुओं के सापेक्ष खिसकता है। दोनों अपने में संगत हैं; बस सवाल अलग-अलग हैं।",
                    },
                    {
                        "en": "The gap between the two is the ayanamsa, and it grows by about a degree every lifetime. A chart drawn for 1950 and one drawn for 2025 use measurably different corrections, which is why the value has to be computed for the birth moment rather than taken as a constant.",
                        "hi": "दोनों के बीच का यही अंतर अयनांश है, और यह हर एक जीवनकाल में लगभग एक अंश बढ़ जाता है। 1950 की कुंडली और 2025 की कुंडली में सुधार का मान नापने लायक़ अलग होता है — इसीलिए यह मान स्थिरांक मानकर नहीं, जन्म-क्षण के लिए गिनकर निकाला जाता है।",
                    },
                ),
            ),
            Section(
                heading={"en": "Which ayanamsa this app uses", "hi": "यह ऐप कौन सा अयनांश लेती है"},
                body=(
                    {
                        "en": "There is more than one candidate, because pinning the sidereal zero to a star is a choice, not a discovery. Lahiri, Raman, Krishnamurti and others place it slightly differently, and the spread between them is a fraction of a degree — small, but enough to move a graha across a boundary when it sits at the very edge of a sign.",
                        "hi": "उम्मीदवार एक से ज़्यादा हैं, क्योंकि निरयन शून्य को किसी तारे से बाँधना खोज नहीं, चुनाव है। लाहिड़ी, रमन, कृष्णमूर्ति और दूसरे इसे थोड़ा-थोड़ा अलग रखते हैं, और उनके बीच का फ़र्क़ अंश के अंश भर का है — छोटा, पर इतना कि किसी राशि के बिल्कुल किनारे बैठा ग्रह सीमा पार कर जाए।",
                    },
                    {
                        "en": "This app uses Lahiri, also called Chitrapaksha — the standard adopted by the Government of India's calendar reform committee and the one nearly every Indian panchang follows. It is computed for your birth moment, corrected for nutation, and printed with your chart so you can see the exact number that was subtracted.",
                        "hi": "यह ऐप लाहिड़ी लेती है, जिसे चित्रपक्ष भी कहते हैं — वही मानक जिसे भारत सरकार की पंचांग सुधार समिति ने अपनाया और जिसे लगभग हर भारतीय पंचांग मानता है। यह आपके जन्म-क्षण के लिए गिना जाता है, अक्ष-कंपन का सुधार लगाकर, और आपकी कुंडली के साथ छापा जाता है ताकि घटाया गया ठीक मान आपको दिखे।",
                    },
                ),
                aside={
                    "en": "The correction is called the ayanamsa. This app uses Lahiri (Chitrapaksha), the Government of India standard, and reports the exact value it used with every chart.",
                    "hi": "इस सुधार को अयनांश कहते हैं। यह ऐप लाहिड़ी (चित्रपक्ष) इस्तेमाल करती है, जो भारत सरकार का मानक है, और हर कुंडली के साथ उसका ठीक मान बताती है।",
                },
            ),
            Section(
                heading={"en": "What to do with two answers", "hi": "दो उत्तरों का क्या करें"},
                body=(
                    {
                        "en": "When a Western site says you are Simha and this app says Karka, nobody has made an error. Convert rather than argue: subtract the ayanamsa from a tropical longitude and you have the sidereal one. The planets did not move; the ruler did.",
                        "hi": "कोई पाश्चात्य साइट कहे आप सिंह हैं और यह ऐप कहे कर्क — तो किसी से चूक नहीं हुई। बहस के बजाय बदल लीजिए: सायन देशांतर में से अयनांश घटाइए, निरयन देशांतर मिल जाएगा। ग्रह हिले नहीं; पैमाना हिला है।",
                    },
                    {
                        "en": "Two Indian sources disagreeing is a different matter, and usually a smaller one: check whether they used the same ayanamsa before checking anything else. Most such quarrels dissolve at that line, and the rest usually turn out to be a birth time entered differently.",
                        "hi": "दो भारतीय स्रोतों का आपस में न मिलना अलग बात है, और प्रायः छोटी बात: कुछ और जाँचने से पहले देखिए कि दोनों ने एक ही अयनांश लिया या नहीं। ऐसे अधिकांश झगड़े यहीं ख़त्म हो जाते हैं, और बाक़ी में प्रायः जन्म समय अलग दर्ज हुआ निकलता है।",
                    },
                ),
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
                    {
                        "en": "Because it is an intersection and not an object, it needs geometry the planets do not: your latitude, your longitude, and the exact instant. Get any of those wrong and the lagna is wrong while every planet on the chart stays perfectly correct — which is exactly why a chart can look right and be useless.",
                        "hi": "चूँकि यह कोई पिंड नहीं बल्कि कटान-बिंदु है, इसे वह ज्यामिति चाहिए जो ग्रहों को नहीं चाहिए: आपका अक्षांश, आपका देशांतर, और ठीक क्षण। इनमें से कुछ भी ग़लत हुआ तो लग्न ग़लत हो जाएगा जबकि कुंडली का हर ग्रह बिल्कुल सही बना रहेगा — इसीलिए कोई कुंडली सही दिखते हुए भी बेकार हो सकती है।",
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
                    {
                        "en": "“Roughly” is doing real work in that sentence. Signs do not rise at equal speed from anywhere but the equator: at Indian latitudes some take well over two hours to clear the horizon and others under ninety minutes. That is why the app computes the ascendant from your coordinates instead of dividing the day into twelve equal parts.",
                        "hi": "उस वाक्य में “लगभग” का असली काम है। भूमध्य रेखा को छोड़कर कहीं भी राशियाँ बराबर गति से नहीं उगतीं: भारतीय अक्षांशों पर कुछ को क्षितिज पार करने में दो घंटे से अच्छा-ख़ासा ज़्यादा लगता है और कुछ को डेढ़ घंटे से भी कम। इसीलिए ऐप दिन को बारह बराबर हिस्सों में बाँटने के बजाय आपके निर्देशांकों से लग्न गिनती है।",
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
                        "en": "The chain is worth seeing once in full. The lagna fixes which rashi is the 1st house. That fixes all twelve. That fixes which house every graha occupies, which house each graha rules, and therefore almost every sentence a reading contains. Sign placements survive a wrong lagna; nothing else does.",
                        "hi": "यह शृंखला एक बार पूरी देख लेनी चाहिए। लग्न तय करता है कि कौन सी राशि पहला भाव है। उससे बारहों तय हो जाते हैं। उससे तय होता है कि हर ग्रह किस भाव में है, कौन ग्रह किस भाव का स्वामी है, और इसलिए किसी भी व्याख्या के लगभग सारे वाक्य। ग़लत लग्न में राशि-स्थितियाँ बच जाती हैं; और कुछ नहीं बचता।",
                    },
                    {
                        "en": "This is also why the lagna is the first thing any reading states. Change it and everything downstream changes with it.",
                        "hi": "इसीलिए कोई भी व्याख्या सबसे पहले लग्न बताती है। वह बदले तो उसके बाद का सब कुछ बदल जाता है।",
                    },
                ),
                aside={
                    "en": "A birth time recalled as “around 7” is the largest single source of wrong charts. If yours is uncertain, treat house-based statements with more caution than sign-based ones.",
                    "hi": "“क़रीब सात बजे” जैसा याद किया हुआ समय ग़लत कुंडलियों का सबसे बड़ा कारण है। आपका समय अनिश्चित हो तो भाव पर टिकी बातों को राशि पर टिकी बातों से ज़्यादा सावधानी से लें।",
                },
            ),
            Section(
                heading={"en": "When the birth time is uncertain", "hi": "जब जन्म समय पक्का न हो"},
                body=(
                    {
                        "en": "Many people simply do not have an exact time, and pretending otherwise helps nobody. Work out what your uncertainty costs: an error of a few minutes rarely moves anything except a lagna sitting near a sign boundary; half an hour can move it; two hours certainly does.",
                        "hi": "बहुत लोगों के पास ठीक समय है ही नहीं, और होने का दिखावा किसी के काम नहीं आता। हिसाब लगाइए कि आपकी अनिश्चितता की क़ीमत क्या है: कुछ मिनटों की चूक प्रायः तभी कुछ बदलती है जब लग्न राशि की सीमा के पास हो; आधा घंटा उसे बदल सकता है; दो घंटे तो बदलेगा ही।",
                    },
                    {
                        "en": "With an uncertain time, read the chart in layers. Planetary signs and nakshatras are safe — they are fixed by the date and, for the Moon, roughly the hour. The dasha timeline is nearly safe, since it depends on the Moon. House placements, the lagna itself and the navamsa are the parts that should be held loosely.",
                        "hi": "समय अनिश्चित हो तो कुंडली परतों में पढ़िए। ग्रहों की राशियाँ और नक्षत्र सुरक्षित हैं — वे तारीख़ से तय हैं, और चंद्रमा के लिए मोटे तौर पर घंटे से। दशा की समय-रेखा भी लगभग सुरक्षित है, क्योंकि वह चंद्रमा पर टिकी है। भाव-स्थितियाँ, स्वयं लग्न और नवांश — इन्हें ढीला पकड़िए।",
                    },
                    {
                        "en": "Traditional practice has a procedure called rectification, which adjusts the birth time until the chart matches remembered events. It is skilled work and this app does not do it, for a plain reason: fitting a time to events you already know, and then reading those events back out of the chart, is a circle. What the app will do is show you the same chart every time from the time you actually entered.",
                        "hi": "परंपरा में इसके लिए “जन्म-शोधन” की विधि है, जिसमें याद की गई घटनाओं से मेल बैठने तक जन्म समय बदला जाता है। यह कुशल काम है और यह ऐप इसे नहीं करती, कारण सीधा है: पहले से पता घटनाओं पर समय बिठाना और फिर उन्हीं घटनाओं को कुंडली में से पढ़ लेना — यह गोल घेरा है। ऐप बस इतना करेगी कि आपने जो समय भरा है, उसी से हर बार वही कुंडली दिखाए।",
                    },
                ),
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
        minutes=5,
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
                    {
                        "en": "This one convention causes more early confusion than anything else in the subject. A “5” in a box does not mean the 5th house — it means Simha, the fifth rashi, is sitting in whichever house that box happens to be.",
                        "hi": "इस एक परंपरा से शुरू में जितनी उलझन होती है, उतनी शायद ही किसी और बात से। किसी खाने में लिखा “5” पाँचवाँ भाव नहीं बताता — वह बताता है कि पाँचवीं राशि सिंह उस खाने वाले भाव में बैठी है।",
                    },
                ),
            ),
            Section(
                heading={"en": "Reading one box, step by step", "hi": "एक खाना, क़दम दर क़दम"},
                body=(
                    {
                        "en": "Start at the top-centre diamond: that is house 1. Read its number — say 2, so Vrishabha is your lagna rashi. Then count anticlockwise. The next box is house 2 and holds the next rashi, Mithuna, and so on all the way round to house 12.",
                        "hi": "ऊपर बीच के खाने से शुरू कीजिए: वही पहला भाव है। उसमें लिखा अंक पढ़िए — मान लीजिए 2, तो आपका लग्न वृषभ हुआ। अब वामावर्त — यानी घड़ी की उल्टी दिशा में — गिनिए। अगला खाना दूसरा भाव है और उसमें अगली राशि मिथुन, और इसी तरह घूमते हुए बारहवें भाव तक।",
                    },
                    {
                        "en": "Whatever graha abbreviations sit inside a box are the grahas in that house. That is the whole reading procedure. Because this app uses whole-sign houses — chapter 14 — the sign and the house always line up exactly, one box, one rashi, no overlap.",
                        "hi": "किसी खाने में जो ग्रह-संक्षेप लिखे हैं, वही उस भाव के ग्रह हैं। पढ़ने की पूरी विधि इतनी ही है। चूँकि यह ऐप पूर्ण-राशि भाव लेती है — अध्याय 14 — इसलिए राशि और भाव हमेशा ठीक-ठीक मेल खाते हैं: एक खाना, एक राशि, कोई ओवरलैप नहीं।",
                    },
                ),
                aside={
                    "en": "If you only remember one thing: numbers in boxes are rashis. Houses are counted by position, always starting from the top-centre.",
                    "hi": "एक ही बात याद रखनी हो तो यह: खानों में लिखे अंक राशियाँ हैं। भाव जगह से गिने जाते हैं, और गिनती हमेशा ऊपर बीच से शुरू होती है।",
                },
            ),
            Section(
                heading={"en": "What the diagram leaves out", "hi": "चित्र क्या छोड़ देता है"},
                body=(
                    {
                        "en": "A square chart is a summary, and it drops most of the precision underneath. It does not show the degree a graha sits at, its nakshatra and pada, whether it is retrograde or combust, or how fast it was moving. Two charts can look identical as diagrams and differ in every one of those.",
                        "hi": "चौकोर कुंडली एक सारांश है, और नीचे की अधिकांश सूक्ष्मता छोड़ देती है। वह यह नहीं दिखाती कि ग्रह किस अंश पर है, उसका नक्षत्र और पाद क्या है, वह वक्री या अस्त है या नहीं, और उसकी गति क्या थी। दो कुंडलियाँ चित्र के तौर पर एक जैसी दिख सकती हैं और इन सब में अलग हो सकती हैं।",
                    },
                    {
                        "en": "That is why the chart screen in this app lists the grahas in a table as well as drawing them. The diagram is for seeing the shape of a chart at a glance; the table is what you check things against.",
                        "hi": "इसीलिए इस ऐप की कुंडली स्क्रीन ग्रहों को बनाने के साथ-साथ सूची में भी देती है। चित्र इसलिए है कि कुंडली की बनावट एक नज़र में दिख जाए; मिलान सूची से किया जाता है।",
                    },
                ),
            ),
            Section(
                heading={"en": "Comparing two apps without a fight", "hi": "दो ऐप मिलाना, बिना झगड़े"},
                body=(
                    {
                        "en": "When another app draws your chart differently, work down a short list before concluding anyone is wrong. Is it drawing North or South Indian style? Is it sidereal or tropical, and on which ayanamsa? Does it use whole-sign houses or a degree-based system? Did it take the same birth time, and the same timezone for that date?",
                        "hi": "कोई दूसरी ऐप आपकी कुंडली अलग बनाए, तो किसी को ग़लत कहने से पहले एक छोटी सूची पर उतरिए। वह उत्तर भारतीय शैली बना रही है या दक्षिण भारतीय? निरयन है या सायन, और कौन सा अयनांश? पूर्ण-राशि भाव ले रही है या अंश-आधारित पद्धति? क्या उसने वही जन्म समय लिया, और उस तारीख़ के लिए वही समय-क्षेत्र?",
                    },
                    {
                        "en": "Nearly every disagreement resolves at one of those four lines, and none of them is a matter of skill. A real difference in the underlying longitudes — the same convention, the same inputs, different answers — is rare, and that is the only case where one of the two is actually wrong.",
                        "hi": "लगभग हर मतभेद इन्हीं चार पंक्तियों में से किसी एक पर सुलझ जाता है, और इनमें से कोई कौशल का मामला नहीं है। असली फ़र्क़ — वही परंपरा, वही इनपुट, फिर भी अलग देशांतर — कम ही होता है, और केवल उसी हाल में दोनों में से कोई सचमुच ग़लत है।",
                    },
                ),
            ),
        ),
        personalise=P.graha_positions,
    ),
)
