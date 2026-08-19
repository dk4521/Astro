"""Part two: the nine grahas, one at a time.

The order is deliberate — the two lights first, then the fast pair, then the two
the tradition calls benefic, then Saturn, then the nodes, and finally the two
states (retrograde, combust) that get attached to any of them. Each chapter says
what the body actually does in the sky before saying what the tradition reads
into it, because the second is much harder to hold sensibly without the first.
"""

from __future__ import annotations

from .. import personalise as P
from ..models import Chapter, Section
from . import PART_GRAHAS

CHAPTERS: tuple[Chapter, ...] = (
    Chapter(
        slug="nine-grahas",
        part=PART_GRAHAS,
        title={"en": "The nine grahas", "hi": "नौ ग्रह"},
        summary={
            "en": "Seven visible bodies and two points where orbits cross.",
            "hi": "सात दिखने वाले पिंड और दो बिंदु जहाँ कक्षाएँ कटती हैं।",
        },
        minutes=7,
        level="basic",
        sections=(
            Section(
                heading={"en": "Why the list stops at Saturn", "hi": "सूची शनि पर क्यों रुकती है"},
                body=(
                    {
                        "en": "Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn. These are the bodies visible to the naked eye, which is exactly why the list ends where it does — the tradition was built by people watching the sky without lenses.",
                        "hi": "सूर्य, चंद्र, मंगल, बुध, गुरु, शुक्र, शनि। ये नंगी आँख से दिखने वाले पिंड हैं, और सूची यहीं ख़त्म होने का कारण भी यही है — यह परंपरा बिना दूरबीन के आकाश देखने वालों ने बनाई थी।",
                    },
                    {
                        "en": "Uranus, Neptune and Pluto are not used in classical Vedic astrology. They were found after the system was complete, and it has no slot for them.",
                        "hi": "शास्त्रीय वैदिक ज्योतिष में यूरेनस, नेपच्यून और प्लूटो का उपयोग नहीं होता। वे व्यवस्था बन जाने के बाद खोजे गए, और उसमें उनके लिए जगह नहीं है।",
                    },
                    {
                        "en": "Some modern schools have tried to add them. That is a live argument inside the tradition rather than a settled correction, and this app stays with the nine — partly because everything else in it, from house rulership to the 120-year dasha cycle, is built on exactly nine and does not survive a tenth being inserted.",
                        "hi": "कुछ आधुनिक धाराओं ने उन्हें जोड़ने की कोशिश की है। यह परंपरा के भीतर की चालू बहस है, कोई तय हो चुका सुधार नहीं — और यह ऐप नौ पर ही टिकी है, कुछ इसलिए भी कि इसमें बाक़ी सब कुछ, भाव-स्वामित्व से लेकर 120 वर्ष के दशा-चक्र तक, ठीक नौ पर बना है और दसवाँ घुसाने पर टिकता नहीं।",
                    },
                ),
                aside={
                    "en": "So the chart you see here will never show Uranus, Neptune or Pluto. That is a stated choice, not an omission.",
                    "hi": "यानी यहाँ दिखने वाली कुंडली में यूरेनस, नेपच्यून या प्लूटो कभी नहीं आएँगे। यह घोषित चुनाव है, चूक नहीं।",
                },
            ),
            Section(
                heading={"en": "What “graha” means", "hi": "“ग्रह” का अर्थ"},
                body=(
                    {
                        "en": "The Sanskrit word means “one that seizes” or “holds”, not “planet”. That is why the Sun and Moon, which are not planets, and Rahu and Ketu, which are not objects at all, sit comfortably in the same list. The category is about what the tradition watches.",
                        "hi": "संस्कृत शब्द का अर्थ है “जो पकड़ता है”, अंग्रेज़ी का “प्लैनेट” नहीं। इसीलिए सूर्य और चंद्र, जो ग्रह नहीं हैं, और राहु-केतु, जो पिंड ही नहीं हैं, एक ही सूची में सहज बैठ जाते हैं। यह श्रेणी इस बारे में है कि परंपरा किसे देखती है।",
                    },
                    {
                        "en": "Translating it as “planet” quietly imports a claim the word never made — that these are objects exerting a force. What the list actually holds is nine moving markers on one circle, seven of them physical and two of them geometric.",
                        "hi": "इसे “प्लैनेट” कहकर अनुवाद करना चुपचाप वह दावा भीतर ले आता है जो शब्द ने कभी किया ही नहीं — कि ये कोई बल लगाने वाले पिंड हैं। सूची में असल में इतना है: एक ही वृत्त पर चलते नौ चिह्न, जिनमें सात भौतिक हैं और दो ज्यामितीय।",
                    },
                ),
            ),
            Section(
                heading={"en": "Nine speeds, nine tempos", "hi": "नौ गतियाँ, नौ लय"},
                body=(
                    {
                        "en": "The single most useful fact about a graha is how fast it moves. The Moon crosses a sign in about two and a quarter days. The Sun, Mercury and Venus each take about a month. Mars takes roughly six weeks, Jupiter a year, Saturn about two and a half years, and Rahu and Ketu about a year and a half.",
                        "hi": "किसी ग्रह के बारे में सबसे काम की एक बात उसकी गति है। चंद्रमा एक राशि क़रीब सवा दो दिन में पार करता है। सूर्य, बुध और शुक्र लगभग एक-एक महीना लेते हैं। मंगल क़रीब छह हफ़्ते, गुरु एक वर्ष, शनि लगभग ढाई वर्ष, और राहु-केतु क़रीब डेढ़ वर्ष।",
                    },
                    {
                        "en": "That range decides how personal a placement can possibly be. Everyone born within a two-day window shares your Moon sign; everyone born within a month shares your Sun; everyone born within a year shares your Jupiter; and half a school year of children shares your Saturn. Speed is the honest measure of how much a placement can single anybody out.",
                        "hi": "यही परास तय करती है कि कोई स्थिति ज़्यादा से ज़्यादा कितनी निजी हो सकती है। दो दिन के भीतर जन्मा हर व्यक्ति आपकी चंद्र-राशि साझा करता है; एक महीने के भीतर जन्मा हर व्यक्ति आपका सूर्य; एक वर्ष के भीतर जन्मा हर व्यक्ति आपका गुरु; और स्कूल की आधी कक्षा आपका शनि। किसी स्थिति से किसी को कितना अलग पहचाना जा सकता है — गति ही उसका ईमानदार पैमाना है।",
                    },
                    {
                        "en": "It also explains why the lagna carries so much weight. It moves through all twelve signs every single day, so it is the one part of the chart that separates two babies born in the same city the same morning.",
                        "hi": "इसी से यह भी समझ आता है कि लग्न पर इतना भार क्यों है। वह हर एक दिन में बारहों राशियाँ पार कर जाता है, इसलिए एक ही शहर में एक ही सुबह जन्मे दो शिशुओं को अलग करने वाला वही एक हिस्सा है।",
                    },
                ),
            ),
            Section(
                heading={"en": "Who owns which sign", "hi": "किस राशि का स्वामी कौन"},
                body=(
                    {
                        "en": "Each of the seven visible grahas rules one or two rashis: Mars takes Mesha and Vrishchika, Venus Vrishabha and Tula, Mercury Mithuna and Kanya, Jupiter Dhanu and Meena, Saturn Makara and Kumbha. The Moon rules Karka alone and the Sun Simha alone. Rahu and Ketu rule nothing — they own no sign, which is part of why the tradition treats them as unlike the rest.",
                        "hi": "सात दृश्य ग्रहों में हर एक एक या दो राशियों का स्वामी है: मंगल के पास मेष और वृश्चिक, शुक्र के पास वृषभ और तुला, बुध के पास मिथुन और कन्या, गुरु के पास धनु और मीन, शनि के पास मकर और कुंभ। चंद्रमा अकेले कर्क का स्वामी है और सूर्य अकेले सिंह का। राहु-केतु किसी के स्वामी नहीं — उनके पास कोई राशि नहीं, और यह भी एक कारण है कि परंपरा उन्हें बाक़ी से अलग मानती है।",
                    },
                    {
                        "en": "The map is not arbitrary: it fans out from Karka and Simha, the Moon's and the Sun's, with Mercury next on both sides, then Venus, then Mars, then Jupiter, then Saturn at the far end. Learn it once as that fan and you will not need to look it up again — and you will need it, because house rulership in chapter 18 is entirely built on it.",
                        "hi": "यह नक़्शा मनमाना नहीं है: यह कर्क और सिंह से — यानी चंद्रमा और सूर्य से — दोनों ओर फैलता है, दोनों तरफ़ अगला बुध, फिर शुक्र, फिर मंगल, फिर गुरु, और सबसे दूर छोर पर शनि। एक बार इसी फैलाव की तरह याद कर लीजिए, दोबारा देखने की ज़रूरत नहीं पड़ेगी — और ज़रूरत पड़ेगी ज़रूर, क्योंकि अध्याय 18 का भाव-स्वामित्व पूरी तरह इसी पर खड़ा है।",
                    },
                ),
            ),
            Section(
                heading={"en": "What your chart records for each", "hi": "कुंडली हर ग्रह के लिए क्या दर्ज करती है"},
                body=(
                    {
                        "en": "For every one of the nine, this app computes and shows the same six things: the rashi, the exact degree within it, the house, the nakshatra and pada, whether the graha is retrograde, and whether it is combust. Nothing is scored, ranked or graded.",
                        "hi": "नौ में से हर एक के लिए यह ऐप वही छह बातें गिनकर दिखाती है: राशि, उसमें ठीक अंश, भाव, नक्षत्र और पाद, ग्रह वक्री है या नहीं, और अस्त है या नहीं। किसी को अंक, श्रेणी या ग्रेड नहीं दिया जाता।",
                    },
                    {
                        "en": "You will meet other vocabulary elsewhere — exaltation, debilitation, strength scores out of some total. Those are real parts of the tradition and you are entitled to read about them, but they are judgements layered on the measurement, and a number that grades your chart is the easiest thing in this subject to sell fear with. This app reports positions and stops there.",
                        "hi": "और कहीं आपको दूसरी शब्दावली भी मिलेगी — उच्च, नीच, किसी कुल में से बल के अंक। ये परंपरा के असली हिस्से हैं और इन्हें पढ़ने का आपको पूरा हक़ है, पर ये माप के ऊपर लगे निर्णय हैं, और कुंडली को अंक देने वाली संख्या इस विषय में डर बेचने का सबसे आसान औज़ार है। यह ऐप स्थितियाँ बताती है और वहीं रुक जाती है।",
                    },
                ),
            ),
        ),
        personalise=P.graha_positions,
    ),
    Chapter(
        slug="sun-and-moon",
        part=PART_GRAHAS,
        title={"en": "Sun and Moon", "hi": "सूर्य और चंद्र"},
        summary={
            "en": "The two lights, and the distance between them that names the day.",
            "hi": "दो प्रकाश, और उनके बीच की दूरी जो दिन का नाम रखती है।",
        },
        minutes=7,
        level="basic",
        sections=(
            Section(
                heading={"en": "The two lights", "hi": "दो प्रकाश"},
                body=(
                    {
                        "en": "The Sun and Moon are called the luminaries. The tradition reads the Sun as the steady self and the Moon as the moving mind — the part of you that changes with the week. In Indian practice the Moon matters more than the Sun, which is why you are asked for your rashi and not your sun sign.",
                        "hi": "सूर्य और चंद्र को ज्योतिर्पिंड कहा जाता है। परंपरा सूर्य को स्थिर आत्म और चंद्र को चलायमान मन की तरह पढ़ती है — वह हिस्सा जो हफ़्ते के साथ बदलता है। भारतीय व्यवहार में चंद्रमा सूर्य से ज़्यादा मायने रखता है, इसीलिए आपसे राशि पूछी जाती है, सूर्य-राशि नहीं।",
                    },
                    {
                        "en": "They are also the only two grahas that never turn retrograde, and the only two that rule a single sign each. In a system built on symmetry, that pairing is not decoration — most of the structure you will meet later is arranged around these two.",
                        "hi": "ये दोनों ही ऐसे ग्रह हैं जो कभी वक्री नहीं होते, और यही दो हैं जिनके पास एक-एक राशि का स्वामित्व है। सममिति पर बनी व्यवस्था में यह जोड़ी सजावट नहीं है — आगे मिलने वाली अधिकांश बनावट इन्हीं दो के इर्द-गिर्द सजी है।",
                    },
                ),
            ),
            Section(
                heading={"en": "The Sun: a degree a day", "hi": "सूर्य: दिन का एक अंश"},
                body=(
                    {
                        "en": "The Sun moves through the zodiac at almost exactly one degree a day, taking about thirty days to cross a sign and a year to complete the circle. Its ingress into a new sign is called a sankranti, and Makara Sankranti — the Sun's entry into Makara — is the one most of the country marks.",
                        "hi": "सूर्य राशिचक्र में लगभग ठीक एक अंश प्रतिदिन चलता है, एक राशि क़रीब तीस दिन में पार करता है और पूरा चक्र एक वर्ष में। किसी नई राशि में उसके प्रवेश को संक्रांति कहते हैं, और मकर संक्रांति — सूर्य का मकर में प्रवेश — वही है जिसे देश का बड़ा हिस्सा मनाता है।",
                    },
                    {
                        "en": "Because it is that regular, your Sun sign is almost fixed by your birth date alone; the time of day only matters if you were born on a day the Sun changed signs. That is also what makes it useless for telling two people apart — an entire month of births shares it.",
                        "hi": "इतनी नियमित चाल के कारण आपकी सूर्य-राशि लगभग सिर्फ़ जन्म-तारीख़ से तय हो जाती है; दिन का समय तभी मायने रखता है जब आप उसी दिन जन्मे हों जिस दिन सूर्य ने राशि बदली। और इसी से वह दो लोगों में फ़र्क़ करने के काम की नहीं रहती — पूरे महीने के जन्म उसे साझा करते हैं।",
                    },
                ),
            ),
            Section(
                heading={"en": "The Moon: the fastest thing on the chart", "hi": "चंद्रमा: कुंडली की सबसे तेज़ चाल"},
                body=(
                    {
                        "en": "The Moon covers about thirteen degrees a day — thirteen times the Sun's pace. It crosses a rashi in roughly two and a quarter days and a nakshatra in about one day, and completes the whole circle in about 27.3 days.",
                        "hi": "चंद्रमा रोज़ क़रीब तेरह अंश तय करता है — सूर्य की गति से तेरह गुना। एक राशि वह लगभग सवा दो दिन में पार करता है और एक नक्षत्र लगभग एक दिन में, और पूरा चक्र क़रीब 27.3 दिन में।",
                    },
                    {
                        "en": "Its speed is not constant, though: the Moon's orbit is an ellipse, so it runs between roughly 12 and 15 degrees a day. That variation is the source of a great deal of calendar trouble later — it is why a tithi is not a fixed number of hours, and why festival dates sometimes disagree between panchangs.",
                        "hi": "पर उसकी गति एक-सी नहीं है: चंद्रमा की कक्षा दीर्घवृत्त है, इसलिए वह मोटे तौर पर रोज़ 12 से 15 अंश के बीच चलता है। यही उतार-चढ़ाव आगे पंचांग की बहुत सारी उलझन की जड़ है — इसी से तिथि घंटों की कोई निश्चित संख्या नहीं होती, और इसी से कभी-कभी दो पंचांगों में त्योहार की तारीख़ अलग हो जाती है।",
                    },
                    {
                        "en": "Because it moves so fast, the Moon is the one body that makes an hour of birth time matter for something other than the lagna. Two hours of error can push it into the next nakshatra, and that changes your dasha timeline — chapter 22 follows that thread.",
                        "hi": "इतनी तेज़ चाल के कारण चंद्रमा ही वह पिंड है जिसके लिए जन्म समय का एक घंटा लग्न के अलावा भी मायने रखता है। दो घंटे की चूक उसे अगले नक्षत्र में धकेल सकती है, और उससे आपकी दशा की समय-रेखा बदल जाती है — अध्याय 22 इसी धागे को पकड़ता है।",
                    },
                ),
            ),
            Section(
                heading={"en": "The gap between them", "hi": "उनके बीच की दूरी"},
                body=(
                    {
                        "en": "The angle between Sun and Moon is the single most used number in the Indian calendar. Every 12 degrees of it is one tithi; 180 degrees is a full moon; zero is a new moon. The whole festival calendar rests on that one measurement.",
                        "hi": "सूर्य और चंद्र के बीच का कोण भारतीय पंचांग की सबसे ज़्यादा इस्तेमाल होने वाली संख्या है। उसके हर 12 अंश की एक तिथि; 180 अंश पर पूर्णिमा; शून्य पर अमावस्या। पूरा त्योहार-पंचांग इसी एक माप पर टिका है।",
                    },
                    {
                        "en": "Thirty tithis make a lunar month, split into two halves of fifteen: shukla paksha while the Moon brightens from new to full, krishna paksha while it darkens back. Say “Shukla Ekadashi” and you have named the eleventh tithi of the brightening half — a position, stated to within about a day.",
                        "hi": "तीस तिथियों का एक चांद्र मास बनता है, जो पंद्रह-पंद्रह के दो पक्षों में बँटा है: अमावस्या से पूर्णिमा तक बढ़ते चंद्रमा का शुक्ल पक्ष, और लौटते अँधेरे का कृष्ण पक्ष। “शुक्ल एकादशी” कहते ही आपने बढ़ते पक्ष की ग्यारहवीं तिथि बता दी — लगभग एक दिन की परिशुद्धता वाली एक स्थिति।",
                    },
                    {
                        "en": "It is worth noticing how much of Indian public life runs on this one subtraction. Ekadashi fasts, Purnima and Amavasya observances, the date of nearly every festival: all of it is the Moon's longitude minus the Sun's, divided by twelve.",
                        "hi": "ध्यान देने लायक़ है कि भारतीय सार्वजनिक जीवन का कितना बड़ा हिस्सा इसी एक घटाव पर चलता है। एकादशी के व्रत, पूर्णिमा और अमावस्या के अनुष्ठान, लगभग हर त्योहार की तारीख़: सब कुछ चंद्रमा के देशांतर में से सूर्य का देशांतर घटाकर, बारह से भाग देकर।",
                    },
                ),
            ),
            Section(
                heading={"en": "Why Indian practice leads with the Moon", "hi": "भारतीय परंपरा चंद्रमा से क्यों चलती है"},
                body=(
                    {
                        "en": "Three of the most-used things in this tradition come from the Moon and nothing else: your janma nakshatra, the starting point of your entire dasha timeline, and the daily panchang. The Sun anchors the year; the Moon anchors almost everything anyone actually consults.",
                        "hi": "इस परंपरा की तीन सबसे ज़्यादा काम आने वाली चीज़ें केवल चंद्रमा से आती हैं: आपका जन्म नक्षत्र, आपकी पूरी दशा-रेखा का आरंभ-बिंदु, और रोज़ का पंचांग। सूर्य वर्ष को थामता है; चंद्रमा लगभग वह सब थामता है जिसे लोग सचमुच देखते हैं।",
                    },
                    {
                        "en": "So when an Indian source and a Western one describe you differently, the difference is usually not interpretation at all. One is reading a body that moves a degree a day, the other one that moves thirteen — and they are also measuring from different zero points, as chapter 3 explained.",
                        "hi": "इसलिए कोई भारतीय स्रोत और कोई पाश्चात्य स्रोत आपका वर्णन अलग-अलग करें, तो फ़र्क़ प्रायः व्याख्या का होता ही नहीं। एक ऐसे पिंड को पढ़ रहा है जो रोज़ एक अंश चलता है, दूसरा उसे जो तेरह — और दोनों अलग शून्य-बिंदुओं से भी नाप रहे हैं, जैसा अध्याय 3 में देखा।",
                    },
                ),
                aside={
                    "en": "When an Indian relative asks “what is your rashi”, they mean the Moon's. Your chart screen shows it under the Moon, and the Sun's separately.",
                    "hi": "कोई घर का बुज़ुर्ग “तुम्हारी राशि क्या है” पूछे तो मतलब चंद्र-राशि से होता है। आपकी कुंडली स्क्रीन उसे चंद्रमा के नीचे दिखाती है, और सूर्य वाली अलग से।",
                },
            ),
        ),
        personalise=P.luminaries,
    ),
    Chapter(
        slug="mars-and-mercury",
        part=PART_GRAHAS,
        title={"en": "Mars and Mercury", "hi": "मंगल और बुध"},
        summary={
            "en": "The fast inner pair, and the manglik business.",
            "hi": "तेज़ चलने वाली भीतरी जोड़ी, और मांगलिक का धंधा।",
        },
        minutes=5,
        level="basic",
        sections=(
            Section(
                heading={"en": "Mars", "hi": "मंगल"},
                body=(
                    {
                        "en": "Mars is read as drive, edge and the will to act. It is also the graha with the worst reputation in popular practice, because of manglik dosha — a configuration that has become a product sold to frighten families, particularly about women and marriage.",
                        "hi": "मंगल को प्रेरणा, धार और करने की इच्छा की तरह पढ़ा जाता है। लोक-व्यवहार में सबसे बदनाम ग्रह भी यही है, मांगलिक दोष के कारण — एक ऐसी स्थिति जो अब परिवारों को डराने के लिए बिकने वाला सामान बन चुकी है, ख़ासकर स्त्रियों और विवाह के मामले में।",
                    },
                    {
                        "en": "In the sky it is unremarkable: Mars circles the zodiac in about 22 months, spending roughly six weeks in a sign, and turns retrograde for about two months once every couple of years. It rules Mesha and Vrishchika, and the tradition assigns it the sharper end of the vocabulary — effort, conflict, surgery, land, brothers.",
                        "hi": "आकाश में उसमें ख़ास कुछ नहीं: मंगल राशिचक्र का चक्कर क़रीब 22 महीनों में पूरा करता है, एक राशि में लगभग छह हफ़्ते रहता है, और हर दो-एक वर्ष में क़रीब दो महीने के लिए वक्री होता है। वह मेष और वृश्चिक का स्वामी है, और परंपरा उसे शब्दावली का तीखा सिरा देती है — श्रम, संघर्ष, शल्य, भूमि, भाई।",
                    },
                ),
            ),
            Section(
                heading={"en": "The manglik claim, stated plainly", "hi": "मांगलिक का दावा, साफ़-साफ़"},
                body=(
                    {
                        "en": "The rule itself is simple arithmetic: Mars falling in the 1st, 2nd, 4th, 7th, 8th or 12th house is called manglik or mangal dosha — and schools disagree even about which of those houses count, and about whether to reckon from the lagna, the Moon or Venus. Anyone can compute it in a second, and this app shows you the house Mars is in, so you can too.",
                        "hi": "नियम अपने आप में मामूली गणित है: मंगल 1, 2, 4, 7, 8 या 12वें भाव में पड़े तो उसे मांगलिक या मंगल दोष कहा जाता है — और इनमें कौन से भाव गिने जाएँ, तथा गिनती लग्न से हो, चंद्रमा से या शुक्र से, इस पर परंपराएँ आपस में ही अलग-अलग हैं। इसे कोई भी पल भर में गिन सकता है, और यह ऐप आपको मंगल का भाव दिखाती है, तो आप भी।",
                    },
                    {
                        "en": "The configuration is computable and real. The claim that it causes a specific misfortune, and that a payment removes it, is neither.",
                        "hi": "वह स्थिति गणनीय है और असली है। यह दावा कि उससे कोई ख़ास दुर्भाग्य आता है, और यह कि पैसा उसे हटा देता है — इनमें से कोई भी न गणनीय है न असली।",
                    },
                    {
                        "en": "It is worth knowing that the schools disagreeing about the rule is itself informative. A configuration whose very definition changes between traditions cannot support the weight of a called-off engagement, and the sheer number of people who are manglik on one definition and not on another should settle the matter for anybody counting.",
                        "hi": "यह जान लेना काम का है कि नियम पर परंपराओं का आपस में न मिलना ही अपने में एक सूचना है। जिस स्थिति की परिभाषा ही परंपरा-दर-परंपरा बदल जाती हो, वह किसी टूटे रिश्ते का भार नहीं उठा सकती — और जितने लोग एक परिभाषा से मांगलिक हैं और दूसरी से नहीं, वह गिनती ही मामला तय कर देनी चाहिए।",
                    },
                ),
                aside={
                    "en": "Chapter 30 returns to this. It is the clearest example of a real measurement turned into a lever.",
                    "hi": "अध्याय 30 इस पर लौटता है। किसी असली माप को दबाव के औज़ार में बदलने का यह सबसे साफ़ उदाहरण है।",
                },
            ),
            Section(
                heading={"en": "Mercury", "hi": "बुध"},
                body=(
                    {
                        "en": "Mercury never strays far from the Sun — it is the innermost planet, so from Earth it always appears close to it. That is why Mercury is combust more often than any other graha, and why the tradition ties it to speech, exchange and calculation.",
                        "hi": "बुध सूर्य से कभी दूर नहीं जाता — वह सबसे भीतरी ग्रह है, इसलिए पृथ्वी से हमेशा सूर्य के पास ही दिखता है। इसी से बुध बाक़ी सब ग्रहों से ज़्यादा बार अस्त होता है, और इसी से परंपरा उसे वाणी, विनिमय और गणना से जोड़ती है।",
                    },
                    {
                        "en": "Its maximum separation from the Sun is about 28 degrees, which has a practical consequence: Mercury can only ever be in the same sign as your Sun, or one on either side. Check any chart and you will find that holds — it is a good first test of whether a chart was computed or invented.",
                        "hi": "सूर्य से उसकी अधिकतम दूरी क़रीब 28 अंश है, और इसका एक व्यावहारिक नतीजा है: बुध या तो आपके सूर्य वाली राशि में होगा, या उसके किसी एक ओर की राशि में। किसी भी कुंडली में जाँच लीजिए, यह बात टिकेगी — कुंडली गिनी गई है या गढ़ी गई, इसकी यह अच्छी पहली परीक्षा है।",
                    },
                ),
            ),
            Section(
                heading={"en": "The retrograde Mercury industry", "hi": "वक्री बुध का कारोबार"},
                body=(
                    {
                        "en": "Mercury turns retrograde about three times a year for around three weeks at a time, which means roughly one day in six is a “Mercury retrograde” day. That frequency is exactly what makes it such reliable content: something goes wrong for everybody about that often.",
                        "hi": "बुध साल में क़रीब तीन बार, हर बार लगभग तीन हफ़्तों के लिए वक्री होता है — यानी हर छह में से क़रीब एक दिन “बुध वक्री” का दिन है। यही आवृत्ति उसे इतना भरोसेमंद विषय बनाती है: लगभग उतनी ही बार सबका कुछ न कुछ बिगड़ता ही है।",
                    },
                    {
                        "en": "And since the transiting sky is identical for everyone alive at that moment, nothing read from it alone is about you in particular. Chapter 12 explains what retrograde motion actually is, and chapter 26 explains why transits are the least personal thing in the subject.",
                        "hi": "और चूँकि उस क्षण का गोचर आकाश जीवित हर व्यक्ति के लिए एक ही है, अकेले उसी से पढ़ी गई कोई बात ख़ास आपके बारे में नहीं होती। अध्याय 12 बताता है कि वक्री गति असल में है क्या, और अध्याय 26 कि गोचर इस विषय की सबसे कम निजी चीज़ क्यों है।",
                    },
                ),
            ),
        ),
        personalise=P.mars_mercury,
    ),
    Chapter(
        slug="jupiter-and-venus",
        part=PART_GRAHAS,
        title={"en": "Jupiter and Venus", "hi": "गुरु और शुक्र"},
        summary={
            "en": "The two the tradition calls benefics — and what that word does not mean.",
            "hi": "जिन दो को परंपरा शुभ कहती है — और उस शब्द का अर्थ क्या नहीं है।",
        },
        minutes=5,
        level="basic",
        sections=(
            Section(
                heading={"en": "Benefic is not a promise", "hi": "शुभ होना वादा नहीं है"},
                body=(
                    {
                        "en": "Jupiter and Venus are classed as benefics: Jupiter as expansion and counsel, Venus as pleasure, art and partnership. The word means the tradition reads their emphasis as easy rather than abrasive. It does not mean their periods are pleasant or their placements lucky.",
                        "hi": "गुरु और शुक्र शुभ ग्रह गिने जाते हैं: गुरु विस्तार और परामर्श की तरह, शुक्र सुख, कला और संबंध की तरह। इस शब्द का अर्थ इतना है कि परंपरा उनके झुकाव को खुरदुरे के बजाय सहज पढ़ती है। इसका अर्थ यह नहीं कि उनकी दशाएँ सुखद होती हैं या उनकी स्थिति भाग्यशाली।",
                    },
                    {
                        "en": "The full four-way split is worth knowing because you will meet it constantly: Jupiter and Venus are natural benefics, Saturn and Mars natural malefics, the Sun mildly malefic, and Mercury and the Moon take their colour from what they sit with — the Moon read as benefic when bright and less so when close to new.",
                        "hi": "पूरा चौतरफ़ा बँटवारा जान लेना काम का है, क्योंकि वह बार-बार मिलेगा: गुरु और शुक्र नैसर्गिक शुभ, शनि और मंगल नैसर्गिक पाप, सूर्य हल्का पाप, और बुध तथा चंद्र अपना रंग साथ वालों से लेते हैं — चंद्रमा पूर्ण के पास शुभ पढ़ा जाता है और अमावस्या के पास कम।",
                    },
                    {
                        "en": "Treat these as labels on a vocabulary, not verdicts on a life. This app does not use them to grade anything, and a reading that turns “malefic” into “bad news” has swapped a technical word for a threat.",
                        "hi": "इन्हें शब्दावली पर लगे लेबल मानिए, किसी जीवन पर सुनाया गया फ़ैसला नहीं। यह ऐप इनसे किसी को अंक नहीं देती, और जो व्याख्या “पाप” को “बुरी ख़बर” में बदल दे, उसने एक तकनीकी शब्द की जगह धमकी रख दी है।",
                    },
                ),
            ),
            Section(
                heading={"en": "Jupiter's twelve years", "hi": "गुरु के बारह वर्ष"},
                body=(
                    {
                        "en": "Jupiter takes about twelve years to go round the zodiac, so it spends roughly a year in each sign. That is slow enough that a whole generation shares a placement, which is a useful reminder of what a chart can and cannot single you out for.",
                        "hi": "गुरु राशिचक्र का चक्कर क़रीब बारह वर्ष में पूरा करता है, यानी हर राशि में लगभग एक वर्ष। यह इतना धीमा है कि एक पूरी पीढ़ी वही स्थिति साझा करती है — और यह याद दिलाने के काम आता है कि कुंडली किस बात पर आपको अलग पहचान सकती है और किस पर नहीं।",
                    },
                    {
                        "en": "That twelve-year rhythm is visible far outside astrology: the Jupiter cycle is why the Kumbh Mela's calendar runs on Jupiter's sign, and why a “Guru year” is a familiar unit in traditional reckoning. It also means your Jupiter return — Jupiter back where it started — lands near ages 12, 24, 36 and so on, for everybody, by construction.",
                        "hi": "बारह वर्ष की यह लय ज्योतिष के बाहर भी दिखती है: गुरु-चक्र के कारण ही कुंभ मेले का हिसाब गुरु की राशि से चलता है, और परंपरागत गणना में “गुरु वर्ष” जाना-पहचाना मान है। इसका यह भी अर्थ है कि आपकी गुरु-वापसी — गुरु का वहीं लौट आना जहाँ से चला था — 12, 24, 36 वर्ष के आसपास पड़ती है, हर किसी के लिए, बनावट से ही।",
                    },
                ),
            ),
            Section(
                heading={"en": "Venus, the evening star", "hi": "शुक्र, संध्या का तारा"},
                body=(
                    {
                        "en": "Venus, like Mercury, is an inner planet and never appears more than about 47 degrees from the Sun. That is why you only ever see it shortly after sunset or shortly before sunrise, and never overhead at midnight — the brightest point in the evening sky is almost always Venus.",
                        "hi": "शुक्र भी बुध की तरह भीतरी ग्रह है और सूर्य से क़रीब 47 अंश से ज़्यादा दूर कभी नहीं दिखता। इसीलिए वह या तो सूर्यास्त के थोड़ी देर बाद दिखता है या सूर्योदय से थोड़ी देर पहले, आधी रात सिर के ऊपर कभी नहीं — शाम के आकाश का सबसे चमकीला बिंदु लगभग हमेशा शुक्र ही होता है।",
                    },
                    {
                        "en": "In chart terms that 47-degree limit means Venus is never more than two signs from your Sun. Together with Mercury's 28 degrees, it is one of the two constraints that make it possible to sanity-check a chart at a glance.",
                        "hi": "कुंडली की भाषा में इस 47 अंश की सीमा का अर्थ है कि शुक्र आपके सूर्य से दो राशि से ज़्यादा दूर कभी नहीं होगा। बुध के 28 अंश के साथ मिलाकर यही वे दो बंधन हैं जिनसे किसी कुंडली को एक नज़र में परखा जा सकता है।",
                    },
                ),
                aside={
                    "en": "Two quick checks on any chart: Mercury within one sign of the Sun, Venus within two. If either fails, something was entered or computed wrongly.",
                    "hi": "किसी भी कुंडली पर दो झटपट जाँच: बुध सूर्य से एक राशि के भीतर, शुक्र दो राशि के भीतर। इनमें से कोई चूके तो कहीं भरने या गिनने में गड़बड़ है।",
                },
            ),
            Section(
                heading={"en": "What these two are actually used for", "hi": "इन दोनों का उपयोग असल में कहाँ होता है"},
                body=(
                    {
                        "en": "Jupiter is the traditional significator — karaka — of teachers, counsel, children and wealth of the non-material sort; Venus of marriage, art, comfort and taste. In practice, that means a reading about a marriage will look at Venus and the 7th house, and a reading about a teacher will look at Jupiter and the 9th.",
                        "hi": "गुरु परंपरा में गुरुजनों, परामर्श, संतान और अभौतिक संपदा का कारक है; शुक्र विवाह, कला, सुख और रुचि का। व्यवहार में इसका अर्थ यह है कि विवाह पर कोई व्याख्या शुक्र और सप्तम भाव देखेगी, और गुरुजन पर कोई व्याख्या गुरु और नवम भाव।",
                    },
                    {
                        "en": "Karakas are a shortcut, and like all shortcuts they can be leaned on too hard. A single graha does not own a subject, and the fact that Venus is the karaka of marriage does not make Venus a verdict on anyone's marriage.",
                        "hi": "कारक एक छोटा रास्ता है, और हर छोटे रास्ते की तरह इस पर ज़रूरत से ज़्यादा भार डाला जा सकता है। कोई एक ग्रह किसी विषय का मालिक नहीं होता, और शुक्र के विवाह-कारक होने से शुक्र किसी के विवाह पर फ़ैसला नहीं बन जाता।",
                    },
                ),
            ),
        ),
        personalise=P.jupiter_venus,
    ),
    Chapter(
        slug="saturn",
        part=PART_GRAHAS,
        title={"en": "Saturn", "hi": "शनि"},
        summary={
            "en": "The slowest visible graha, and the most feared — mostly by marketing.",
            "hi": "दृश्य ग्रहों में सबसे धीमा, और सबसे डरावना — ज़्यादातर प्रचार की वजह से।",
        },
        minutes=5,
        level="basic",
        sections=(
            Section(
                heading={"en": "Thirty years, two and a half per sign", "hi": "तीस वर्ष, ढाई प्रति राशि"},
                body=(
                    {
                        "en": "Saturn takes about 29.5 years to circle the zodiac, so it sits in each sign for roughly two and a half years. It is the slowest of the seven visible grahas, and the last one the unaided eye can follow, which is why the classical list ends with it.",
                        "hi": "शनि राशिचक्र का चक्कर क़रीब 29.5 वर्ष में पूरा करता है, यानी हर राशि में लगभग ढाई वर्ष। सात दृश्य ग्रहों में वही सबसे धीमा है, और नंगी आँख जिसे देख सके ऐसा आख़िरी — इसीलिए शास्त्रीय सूची उसी पर ख़त्म होती है।",
                    },
                    {
                        "en": "Slowness is the whole of Saturn's character in the tradition: time, limit, weight, the things that take as long as they take. It rules Makara and Kumbha, and is read as the graha of labour, delay, structure and old age — the opposite end of the vocabulary from Jupiter's expansion.",
                        "hi": "परंपरा में शनि का पूरा स्वभाव उसी धीमेपन में है: काल, सीमा, भार, वे चीज़ें जो जितना समय लेती हैं उतना लेती ही हैं। वह मकर और कुंभ का स्वामी है, और श्रम, विलंब, ढाँचे तथा वृद्धावस्था के ग्रह की तरह पढ़ा जाता है — गुरु के विस्तार से ठीक उलटा सिरा।",
                    },
                ),
            ),
            Section(
                heading={"en": "What sade sati actually is", "hi": "साढ़ेसाती असल में है क्या"},
                body=(
                    {
                        "en": "Sade sati — the famous seven-and-a-half-year stretch — is simply Saturn transiting the sign before your Moon, the sign of your Moon, and the one after. Three signs, about two and a half years each, and the name is just Hindi for “seven and a half”.",
                        "hi": "साढ़ेसाती — वह मशहूर साढ़े सात वर्ष — बस इतनी है कि शनि आपकी चंद्र-राशि से पिछली राशि, फिर चंद्र-राशि, फिर अगली राशि से गुज़रे। तीन राशियाँ, हर एक क़रीब ढाई वर्ष, और नाम में उसी जोड़ के सिवा कुछ नहीं।",
                    },
                    {
                        "en": "It happens to everyone, roughly three times in a long life, on a fixed schedule anyone can compute. Nothing about it is a personal judgement, and nothing about it needs to be bought off.",
                        "hi": "यह हर किसी के साथ होती है, लंबे जीवन में क़रीब तीन बार, एक तय समय-सारणी पर जिसे कोई भी गिन सकता है। इसमें कुछ भी किसी व्यक्ति पर सुनाया गया फ़ैसला नहीं है, और इसमें कुछ भी ऐसा नहीं जिसे पैसे देकर टालना पड़े।",
                    },
                    {
                        "en": "You can work out your own without any help. Find your Moon's rashi on the chart screen, note the sign before and after it, and check where Saturn is transiting now. If it is in any of those three, you are in it; if not, count forward. The dates are arithmetic on a 29.5-year orbit and nobody owns them.",
                        "hi": "अपनी साढ़ेसाती आप बिना किसी मदद के निकाल सकते हैं। कुंडली स्क्रीन पर अपनी चंद्र-राशि देखिए, उससे पिछली और अगली राशि नोट कीजिए, और देखिए कि शनि इस समय किस राशि में चल रहा है। इन तीन में से किसी में हो तो आप उसी में हैं; न हो तो आगे गिन लीजिए। तारीख़ें 29.5 वर्ष की कक्षा पर लगा गणित हैं और उन पर किसी का मालिकाना नहीं।",
                    },
                ),
                aside={
                    "en": "If an app or an astrologer introduces sade sati with a countdown and a remedy price, you are being sold something. The dates are arithmetic; they are free.",
                    "hi": "कोई ऐप या ज्योतिषी साढ़ेसाती की बात उल्टी गिनती और उपाय के दाम के साथ शुरू करे, तो आपको कुछ बेचा जा रहा है। तारीख़ें गणित हैं; वे मुफ़्त हैं।",
                },
            ),
            Section(
                heading={"en": "The returns nobody sells you", "hi": "वे लौटाव जो कोई नहीं बेचता"},
                body=(
                    {
                        "en": "The same orbit produces another well-known landmark: the Saturn return, when Saturn comes back to the sign it occupied at your birth. Because the period is about 29.5 years, that falls near ages 29–30 and again near 58–59, for everyone born on this planet.",
                        "hi": "उसी कक्षा से एक और जाना-पहचाना पड़ाव बनता है: शनि-वापसी, जब शनि उसी राशि में लौट आता है जिसमें वह आपके जन्म के समय था। अवधि क़रीब 29.5 वर्ष होने से यह 29–30 वर्ष की उम्र के आसपास पड़ती है और फिर 58–59 के आसपास — इस ग्रह पर जन्मे हर व्यक्ति के लिए।",
                    },
                    {
                        "en": "Notice how little that can tell you about a person. A landmark that arrives for a billion people in the same year is a statement about calendars, not about anybody's life. It is a useful test to carry: the slower the graha, the less any statement about it can be specifically yours.",
                        "hi": "ध्यान दीजिए कि इससे किसी व्यक्ति के बारे में कितना कम कहा जा सकता है। जो पड़ाव एक ही वर्ष में करोड़ों लोगों पर आता हो, वह पंचांग के बारे में बयान है, किसी के जीवन के बारे में नहीं। यह जाँच साथ रखने लायक़ है: ग्रह जितना धीमा, उसके बारे में कही गई बात उतनी ही कम ख़ास आपकी।",
                    },
                ),
            ),
            Section(
                heading={"en": "Reading Saturn without doom", "hi": "शनि को डर के बिना पढ़ना"},
                body=(
                    {
                        "en": "The tradition's Saturn vocabulary is genuinely about difficulty — slowness, restriction, work that pays late. But difficulty described is not misfortune predicted, and a period named after Saturn is a label on a stretch of time, not a sentence passed on it.",
                        "hi": "परंपरा की शनि-शब्दावली सचमुच कठिनाई की ही है — धीमापन, बंधन, देर से फल देने वाला श्रम। पर वर्णित कठिनाई भविष्यवाणी की गई दुर्घटना नहीं है, और शनि के नाम पर पड़ी दशा समय के एक हिस्से पर लगा लेबल है, उस पर सुनाई गई सज़ा नहीं।",
                    },
                    {
                        "en": "The practical damage from Saturn is almost never astrological. It is a person told at nineteen that the next seven years will go badly, deciding in advance that effort is pointless. If a reading leaves you smaller than it found you, it has stopped describing the sky — chapter 30 makes that a rule.",
                        "hi": "शनि से होने वाला व्यावहारिक नुक़सान लगभग कभी ज्योतिषीय नहीं होता। वह यह होता है कि उन्नीस वर्ष के किसी व्यक्ति से कह दिया जाए कि अगले सात साल ख़राब जाएँगे, और वह पहले से तय कर ले कि कोशिश बेकार है। कोई व्याख्या आपको उससे छोटा छोड़ जाए जितना उसने आपको पाया था, तो उसने आकाश का वर्णन करना बंद कर दिया है — अध्याय 30 इसे नियम बनाता है।",
                    },
                ),
            ),
        ),
        personalise=P.saturn,
    ),
    Chapter(
        slug="rahu-and-ketu",
        part=PART_GRAHAS,
        title={"en": "Rahu and Ketu", "hi": "राहु और केतु"},
        summary={
            "en": "Two points where orbits cross — not objects, and always exactly opposite.",
            "hi": "दो बिंदु जहाँ कक्षाएँ कटती हैं — पिंड नहीं, और हमेशा ठीक आमने-सामने।",
        },
        minutes=5,
        level="intermediate",
        sections=(
            Section(
                heading={"en": "Where the eclipse comes from", "hi": "ग्रहण कहाँ से आता है"},
                body=(
                    {
                        "en": "The Moon's orbit is tilted about five degrees against the Sun's apparent path. The two points where they cross are Rahu and Ketu. There is nothing there to see. When the Moon happens to be at one of them at new or full moon, you get an eclipse — which is why the tradition describes them as swallowing the lights.",
                        "hi": "चंद्रमा की कक्षा सूर्य के आभासी मार्ग से क़रीब पाँच अंश झुकी है। जिन दो बिंदुओं पर वे कटती हैं, वही राहु और केतु हैं। वहाँ देखने को कुछ नहीं है। अमावस्या या पूर्णिमा को चंद्रमा उनमें से किसी एक पर पड़ जाए तो ग्रहण होता है — इसीलिए परंपरा उन्हें प्रकाशों को निगलने वाला कहती है।",
                    },
                    {
                        "en": "They are always exactly 180 degrees apart, because they are two ends of one line. Locate one and you have located the other — they cannot disagree.",
                        "hi": "वे हमेशा ठीक 180 अंश दूर रहते हैं, क्योंकि वे एक ही रेखा के दो सिरे हैं। एक का पता चल गया तो दूसरे का भी — उनमें मतभेद संभव ही नहीं।",
                    },
                    {
                        "en": "This is the cleanest illustration in the whole subject of the difference between a body and a construct. Rahu is a place where two orbital planes intersect. It has no mass, no surface and no light, and the fact that a tradition can nonetheless read it consistently tells you something honest about what the tradition is doing.",
                        "hi": "पिंड और रचना के फ़र्क़ का इस पूरे विषय में इससे साफ़ उदाहरण नहीं। राहु वह जगह है जहाँ दो कक्षा-तल कटते हैं। उसका न द्रव्यमान है, न सतह, न प्रकाश — और फिर भी परंपरा उसे लगातार पढ़ पाती है, यह तथ्य ईमानदारी से बताता है कि परंपरा कर क्या रही है।",
                    },
                ),
                aside={
                    "en": "They always move backwards through the zodiac, so your chart marks them retrograde. That is their normal state, not an anomaly.",
                    "hi": "वे राशिचक्र में हमेशा पीछे की ओर चलते हैं, इसलिए आपकी कुंडली उन्हें वक्री दिखाती है। यह उनकी सामान्य दशा है, कोई असामान्यता नहीं।",
                },
            ),
            Section(
                heading={"en": "Eighteen and a half years", "hi": "साढ़े अठारह वर्ष"},
                body=(
                    {
                        "en": "The nodal line does not stand still — it drifts backwards around the zodiac, completing a circuit in about 18.6 years and spending roughly a year and a half in each sign. That cycle is why eclipses recur in families of dates, and why eclipse seasons come round about every six months.",
                        "hi": "यह पात-रेखा स्थिर नहीं रहती — वह राशिचक्र में पीछे की ओर सरकती है, क़रीब 18.6 वर्ष में एक चक्कर पूरा करती है और हर राशि में लगभग डेढ़ वर्ष रहती है। इसी चक्र से ग्रहण तारीख़ों के परिवारों में लौटते हैं, और हर छह महीने के आसपास ग्रहण-ऋतु आती है।",
                    },
                    {
                        "en": "So Rahu and Ketu are slow, and everything said in chapter 10 about slow grahas applies here twice over: everyone born within about eighteen months shares your nodal placement exactly.",
                        "hi": "यानी राहु-केतु धीमे हैं, और अध्याय 10 में धीमे ग्रहों के बारे में जो कहा गया वह यहाँ दुगुना लागू होता है: क़रीब डेढ़ वर्ष के भीतर जन्मा हर व्यक्ति आपकी राहु-केतु स्थिति ठीक-ठीक साझा करता है।",
                    },
                ),
            ),
            Section(
                heading={"en": "Mean and true", "hi": "मध्यम और स्पष्ट"},
                body=(
                    {
                        "en": "There are two conventions: the mean node, a smooth average, and the true node, which wobbles. They differ by a few arc-minutes. Mainstream Indian practice reads the mean node — which is why two charts drawn on different conventions disagree slightly, and neither of them is wrong.",
                        "hi": "दो परंपराएँ हैं: मध्यम पात, जो सधा हुआ औसत है, और स्पष्ट पात, जो डोलता है। दोनों में कुछ कलाओं का अंतर होता है। मुख्यधारा की भारतीय परंपरा मध्यम पात लेती है — इसीलिए अलग-अलग परंपरा पर बनी दो कुंडलियाँ थोड़ी अलग होती हैं, और उनमें कोई ग़लत नहीं।",
                    },
                    {
                        "en": "This app uses the mean node, and always reports Rahu and Ketu as retrograde because in that model they only ever move backwards. The true node occasionally turns direct for short stretches, which is one visible sign of which convention a chart was drawn on.",
                        "hi": "यह ऐप मध्यम पात लेती है, और राहु-केतु को हमेशा वक्री बताती है क्योंकि उस मॉडल में वे केवल पीछे ही चलते हैं। स्पष्ट पात कभी-कभी थोड़े समय के लिए मार्गी हो जाता है — किसी कुंडली में यह देखकर बताया जा सकता है कि वह किस परंपरा पर बनी है।",
                    },
                ),
            ),
            Section(
                heading={"en": "The kaal sarp product", "hi": "कालसर्प नाम का सामान"},
                body=(
                    {
                        "en": "When all seven visible grahas happen to fall on one side of the Rahu–Ketu axis, popular practice calls it kaal sarp dosha. The configuration is perfectly real and takes one glance at a chart to verify: the axis is a straight line, and either everything is on one side of it or something is not.",
                        "hi": "जब सातों दृश्य ग्रह संयोग से राहु-केतु धुरी के एक ही ओर पड़ जाएँ, तो लोक-व्यवहार उसे कालसर्प दोष कहता है। यह स्थिति बिल्कुल असली है और कुंडली पर एक नज़र में जाँची जा सकती है: धुरी एक सीधी रेखा है, या तो सब कुछ उसके एक ओर है या कुछ नहीं है।",
                    },
                    {
                        "en": "What has been built on top of it is not real. It appears in no classical text of any standing, it arrived in popular practice within living memory, and it exists today mainly as a reason to sell a puja. The measurement is free and checkable; the fear attached to it was manufactured, and recently.",
                        "hi": "उस पर जो कुछ खड़ा किया गया है वह असली नहीं है। किसी प्रतिष्ठित शास्त्रीय ग्रंथ में वह नहीं मिलता, लोक-व्यवहार में वह अभी की पीढ़ियों के भीतर आया, और आज उसका मुख्य अस्तित्व एक पूजा बेचने के कारण के रूप में है। माप मुफ़्त है और जाँचा जा सकता है; उससे जोड़ा गया डर गढ़ा हुआ है, और हाल का।",
                    },
                ),
                aside={
                    "en": "This app will not tell you that you have a dosha. It will show you where Rahu and Ketu are and let you check the claim yourself.",
                    "hi": "यह ऐप आपसे यह नहीं कहेगी कि आपको कोई दोष है। वह राहु-केतु की जगह दिखा देगी और दावे की जाँच आप पर छोड़ देगी।",
                },
            ),
        ),
        personalise=P.nodes,
    ),
    Chapter(
        slug="retrograde-combust",
        part=PART_GRAHAS,
        title={"en": "Retrograde and combustion", "hi": "वक्री और अस्त"},
        summary={
            "en": "Two states with real astronomy behind them, and a lot of fear attached.",
            "hi": "दो अवस्थाएँ, जिनके पीछे असली खगोल है और ऊपर बहुत सारा डर।",
        },
        minutes=5,
        level="intermediate",
        sections=(
            Section(
                heading={"en": "Retrograde is a trick of perspective", "hi": "वक्री होना दृष्टि का खेल है"},
                body=(
                    {
                        "en": "A retrograde planet is not moving backwards. We watch from a moving platform: as Earth overtakes an outer planet on the inside track, that planet appears to loop backwards against the stars for a few weeks, then resume. It is the same illusion as a slower car sliding backwards as you pass it.",
                        "hi": "वक्री ग्रह पीछे नहीं चल रहा होता। हम एक चलते हुए मंच से देख रहे हैं: पृथ्वी जब भीतरी पटरी से किसी बाहरी ग्रह को पार करती है, तो वह ग्रह कुछ हफ़्तों के लिए तारों के सापेक्ष पीछे की ओर घूमता दिखता है, फिर सीधा हो जाता है। यह वही भ्रम है जो किसी धीमी गाड़ी को पार करते समय उसके पीछे सरकने में दिखता है।",
                    },
                    {
                        "en": "Nothing about the planet changes. What changes is our viewing angle.",
                        "hi": "ग्रह में कुछ नहीं बदलता। जो बदलता है वह हमारा देखने का कोण है।",
                    },
                    {
                        "en": "The engine detects it the honest way, by measuring speed: when a graha's longitude is decreasing rather than increasing, the chart marks it retrograde. No table is consulted and no rule is applied — it is the same arithmetic an observatory would do.",
                        "hi": "इंजन इसे ईमानदार तरीक़े से पकड़ता है, गति नापकर: जब किसी ग्रह का देशांतर बढ़ने के बजाय घट रहा हो, कुंडली उसे वक्री दिखा देती है। न कोई सारणी देखी जाती है, न कोई नियम लगाया जाता है — यह वही गणित है जो कोई वेधशाला करेगी।",
                    },
                ),
            ),
            Section(
                heading={"en": "Who can, and how often", "hi": "कौन हो सकता है, और कितनी बार"},
                body=(
                    {
                        "en": "The Sun and Moon never turn retrograde — from Earth we are not overtaking either. Mercury does it about three times a year for three weeks; Venus once every 19 months for about six weeks; Mars once every 26 months for two to three months. Jupiter is retrograde about four months of every year, and Saturn about four and a half.",
                        "hi": "सूर्य और चंद्र कभी वक्री नहीं होते — पृथ्वी से हम इनमें से किसी को पार नहीं कर रहे। बुध साल में क़रीब तीन बार, तीन-तीन हफ़्ते के लिए; शुक्र हर 19 महीने में एक बार, क़रीब छह हफ़्ते; मंगल हर 26 महीने में एक बार, दो से तीन महीने। गुरु हर वर्ष के क़रीब चार महीने वक्री रहता है, और शनि क़रीब साढ़े चार।",
                    },
                    {
                        "en": "Look at those last two numbers again. Roughly a third of everyone alive was born with Jupiter retrograde, and a bit more than a third with Saturn retrograde. A state that common cannot carry a personal verdict, and any reading that treats it as a flaw is describing a third of humanity.",
                        "hi": "उन आख़िरी दो संख्याओं को दोबारा देखिए। जीवित लोगों में क़रीब एक तिहाई गुरु के वक्री रहते जन्मे हैं, और कुछ ज़्यादा ही एक तिहाई शनि के वक्री रहते। इतनी आम अवस्था किसी व्यक्ति पर फ़ैसला नहीं ढो सकती, और जो व्याख्या उसे दोष की तरह ले, वह मानवता के एक तिहाई हिस्से का वर्णन कर रही है।",
                    },
                ),
            ),
            Section(
                heading={"en": "Combustion is proximity", "hi": "अस्त होना निकटता है"},
                body=(
                    {
                        "en": "A graha is combust when it sits close enough to the Sun to be lost in its glare — invisible to an observer. The threshold differs by graha and by school; it is a statement about visibility, not damage.",
                        "hi": "कोई ग्रह तब अस्त होता है जब वह सूर्य के इतने पास हो कि उसकी चमक में खो जाए — देखने वाले को दिखे ही नहीं। यह सीमा हर ग्रह और हर परंपरा में अलग है; यह दिखने की बात है, हानि की नहीं।",
                    },
                    {
                        "en": "This app uses the thresholds most modern panchangs follow: the Moon within 12 degrees of the Sun, Mars 17, Mercury 14, Jupiter 11, Venus 10, Saturn 15. Those exact numbers are worth knowing, because they are the only reason your chart marks a graha combust — you can measure the separation yourself from the degrees on the chart screen and confirm it.",
                        "hi": "यह ऐप वही सीमाएँ लेती है जिन्हें अधिकांश आधुनिक पंचांग मानते हैं: चंद्रमा सूर्य से 12 अंश के भीतर, मंगल 17, बुध 14, गुरु 11, शुक्र 10, शनि 15। ये ठीक-ठीक संख्याएँ जान लेनी चाहिए, क्योंकि आपकी कुंडली किसी ग्रह को अस्त केवल इन्हीं के कारण दिखाती है — कुंडली स्क्रीन पर दिए अंशों से आप अंतर ख़ुद नापकर पुष्टि कर सकते हैं।",
                    },
                    {
                        "en": "Mercury and Venus are combust far more often than anything else, and now you know why: they never get more than 28 and 47 degrees from the Sun in the first place, so a good fraction of that range is inside the threshold.",
                        "hi": "बुध और शुक्र बाक़ी सबसे कहीं ज़्यादा बार अस्त होते हैं, और अब कारण पता है: वे सूर्य से क्रमशः 28 और 47 अंश से आगे जाते ही नहीं, इसलिए उस परास का अच्छा-ख़ासा हिस्सा सीमा के भीतर ही पड़ता है।",
                    },
                ),
                aside={
                    "en": "The tradition does read these as an emphasis turned inward, working out of sight. That is a long way from harm, and this app will not frame it as harm.",
                    "hi": "परंपरा इन्हें भीतर की ओर मुड़े हुए ज़ोर की तरह पढ़ती ज़रूर है, जो नज़र से बाहर काम करता है। वह हानि से बहुत दूर की बात है, और यह ऐप उसे हानि की तरह नहीं रखेगी।",
                },
            ),
            Section(
                heading={"en": "What the chart says and stops saying", "hi": "कुंडली क्या कहती है और कहाँ रुक जाती है"},
                body=(
                    {
                        "en": "Your chart marks both states with a flag and no adjective. Retrograde means the longitude was decreasing; combust means the separation from the Sun was inside the orb above. Both are facts about the sky at your birth minute, and both can be checked against any ephemeris.",
                        "hi": "आपकी कुंडली दोनों अवस्थाओं पर बस एक चिह्न लगाती है, कोई विशेषण नहीं। वक्री का अर्थ है देशांतर घट रहा था; अस्त का अर्थ है सूर्य से दूरी ऊपर दी सीमा के भीतर थी। दोनों आपके जन्म-मिनट के आकाश के तथ्य हैं, और दोनों किसी भी पंचांग-सारणी से मिलाए जा सकते हैं।",
                    },
                    {
                        "en": "What the app will not do is convert a flag into a warning. If you read elsewhere that a combust graha is “destroyed” or a retrograde one “karmic”, you are reading interpretation — often the kind that arrives with a remedy attached. Hold the flag; treat the adjective as someone's opinion.",
                        "hi": "ऐप जो नहीं करेगी वह है इस चिह्न को चेतावनी में बदलना। कहीं और पढ़ें कि अस्त ग्रह “नष्ट” हो गया या वक्री ग्रह “कार्मिक” है, तो आप व्याख्या पढ़ रहे हैं — प्रायः वह क़िस्म जो उपाय साथ लेकर आती है। चिह्न रखिए; विशेषण को किसी की राय मानिए।",
                    },
                ),
            ),
        ),
        personalise=P.marked_grahas,
    ),
)
