"""Part four: the twenty-seven nakshatras.

The oldest layer in the system and the one an Indian reader is most likely to
have met before opening this app — at a temple, in a name, in a wedding date.
These four chapters take it from the arithmetic upward, because the nakshatra is
also where the machinery of part five starts.
"""

from __future__ import annotations

from .. import personalise as P
from ..models import Chapter, Section
from . import PART_NAKSHATRAS

CHAPTERS: tuple[Chapter, ...] = (
    Chapter(
        slug="twenty-seven-nakshatras",
        part=PART_NAKSHATRAS,
        title={"en": "The 27 nakshatras", "hi": "सत्ताईस नक्षत्र"},
        summary={
            "en": "The older layer, and the more distinctively Indian one.",
            "hi": "पुरानी परत, और ज़्यादा विशिष्ट रूप से भारतीय भी।",
        },
        minutes=5,
        level="intermediate",
        sections=(
            Section(
                heading={"en": "One for each day of the Moon", "hi": "चंद्रमा के हर दिन के लिए एक"},
                body=(
                    {
                        "en": "Before the twelve rashis were adopted, Indian astronomy tracked the Moon through 27 nakshatras — roughly one for each day of its journey round the sky. Each is 13 degrees and 20 minutes wide, and 27 of them make exactly 360.",
                        "hi": "बारह राशियाँ अपनाए जाने से पहले भारतीय खगोल चंद्रमा को 27 नक्षत्रों से होकर देखता था — मोटे तौर पर उसकी आकाश-यात्रा के हर दिन के लिए एक। हर नक्षत्र 13 अंश 20 कला चौड़ा है, और सत्ताईस मिलकर ठीक 360 बनते हैं।",
                    },
                    {
                        "en": "They are the older layer, and in daily Indian practice the more used one. A temple asks for your nakshatra, not your sign.",
                        "hi": "यह पुरानी परत है, और रोज़मर्रा के भारतीय व्यवहार में ज़्यादा काम आने वाली भी। मंदिर आपका नक्षत्र पूछता है, राशि नहीं।",
                    },
                    {
                        "en": "The names are old and mostly point at the star group that marks each stretch: Ashwini, Bharani, Krittika, Rohini, and on to Revati. Several are named in the Rig Veda, which puts this scheme centuries ahead of the twelve-sign zodiac in Indian use.",
                        "hi": "नाम पुराने हैं और प्रायः उसी तारा-समूह की ओर इशारा करते हैं जो उस हिस्से पर निशान लगाता है: अश्विनी, भरणी, कृत्तिका, रोहिणी, और आगे रेवती तक। इनमें से कई ऋग्वेद में मिलते हैं, जो इस व्यवस्था को भारतीय प्रयोग में बारह-राशि वाले चक्र से सदियों आगे रखता है।",
                    },
                ),
            ),
            Section(
                heading={"en": "How they sit against the rashis", "hi": "राशियों के सापेक्ष ये कैसे बैठते हैं"},
                body=(
                    {
                        "en": "Twenty-seven does not divide into twelve, so the two grids do not line up. Each rashi of 30 degrees holds two and a quarter nakshatras, which means most nakshatras sit inside one sign but nine of them straddle a boundary — Krittika begins in Mesha and finishes in Vrishabha, and so on round the circle.",
                        "hi": "सत्ताईस बारह से नहीं कटता, इसलिए दोनों जालियाँ आपस में मेल नहीं खातीं। तीस अंश की हर राशि में सवा दो नक्षत्र आते हैं, यानी अधिकांश नक्षत्र किसी एक राशि के भीतर रहते हैं पर नौ सीमा पर फैले होते हैं — कृत्तिका मेष में शुरू होकर वृषभ में ख़त्म होती है, और इसी तरह पूरे चक्र में।",
                    },
                    {
                        "en": "That mismatch is not a flaw. The two systems were built to answer different questions — one divides the Sun's year into twelve, the other the Moon's month into twenty-seven — and a chart carries both because Indian practice needs both.",
                        "hi": "यह बेमेल कोई ख़ामी नहीं है। दोनों व्यवस्थाएँ अलग सवालों के लिए बनी थीं — एक सूर्य के वर्ष को बारह में बाँटती है, दूसरी चंद्रमा के मास को सत्ताईस में — और कुंडली दोनों ढोती है क्योंकि भारतीय व्यवहार को दोनों चाहिए।",
                    },
                ),
            ),
            Section(
                heading={"en": "What they are actually used for", "hi": "इनका उपयोग असल में कहाँ होता है"},
                body=(
                    {
                        "en": "Four things, and you have probably met at least two. Your janma nakshatra names you at a temple and in traditional ceremony. It sets the start of your dasha timeline, which is the whole of part five. It is half of the matching procedure families use before a marriage. And the daily nakshatra is one of the five limbs of the panchang, which is how a muhurta — an auspicious time — is chosen.",
                        "hi": "चार काम, और इनमें से कम से कम दो से आपका सामना हो ही चुका होगा। आपका जन्म नक्षत्र मंदिर और परंपरागत संस्कारों में आपका नाम रखता है। वही आपकी दशा-रेखा का आरंभ तय करता है, जो पूरा पाँचवाँ भाग है। विवाह से पहले परिवार जो मिलान करते हैं, उसका आधा वही है। और दिन का नक्षत्र पंचांग के पाँच अंगों में से एक है, जिससे मुहूर्त निकाला जाता है।",
                    },
                    {
                        "en": "The marriage-matching use deserves a flag now and a proper treatment in chapter 30. The point-scoring system built on nakshatras — the ashtakoot or “36 gunas” — is arithmetic anyone can do, and it has also become a reason to refuse a match. A score out of 36 is not a fact about two people.",
                        "hi": "विवाह-मिलान वाले उपयोग पर अभी एक निशान लगा दीजिए, पूरी बात अध्याय 30 में। नक्षत्रों पर बनी अंक-प्रणाली — अष्टकूट या “36 गुण” — ऐसा गणित है जो कोई भी कर सकता है, और वही रिश्ता ठुकराने का कारण भी बन चुका है। 36 में से मिला अंक दो व्यक्तियों के बारे में तथ्य नहीं है।",
                    },
                ),
            ),
            Section(
                heading={"en": "Twenty-seven or twenty-eight", "hi": "सत्ताईस या अट्ठाईस"},
                body=(
                    {
                        "en": "Older texts sometimes count 28, inserting Abhijit between Uttara Ashadha and Shravana. The 28-fold scheme is genuinely ancient and survives in some ritual contexts, but it breaks the clean 13°20' division, so classical astrology settled on 27 and left Abhijit as a special case used for choosing auspicious times.",
                        "hi": "पुराने ग्रंथ कभी-कभी अट्ठाईस गिनते हैं, उत्तराषाढ़ा और श्रवण के बीच अभिजित जोड़कर। अट्ठाईस वाली व्यवस्था सचमुच प्राचीन है और कुछ अनुष्ठानों में आज भी चलती है, पर उससे 13°20' का साफ़ विभाजन टूट जाता है, इसलिए शास्त्रीय ज्योतिष सत्ताईस पर ठहरा और अभिजित को मुहूर्त के लिए एक विशेष स्थिति की तरह छोड़ दिया।",
                    },
                    {
                        "en": "This app uses 27, equal in width, computed by dividing the sidereal longitude by 13°20'. That is one division, checkable by hand from the degrees printed on your chart.",
                        "hi": "यह ऐप सत्ताईस लेती है, सब बराबर चौड़ाई के, निरयन देशांतर को 13°20' से भाग देकर। यह एक ही भाग है, और आपकी कुंडली पर छपे अंशों से हाथ से जाँचा जा सकता है।",
                    },
                ),
                aside={
                    "en": "Your nakshatra and its pada are on the chart screen for all nine grahas and the lagna, not only the Moon.",
                    "hi": "आपका नक्षत्र और उसका पाद कुंडली स्क्रीन पर नौ ग्रहों और लग्न — सबके लिए है, केवल चंद्रमा के लिए नहीं।",
                },
            ),
        ),
        personalise=P.janma_nakshatra,
    ),
    Chapter(
        slug="padas",
        part=PART_NAKSHATRAS,
        title={"en": "Padas and the 108", "hi": "पाद और 108"},
        summary={
            "en": "Four quarters to a nakshatra, and where that famous number comes from.",
            "hi": "हर नक्षत्र के चार पाद, और वह मशहूर संख्या कहाँ से आती है।",
        },
        minutes=5,
        level="intermediate",
        sections=(
            Section(
                heading={"en": "Three degrees twenty", "hi": "तीन अंश बीस कला"},
                body=(
                    {
                        "en": "Each nakshatra divides into four padas of 3 degrees 20 minutes. That gives 108 padas in the circle — the same 108 that recurs throughout Indian tradition, and not by coincidence.",
                        "hi": "हर नक्षत्र चार पादों में बँटता है, हर पाद 3 अंश 20 कला का। इससे चक्र में 108 पाद बनते हैं — वही 108 जो भारतीय परंपरा में बार-बार लौटता है, और संयोग से नहीं।",
                    },
                    {
                        "en": "The number falls out of the arithmetic rather than being chosen: 27 nakshatras times 4 padas, or equivalently 12 signs times 9 divisions. That second reading is the important one, and the next section follows it.",
                        "hi": "यह संख्या चुनी नहीं गई, गणित से निकल आई है: 27 नक्षत्र गुणा 4 पाद, या उतना ही सही, 12 राशि गुणा 9 विभाग। दूसरा पाठ ही ज़रूरी है, और अगला खंड उसी को पकड़ता है।",
                    },
                ),
            ),
            Section(
                heading={"en": "Where 108 shows up", "hi": "108 कहाँ-कहाँ दिखता है"},
                body=(
                    {
                        "en": "A japa mala has 108 beads. There are 108 Divya Desams, 108 Upanishads in the standard list, 108 repetitions in countless ritual counts. Some of that is deliberate reference to this division of the sky, some of it is later reasoning applied backwards, and the honest answer about which is which is that nobody knows for certain.",
                        "hi": "जप की माला में 108 मनके होते हैं। 108 दिव्य देशम हैं, मानक सूची में 108 उपनिषद, अनगिनत अनुष्ठानों में 108 आवृत्तियाँ। इसमें कुछ इसी आकाश-विभाजन का जान-बूझकर किया गया संदर्भ है, कुछ बाद में उल्टा जोड़ा गया तर्क — और ईमानदार उत्तर यह है कि कौन सा क्या है, यह निश्चित रूप से कोई नहीं जानता।",
                    },
                    {
                        "en": "What is certain is the arithmetic. If you divide the zodiac by the finest unit this tradition routinely uses, you get 108 of them, and this app's engine snaps every longitude to that same 3°20' grid so that rashi, nakshatra, pada and navamsa can never disagree with each other.",
                        "hi": "जो निश्चित है वह गणित है। राशिचक्र को उस सबसे सूक्ष्म इकाई से भाग दीजिए जिसे यह परंपरा नियमित रूप से इस्तेमाल करती है, तो 108 मिलते हैं — और इस ऐप का इंजन हर देशांतर को उसी 3°20' की जाली पर बिठाता है, ताकि राशि, नक्षत्र, पाद और नवांश आपस में कभी न टकराएँ।",
                    },
                ),
            ),
            Section(
                heading={"en": "The naming syllable", "hi": "नामाक्षर"},
                body=(
                    {
                        "en": "The pada decides the syllable a child is traditionally named with. Each of the 108 padas carries a fixed sound — Ashwini's four are Chu, Che, Cho, La — and a traditionally named child gets a first syllable from the pada the Moon occupied at birth.",
                        "hi": "पाद ही तय करता है कि परंपरा से शिशु का नाम किस अक्षर से रखा जाए। 108 पादों में से हर एक पर एक निश्चित ध्वनि है — अश्विनी के चार हैं चू, चे, चो, ला — और परंपरा से नाम पाने वाले शिशु का पहला अक्षर उसी पाद से आता है जिसमें जन्म के समय चंद्रमा था।",
                    },
                    {
                        "en": "This is worth knowing even if you find the practice quaint, because it means a great many Indians are carrying a piece of their chart in their name. If an older relative knows the syllable your naming ceremony used, that is independent evidence about your birth time — sometimes better evidence than the time anybody remembers.",
                        "hi": "यह जान लेना काम का है, चाहे यह चलन आपको पुराना लगे, क्योंकि इसका अर्थ है कि बहुत सारे भारतीय अपनी कुंडली का एक टुकड़ा अपने नाम में लिए घूम रहे हैं। घर का कोई बुज़ुर्ग नामकरण में लिया गया अक्षर जानता हो, तो वह आपके जन्म समय का एक स्वतंत्र प्रमाण है — कभी-कभी उस समय से बेहतर प्रमाण जो किसी को याद है।",
                    },
                ),
            ),
            Section(
                heading={"en": "The pada feeds the navamsa", "hi": "पाद से नवांश बनता है"},
                body=(
                    {
                        "en": "And it feeds the navamsa — the divisional chart read for marriage. This is the same division seen twice: a pada is a quarter of a nakshatra, a navamsa is a ninth of a sign, and both come out to 3°20'. Locate a graha's pada and you have located its navamsa.",
                        "hi": "और इसी से नवांश बनता है — वह विभाग-कुंडली जिसे विवाह के लिए पढ़ा जाता है। यह एक ही विभाजन को दो बार देखना है: पाद नक्षत्र का चौथाई है, नवांश राशि का नवाँ हिस्सा, और दोनों 3°20' पर आते हैं। किसी ग्रह का पाद पता चल गया तो उसका नवांश भी पता चल गया।",
                    },
                    {
                        "en": "Chapter 28 works through what the navamsa is for. The reason to see the connection now is that it explains why padas are treated as significant at all: they are the hinge between the nakshatra system and the divisional charts.",
                        "hi": "नवांश किस काम आता है, यह अध्याय 28 खोलता है। यह संबंध अभी देख लेने का कारण यह है कि इसी से समझ आता है कि पाद को महत्व क्यों दिया जाता है: वही नक्षत्र-व्यवस्था और विभाग-कुंडलियों के बीच की कब्ज़ा है।",
                    },
                ),
            ),
            Section(
                heading={"en": "The finest thing your chart claims", "hi": "कुंडली का सबसे सूक्ष्म दावा"},
                body=(
                    {
                        "en": "A pada is the smallest division this app reports, and that makes it the most fragile. The Moon crosses one in about six hours, so a birth time out by that much moves it. The lagna crosses one in about eight minutes — so for the lagna's pada, even a carefully remembered time is not enough.",
                        "hi": "पाद इस ऐप का बताया सबसे छोटा विभाजन है, और इसीलिए सबसे नाज़ुक भी। चंद्रमा एक पाद क़रीब छह घंटे में पार करता है, यानी इतनी चूक उसे हिला देती है। लग्न एक पाद क़रीब आठ मिनट में पार कर जाता है — इसलिए लग्न के पाद के लिए ध्यान से याद रखा गया समय भी काफ़ी नहीं।",
                    },
                    {
                        "en": "So use padas the way you would use any high-precision measurement: only when the input justifies it. If your birth time came off a hospital record to the minute, the pada is meaningful. If it came from a family memory of “just after sunrise”, read the nakshatra and leave the pada alone.",
                        "hi": "इसलिए पाद का उपयोग वैसे ही कीजिए जैसे किसी भी उच्च-परिशुद्धता वाले माप का: तभी जब इनपुट उसका हक़दार हो। आपका जन्म समय अस्पताल के रिकॉर्ड से मिनट तक मिला हो तो पाद अर्थपूर्ण है। और अगर वह “सूर्योदय के ठीक बाद” जैसी पारिवारिक स्मृति से आया हो, तो नक्षत्र पढ़िए और पाद छोड़ दीजिए।",
                    },
                ),
                aside={
                    "en": "Rule of thumb: the finer the division, the more birth-time accuracy it demands. Rashi tolerates hours, nakshatra tolerates an hour, pada tolerates minutes.",
                    "hi": "मोटा नियम: विभाजन जितना सूक्ष्म, जन्म समय की परिशुद्धता उतनी ज़्यादा चाहिए। राशि घंटे झेल लेती है, नक्षत्र एक घंटा, पाद केवल मिनट।",
                },
            ),
        ),
        personalise=P.pada_navamsa,
    ),
    Chapter(
        slug="nakshatra-lords",
        part=PART_NAKSHATRAS,
        title={"en": "Nakshatra lords", "hi": "नक्षत्र स्वामी"},
        summary={
            "en": "A nine-graha cycle repeating three times — the hinge the dasha system turns on.",
            "hi": "नौ ग्रहों का चक्र, तीन बार दोहराया हुआ — दशा-पद्धति इसी कब्ज़े पर घूमती है।",
        },
        minutes=4,
        level="intermediate",
        sections=(
            Section(
                heading={"en": "Ketu, Venus, Sun, Moon…", "hi": "केतु, शुक्र, सूर्य, चंद्र…"},
                body=(
                    {
                        "en": "The 27 nakshatras are assigned lords in a fixed nine-graha cycle: Ketu, Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury — repeated three times. Ashwini is Ketu's, Bharani is Venus's, and so on.",
                        "hi": "सत्ताईस नक्षत्रों के स्वामी नौ ग्रहों के एक निश्चित चक्र से मिलते हैं: केतु, शुक्र, सूर्य, चंद्र, मंगल, राहु, गुरु, शनि, बुध — यही क्रम तीन बार। अश्विनी केतु की, भरणी शुक्र की, और आगे इसी तरह।",
                    },
                    {
                        "en": "This ordering is not decoration. It is what makes the Vimshottari dasha work, and you will meet it again in chapter 23.",
                        "hi": "यह क्रम सजावट नहीं है। यही विम्शोत्तरी दशा को चलाता है, और अध्याय 23 में यह फिर मिलेगा।",
                    },
                ),
            ),
            Section(
                heading={"en": "Three rounds of nine", "hi": "नौ के तीन दौर"},
                body=(
                    {
                        "en": "Because 27 is three times nine, the cycle completes exactly three times around the zodiac with nothing left over. The tenth nakshatra, Magha, is ruled by Ketu again; so is the nineteenth, Moola. Each graha therefore owns exactly three nakshatras, evenly spaced 120 degrees apart.",
                        "hi": "चूँकि 27 नौ का तीन गुना है, यह चक्र राशिचक्र में ठीक तीन बार पूरा होता है और कुछ बचता नहीं। दसवाँ नक्षत्र मघा फिर केतु का है; उन्नीसवाँ मूल भी। यानी हर ग्रह के पास ठीक तीन नक्षत्र हैं, और वे 120-120 अंश की बराबर दूरी पर हैं।",
                    },
                    {
                        "en": "That regularity means you can work out any nakshatra's lord by counting rather than looking it up. Number the nakshatras from Ashwini as 1, take the remainder after dividing by 9, and read off the cycle. Nakshatra 14, Chitra: 14 minus 9 is 5, and the fifth in the cycle is Mars.",
                        "hi": "इस नियमितता का अर्थ है कि किसी भी नक्षत्र का स्वामी सूची देखे बिना, गिनकर निकाला जा सकता है। अश्विनी को 1 मानकर नक्षत्रों की गिनती कीजिए, 9 से भाग देकर शेष लीजिए, और चक्र में वहीं पढ़ लीजिए। चौदहवाँ नक्षत्र चित्रा: 14 में से 9 गया, बचा 5, और चक्र में पाँचवाँ मंगल है।",
                    },
                ),
            ),
            Section(
                heading={"en": "Why this particular order", "hi": "यही क्रम क्यों"},
                body=(
                    {
                        "en": "The honest answer is that the texts state it rather than derive it. It is not the order of the weekdays, nor of orbital speed, nor of the rashi rulerships you learned in chapter 6. It is its own sequence, handed down, and the dasha years attached to each graha — Ketu 7, Venus 20, Sun 6 — are handed down with it.",
                        "hi": "ईमानदार उत्तर यह है कि ग्रंथ इसे बताते हैं, निकालकर नहीं दिखाते। यह न वारों का क्रम है, न कक्षा-गति का, न अध्याय 6 वाले राशि-स्वामित्व का। यह अपना अलग क्रम है, परंपरा से आया हुआ — और हर ग्रह से जुड़े दशा-वर्ष भी उसी के साथ आए हैं: केतु 7, शुक्र 20, सूर्य 6।",
                    },
                    {
                        "en": "It is worth being clear about that. A system can be internally exact and still rest on a convention nobody can justify from first principles. Vimshottari is exactly that: the arithmetic downstream of this order is rigorous, and the order itself is inherited.",
                        "hi": "इस पर साफ़ रहना चाहिए। कोई व्यवस्था अपने भीतर बिल्कुल सटीक हो सकती है और फिर भी ऐसी परिपाटी पर टिकी हो जिसे मूल सिद्धांतों से कोई सिद्ध न कर सके। विम्शोत्तरी ठीक ऐसी ही है: इस क्रम के आगे का सारा गणित कड़ा है, और क्रम स्वयं विरासत में मिला है।",
                    },
                ),
            ),
            Section(
                heading={"en": "Finding yours", "hi": "अपना निकालना"},
                body=(
                    {
                        "en": "Your chart screen names the nakshatra of every graha, and the lord follows from the cycle above. The one that matters most is the Moon's: its lord is the graha that rules the first mahadasha of your life, and therefore the graha your entire timeline starts from.",
                        "hi": "आपकी कुंडली स्क्रीन हर ग्रह का नक्षत्र बताती है, और स्वामी ऊपर वाले चक्र से निकल आता है। सबसे ज़्यादा मायने चंद्रमा वाला रखता है: उसका स्वामी ही वह ग्रह है जो आपके जीवन की पहली महादशा चलाता है, और इसलिए वह ग्रह जिससे आपकी पूरी समय-रेखा शुरू होती है।",
                    },
                    {
                        "en": "That is the whole bridge between this part and the next. One measurement — where the Moon stood — picks a lord, and that lord picks the starting point of a hundred and twenty years of arithmetic.",
                        "hi": "इस भाग और अगले के बीच का पूरा पुल इतना ही है। एक माप — चंद्रमा कहाँ खड़ा था — एक स्वामी चुनता है, और वह स्वामी एक सौ बीस वर्ष के गणित का आरंभ-बिंदु चुनता है।",
                    },
                ),
                aside={
                    "en": "Three nakshatras per graha, 120 degrees apart. If you know one of a graha's three, the other two are a third of the circle away in each direction.",
                    "hi": "हर ग्रह के तीन नक्षत्र, 120-120 अंश पर। किसी ग्रह का एक नक्षत्र पता हो तो बाक़ी दो दोनों दिशाओं में चक्र के एक-तिहाई पर मिलेंगे।",
                },
            ),
        ),
        personalise=P.janma_nakshatra,
    ),
    Chapter(
        slug="janma-nakshatra",
        part=PART_NAKSHATRAS,
        title={"en": "The janma nakshatra", "hi": "जन्म नक्षत्र"},
        summary={
            "en": "The single measurement your whole timeline unfolds from.",
            "hi": "वह एक माप जिससे आपकी पूरी समय-रेखा खुलती है।",
        },
        minutes=5,
        level="intermediate",
        sections=(
            Section(
                heading={"en": "Where the Moon stood", "hi": "चंद्रमा कहाँ खड़ा था"},
                body=(
                    {
                        "en": "The nakshatra the Moon occupied at birth is the janma nakshatra. In daily practice it is the most used fact in the chart: it names you at a temple, and it sets the starting point of your dasha timeline.",
                        "hi": "जन्म के समय चंद्रमा जिस नक्षत्र में था, वही जन्म नक्षत्र है। रोज़मर्रा के व्यवहार में यह कुंडली का सबसे ज़्यादा काम आने वाला तथ्य है: मंदिर में यही आपका नाम है, और यही आपकी दशा-रेखा का आरंभ-बिंदु तय करता है।",
                    },
                    {
                        "en": "How far the Moon had already travelled into it decides how much of your first dasha was already spent when you were born. One measurement, and the next hundred and twenty years of the timeline follow from it.",
                        "hi": "चंद्रमा उसमें कितना आगे बढ़ चुका था, इसी से तय होता है कि आपके जन्म के समय पहली दशा का कितना हिस्सा बीत चुका था। एक माप, और उसके बाद की एक सौ बीस वर्ष की समय-रेखा उसी से निकल आती है।",
                    },
                    {
                        "en": "Because the Moon crosses a nakshatra in about a day, this is one of the few chart facts that survives an imperfect birth time. Unless you were born within an hour or so of a boundary, an error of a couple of hours will not move it — which is exactly why it carries so much of the tradition's weight.",
                        "hi": "चंद्रमा एक नक्षत्र क़रीब एक दिन में पार करता है, इसलिए कुंडली के जो थोड़े तथ्य अधूरे जन्म समय में भी बचे रहते हैं, यह उनमें है। जब तक आप किसी सीमा के एक-दो घंटे के भीतर न जन्मे हों, दो घंटे की चूक इसे नहीं हिलाएगी — और इसीलिए परंपरा का इतना भार इस पर टिका है।",
                    },
                ),
            ),
            Section(
                heading={"en": "Where you will meet it", "hi": "यह आपको कहाँ मिलेगा"},
                body=(
                    {
                        "en": "A temple sankalpa asks for your nakshatra, your gotra and your name — not your rashi and never your date of birth in the Gregorian sense. A traditional birthday is reckoned by the return of your nakshatra rather than the calendar date, which is why it moves around the year.",
                        "hi": "मंदिर का संकल्प आपका नक्षत्र, गोत्र और नाम पूछता है — राशि नहीं, और अंग्रेज़ी तारीख़ तो कभी नहीं। परंपरागत जन्मदिन तारीख़ से नहीं, आपके नक्षत्र के लौट आने से गिना जाता है, इसीलिए वह हर साल आगे-पीछे होता है।",
                    },
                    {
                        "en": "It is also half of the ashtakoot matching families run before a wedding. That procedure takes the two janma nakshatras, scores eight categories out of a total of 36, and produces a number. The arithmetic is real; what has been built on it — refusing a match on a score — is a use of the tradition this course will not endorse.",
                        "hi": "विवाह से पहले परिवार जो अष्टकूट मिलान करते हैं, उसका आधा भी यही है। उस विधि में दोनों के जन्म नक्षत्र लेकर आठ कूटों में कुल 36 में से अंक दिए जाते हैं और एक संख्या निकलती है। गणित असली है; उस पर जो खड़ा किया गया — अंक देखकर रिश्ता ठुकराना — परंपरा का वह उपयोग है जिसका यह पाठ्यक्रम समर्थन नहीं करेगा।",
                    },
                ),
            ),
            Section(
                heading={"en": "Gandmool and other labels", "hi": "गंडमूल और दूसरे लेबल"},
                body=(
                    {
                        "en": "Six nakshatras — Ashwini, Ashlesha, Magha, Jyeshtha, Moola and Revati — sit at the junctions between signs, and a child born under one of them is called gandmool. Families are sometimes told this is inauspicious and that a specific ritual is needed within the first month.",
                        "hi": "छह नक्षत्र — अश्विनी, आश्लेषा, मघा, ज्येष्ठा, मूल और रेवती — राशियों की संधियों पर पड़ते हैं, और इनमें जन्मे शिशु को गंडमूल कहा जाता है। कभी-कभी परिवारों से कहा जाता है कि यह अशुभ है और पहले महीने के भीतर कोई विशेष अनुष्ठान ज़रूरी है।",
                    },
                    {
                        "en": "The measurement is trivially true: those six do sit at junctions, by construction of the two grids. Everything after that is interpretation, and roughly a fifth of all children are born under one of them. A label that applies to one child in five is not a diagnosis of anything, and no newborn needs to be treated as a problem to be fixed.",
                        "hi": "माप बिल्कुल सही है: दोनों जालियों की बनावट से ही वे छह संधियों पर पड़ते हैं। उसके आगे सब व्याख्या है, और क़रीब हर पाँचवाँ बच्चा इन्हीं में से किसी में जन्मता है। जो लेबल पाँच में से एक बच्चे पर लगता हो वह किसी बात का निदान नहीं है, और किसी नवजात को सुधारी जाने वाली समस्या की तरह लेने की ज़रूरत नहीं।",
                    },
                ),
                aside={
                    "en": "This app names your nakshatra and stops. It does not tell you that yours is auspicious or inauspicious, because that is not a property a measurement has.",
                    "hi": "यह ऐप आपका नक्षत्र बताकर रुक जाती है। वह यह नहीं कहती कि आपका शुभ है या अशुभ, क्योंकि किसी माप का ऐसा कोई गुण होता ही नहीं।",
                },
            ),
            Section(
                heading={"en": "Nakshatra or rashi", "hi": "नक्षत्र या राशि"},
                body=(
                    {
                        "en": "Both come from the same measurement — the Moon's longitude — read against two different grids. The rashi divides that longitude by 30, the nakshatra by 13°20'. Neither is more true than the other; they are two resolutions of one number.",
                        "hi": "दोनों एक ही माप से आते हैं — चंद्रमा के देशांतर से — बस दो अलग जालियों पर पढ़े हुए। राशि उस देशांतर को 30 से बाँटती है, नक्षत्र 13°20' से। इनमें कोई दूसरे से ज़्यादा सच्चा नहीं; ये एक ही संख्या के दो विभेदन हैं।",
                    },
                    {
                        "en": "Which one someone wants depends entirely on what they are doing. Ritual and naming want the nakshatra. Ordinary conversation wants the rashi. The dasha system wants the nakshatra and the exact fraction traversed within it — and that fraction is where part five begins.",
                        "hi": "कोई कौन सा चाहता है, यह पूरी तरह इस पर है कि वह कर क्या रहा है। अनुष्ठान और नामकरण को नक्षत्र चाहिए। आम बातचीत को राशि। दशा-पद्धति को नक्षत्र चाहिए और उसमें तय हुआ ठीक-ठीक अंश — और वहीं से पाँचवाँ भाग शुरू होता है।",
                    },
                ),
            ),
        ),
        personalise=P.janma_nakshatra,
    ),
)
