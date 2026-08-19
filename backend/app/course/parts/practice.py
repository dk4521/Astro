"""Part six: practice.

The last three chapters are the reason the other twenty-seven are written the
way they are. One divisional chart, one honest account of the method's limits,
and one chapter about the harm this tradition is put to — including the
helplines, which the test suite pins so that a future edit cannot quietly drop
them.
"""

from __future__ import annotations

from .. import personalise as P
from ..models import Chapter, Section
from . import PART_PRACTICE

CHAPTERS: tuple[Chapter, ...] = (
    Chapter(
        slug="navamsa",
        part=PART_PRACTICE,
        title={"en": "Divisional charts", "hi": "विभाग-कुंडलियाँ"},
        summary={
            "en": "The navamsa: a magnification, not a second opinion.",
            "hi": "नवांश: आवर्धन, दूसरी राय नहीं।",
        },
        minutes=5,
        level="intermediate",
        sections=(
            Section(
                heading={"en": "Dividing a sign by nine", "hi": "राशि को नौ से बाँटना"},
                body=(
                    {
                        "en": "Divide each 30-degree sign into nine parts of 3 degrees 20 minutes and you get the navamsa — the same width as a pada, which is not a coincidence. Each part maps to a sign, producing a second chart from the same longitudes.",
                        "hi": "तीस अंश की हर राशि को 3 अंश 20 कला के नौ हिस्सों में बाँटिए और नवांश मिलता है — पाद के बराबर चौड़ाई, और यह संयोग नहीं है। हर हिस्सा किसी राशि पर जाता है, और उन्हीं देशांतरों से दूसरी कुंडली बन जाती है।",
                    },
                    {
                        "en": "The mapping follows one rule. For a movable sign the nine parts start from that sign itself; for a fixed sign they start from the ninth sign from it; for a dual sign from the fifth. Run the count forward from there and every one of the 108 divisions has a navamsa sign, fixed by arithmetic and nothing else.",
                        "hi": "यह मिलान एक ही नियम से चलता है। चर राशि के लिए नौ हिस्से उसी राशि से शुरू होते हैं; स्थिर राशि के लिए उससे नवीं राशि से; द्विस्वभाव के लिए पाँचवीं से। वहाँ से आगे गिनते जाइए और 108 में से हर विभाजन की एक नवांश राशि निकल आती है, केवल गणित से तय।",
                    },
                ),
            ),
            Section(
                heading={"en": "What it is read for", "hi": "इसे किसलिए पढ़ा जाता है"},
                body=(
                    {
                        "en": "The navamsa is traditionally read for marriage and for the strength of a placement. It is not independent evidence: it is the same measurement viewed at higher magnification, so a shaky birth time makes it shakier, not steadier.",
                        "hi": "नवांश परंपरा में विवाह के लिए और किसी स्थिति के बल के लिए पढ़ा जाता है। यह स्वतंत्र प्रमाण नहीं है: यह वही माप है, बस ज़्यादा आवर्धन पर देखा हुआ — इसलिए डगमगाता जन्म समय इसे ज़्यादा डगमगाता है, स्थिर नहीं करता।",
                    },
                    {
                        "en": "There is a real idea underneath the marriage association. A navamsa is a ninth of a sign, and nine is the count the tradition attaches to completion, so the navamsa was read as what a placement matures into. Whether you find that persuasive is a separate question from whether the arithmetic is right, and the arithmetic is right.",
                        "hi": "विवाह वाले जुड़ाव के नीचे एक असली विचार है। नवांश राशि का नवाँ हिस्सा है, और नौ वह संख्या है जिसे परंपरा पूर्णता से जोड़ती है — इसलिए नवांश को यह पढ़ा गया कि कोई स्थिति पक कर क्या बनती है। यह आपको ठीक लगता है या नहीं, यह सवाल अलग है और गणित सही है या नहीं यह अलग — और गणित सही है।",
                    },
                ),
                aside={
                    "en": "Of the divisional charts, the navamsa is by far the most widely read. The higher divisions — D10 for work, D12 for parents — are specialist tools, and schools differ on how to construct them.",
                    "hi": "विभाग-कुंडलियों में नवांश ही सबसे ज़्यादा पढ़ा जाता है। ऊँचे विभाग — कर्म के लिए दशांश, माता-पिता के लिए द्वादशांश — विशेषज्ञों के औज़ार हैं, और उन्हें बनाने के तरीक़े पर परंपराएँ आपस में अलग-अलग हैं।",
                },
            ),
            Section(
                heading={"en": "Magnification, and what it costs", "hi": "आवर्धन, और उसकी क़ीमत"},
                body=(
                    {
                        "en": "Think about what dividing by nine does to error. A graha needs to move 30 degrees to change rashi but only 3°20' to change navamsa, so any uncertainty in the birth time has nine times the effect here. The lagna changes navamsa about every eight minutes.",
                        "hi": "सोचिए कि नौ से बाँटने पर चूक का क्या होता है। किसी ग्रह को राशि बदलने के लिए 30 अंश चलना पड़ता है, नवांश बदलने के लिए केवल 3°20' — यानी जन्म समय की कोई भी अनिश्चितता यहाँ नौ गुना असर करती है। लग्न क़रीब हर आठ मिनट में नवांश बदल देता है।",
                    },
                    {
                        "en": "So the navamsa is the part of a chart that most deserves a stated birth time and least deserves confident use without one. If your time came from a memory, the navamsa lagna is close to noise, and a reading built on it is building on sand while sounding more precise than the birth chart it came from.",
                        "hi": "इसलिए नवांश कुंडली का वह हिस्सा है जिसे सबसे ज़्यादा पक्के जन्म समय की दरकार है और बिना उसके सबसे कम भरोसे से इस्तेमाल होना चाहिए। आपका समय स्मृति से आया हो तो नवांश लग्न लगभग शोर है, और उस पर बनी व्याख्या रेत पर खड़ी होकर उस जन्म कुंडली से भी ज़्यादा परिशुद्ध सुनाई देती है जिससे वह निकली है।",
                    },
                ),
            ),
            Section(
                heading={"en": "The sixteen divisions", "hi": "सोलह विभाग"},
                body=(
                    {
                        "en": "The classical scheme names sixteen vargas: D1 the birth chart, D2 for wealth, D3 siblings, D7 children, D9 the navamsa, D10 career, D12 parents, up to D60. Each divides a sign into that many parts and maps each part to a sign.",
                        "hi": "शास्त्रीय व्यवस्था सोलह वर्गों को नाम देती है: जन्म कुंडली स्वयं, धन के लिए होरा, भाई-बहन के लिए द्रेष्काण, संतान के लिए सप्तांश, नवांश, कर्म के लिए दशांश, माता-पिता के लिए द्वादशांश, और आगे षष्ट्यंश तक। हर एक राशि को उतने हिस्सों में बाँटता है और हर हिस्से को किसी राशि पर भेजता है।",
                    },
                    {
                        "en": "The D60 divides a sign into sixty parts of half a degree, which the lagna crosses in about a minute. Whatever one thinks of the interpretation, a chart that changes every minute cannot be computed from a birth time nobody recorded to the minute — and most were not. This app computes the navamsa and stops there, deliberately.",
                        "hi": "षष्ट्यंश राशि को आधे-आधे अंश के साठ हिस्सों में बाँटता है, जिन्हें लग्न क़रीब एक मिनट में पार कर जाता है। व्याख्या के बारे में जो भी राय हो, हर मिनट बदलने वाली कुंडली उस जन्म समय से नहीं निकाली जा सकती जिसे किसी ने मिनट तक दर्ज ही नहीं किया — और अधिकांश दर्ज हुए ही नहीं। यह ऐप नवांश गिनकर वहीं रुक जाती है, जान-बूझकर।",
                    },
                ),
            ),
        ),
        personalise=P.navamsa_lagna,
    ),
    Chapter(
        slug="what-it-cannot-say",
        part=PART_PRACTICE,
        title={"en": "What astrology cannot say", "hi": "ज्योतिष क्या नहीं कह सकता"},
        summary={
            "en": "The honest boundary, drawn from the inside.",
            "hi": "ईमानदार सीमा, भीतर से खींची हुई।",
        },
        minutes=5,
        level="intermediate",
        sections=(
            Section(
                heading={"en": "Shared skies", "hi": "साझा आकाश"},
                body=(
                    {
                        "en": "Everyone born in your city that hour shares your lagna. Everyone born that month shares your Sun. A chart cannot pick you out of that crowd, and any reading that claims to name a specific event is claiming more than the method supports.",
                        "hi": "उस घंटे आपके शहर में जन्मा हर व्यक्ति आपका लग्न साझा करता है। उस महीने जन्मा हर व्यक्ति आपका सूर्य। कुंडली आपको उस भीड़ से अलग नहीं कर सकती, और जो व्याख्या किसी ख़ास घटना का नाम लेने का दावा करे, वह पद्धति से ज़्यादा का दावा कर रही है।",
                    },
                    {
                        "en": "Put a number on it. A large Indian city can see a few dozen births in an hour; the whole country sees roughly three thousand. All of them share a lagna to within a couple of degrees, and everything a chart says follows from positions they hold in common.",
                        "hi": "इस पर संख्या रखिए। किसी बड़े भारतीय शहर में एक घंटे में कुछ दर्जन जन्म हो सकते हैं; पूरे देश में क़रीब तीन हज़ार। इन सबका लग्न दो-एक अंश के भीतर एक ही है, और कुंडली जो कुछ कहती है वह उन्हीं साझा स्थितियों से निकलता है।",
                    },
                    {
                        "en": "Twins make the point sharpest. Born minutes apart, they share every graha to a fraction of a degree and usually the same lagna, and they go on to live different lives. That is not a puzzle the tradition has solved; it is a boundary the tradition runs into.",
                        "hi": "जुड़वाँ इस बात को सबसे तीखा कर देते हैं। कुछ मिनटों के अंतर पर जन्मे, उनके सारे ग्रह अंश के अंश तक एक हैं और लग्न भी प्रायः वही — और आगे उनका जीवन अलग-अलग चलता है। यह कोई पहेली नहीं जिसे परंपरा ने सुलझा लिया हो; यह वह सीमा है जिससे परंपरा टकराती है।",
                    },
                ),
            ),
            Section(
                heading={"en": "The specific refusals", "hi": "साफ़ इनकार"},
                body=(
                    {
                        "en": "Some things this app will not do, stated so you can hold it to them. It will not estimate anyone's lifespan or the timing of a death. It will not diagnose an illness or tell you whether to take a medicine. It will not name a date on which something will happen to you.",
                        "hi": "कुछ बातें यह ऐप नहीं करेगी, और यहाँ लिखी हैं ताकि आप इसे इन पर पकड़ सकें। वह किसी की आयु या मृत्यु का समय नहीं आँकेगी। वह किसी रोग का निदान नहीं करेगी और न यह बताएगी कि कोई दवा लेनी है या नहीं। वह ऐसी कोई तारीख़ नहीं बताएगी जिस दिन आपके साथ कुछ होगा।",
                    },
                    {
                        "en": "It will not tell you whether to marry a particular person, take a particular job, or make a legal or financial decision. And it will not tell you that a chart is weak, cursed, afflicted or in need of a remedy — because none of those are properties a set of coordinates has.",
                        "hi": "वह यह नहीं बताएगी कि किसी ख़ास व्यक्ति से विवाह करें या नहीं, कोई ख़ास नौकरी लें या नहीं, या कोई क़ानूनी-आर्थिक निर्णय कैसे करें। और वह यह भी नहीं कहेगी कि कोई कुंडली कमज़ोर, शापित, पीड़ित या उपाय की ज़रूरतमंद है — क्योंकि निर्देशांकों के समुच्चय का ऐसा कोई गुण होता ही नहीं।",
                    },
                ),
            ),
            Section(
                heading={"en": "Where the evidence actually stands", "hi": "प्रमाण असल में कहाँ खड़ा है"},
                body=(
                    {
                        "en": "It is worth being plain rather than diplomatic. Controlled studies have repeatedly failed to find that astrologers can match charts to biographies better than chance, and there is no known mechanism by which a planet's position would act on a person. That is the state of the evidence, and this course is not going to pretend otherwise.",
                        "hi": "यहाँ कूटनीति के बजाय सीधी बात ठीक है। नियंत्रित अध्ययनों में बार-बार यह नहीं मिला कि ज्योतिषी कुंडलियों को जीवन-वृत्तों से संयोग से बेहतर मिला पाते हों, और ऐसा कोई ज्ञात तंत्र भी नहीं जिससे किसी ग्रह की स्थिति व्यक्ति पर असर करे। प्रमाण की स्थिति यही है, और यह पाठ्यक्रम इसके उलट दिखावा नहीं करेगा।",
                    },
                    {
                        "en": "What survives that is still real. The astronomy is exact and independently checkable. The tradition is a coherent body of knowledge, worth studying as a tradition. And a structured vocabulary for describing a period of your life is genuinely useful to a lot of people — the way a well-chosen question is useful, not the way a diagnosis is.",
                        "hi": "इसके बाद भी जो बचता है वह असली है। खगोल सटीक है और स्वतंत्र रूप से जाँचा जा सकता है। परंपरा ज्ञान का एक संगत पिंड है, जिसे परंपरा की तरह पढ़ना सार्थक है। और अपने जीवन के किसी काल का वर्णन करने की एक सुगठित शब्दावली बहुत लोगों के सचमुच काम आती है — उस तरह जैसे कोई सही सवाल काम आता है, उस तरह नहीं जैसे कोई निदान।",
                    },
                ),
            ),
            Section(
                heading={"en": "What it can offer", "hi": "यह क्या दे सकता है"},
                body=(
                    {
                        "en": "What it can offer is a vocabulary for describing a period, and a mirror many people find useful. That is a real thing. It is also a smaller thing than what is usually sold.",
                        "hi": "जो वह दे सकता है वह है किसी काल का वर्णन करने की शब्दावली, और एक आईना जो बहुतों को काम आता है। यह असली चीज़ है। और यह उससे छोटी चीज़ भी है जो आमतौर पर बेची जाती है।",
                    },
                    {
                        "en": "Held that way it is hard to be hurt by. A description you can disagree with, applied to a stretch of time you are living through anyway, costs nothing and occasionally shows you something. A verdict handed down about your future, with a price attached to changing it, is a different transaction entirely — and telling those two apart is the single most useful thing this course can leave you with.",
                        "hi": "इस तरह थामा जाए तो इससे चोट लगना कठिन है। ऐसा वर्णन जिससे आप असहमत हो सकें, और जो उसी समय पर लागू हो जिसे आप वैसे भी जी रहे हैं — उसकी कोई क़ीमत नहीं और कभी-कभी वह कुछ दिखा भी देता है। आपके भविष्य पर सुनाया गया फ़ैसला, जिसे बदलने का दाम लगा हो, बिल्कुल दूसरा सौदा है — और इन दोनों में फ़र्क़ कर पाना ही सबसे काम की चीज़ है जो यह पाठ्यक्रम आपके पास छोड़ सकता है।",
                    },
                ),
            ),
        ),
        personalise=P.nothing_is_a_verdict,
    ),
    Chapter(
        slug="reading-responsibly",
        part=PART_PRACTICE,
        title={"en": "Reading responsibly", "hi": "ज़िम्मेदारी से पढ़ना"},
        summary={
            "en": "The dosha business, and what to do when a chart is being used against someone.",
            "hi": "दोष का धंधा, और जब कुंडली किसी के ख़िलाफ़ इस्तेमाल हो रही हो तब क्या करें।",
        },
        minutes=7,
        level="basic",
        sections=(
            Section(
                heading={"en": "A measurement turned into a lever", "hi": "माप, जो दबाव का औज़ार बना"},
                body=(
                    {
                        "en": "Manglik dosha, kaal sarp, sade sati. Each names a real, computable configuration. Each has also become a product: a diagnosis to frighten someone with, and a payment offered as the cure.",
                        "hi": "मांगलिक दोष, कालसर्प, साढ़ेसाती। हर एक किसी असली, गणनीय स्थिति का नाम है। और हर एक अब सामान भी बन चुका है: डराने के लिए एक निदान, और इलाज के नाम पर एक भुगतान।",
                    },
                    {
                        "en": "The configuration is a fact about where planets were. The claim that it causes a specific misfortune, and the claim that money removes it, are neither of those things.",
                        "hi": "वह स्थिति इस बात का तथ्य है कि ग्रह कहाँ थे। यह दावा कि उससे कोई ख़ास दुर्भाग्य आता है, और यह कि पैसा उसे हटा देता है — इनमें से कोई तथ्य नहीं है।",
                    },
                    {
                        "en": "Notice the shape all three share. A configuration common enough that a large fraction of people have it, a name that sounds like a verdict, and a fix that costs money. That shape is the product, and it works the same way whichever configuration is plugged into it.",
                        "hi": "तीनों में एक ही बनावट देखिए। ऐसी स्थिति जो इतनी आम है कि लोगों का बड़ा हिस्सा उसमें आता है, ऐसा नाम जो फ़ैसले जैसा लगता है, और ऐसा इलाज जिसका दाम है। सामान यही बनावट है, और उसमें कोई भी स्थिति डाल दीजिए, वह उसी तरह काम करती है।",
                    },
                ),
            ),
            Section(
                heading={"en": "When a chart is used as an excuse", "hi": "जब कुंडली बहाना बन जाए"},
                body=(
                    {
                        "en": "The most common harm this tradition is put to is not a wrong prediction. It is an explanation offered where a different response was needed — a marriage blamed on a dosha rather than on violence, a depression treated as a planetary period rather than an illness.",
                        "hi": "इस परंपरा से होने वाली सबसे आम हानि ग़लत भविष्यवाणी नहीं है। वह है ऐसी जगह व्याख्या देना जहाँ कुछ और चाहिए था — किसी विवाह का दोष हिंसा के बजाय कुंडली पर, किसी अवसाद को रोग के बजाय दशा मान लेना।",
                    },
                    {
                        "en": "No chart can make anyone hit you. If someone is being harmed, the answer is help, not a remedy.",
                        "hi": "कोई कुंडली किसी से मारपीट नहीं करवाती। अगर किसी को नुक़सान पहुँचाया जा रहा है, तो उत्तर मदद है, उपाय नहीं।",
                    },
                    {
                        "en": "The same holds for anything a doctor should be looking at. A dasha is not a diagnosis, a transit is not a treatment plan, and a period ending is not a reason to stop medication. If a reading is being used to postpone care, the reading is the problem.",
                        "hi": "यही बात हर उस मामले पर लागू है जिसे किसी चिकित्सक को देखना चाहिए। दशा निदान नहीं है, गोचर इलाज की योजना नहीं है, और किसी काल का ख़त्म होना दवा बंद करने का कारण नहीं है। कोई व्याख्या इलाज टालने के काम आ रही हो, तो समस्या वह व्याख्या ही है।",
                    },
                ),
                aside={
                    "en": "This app stops reading charts entirely for someone in crisis and offers real help instead: Tele-MANAS 14416, AASRA +91-9820466726, Women Helpline 181, or 112 for immediate danger.",
                    "hi": "संकट में होने पर यह ऐप कुंडली पढ़ना पूरी तरह रोक देती है और असली मदद सामने रखती है: टेली-मानस 14416, आसरा +91-9820466726, महिला हेल्पलाइन 181, या तुरंत ख़तरे में 112।",
                },
            ),
            Section(
                heading={"en": "Matching, and who pays for it", "hi": "मिलान, और उसकी क़ीमत कौन चुकाता है"},
                body=(
                    {
                        "en": "The ashtakoot procedure scores two janma nakshatras across eight categories out of 36. The arithmetic is ordinary and takes a minute. What it has become is a gate: a number below some threshold used to call off a match, and a manglik label used to demand a larger dowry or a ritual marriage to a tree or a pot before the real one.",
                        "hi": "अष्टकूट विधि दो जन्म नक्षत्रों को आठ कूटों में 36 में से अंक देती है। गणित सामान्य है और मिनट भर का। पर वह अब एक फाटक बन चुकी है: किसी सीमा से कम अंक रिश्ता तोड़ने का कारण, और मांगलिक का लेबल बड़ा दहेज माँगने या असली विवाह से पहले पेड़ या घड़े से विवाह कराने का बहाना।",
                    },
                    {
                        "en": "The cost of this falls unevenly, and it is worth saying who pays it: overwhelmingly women, and most heavily women whose families have least power to argue. A tradition being used that way is not being honoured by it.",
                        "hi": "इसकी क़ीमत सब पर बराबर नहीं पड़ती, और यह कह देना चाहिए कि चुकाता कौन है: भारी बहुमत में स्त्रियाँ, और सबसे ज़्यादा वे स्त्रियाँ जिनके परिवारों के पास बहस करने की सबसे कम ताक़त है। परंपरा का इस तरह इस्तेमाल उसका सम्मान नहीं है।",
                    },
                ),
            ),
            Section(
                heading={"en": "How the sale is made", "hi": "बिक्री कैसे होती है"},
                body=(
                    {
                        "en": "The pattern is consistent enough to name. First, a fact you can verify — your Moon is in this sign, Saturn is transiting that one. It checks out, so you extend trust. Then a claim you cannot verify, delivered in the same tone. Then urgency: a window closing, a period starting. Then the price.",
                        "hi": "ढर्रा इतना एक-सा है कि उसे नाम दिया जा सकता है। पहले ऐसा तथ्य जिसे आप जाँच सकते हैं — आपका चंद्रमा इस राशि में है, शनि उस राशि से गुज़र रहा है। वह सही निकलता है, तो आप भरोसा बढ़ा देते हैं। फिर वैसे ही स्वर में ऐसा दावा जिसे आप जाँच नहीं सकते। फिर जल्दबाज़ी: बंद होती खिड़की, शुरू होता काल। फिर दाम।",
                    },
                    {
                        "en": "The verifiable part is doing a job — it is there to buy credibility for the unverifiable part. That is exactly why this course spends so long on arithmetic you can check yourself: once you can verify the first step on your own, it stops being currency anyone can spend on you.",
                        "hi": "जाँचा जा सकने वाला हिस्सा एक काम कर रहा है — वह न जाँचे जा सकने वाले हिस्से के लिए विश्वसनीयता ख़रीद रहा है। इसीलिए यह पाठ्यक्रम उस गणित पर इतना समय देता है जिसे आप ख़ुद जाँच सकें: पहला क़दम आप स्वयं जाँचने लगें, तो वह किसी के लिए आप पर ख़र्च करने की मुद्रा नहीं रह जाता।",
                    },
                ),
            ),
            Section(
                heading={"en": "A working standard", "hi": "एक काम का मानक"},
                body=(
                    {
                        "en": "A reading that frightens you, ranks your chart as weak, or ends in something for sale has stopped describing the sky. You are allowed to walk away from it — including from this app.",
                        "hi": "जो व्याख्या आपको डराए, आपकी कुंडली को कमज़ोर ठहराए, या किसी बिकाऊ चीज़ पर ख़त्म हो — वह आकाश का वर्णन करना बंद कर चुकी है। उससे हट जाना आपका अधिकार है — इस ऐप से भी।",
                    },
                    {
                        "en": "Four questions cover most cases. Which measurement is this based on, and can I see it? Would this statement be false for anyone born the same hour? Does it tell me what to do, or describe an area? And is there something to buy at the end of it?",
                        "hi": "चार सवाल अधिकांश मामले ढँक लेते हैं। यह किस माप पर टिकी है, और क्या वह माप मुझे दिख सकता है? क्या यह बात उसी घंटे जन्मे किसी और के लिए ग़लत होगी? यह मुझे करना क्या है यह बताती है, या किसी क्षेत्र का वर्णन करती है? और क्या इसके अंत में कुछ ख़रीदने को है?",
                    },
                ),
            ),
            Section(
                heading={"en": "Where to go from here", "hi": "यहाँ से आगे"},
                body=(
                    {
                        "en": "You have the whole of the machinery now: coordinates, grahas, houses, nakshatras, and three ways of putting a clock on them. Open your own chart and read it back — name every number, check the two or three you can compute by hand, and notice which parts of it depend on a birth time you are sure of.",
                        "hi": "अब पूरा तंत्र आपके पास है: निर्देशांक, ग्रह, भाव, नक्षत्र, और उन पर घड़ी रखने के तीन तरीक़े। अपनी कुंडली खोलकर उसे वापस पढ़िए — हर संख्या का नाम लीजिए, दो-तीन को हाथ से जाँचिए, और देखिए कि उसका कौन सा हिस्सा उस जन्म समय पर टिका है जिस पर आपको भरोसा है।",
                    },
                    {
                        "en": "If you want to go further, go to the sources rather than to the market — the classical texts, a teacher who will show you their working, a panchang you can check against this one. And keep the habit this course was built around: separate the measurement from the reading, every single time, and you can take the tradition as seriously as it deserves without ever being at its mercy.",
                        "hi": "और आगे जाना हो तो बाज़ार की ओर नहीं, स्रोतों की ओर जाइए — शास्त्रीय ग्रंथ, ऐसा शिक्षक जो अपनी गणना दिखा दे, ऐसा पंचांग जिसे इससे मिलाया जा सके। और वह आदत बनाए रखिए जिस पर यह पाठ्यक्रम खड़ा है: माप और व्याख्या को हर बार अलग रखिए — फिर आप परंपरा को उतनी ही गंभीरता से ले सकेंगे जितनी वह हक़दार है, और कभी उसकी दया पर नहीं रहेंगे।",
                    },
                ),
            ),
        ),
        personalise=P.nothing_is_a_verdict,
    ),
)
