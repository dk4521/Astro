"""Part three: the twelve houses.

Houses are where a chart stops being astronomy and starts being about a life,
so this is where the course is most careful. Every chapter here repeats the same
discipline in a different form: a house names an area, never an outcome.
"""

from __future__ import annotations

from .. import personalise as P
from ..models import Chapter, Section
from . import PART_HOUSES

CHAPTERS: tuple[Chapter, ...] = (
    Chapter(
        slug="what-houses-are",
        part=PART_HOUSES,
        title={"en": "What houses are", "hi": "भाव क्या हैं"},
        summary={
            "en": "Rashis divide the sky. Houses divide life.",
            "hi": "राशियाँ आकाश बाँटती हैं। भाव जीवन बाँटते हैं।",
        },
        minutes=4,
        level="intermediate",
        sections=(
            Section(
                heading={"en": "Counted from the lagna", "hi": "लग्न से गिने हुए"},
                body=(
                    {
                        "en": "The 1st house is you — body, temperament, how you arrive in a room. The 4th is home and inner ground, the 7th partnership, the 10th work and public role. The others fill in the rest of a life.",
                        "hi": "पहला भाव आप हैं — शरीर, स्वभाव, किसी जगह पहुँचने का ढंग। चौथा घर और भीतरी ज़मीन, सातवाँ साझेदारी, दसवाँ कर्म और सार्वजनिक भूमिका। बाक़ी भाव जीवन का शेष हिस्सा भरते हैं।",
                    },
                    {
                        "en": "They are counted from the lagna. If your lagna is Vrishabha, then Vrishabha is your 1st house, Mithuna your 2nd, and so on around the circle.",
                        "hi": "ये लग्न से गिने जाते हैं। आपका लग्न वृषभ है तो वृषभ आपका पहला भाव, मिथुन दूसरा, और इसी क्रम में पूरा चक्र।",
                    },
                    {
                        "en": "The counting is always forwards through the signs and always wraps around: after the 12th you are back at the 1st. Nothing here is chosen or weighted — given a lagna, the twelve houses follow by one subtraction, which is exactly how the engine computes them.",
                        "hi": "गिनती हमेशा राशियों के क्रम में आगे बढ़ती है और हमेशा लौट आती है: बारहवें के बाद फिर पहला। इसमें कुछ भी चुना या तौला नहीं जाता — लग्न मिल जाए तो बारहों भाव एक घटाव से निकल आते हैं, और इंजन उन्हें ठीक इसी तरह गिनता है।",
                    },
                ),
            ),
            Section(
                heading={"en": "Two coordinates, not one", "hi": "एक नहीं, दो निर्देशांक"},
                body=(
                    {
                        "en": "Every graha in your chart carries two placements at once, and confusing them is the most common beginner error. Its rashi says what part of the sky it was in. Its house says what area of life the tradition reads it into. The rashi is astronomy; the house is astronomy plus your birth time and place.",
                        "hi": "आपकी कुंडली के हर ग्रह पर एक साथ दो स्थितियाँ होती हैं, और इन्हें आपस में गड्डमड्ड करना शुरुआत की सबसे आम चूक है। उसकी राशि बताती है कि वह आकाश के किस हिस्से में था। उसका भाव बताता है कि परंपरा उसे जीवन के किस क्षेत्र में पढ़ती है। राशि खगोल है; भाव खगोल के साथ आपका जन्म समय और स्थान।",
                    },
                    {
                        "en": "That difference has a practical consequence you already met in chapter 4: signs survive a wrong birth time and houses do not. When you are unsure of your time, read the sign statements and hold the house statements loosely.",
                        "hi": "इस फ़र्क़ का एक व्यावहारिक नतीजा अध्याय 4 में आ चुका है: ग़लत जन्म समय में राशियाँ बच जाती हैं, भाव नहीं। समय पर भरोसा न हो तो राशि वाली बातें पढ़िए और भाव वाली बातों को ढीला पकड़िए।",
                    },
                ),
            ),
            Section(
                heading={"en": "An area, not an outcome", "hi": "क्षेत्र, नतीजा नहीं"},
                body=(
                    {
                        "en": "A house names a region of life the way a chapter heading names a region of a book. It says where a discussion is happening, not how it ends. A graha in the 7th places an emphasis in the territory of partnership; it does not report a marriage, a divorce, or a date.",
                        "hi": "भाव जीवन के किसी क्षेत्र का नाम उसी तरह रखता है जैसे अध्याय का शीर्षक किताब के किसी हिस्से का। वह बताता है कि बात कहाँ हो रही है, यह नहीं कि वह कैसे ख़त्म होगी। सप्तम भाव में बैठा ग्रह ज़ोर को साझेदारी के इलाक़े में रखता है; वह न विवाह बताता है, न तलाक़, न कोई तारीख़।",
                    },
                    {
                        "en": "Keep that sentence handy for the next five chapters. Everything about houses gets misused in the same way — by sliding from “this area” to “this event”, and then attaching a date to it.",
                        "hi": "यह वाक्य अगले पाँच अध्यायों के लिए पास रखिए। भावों का दुरुपयोग हमेशा एक ही ढंग से होता है — “यह क्षेत्र” से खिसककर “यह घटना” पर आ जाना, और फिर उस पर तारीख़ चिपका देना।",
                    },
                ),
            ),
            Section(
                heading={"en": "Reading one graha completely", "hi": "एक ग्रह को पूरा पढ़ना"},
                body=(
                    {
                        "en": "Put the pieces together and a single line of a reading has a visible structure. “Venus in Karka in the 3rd” is three separate facts: which graha, which sign it stood in, which house that sign is for you. The first is astronomy, the second is astronomy, the third depends on your lagna.",
                        "hi": "टुकड़ों को जोड़िए तो किसी व्याख्या की एक पंक्ति की बनावट साफ़ दिखती है। “शुक्र कर्क में, तीसरे भाव में” — यह तीन अलग तथ्य हैं: कौन सा ग्रह, वह किस राशि में खड़ा था, और वह राशि आपके लिए कौन सा भाव है। पहला खगोल, दूसरा खगोल, और तीसरा आपके लग्न पर टिका।",
                    },
                    {
                        "en": "Chapter 18 adds the fourth piece — the houses that graha rules — and after that you can take apart any sentence an astrologer says to you and name which part of it is measurement and which part is reading.",
                        "hi": "अध्याय 18 चौथा टुकड़ा जोड़ता है — वह ग्रह किन भावों का स्वामी है — और उसके बाद कोई ज्योतिषी जो भी वाक्य कहे, आप उसे खोलकर बता सकेंगे कि उसमें माप कौन सा हिस्सा है और व्याख्या कौन सा।",
                    },
                ),
            ),
        ),
        personalise=P.houses_from_lagna,
    ),
    Chapter(
        slug="whole-sign",
        part=PART_HOUSES,
        title={"en": "Whole-sign houses", "hi": "पूर्ण-राशि भाव"},
        summary={
            "en": "One house is exactly one rashi. Why this app uses the oldest system.",
            "hi": "एक भाव यानी ठीक एक राशि। यह ऐप सबसे पुरानी पद्धति क्यों लेती है।",
        },
        minutes=4,
        level="intermediate",
        sections=(
            Section(
                heading={"en": "Systems that disagree", "hi": "आपस में न मिलने वाली पद्धतियाँ"},
                body=(
                    {
                        "en": "There are several ways to draw house boundaries, and they give different answers. This app uses whole-sign houses: one house is exactly one rashi, no more and no less. It is the oldest system and the standard in both North and South Indian practice.",
                        "hi": "भाव की सीमाएँ खींचने के कई तरीक़े हैं, और वे अलग-अलग उत्तर देते हैं। यह ऐप पूर्ण-राशि भाव लेती है: एक भाव यानी ठीक एक राशि, न कम न ज़्यादा। यह सबसे पुरानी पद्धति है और उत्तर तथा दक्षिण, दोनों की भारतीय परंपरा का मानक।",
                    },
                    {
                        "en": "The practical effect is that a graha never straddles two houses. Systems that split houses by degree can put the same graha in a different house — one reason two apps can disagree about the same birth.",
                        "hi": "व्यावहारिक असर यह है कि कोई ग्रह कभी दो भावों के बीच नहीं फँसता। जो पद्धतियाँ भावों को अंश से बाँटती हैं, वे उसी ग्रह को दूसरे भाव में रख सकती हैं — एक ही जन्म पर दो ऐप के अलग-अलग कहने का यह भी एक कारण है।",
                    },
                ),
                aside={
                    "en": "When an app shows a house number without saying which system produced it, the number is not checkable. Yours reports whole-sign, every time.",
                    "hi": "कोई ऐप भाव-संख्या दिखाए और यह न बताए कि वह किस पद्धति से निकली, तो उस संख्या की जाँच नहीं हो सकती। आपकी ऐप हर बार पूर्ण-राशि बताती है।",
                },
            ),
            Section(
                heading={"en": "What the alternatives do", "hi": "बाक़ी पद्धतियाँ क्या करती हैं"},
                body=(
                    {
                        "en": "Degree-based systems — Placidus, Koch, and in Indian practice the Sripati and bhava-chalita schemes — treat the exact degree of the lagna as the cusp of the 1st house and divide from there. A lagna at 27° of Vrishabha then puts the last three degrees of Vrishabha and most of Mithuna into the 1st house.",
                        "hi": "अंश-आधारित पद्धतियाँ — प्लेसिडस, कोच, और भारतीय परंपरा में श्रीपति तथा भावचलित — लग्न के ठीक अंश को पहले भाव का मध्य या आरंभ मानकर वहीं से बाँटती हैं। लग्न वृषभ के 27 अंश पर हो तो वृषभ के आख़िरी तीन अंश और मिथुन का बड़ा हिस्सा पहले भाव में आ जाता है।",
                    },
                    {
                        "en": "Under whole-sign, that same chart puts all of Vrishabha in the 1st and all of Mithuna in the 2nd. Neither approach is a mistake — they answer slightly different questions about what a house is — but they can move a graha by a whole house, and readings built on them will differ accordingly.",
                        "hi": "पूर्ण-राशि में वही कुंडली पूरे वृषभ को पहले भाव में और पूरे मिथुन को दूसरे में रखती है। इनमें कोई ग़लती नहीं — दोनों “भाव है क्या” के थोड़े अलग सवालों का उत्तर देते हैं — पर वे किसी ग्रह को पूरा एक भाव खिसका सकते हैं, और उन पर बनी व्याख्याएँ उसी हिसाब से अलग होंगी।",
                    },
                ),
            ),
            Section(
                heading={"en": "Why this app picked one and says so", "hi": "यह ऐप एक चुनकर बता क्यों देती है"},
                body=(
                    {
                        "en": "Whole-sign is the system the classical Sanskrit texts assume, the one both Indian chart styles are drawn for, and the one that needs no extra choices — no cusp convention, no interpolation, no latitude limits that break near the poles. It is also the only one where the diagram you see and the numbers you check cannot come apart.",
                        "hi": "पूर्ण-राशि वही पद्धति है जिसे शास्त्रीय संस्कृत ग्रंथ मानकर चलते हैं, जिसके लिए दोनों भारतीय कुंडली-शैलियाँ बनी हैं, और जिसमें कोई अतिरिक्त चुनाव करना ही नहीं पड़ता — न भाव-संधि की परंपरा, न अंतर्वेशन, न ध्रुवों के पास टूट जाने वाली अक्षांश-सीमाएँ। और यही अकेली पद्धति है जिसमें आपको दिखने वाला चित्र और आपके जाँचे जाने वाले अंक कभी अलग नहीं हो सकते।",
                    },
                    {
                        "en": "The point is less which system is right than that a chart should name the one it used. A house number without a stated system is an unfalsifiable number, and the whole purpose of this app is that you can check what it tells you.",
                        "hi": "मुद्दा इतना नहीं कि कौन सी पद्धति सही है, बल्कि यह कि कुंडली को अपनी ली हुई पद्धति बतानी चाहिए। पद्धति बताए बिना दी गई भाव-संख्या ऐसी संख्या है जिसे ग़लत सिद्ध ही नहीं किया जा सकता, और इस ऐप का पूरा उद्देश्य यही है कि जो वह कहे उसे आप जाँच सकें।",
                    },
                ),
            ),
            Section(
                heading={"en": "Checking your own house numbers", "hi": "अपने भाव-अंक ख़ुद जाँचना"},
                body=(
                    {
                        "en": "Whole-sign has one practical advantage over every alternative: you can verify it without a computer. Find your lagna's rashi, count forward through the twelve signs, and you have all twelve houses. Then take any graha, look up its rashi, and count how many signs it is from the lagna — that number, plus one, is its house.",
                        "hi": "बाक़ी सब पद्धतियों पर पूर्ण-राशि का एक व्यावहारिक लाभ है: इसे बिना कंप्यूटर जाँचा जा सकता है। अपने लग्न की राशि लीजिए, बारह राशियों में आगे गिनते जाइए, और बारहों भाव मिल गए। फिर कोई भी ग्रह लीजिए, उसकी राशि देखिए, और गिनिए कि वह लग्न से कितनी राशि दूर है — उसमें एक जोड़ दीजिए, वही उसका भाव है।",
                    },
                    {
                        "en": "Do that once for every graha on your chart screen and you have independently reproduced the app's house column. That is not a trivial exercise: it is the moment the numbers stop being something you are told and become something you know.",
                        "hi": "अपनी कुंडली स्क्रीन के हर ग्रह के लिए यह एक बार कर लीजिए, और आपने ऐप का भाव-स्तंभ स्वतंत्र रूप से दोबारा बना लिया। यह मामूली अभ्यास नहीं है: यही वह क्षण है जब संख्याएँ बताई हुई चीज़ नहीं रह जातीं, जानी हुई चीज़ बन जाती हैं।",
                    },
                ),
            ),
        ),
        personalise=P.houses_from_lagna,
    ),
    Chapter(
        slug="kendra-trikona",
        part=PART_HOUSES,
        title={"en": "Kendras and trikonas", "hi": "केंद्र और त्रिकोण"},
        summary={
            "en": "The two groupings that carry most of the tradition's weight.",
            "hi": "वे दो समूह जिन पर परंपरा का अधिकांश भार टिका है।",
        },
        minutes=4,
        level="intermediate",
        sections=(
            Section(
                heading={"en": "Angles and trines", "hi": "केंद्र और त्रिकोण"},
                body=(
                    {
                        "en": "Houses 1, 4, 7 and 10 are the kendras — the angles, read as the structure of a life. Houses 1, 5 and 9 are the trikonas, read as its sustaining thread. The 1st belongs to both, which is why it carries so much.",
                        "hi": "पहला, चौथा, सातवाँ और दसवाँ भाव केंद्र हैं — जीवन के ढाँचे की तरह पढ़े जाते हैं। पहला, पाँचवाँ और नवाँ त्रिकोण हैं, जो उसे थामे रखने वाले धागे की तरह पढ़े जाते हैं। पहला दोनों में है, इसीलिए उस पर इतना भार है।",
                    },
                    {
                        "en": "The geometry is not arbitrary. Kendras are the four quarters of the circle, ninety degrees apart, the same four points a building is squared to. Trikonas are the three points of an equilateral triangle, a hundred and twenty degrees apart. Both groupings are simply the symmetries a twelve-part circle allows.",
                        "hi": "यह ज्यामिति मनमानी नहीं है। केंद्र वृत्त के चार चौथाई हैं, नब्बे-नब्बे अंश पर — वही चार बिंदु जिन पर कोई इमारत सीधी की जाती है। त्रिकोण समबाहु त्रिभुज के तीन कोने हैं, एक सौ बीस अंश पर। दोनों समूह बस वे सममितियाँ हैं जो बारह हिस्सों वाला वृत्त होने देता है।",
                    },
                ),
            ),
            Section(
                heading={"en": "The difficult ones, honestly", "hi": "कठिन भाव, ईमानदारी से"},
                body=(
                    {
                        "en": "Houses 6, 8 and 12 are called dusthanas, the difficult ones. It is worth saying plainly: that label describes friction, effort and things worked out privately. It is not a sentence, and grahas there are not damaged.",
                        "hi": "छठा, आठवाँ और बारहवाँ भाव दुस्थान कहे जाते हैं, यानी कठिन। साफ़ कह देना चाहिए: यह लेबल घर्षण, श्रम और चुपचाप निपटाई जाने वाली चीज़ों का वर्णन करता है। यह सज़ा नहीं है, और वहाँ बैठे ग्रह क्षतिग्रस्त नहीं होते।",
                    },
                    {
                        "en": "Read them as the parts of life that do not happen in public: illness and its treatment, debt and its repayment, inheritance, research, sleep, exile, the sixth house's daily grind and the twelfth's withdrawal. Every functioning life contains all of that, and a chart with nothing in these houses is not a luckier chart.",
                        "hi": "इन्हें जीवन के उन हिस्सों की तरह पढ़िए जो सार्वजनिक रूप से नहीं होते: रोग और उसका इलाज, ऋण और उसकी अदायगी, उत्तराधिकार, शोध, नींद, प्रवास, छठे भाव की रोज़ की खटपट और बारहवें का हट जाना। हर चलते-फिरते जीवन में यह सब होता है, और जिस कुंडली के इन भावों में कुछ न हो वह ज़्यादा भाग्यशाली कुंडली नहीं है।",
                    },
                ),
            ),
            Section(
                heading={"en": "The growth houses", "hi": "उपचय भाव"},
                body=(
                    {
                        "en": "There is a third grouping worth knowing, because it cuts across the first two: houses 3, 6, 10 and 11 are the upachayas, the ones that “grow”. The tradition reads them as areas that improve with effort and age rather than arriving ready-made.",
                        "hi": "एक तीसरा समूह भी जान लेने लायक़ है, क्योंकि वह पहले दोनों को काटता है: तीसरा, छठा, दसवाँ और ग्यारहवाँ भाव उपचय हैं, यानी “बढ़ने वाले”। परंपरा इन्हें ऐसे क्षेत्रों की तरह पढ़ती है जो बने-बनाए मिलने के बजाय श्रम और उम्र के साथ बेहतर होते हैं।",
                    },
                    {
                        "en": "Notice that the 6th is a dusthana and an upachaya at once, and the 10th is a kendra and an upachaya. The groupings overlap because they answer different questions, and a house's membership in one of them was never meant to be a score.",
                        "hi": "ध्यान दीजिए कि छठा भाव एक साथ दुस्थान भी है और उपचय भी, और दसवाँ केंद्र भी है और उपचय भी। ये समूह एक-दूसरे पर चढ़ते हैं क्योंकि वे अलग-अलग सवालों के उत्तर हैं, और किसी भाव का किसी समूह में होना कभी अंक देने के लिए बनाया ही नहीं गया था।",
                    },
                ),
            ),
            Section(
                heading={"en": "What the groupings are for", "hi": "इन समूहों का काम क्या है"},
                body=(
                    {
                        "en": "Their real use is as a summary. A reader glancing at a chart uses them to see its shape quickly — where the weight sits, whether the emphasis is public or private — before saying anything at all about any single graha.",
                        "hi": "इनका असली उपयोग सारांश की तरह है। कुंडली पर एक नज़र डालने वाला इन्हीं से उसकी बनावट झट से देख लेता है — भार कहाँ है, ज़ोर सार्वजनिक है या निजी — किसी एक ग्रह के बारे में कुछ भी कहने से पहले।",
                    },
                    {
                        "en": "Where they get abused is in scoring: counting grahas in kendras and trikonas, subtracting the ones in dusthanas, and announcing a chart as strong or weak. This app does not do that, and it is worth being suspicious of anything that does. A life is not a total.",
                        "hi": "इनका दुरुपयोग अंक देने में होता है: केंद्र-त्रिकोण के ग्रह गिनना, दुस्थान वालों को घटाना, और कुंडली को बलवान या कमज़ोर घोषित कर देना। यह ऐप ऐसा नहीं करती, और जो करे उससे सतर्क रहना चाहिए। जीवन कोई जोड़ नहीं है।",
                    },
                ),
            ),
        ),
        personalise=P.kendra_trikona,
    ),
    Chapter(
        slug="houses-one-to-six",
        part=PART_HOUSES,
        title={"en": "Houses 1 to 6", "hi": "भाव 1 से 6"},
        summary={
            "en": "Body, resources, effort, roots, mind, friction.",
            "hi": "शरीर, संसाधन, प्रयास, जड़ें, मन, घर्षण।",
        },
        minutes=6,
        level="intermediate",
        sections=(
            Section(
                heading={"en": "The first six", "hi": "पहले छह"},
                body=(
                    {
                        "en": "1st: the body and the self as it appears. 2nd: what you hold — money, family, speech. 3rd: effort, hands, siblings, short journeys. 4th: home, mother, the ground under you. 5th: mind, creativity, children, what you make. 6th: work, service, illness, conflict — the friction of daily life.",
                        "hi": "पहला: शरीर और जैसा दिखता है वैसा स्व। दूसरा: जो आपके पास है — धन, कुटुंब, वाणी। तीसरा: प्रयास, हाथ, भाई-बहन, छोटी यात्राएँ। चौथा: घर, माता, पैरों के नीचे की ज़मीन। पाँचवाँ: मन, सृजन, संतान, जो आप रचते हैं। छठा: काम, सेवा, रोग, विवाद — रोज़मर्रा का घर्षण।",
                    },
                    {
                        "en": "These are areas, not outcomes. A graha in the 6th does not mean illness; it means the tradition reads that graha's emphasis as playing out in the region of work, service and friction.",
                        "hi": "ये क्षेत्र हैं, नतीजे नहीं। छठे भाव में बैठा ग्रह रोग नहीं बताता; उसका अर्थ इतना है कि परंपरा उस ग्रह के ज़ोर को काम, सेवा और घर्षण के इलाक़े में काम करता पढ़ती है।",
                    },
                ),
            ),
            Section(
                heading={"en": "First and second: the self and what it holds", "hi": "पहला और दूसरा: स्व और उसकी पकड़"},
                body=(
                    {
                        "en": "The 1st house is the widest of the twelve. It carries the physical body, health in the general sense, temperament, and the impression you make before you have said anything. Because it is also the anchor every other house is counted from, it turns up in almost every reading — which is a structural fact about the counting, not a statement that you are unusually central.",
                        "hi": "पहला भाव बारहों में सबसे चौड़ा है। उसमें भौतिक शरीर, सामान्य अर्थ में स्वास्थ्य, स्वभाव, और कुछ कहने से पहले पड़ने वाला प्रभाव — सब आता है। और चूँकि बाक़ी हर भाव की गिनती उसी से होती है, वह लगभग हर व्याख्या में आ जाता है — यह गिनती की बनावट का तथ्य है, यह बयान नहीं कि आप कुछ ख़ास केंद्र में हैं।",
                    },
                    {
                        "en": "The 2nd is what is held rather than what is: accumulated money as opposed to earning, the family you were born into, food, and — a pairing that surprises people — speech. The old logic is that all four are things taken in and given out by the same mouth and the same household.",
                        "hi": "दूसरा भाव यह नहीं कि आप क्या हैं, बल्कि यह कि आपके पास क्या है: कमाई नहीं, जमा हुआ धन; वह कुल जिसमें आप जन्मे; अन्न; और — लोगों को चौंकाने वाली जोड़ी — वाणी। पुराना तर्क यह है कि ये चारों एक ही मुख और एक ही घर से भीतर आती और बाहर जाती हैं।",
                    },
                ),
            ),
            Section(
                heading={"en": "Third and fourth: effort and ground", "hi": "तीसरा और चौथा: प्रयास और ज़मीन"},
                body=(
                    {
                        "en": "The 3rd is the house of one's own effort — the hands, courage in the ordinary sense of doing the thing, younger siblings, short journeys, writing and messages. It is an upachaya, so the tradition reads it as an area that rewards repetition.",
                        "hi": "तीसरा अपने ही प्रयास का भाव है — हाथ, काम कर डालने वाला सामान्य साहस, छोटे भाई-बहन, छोटी यात्राएँ, लेखन और संदेश। यह उपचय है, इसलिए परंपरा इसे ऐसे क्षेत्र की तरह पढ़ती है जो दोहराव से फल देता है।",
                    },
                    {
                        "en": "The 4th is its opposite in temperament: the fixed ground rather than the moving hands. Home in the literal sense of a house and land, the mother, vehicles, schooling, and the private inner floor a person stands on. It sits at the bottom of the chart, directly under the 10th, and that vertical pairing — private base, public role — is one of the most used axes in the whole system.",
                        "hi": "चौथा स्वभाव में उसका उलटा है: चलते हाथ नहीं, टिकी हुई ज़मीन। घर अपने सीधे अर्थ में — मकान और भूमि, माता, वाहन, शिक्षा, और वह निजी भीतरी फ़र्श जिस पर व्यक्ति खड़ा होता है। यह कुंडली में सबसे नीचे बैठता है, ठीक दसवें के नीचे, और यही खड़ी जोड़ी — निजी आधार और सार्वजनिक भूमिका — पूरी व्यवस्था की सबसे ज़्यादा काम आने वाली धुरियों में से है।",
                    },
                ),
            ),
            Section(
                heading={"en": "Fifth and sixth: what you make, what resists", "hi": "पाँचवाँ और छठा: जो रचते हैं, जो रोकता है"},
                body=(
                    {
                        "en": "The 5th covers everything a person produces from inside themselves: children, creative work, intelligence and study, and — in older texts — merit carried forward. It is a trikona, which is why readings lean on it heavily when they want to say something about how a life sustains itself.",
                        "hi": "पाँचवें में वह सब आता है जो व्यक्ति अपने भीतर से रचता है: संतान, सृजनात्मक काम, बुद्धि और अध्ययन, और पुराने ग्रंथों में — आगे लाया हुआ पुण्य। यह त्रिकोण है, इसीलिए जब कोई व्याख्या यह कहना चाहे कि कोई जीवन अपने को कैसे थामे रखता है, तो वह इसी पर सबसे ज़्यादा टिकती है।",
                    },
                    {
                        "en": "The 6th is the house of resistance: daily work as opposed to career, service and the people who do it, debts, opponents, and illness. Its bad reputation comes from that last item, but notice how much of the list is ordinary and necessary. A chart with weight in the 6th is describing a life with a lot of daily work in it, and no honest reading can turn that into a diagnosis.",
                        "hi": "छठा प्रतिरोध का भाव है: कैरियर नहीं, रोज़ का काम; सेवा और उसे करने वाले लोग; ऋण; विरोधी; और रोग। उसकी बदनामी इसी आख़िरी मद से आई है, पर देखिए कि सूची का कितना हिस्सा सामान्य और ज़रूरी है। जिस कुंडली में छठे का भार हो, वह ऐसे जीवन का वर्णन कर रही है जिसमें रोज़ का काम बहुत है — और कोई ईमानदार व्याख्या उसे निदान में नहीं बदल सकती।",
                    },
                ),
                aside={
                    "en": "The 6th, 8th and 12th get called difficult. They are also where medicine, research and rest live. Difficulty described is not misfortune predicted.",
                    "hi": "छठे, आठवें और बारहवें को कठिन कहा जाता है। चिकित्सा, शोध और विश्राम भी वहीं रहते हैं। वर्णित कठिनाई भविष्यवाणी की गई दुर्घटना नहीं है।",
                },
            ),
            Section(
                heading={"en": "How to use a list like this", "hi": "ऐसी सूची का उपयोग कैसे करें"},
                body=(
                    {
                        "en": "Do not memorise the keywords. What matters is the logic of the sequence: the circle starts with the body, moves to what the body holds, then to what it does, then to where it rests, then to what it produces, then to what resists it. Each house follows from the one before.",
                        "hi": "शब्द रटिए मत। असल बात इस क्रम का तर्क है: चक्र शरीर से शुरू होता है, फिर शरीर के पास क्या है, फिर वह करता क्या है, फिर वह टिकता कहाँ है, फिर वह रचता क्या है, फिर उसे रोकता क्या है। हर भाव अपने पिछले से निकलता है।",
                    },
                    {
                        "en": "Once you see the sequence, the second six are easy — they are the same six seen from the other side of the circle, which is exactly how the next chapter presents them.",
                        "hi": "यह क्रम एक बार दिख जाए तो अगले छह आसान हैं — वे वही छह हैं, बस चक्र के दूसरी ओर से देखे हुए, और अगला अध्याय उन्हें ठीक इसी तरह रखता है।",
                    },
                ),
            ),
        ),
        personalise=P.busiest_house,
    ),
    Chapter(
        slug="houses-seven-to-twelve",
        part=PART_HOUSES,
        title={"en": "Houses 7 to 12", "hi": "भाव 7 से 12"},
        summary={
            "en": "Partnership, change, meaning, work, gain, retreat.",
            "hi": "साझेदारी, परिवर्तन, अर्थ, कर्म, लाभ, निवृत्ति।",
        },
        minutes=5,
        level="intermediate",
        sections=(
            Section(
                heading={"en": "The second six", "hi": "दूसरे छह"},
                body=(
                    {
                        "en": "7th: partnership, contracts, the other person. 8th: change, inheritance, what is hidden. 9th: meaning, teachers, long journeys, belief. 10th: work and public role. 11th: gains, networks, what comes back. 12th: retreat, sleep, foreign places, expense.",
                        "hi": "सातवाँ: साझेदारी, अनुबंध, सामने वाला व्यक्ति। आठवाँ: परिवर्तन, उत्तराधिकार, जो छिपा है। नवाँ: अर्थ, गुरुजन, लंबी यात्राएँ, आस्था। दसवाँ: कर्म और सार्वजनिक भूमिका। ग्यारहवाँ: लाभ, संपर्क, जो लौटकर आता है। बारहवाँ: निवृत्ति, नींद, परदेस, व्यय।",
                    },
                    {
                        "en": "Notice how the pairs sit opposite: 1 and 7 (self and other), 4 and 10 (private ground and public role), 6 and 12 (daily friction and withdrawal). The circle is built from those tensions.",
                        "hi": "देखिए कि जोड़े आमने-सामने कैसे बैठे हैं: 1 और 7 (स्व और अन्य), 4 और 10 (निजी ज़मीन और सार्वजनिक भूमिका), 6 और 12 (रोज़ का घर्षण और हट जाना)। चक्र इन्हीं तनावों से बना है।",
                    },
                ),
            ),
            Section(
                heading={"en": "Seventh and eighth: the other, and what changes", "hi": "सातवाँ और आठवाँ: अन्य, और जो बदलता है"},
                body=(
                    {
                        "en": "The 7th is whoever is across the table: a spouse, a business partner, a client, an opponent in a negotiation. It is the exact opposite point to the 1st, which is the tradition's way of saying that the self and the other are one axis and cannot be read apart.",
                        "hi": "सातवाँ वह है जो मेज़ के आर-पार बैठा है: जीवनसाथी, कारोबारी साझेदार, ग्राहक, सौदेबाज़ी में विरोधी। यह पहले के ठीक सामने का बिंदु है, और परंपरा इसी तरह कहती है कि स्व और अन्य एक ही धुरी हैं और अलग-अलग नहीं पढ़े जा सकते।",
                    },
                    {
                        "en": "The 8th is transformation: inheritance and the money of others, joint resources, research and hidden things, and — in classical texts — longevity, which is the single most misused reading in this subject. This app will not compute a lifespan or hint at one, and neither should anyone else, from any house.",
                        "hi": "आठवाँ रूपांतरण है: उत्तराधिकार और दूसरों का धन, साझा संसाधन, शोध और छिपी हुई बातें, और शास्त्रीय ग्रंथों में — आयु, जो इस विषय की सबसे ज़्यादा दुरुपयोग की गई व्याख्या है। यह ऐप न आयु गिनेगी, न उसका इशारा करेगी, और किसी और को भी किसी भी भाव से ऐसा नहीं करना चाहिए।",
                    },
                ),
                aside={
                    "en": "No reading in this app estimates lifespan, from the 8th house or anywhere else. That is a firm line, not a limitation of the engine.",
                    "hi": "इस ऐप की कोई व्याख्या आयु का अनुमान नहीं लगाती — न आठवें भाव से, न कहीं और से। यह पक्की रेखा है, इंजन की कोई कमी नहीं।",
                },
            ),
            Section(
                heading={"en": "Ninth and tenth: meaning and role", "hi": "नवाँ और दसवाँ: अर्थ और भूमिका"},
                body=(
                    {
                        "en": "The 9th is the second trikona and one of the most emphasised houses in Indian practice: teachers, the father in many schools, long journeys and pilgrimage, higher study, law and philosophy — the frameworks a person borrows to make sense of things.",
                        "hi": "नवाँ दूसरा त्रिकोण है और भारतीय परंपरा के सबसे ज़ोर दिए जाने वाले भावों में से एक: गुरुजन, कई परंपराओं में पिता, लंबी यात्राएँ और तीर्थ, उच्च अध्ययन, विधि और दर्शन — वे ढाँचे जो व्यक्ति चीज़ों को समझने के लिए उधार लेता है।",
                    },
                    {
                        "en": "The 10th sits at the top of the chart, the highest point the sky reached: career, standing, the work you are known for, and authority in the ordinary sense of who answers to whom. It is a kendra and an upachaya at once, which is the tradition's way of saying that a public role is both structural and built over time.",
                        "hi": "दसवाँ कुंडली में सबसे ऊपर बैठता है, आकाश का सबसे ऊँचा बिंदु: कैरियर, प्रतिष्ठा, वह काम जिससे आप पहचाने जाते हैं, और सामान्य अर्थ में अधिकार — कौन किसे जवाब देता है। यह एक साथ केंद्र भी है और उपचय भी, और परंपरा इसी से कहती है कि सार्वजनिक भूमिका ढाँचा भी है और समय के साथ बनाई भी जाती है।",
                    },
                ),
            ),
            Section(
                heading={"en": "Eleventh and twelfth: return and release", "hi": "ग्यारहवाँ और बारहवाँ: लौटना और छोड़ना"},
                body=(
                    {
                        "en": "The 11th is income as opposed to accumulated wealth, the networks and elder siblings and friends through which things come back to you, and the fulfilment of what was wanted. The 2nd holds; the 11th receives.",
                        "hi": "ग्यारहवाँ जमा धन नहीं, आय है; वे संपर्क, बड़े भाई-बहन और मित्र जिनके रास्ते चीज़ें लौटकर आती हैं; और जो चाहा गया था उसकी पूर्ति। दूसरा रखता है; ग्यारहवाँ पाता है।",
                    },
                    {
                        "en": "The 12th is the last house and the one about letting go: sleep and dreams, expenditure, foreign lands and living far from where you began, hospitals and retreats, and what old texts call liberation. Its reputation as the house of loss is a narrow reading of a wider idea — everything that leaves the circle leaves through here, including things anyone would be glad to be rid of.",
                        "hi": "बारहवाँ आख़िरी भाव है और छोड़ने के बारे में है: नींद और स्वप्न, व्यय, परदेस और जन्मस्थान से दूर बसना, चिकित्सालय और एकांतवास, और जिसे पुराने ग्रंथ मोक्ष कहते हैं। उसे हानि का भाव कहना एक बड़े विचार का सँकरा पाठ है — जो कुछ भी चक्र से बाहर जाता है यहीं से जाता है, वह भी जिससे छुटकारा पाकर कोई भी ख़ुश होगा।",
                    },
                ),
            ),
            Section(
                heading={"en": "The four axes", "hi": "चार धुरियाँ"},
                body=(
                    {
                        "en": "Once all twelve are in view, the cleanest way to hold them is as six opposed pairs: 1–7 self and other, 2–8 what you hold and what is held jointly, 3–9 near effort and far meaning, 4–10 private ground and public role, 5–11 what you make and what returns, 6–12 daily friction and release from it.",
                        "hi": "बारहों सामने आ जाएँ तो उन्हें थामने का सबसे साफ़ तरीक़ा है छह आमने-सामने की जोड़ियाँ: 1–7 स्व और अन्य, 2–8 अपनी पकड़ और साझा पकड़, 3–9 पास का प्रयास और दूर का अर्थ, 4–10 निजी ज़मीन और सार्वजनिक भूमिका, 5–11 जो रचते हैं और जो लौटता है, 6–12 रोज़ का घर्षण और उससे छुटकारा।",
                    },
                    {
                        "en": "Held that way the twelve stop being a list to memorise and become a structure you can rebuild from either end. It also makes readings easier to check: a statement about your 7th that ignores your 1st is only using half an axis.",
                        "hi": "इस तरह पकड़ने पर बारह भाव रटने की सूची नहीं रह जाते, एक ऐसी बनावट बन जाते हैं जिसे किसी भी सिरे से दोबारा खड़ा किया जा सकता है। इससे व्याख्याओं की जाँच भी आसान होती है: आपके सातवें पर कही गई बात जो आपके पहले को छोड़ दे, वह आधी धुरी ही इस्तेमाल कर रही है।",
                    },
                ),
            ),
        ),
        personalise=P.busiest_house,
    ),
    Chapter(
        slug="house-lords",
        part=PART_HOUSES,
        title={"en": "House lords", "hi": "भावेश"},
        summary={
            "en": "How an empty house still gets read.",
            "hi": "ख़ाली भाव भी कैसे पढ़ा जाता है।",
        },
        minutes=5,
        level="intermediate",
        sections=(
            Section(
                heading={"en": "Nine grahas, twelve houses", "hi": "नौ ग्रह, बारह भाव"},
                body=(
                    {
                        "en": "Most houses in most charts are empty — nine grahas cannot fill twelve houses. An empty house is not a blank. It is read through its lord: the graha that rules the sign occupying it, and wherever that graha happens to sit.",
                        "hi": "अधिकांश कुंडलियों में अधिकांश भाव ख़ाली होते हैं — नौ ग्रह बारह भाव भर ही नहीं सकते। ख़ाली भाव कोरा नहीं होता। उसे उसके स्वामी से पढ़ा जाता है: जो ग्रह उस भाव में पड़ी राशि का स्वामी है, और वह ग्रह जहाँ भी बैठा हो।",
                    },
                    {
                        "en": "This is why a reading can say something about your 7th house when nothing is in it. The link runs: house → its sign → that sign's lord → where the lord sits.",
                        "hi": "इसीलिए कोई व्याख्या आपके सप्तम भाव के बारे में कुछ कह सकती है जबकि उसमें कुछ है ही नहीं। कड़ी इस तरह चलती है: भाव → उसकी राशि → उस राशि का स्वामी → वह स्वामी कहाँ बैठा है।",
                    },
                    {
                        "en": "At minimum three houses in every chart are empty, and in practice it is usually six or seven. So this is not an edge case — it is how most of a chart gets read at all.",
                        "hi": "हर कुंडली में कम से कम तीन भाव ख़ाली रहते ही हैं, और व्यवहार में प्रायः छह-सात। यानी यह कोई किनारे का मामला नहीं है — कुंडली का बड़ा हिस्सा पढ़ा ही इसी तरह जाता है।",
                    },
                ),
            ),
            Section(
                heading={"en": "Walking the chain", "hi": "कड़ी पर चलना"},
                body=(
                    {
                        "en": "Take a worked example. Suppose your lagna is Vrishabha. Then your 7th house is Vrishchika, whose lord is Mars. Look up where Mars actually is — say the 10th house. The tradition then reads your 7th house “through” the 10th: the area of partnership, described in the language of public work.",
                        "hi": "एक हल किया हुआ उदाहरण लीजिए। मान लीजिए आपका लग्न वृषभ है। तब आपका सप्तम भाव वृश्चिक हुआ, जिसका स्वामी मंगल है। अब देखिए मंगल असल में कहाँ है — मान लीजिए दसवें भाव में। परंपरा तब आपके सप्तम भाव को दसवें “के रास्ते” पढ़ती है: साझेदारी का क्षेत्र, सार्वजनिक कर्म की भाषा में कहा हुआ।",
                    },
                    {
                        "en": "Every step in that chain is checkable on your chart screen. The lagna is printed, the sign of each house follows from it, the lord of each sign is the fixed map from chapter 6, and the position of every graha is listed. Nothing in the chain is an opinion until the last step, where somebody says what the combination means.",
                        "hi": "इस कड़ी का हर क़दम आपकी कुंडली स्क्रीन पर जाँचा जा सकता है। लग्न छपा है, हर भाव की राशि उसी से निकलती है, हर राशि का स्वामी अध्याय 6 का तय नक़्शा है, और हर ग्रह की स्थिति सूची में दी है। कड़ी में कुछ भी राय नहीं है — केवल आख़िरी क़दम पर, जब कोई कहता है कि इस मेल का अर्थ क्या है।",
                    },
                ),
            ),
            Section(
                heading={"en": "Where this gets stretched too far", "hi": "यह कहाँ ज़रूरत से ज़्यादा खींच दी जाती है"},
                body=(
                    {
                        "en": "The chain can be run again from wherever it lands — the lord of the house the lord sits in, and so on — and some readers keep going for four or five steps. Every step multiplies the number of statements that can be made, which is exactly why long chains feel impressive and mean less.",
                        "hi": "यह कड़ी वहाँ से आगे भी चलाई जा सकती है — जिस भाव में स्वामी बैठा है उसका स्वामी, और फिर उसका — और कुछ पढ़ने वाले चार-पाँच क़दम तक चलते जाते हैं। हर क़दम कहे जा सकने वाले वाक्यों की संख्या गुणा कर देता है, और इसीलिए लंबी कड़ियाँ प्रभावशाली लगती हैं और अर्थ कम रखती हैं।",
                    },
                    {
                        "en": "A practical limit: one step is a reading, two is a stretch, three is a story. If a reading you are given required four hops to arrive, ask what it would have said had any one of them landed elsewhere.",
                        "hi": "एक व्यावहारिक सीमा: एक क़दम व्याख्या है, दो खिंचाव, तीन कहानी। कोई व्याख्या आपको चार छलाँगों के बाद मिले, तो पूछिए कि इनमें से कोई एक कहीं और गिरती तो वह क्या कहती।",
                    },
                ),
            ),
            Section(
                heading={"en": "Why lords matter more than occupants", "hi": "स्वामी बैठे हुए ग्रहों से ज़्यादा क्यों मायने रखते हैं"},
                body=(
                    {
                        "en": "There is a quiet asymmetry here worth noticing. A graha occupies exactly one house, but rules one or two — so every graha in your chart is carrying two or three jobs at once. Saturn in your 3rd house is also, say, the lord of your 9th and 10th, and any statement about Saturn is simultaneously a statement about all three.",
                        "hi": "यहाँ एक चुपचाप असंतुलन है जिस पर ध्यान देना चाहिए। कोई ग्रह ठीक एक भाव में बैठता है, पर स्वामी एक या दो का होता है — यानी आपकी कुंडली का हर ग्रह एक साथ दो-तीन काम ढो रहा है। आपके तीसरे भाव में बैठा शनि, मान लीजिए, नवम और दशम का स्वामी भी है, और शनि पर कही गई कोई भी बात एक साथ तीनों के बारे में है।",
                    },
                    {
                        "en": "That is the real reason readings sound interconnected: they are, structurally, because nine bodies are doing twenty-one jobs. It is also the reason a reading can be spun almost any direction — with that much overlap, a determined reader can connect any house to any outcome. Knowing the mechanism is what lets you tell a careful reading from a flexible one.",
                        "hi": "व्याख्याएँ आपस में गुँथी हुई क्यों लगती हैं, असली कारण यही है: वे बनावट से ही गुँथी हैं, क्योंकि नौ पिंड इक्कीस काम कर रहे हैं। और इसी कारण किसी व्याख्या को लगभग किसी भी दिशा में घुमाया जा सकता है — इतने ओवरलैप में कोई ठाना हुआ पढ़ने वाला किसी भी भाव को किसी भी नतीजे से जोड़ सकता है। तंत्र जान लेना ही आपको सधी हुई व्याख्या और लचीली व्याख्या में फ़र्क़ करने देता है।",
                    },
                ),
            ),
        ),
        personalise=P.house_lords,
    ),
)
