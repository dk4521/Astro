"""Part five: time.

Dashas, transits and the panchang — the three ways this tradition puts a clock
on a chart. This is the part most readers come for and the part most easily
turned into a product, so every chapter states its arithmetic first and its
interpretation second.
"""

from __future__ import annotations

from .. import personalise as P
from ..models import Chapter, Section
from . import PART_TIME

CHAPTERS: tuple[Chapter, ...] = (
    Chapter(
        slug="vimshottari-idea",
        part=PART_TIME,
        title={"en": "Vimshottari: the idea", "hi": "विम्शोत्तरी: मूल विचार"},
        summary={
            "en": "A 120-year clock, in a fixed order that never changes.",
            "hi": "120 वर्ष की एक घड़ी, ऐसे क्रम में जो कभी नहीं बदलता।",
        },
        minutes=6,
        level="intermediate",
        sections=(
            Section(
                heading={"en": "One hundred and twenty years", "hi": "एक सौ बीस वर्ष"},
                body=(
                    {
                        "en": "Vimshottari is a sequence of periods, each ruled by one graha, running in a fixed order: Ketu 7 years, Venus 20, Sun 6, Moon 10, Mars 7, Rahu 18, Jupiter 16, Saturn 19, Mercury 17. Add them and you get 120.",
                        "hi": "विम्शोत्तरी दशाओं की एक शृंखला है, हर दशा का एक स्वामी ग्रह, और क्रम निश्चित: केतु 7 वर्ष, शुक्र 20, सूर्य 6, चंद्र 10, मंगल 7, राहु 18, गुरु 16, शनि 19, बुध 17। जोड़िए तो 120 बनते हैं।",
                    },
                    {
                        "en": "The order never changes for anyone. What differs is where in the sequence you start, and how much of that first period had already run when you were born.",
                        "hi": "क्रम किसी के लिए नहीं बदलता। जो बदलता है वह यह कि आप शृंखला में कहाँ से शुरू करते हैं, और जन्म के समय उस पहली दशा का कितना हिस्सा बीत चुका था।",
                    },
                    {
                        "en": "The name says as much: vimshottari means “one hundred and twenty”. It is the most widely used of many dasha systems — the texts describe dozens — and it is the one this app computes, because it is the one nearly every Indian reading you will encounter is built on.",
                        "hi": "नाम में ही यह कहा हुआ है: विम्शोत्तरी यानी “एक सौ बीस”। कई दशा-पद्धतियों में — ग्रंथ दर्जनों बताते हैं — यही सबसे ज़्यादा चलती है, और यही ऐप गिनती है, क्योंकि आपको मिलने वाली लगभग हर भारतीय व्याख्या इसी पर बनी होती है।",
                    },
                ),
            ),
            Section(
                heading={"en": "Why the sequence starts where it does", "hi": "शृंखला वहीं से क्यों शुरू होती है"},
                body=(
                    {
                        "en": "The order is exactly the nakshatra-lord cycle from chapter 21 — Ketu, Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury — and that is the whole connection. Your janma nakshatra names a lord, and that lord's period is the one you were born inside.",
                        "hi": "यह क्रम ठीक वही नक्षत्र-स्वामी चक्र है जो अध्याय 21 में आया — केतु, शुक्र, सूर्य, चंद्र, मंगल, राहु, गुरु, शनि, बुध — और पूरा संबंध इतना ही है। आपका जन्म नक्षत्र एक स्वामी बताता है, और उसी स्वामी की दशा में आप जन्मे थे।",
                    },
                    {
                        "en": "After that the sequence simply runs on. Whoever starts in Rahu goes to Jupiter, then Saturn, then Mercury, then wraps around to Ketu — the cycle is a circle, so everyone eventually walks the same 120 years in the same order, just entering it at a different door.",
                        "hi": "उसके बाद शृंखला बस चलती रहती है। जो राहु से शुरू हुआ वह गुरु पर जाएगा, फिर शनि, फिर बुध, फिर घूमकर केतु — चक्र वृत्त है, इसलिए हर कोई अंततः वही 120 वर्ष उसी क्रम में चलता है, बस दरवाज़ा अलग होता है।",
                    },
                ),
            ),
            Section(
                heading={"en": "A marker, not a schedule", "hi": "चिह्न, समय-सारणी नहीं"},
                body=(
                    {
                        "en": "A dasha marks which theme the tradition considers foreground at a given time. It is not a calendar of events, and no honest reading will tell you what will happen during one.",
                        "hi": "दशा बताती है कि किसी काल में परंपरा किस विषय को अग्रभूमि में मानती है। यह घटनाओं का पंचांग नहीं है, और कोई ईमानदार व्याख्या यह नहीं बताएगी कि उस दौरान क्या होगा।",
                    },
                    {
                        "en": "The most useful way to hold it is as a chapter heading on a stretch of your life, written by a system that had never met you. A Saturn mahadasha is nineteen years long. Any statement that applies to a nineteen-year block is, by construction, either very general or wrong.",
                        "hi": "इसे थामने का सबसे काम का तरीक़ा यह है: आपके जीवन के एक हिस्से पर लगा अध्याय-शीर्षक, जिसे ऐसी व्यवस्था ने लिखा है जो आपसे कभी मिली नहीं। शनि की महादशा उन्नीस वर्ष की होती है। उन्नीस वर्ष के खंड पर लागू होने वाली कोई भी बात बनावट से ही या तो बहुत सामान्य होगी या ग़लत।",
                    },
                ),
                aside={
                    "en": "Vimshottari is counted in years of 365.25 days. Texts that use a 360-day year produce dates that drift — one reason two panchangs disagree about exactly when a period turns.",
                    "hi": "विम्शोत्तरी 365.25 दिन के वर्ष से गिनी जाती है। जो ग्रंथ 360 दिन का वर्ष लेते हैं उनकी तारीख़ें खिसक जाती हैं — दो पंचांगों में दशा-परिवर्तन का ठीक दिन अलग होने का यह भी एक कारण है।",
                },
            ),
            Section(
                heading={"en": "What it can and cannot support", "hi": "यह किसका भार उठा सकती है, किसका नहीं"},
                body=(
                    {
                        "en": "The arithmetic is exact. Given a birth moment, the start and end date of every period for a hundred and twenty years is fixed, and two engines that agree on the Moon's longitude will agree on every one of those dates to within a day.",
                        "hi": "गणित बिल्कुल सटीक है। जन्म-क्षण मिल जाए तो एक सौ बीस वर्ष की हर दशा की आरंभ और अंत तिथि तय है, और चंद्रमा के देशांतर पर सहमत दो इंजन उन सारी तारीख़ों पर एक दिन के भीतर सहमत होंगे।",
                    },
                    {
                        "en": "Exactness of the arithmetic is not evidence for the interpretation. It is entirely possible — and this is the honest position — for the dates to be computed perfectly and for the claim that they correspond to anything in a life to remain unproven. Keep those two facts in separate hands.",
                        "hi": "गणित का सटीक होना व्याख्या का प्रमाण नहीं है। यह पूरी तरह संभव है — और ईमानदार स्थिति यही है — कि तारीख़ें बिल्कुल ठीक निकलें और यह दावा अप्रमाणित बना रहे कि उनका किसी जीवन में कुछ मेल है। इन दोनों तथ्यों को अलग-अलग हाथों में रखिए।",
                    },
                    {
                        "en": "The practical test is the same one from chapter 1: ask what the statement could have come from. A dasha is derived from one number, the Moon's longitude at birth. Anything a period-based reading claims to know beyond “which graha's turn it is” did not come from that number.",
                        "hi": "व्यावहारिक जाँच वही है जो अध्याय 1 में थी: पूछिए कि यह बात किससे निकल सकती थी। दशा एक ही संख्या से निकलती है — जन्म के समय चंद्रमा का देशांतर। दशा-आधारित कोई व्याख्या “किस ग्रह की बारी है” से आगे जो कुछ जानने का दावा करे, वह उस संख्या से नहीं आया।",
                    },
                ),
            ),
            Section(
                heading={"en": "How to read a period", "hi": "किसी दशा को कैसे पढ़ें"},
                body=(
                    {
                        "en": "Take the graha's vocabulary from part two, take the houses it occupies and rules from part three, and read the period as an emphasis on those areas. That is the entire legitimate procedure, and it produces a description of a theme rather than a forecast of an event.",
                        "hi": "उस ग्रह की शब्दावली दूसरे भाग से लीजिए, वह किन भावों में है और किनका स्वामी है यह तीसरे भाग से, और दशा को उन्हीं क्षेत्रों पर पड़े ज़ोर की तरह पढ़िए। पूरी वैध विधि इतनी ही है, और उससे किसी घटना की भविष्यवाणी नहीं, किसी विषय का वर्णन निकलता है।",
                    },
                    {
                        "en": "What you should not accept from any source, including this one: a date on which something will happen, a warning that a period will be bad, or a remedy priced against it. Those are the three shapes the misuse takes, and chapter 30 deals with all three.",
                        "hi": "किसी भी स्रोत से — इस ऐप से भी — जो नहीं मानना चाहिए: कोई तारीख़ जिस पर कुछ होगा, यह चेतावनी कि कोई काल बुरा जाएगा, या उसके बदले दाम पर बिकता कोई उपाय। दुरुपयोग इन्हीं तीन रूपों में आता है, और अध्याय 30 तीनों को देखता है।",
                    },
                ),
            ),
        ),
        personalise=P.dasha_now,
    ),
    Chapter(
        slug="dasha-balance",
        part=PART_TIME,
        title={"en": "Where your timeline starts", "hi": "आपकी समय-रेखा कहाँ से शुरू होती है"},
        summary={
            "en": "The balance at birth, and why nobody starts at the beginning.",
            "hi": "जन्म के समय बची दशा, और कोई भी शुरुआत से क्यों नहीं चलता।",
        },
        minutes=4,
        level="intermediate",
        sections=(
            Section(
                heading={"en": "The unfinished first period", "hi": "अधूरी पहली दशा"},
                body=(
                    {
                        "en": "Your first mahadasha is ruled by the lord of your janma nakshatra. But you were not born at the instant that nakshatra began — the Moon was already some way into it. That fraction is the part of the period that had already elapsed.",
                        "hi": "आपकी पहली महादशा का स्वामी आपके जन्म नक्षत्र का स्वामी होता है। पर आप उस क्षण नहीं जन्मे जब वह नक्षत्र शुरू हुआ था — चंद्रमा उसमें कुछ आगे बढ़ चुका था। वही अंश उस दशा का बीत चुका हिस्सा है।",
                    },
                    {
                        "en": "So almost nobody starts life at the beginning of a dasha. The remainder is called the balance, and everything after it follows in strict order.",
                        "hi": "इसलिए लगभग कोई भी जीवन दशा के आरंभ से शुरू नहीं करता। जो बचा रहता है उसे शेष दशा कहते हैं, और उसके बाद सब कुछ कड़े क्रम में चलता है।",
                    },
                ),
            ),
            Section(
                heading={"en": "The arithmetic, worked", "hi": "गणित, हल करके"},
                body=(
                    {
                        "en": "Suppose the Moon was 40% of the way through Rohini, whose lord is the Moon, a period of 10 years. Then 40% of 10 years — four years — had already passed before you were born, and your Moon mahadasha runs for the remaining six. On your sixth birthday, near enough, it hands over to Mars.",
                        "hi": "मान लीजिए चंद्रमा रोहिणी का 40% पार कर चुका था, जिसका स्वामी चंद्र है और दशा 10 वर्ष की। तब 10 वर्ष का 40% — यानी चार वर्ष — आपके जन्म से पहले ही बीत चुका था, और आपकी चंद्र महादशा बचे हुए छह वर्ष चलेगी। लगभग आपके छठे जन्मदिन पर वह मंगल को सौंप देगी।",
                    },
                    {
                        "en": "That is the whole calculation: fraction of the nakshatra remaining, times the lord's allotted years. Everything downstream — every mahadasha boundary for the next hundred and twenty years — is that one number plus fixed addition.",
                        "hi": "पूरी गणना इतनी ही है: नक्षत्र का बचा हुआ अंश, गुणा स्वामी के तय वर्ष। उसके आगे सब कुछ — अगले एक सौ बीस वर्ष की हर महादशा की सीमा — उसी एक संख्या में तय जोड़ लगाते जाने से बनता है।",
                    },
                    {
                        "en": "This app computes that fraction from the Moon's exact longitude, counts in years of 365.25 days, and shows you the resulting dates. You can check the first one by hand from the degrees on your chart screen, and if the first is right the rest are arithmetic.",
                        "hi": "यह ऐप वह अंश चंद्रमा के ठीक देशांतर से निकालती है, 365.25 दिन के वर्ष से गिनती है, और बनी हुई तारीख़ें दिखा देती है। पहली तारीख़ आप कुंडली स्क्रीन के अंशों से हाथ से जाँच सकते हैं, और पहली सही निकली तो बाक़ी सब जोड़-भर है।",
                    },
                ),
            ),
            Section(
                heading={"en": "Why the Moon's precision matters here", "hi": "यहाँ चंद्रमा की परिशुद्धता क्यों मायने रखती है"},
                body=(
                    {
                        "en": "The Moon crosses a nakshatra in about 24 hours, so an hour of birth-time error moves the fraction by roughly 4% — which, on a 20-year Venus period, is about ten months of shift in every date that follows.",
                        "hi": "चंद्रमा एक नक्षत्र क़रीब 24 घंटे में पार करता है, इसलिए जन्म समय की एक घंटे की चूक उस अंश को क़रीब 4% खिसका देती है — और शुक्र की 20 वर्ष की दशा पर यह आगे की हर तारीख़ में क़रीब दस महीने का फ़र्क़ है।",
                    },
                    {
                        "en": "This is the honest reason to distrust dasha dates quoted to the day. The arithmetic is exact, but it is exact about an input most people know only approximately. A period boundary given as a month is defensible; one given as a date, from a remembered time, is precision the input cannot carry.",
                        "hi": "दिन तक बताई गई दशा-तारीख़ों पर संदेह करने का ईमानदार कारण यही है। गणित सटीक है, पर वह ऐसे इनपुट के बारे में सटीक है जिसे अधिकांश लोग केवल मोटे तौर पर जानते हैं। महीने के रूप में बताई गई दशा-संधि टिक सकती है; याद किए हुए समय से दिन के रूप में बताई गई संधि वह परिशुद्धता है जो इनपुट ढो ही नहीं सकता।",
                    },
                ),
                aside={
                    "en": "If your birth time is a family estimate, read your dasha boundaries as “somewhere in this year”, not as dates.",
                    "hi": "आपका जन्म समय घर के अनुमान से आया हो, तो दशा की संधियों को “इस साल में कहीं” की तरह पढ़िए, तारीख़ की तरह नहीं।",
                },
            ),
            Section(
                heading={"en": "What the balance is not", "hi": "शेष दशा क्या नहीं है"},
                body=(
                    {
                        "en": "It is common to hear that being born in the balance of a particular graha's period says something about a person's early life or their nature. Notice what that claim requires: it treats an accident of where the Moon happened to be as a statement about a childhood.",
                        "hi": "यह सुनने को मिलता रहता है कि किसी ख़ास ग्रह की शेष दशा में जन्म लेना व्यक्ति के आरंभिक जीवन या स्वभाव के बारे में कुछ कहता है। ध्यान दीजिए कि इस दावे को क्या चाहिए: वह चंद्रमा के संयोग से कहाँ होने को किसी बचपन के बारे में बयान बना देता है।",
                    },
                    {
                        "en": "The balance is a starting offset, nothing more — the same role a page number plays when you open a book partway through. It tells you where the sequence begins. It does not tell you what the book says.",
                        "hi": "शेष दशा बस एक आरंभिक खिसकाव है, इससे ज़्यादा कुछ नहीं — वही काम जो किसी किताब को बीच से खोलने पर पन्ने की संख्या करती है। वह बताती है कि शृंखला कहाँ से शुरू होती है। यह नहीं बताती कि किताब में लिखा क्या है।",
                    },
                ),
            ),
        ),
        personalise=P.dasha_balance,
    ),
    Chapter(
        slug="sub-periods",
        part=PART_TIME,
        title={"en": "Periods inside periods", "hi": "दशा के भीतर दशा"},
        summary={
            "en": "Antardasha, pratyantardasha, and how deep is useful.",
            "hi": "अंतर्दशा, प्रत्यंतर्दशा, और कितनी गहराई काम की है।",
        },
        minutes=4,
        level="intermediate",
        sections=(
            Section(
                heading={"en": "The same order, nested", "hi": "वही क्रम, भीतर दोहराया हुआ"},
                body=(
                    {
                        "en": "Each mahadasha divides into antardashas in the same nine-graha order, proportional to their years. Those divide again into pratyantardashas, and so on as deep as you like.",
                        "hi": "हर महादशा उसी नौ-ग्रह क्रम में अंतर्दशाओं में बँटती है, उनके वर्षों के अनुपात में। वे फिर प्रत्यंतर्दशाओं में बँटती हैं, और जितना गहरा चाहें उतना।",
                    },
                    {
                        "en": "One rule does the whole job: a sub-period always begins with the graha ruling the period it sits inside. A Venus mahadasha opens with Venus–Venus, then Venus–Sun, Venus–Moon, and on through the cycle back to Venus–Ketu.",
                        "hi": "पूरा काम एक ही नियम करता है: कोई भी उप-दशा उसी ग्रह से शुरू होती है जो उसकी ऊपरी दशा का स्वामी है। शुक्र की महादशा शुक्र-शुक्र से खुलती है, फिर शुक्र-सूर्य, शुक्र-चंद्र, और चक्र में घूमते हुए वापस शुक्र-केतु तक।",
                    },
                ),
            ),
            Section(
                heading={"en": "The proportion, worked", "hi": "अनुपात, हल करके"},
                body=(
                    {
                        "en": "The length of a sub-period is its own allotment times the parent's, divided by 120. Inside Venus's 20 years, Saturn's antardasha runs 20 × 19 ÷ 120 — about three years and two months. Inside that, Mercury's pratyantardasha runs the same way again, and comes to about five and a half months.",
                        "hi": "किसी उप-दशा की लंबाई है: उसका अपना हिस्सा गुणा ऊपरी दशा का हिस्सा, भाग 120। शुक्र के 20 वर्षों के भीतर शनि की अंतर्दशा 20 × 19 ÷ 120 चलती है — क़रीब तीन वर्ष दो महीने। उसी के भीतर बुध की प्रत्यंतर्दशा फिर उसी तरह निकलती है, और क़रीब साढ़े पाँच महीने बैठती है।",
                    },
                    {
                        "en": "Because every level uses the same divisor, the nine sub-periods of any period always add back up to exactly the parent. The scheme is self-consistent at every depth, which is part of why it is so easy to keep subdividing.",
                        "hi": "हर स्तर पर वही भाजक लगने से किसी भी दशा की नौ उप-दशाएँ जुड़कर ठीक ऊपरी दशा बन जाती हैं। यह व्यवस्था हर गहराई पर अपने भीतर संगत है, और इसीलिए बाँटते चले जाना इतना आसान है।",
                    },
                ),
            ),
            Section(
                heading={"en": "Three levels, and why it stops there", "hi": "तीन स्तर, और वहीं क्यों रुकना"},
                body=(
                    {
                        "en": "This app computes three levels, which is enough to name a period of a few months. Going deeper is arithmetically easy and interpretively meaningless — precision past the point where anything can be checked is just decoration.",
                        "hi": "यह ऐप तीन स्तर गिनती है, जो कुछ महीनों के काल को नाम देने के लिए काफ़ी है। इससे गहरे जाना गणित में आसान है और व्याख्या में निरर्थक — जहाँ कुछ जाँचा ही न जा सके, उससे आगे की परिशुद्धता केवल सजावट है।",
                    },
                    {
                        "en": "Put the numbers side by side and the point makes itself. The classical scheme has five named levels; the fifth divides a life into segments of a few days. Meanwhile the input — your birth time — is usually known to somewhere between a minute and an hour. Computing to the day from an input good to the hour is not accuracy, it is theatre.",
                        "hi": "संख्याएँ अगल-बग़ल रखिए और बात अपने आप कह देती है। शास्त्रीय व्यवस्था में पाँच नामित स्तर हैं; पाँचवाँ जीवन को कुछ दिनों के टुकड़ों में बाँट देता है। और इनपुट — आपका जन्म समय — प्रायः एक मिनट से एक घंटे के बीच कहीं ज्ञात होता है। घंटे भर की परिशुद्धता वाले इनपुट से दिन तक गिनना सटीकता नहीं, नाटक है।",
                    },
                ),
            ),
            Section(
                heading={"en": "Reading a nested label", "hi": "जुड़ा हुआ नाम पढ़ना"},
                body=(
                    {
                        "en": "A label like “Venus–Saturn–Mercury” names three grahas from outside in: the mahadasha, the antardasha, the pratyantardasha. Read it as three levels of emphasis on one stretch of time, the outermost being the broadest.",
                        "hi": "“शुक्र-शनि-बुध” जैसा नाम बाहर से भीतर की ओर तीन ग्रह बताता है: महादशा, अंतर्दशा, प्रत्यंतर्दशा। इसे समय के एक हिस्से पर पड़े ज़ोर के तीन स्तरों की तरह पढ़िए, जिसमें सबसे बाहर वाला सबसे चौड़ा है।",
                    },
                    {
                        "en": "The tradition reads the combination — how the three grahas sit relative to each other in your chart — rather than the three separately. That is a legitimate procedure. What is not legitimate is the version that arrives with a date, a fear and a fee, and the tighter the period quoted, the more likely you are looking at the second kind.",
                        "hi": "परंपरा तीनों को अलग-अलग नहीं, उनके मेल को पढ़ती है — यानी आपकी कुंडली में वे तीन ग्रह एक-दूसरे के सापेक्ष कैसे बैठे हैं। यह वैध विधि है। अवैध वह रूप है जो तारीख़, डर और शुल्क के साथ आता है — और बताया गया काल जितना कसा हुआ हो, दूसरी क़िस्म होने की संभावना उतनी ज़्यादा।",
                    },
                ),
                aside={
                    "en": "Your timeline screen shows three levels and the period active now. Nothing on it is generated; it is the same arithmetic, run forward from your birth moment.",
                    "hi": "आपकी समय-रेखा स्क्रीन तीन स्तर और इस समय चल रही दशा दिखाती है। उसमें कुछ भी मशीन-रचित नहीं; वही गणित है, आपके जन्म-क्षण से आगे चलाया हुआ।",
                },
            ),
        ),
        personalise=P.sub_periods,
    ),
    Chapter(
        slug="gochara",
        part=PART_TIME,
        title={"en": "Transits", "hi": "गोचर"},
        summary={
            "en": "Where the planets are now, against where they were when you were born.",
            "hi": "ग्रह इस समय कहाँ हैं, आपके जन्म के समय की स्थिति के सामने रखकर।",
        },
        minutes=4,
        level="intermediate",
        sections=(
            Section(
                heading={"en": "Two clocks at once", "hi": "एक साथ दो घड़ियाँ"},
                body=(
                    {
                        "en": "The birth chart is frozen. Gochara — transit — is the live sky, read against that frozen picture. Saturn taking two and a half years per sign, Jupiter one year, the Moon two and a quarter days: each is a different tempo laid over the same chart.",
                        "hi": "जन्म कुंडली जमी हुई है। गोचर जीवित आकाश है, जिसे उसी जमी हुई तस्वीर के सामने रखकर पढ़ा जाता है। शनि हर राशि में ढाई वर्ष, गुरु एक वर्ष, चंद्रमा सवा दो दिन: हर एक उसी कुंडली पर पड़ी अलग लय है।",
                    },
                    {
                        "en": "Indian practice usually reads transits from the Moon's sign rather than the lagna — “Saturn in the twelfth from your Moon”, not from your ascendant. That convention is worth knowing, because a transit statement means different things depending on which anchor the speaker used, and many do not say.",
                        "hi": "भारतीय परंपरा गोचर प्रायः लग्न से नहीं, चंद्र-राशि से पढ़ती है — “आपके चंद्रमा से बारहवें शनि”, लग्न से नहीं। यह परिपाटी जान लेनी चाहिए, क्योंकि गोचर पर कही गई बात इस पर बदल जाती है कि कहने वाले ने कौन सा आधार लिया — और कई बताते ही नहीं।",
                    },
                ),
            ),
            Section(
                heading={"en": "The same sky for everybody", "hi": "सबके लिए एक ही आकाश"},
                body=(
                    {
                        "en": "Sade sati, from chapter 10, is a transit. So is every “Mercury retrograde” post you have seen — and since the transiting sky is the same for everyone alive, anything read from transits alone is by definition not about you specifically.",
                        "hi": "अध्याय 10 वाली साढ़ेसाती गोचर है। और वह हर “बुध वक्री” वाली पोस्ट भी जो आपने देखी है — और चूँकि गोचर का आकाश जीवित हर व्यक्ति के लिए एक ही है, अकेले गोचर से पढ़ी गई कोई बात परिभाषा से ही ख़ास आपके बारे में नहीं होती।",
                    },
                    {
                        "en": "What makes a transit reading personal at all is the second half: the transit is read against your chart, so Saturn in Kumbha means one thing for someone with a Kumbha Moon and another for someone with a Simha Moon. Drop that half and you have a horoscope column, which is a genre, not a reading.",
                        "hi": "गोचर की व्याख्या को निजी बनाने वाला दूसरा आधा हिस्सा है: गोचर आपकी कुंडली के सामने रखकर पढ़ा जाता है, इसलिए कुंभ में शनि का अर्थ कुंभ-चंद्र वाले के लिए कुछ और है और सिंह-चंद्र वाले के लिए कुछ और। वह आधा हिस्सा हटा दीजिए तो जो बचेगा वह अख़बार का राशिफल है — एक विधा, व्याख्या नहीं।",
                    },
                ),
            ),
            Section(
                heading={"en": "How the tempos stack", "hi": "लय कैसे एक पर एक चढ़ती हैं"},
                body=(
                    {
                        "en": "The slow bodies are what people mean by a transit worth naming. Saturn spends two and a half years per sign, Rahu and Ketu about eighteen months, Jupiter a year. Between them they define a background that changes on the scale of years.",
                        "hi": "नाम लेने लायक़ गोचर से लोगों का मतलब धीमे पिंडों से होता है। शनि हर राशि में ढाई वर्ष रहता है, राहु-केतु क़रीब डेढ़ वर्ष, गुरु एक वर्ष। मिलकर ये वर्षों के पैमाने पर बदलने वाली पृष्ठभूमि बनाते हैं।",
                    },
                    {
                        "en": "The fast ones — Sun, Mercury, Venus, Mars — change the picture monthly, and the Moon changes it every couple of days. Muhurta, the choosing of an auspicious time, works almost entirely at that fast end, which is why it needs the panchang and not the birth chart.",
                        "hi": "तेज़ पिंड — सूर्य, बुध, शुक्र, मंगल — तस्वीर हर महीने बदलते हैं, और चंद्रमा हर दो दिन में। मुहूर्त, यानी शुभ समय चुनना, लगभग पूरा उसी तेज़ सिरे पर चलता है — इसीलिए उसे जन्म कुंडली नहीं, पंचांग चाहिए।",
                    },
                ),
            ),
            Section(
                heading={"en": "What this app computes", "hi": "यह ऐप क्या गिनती है"},
                body=(
                    {
                        "en": "The Today screen gives you the live sky honestly and narrowly: the panchang for right now, the Moon's current rashi and nakshatra, the Sun's current rashi, and which of your dasha periods is running. It does not produce a daily prediction, and it never will.",
                        "hi": "आज वाली स्क्रीन जीवित आकाश ईमानदारी से और सीमित रूप में देती है: अभी का पंचांग, चंद्रमा की इस समय की राशि और नक्षत्र, सूर्य की इस समय की राशि, और आपकी कौन सी दशा चल रही है। वह रोज़ का कोई फल नहीं बनाती, और कभी नहीं बनाएगी।",
                    },
                    {
                        "en": "With those numbers you can do the transit reasoning yourself, which is the point. Compare the Moon's rashi today with your birth Moon's, or check where a slow graha is against the sign before and after your Moon. The measurements are free; what is sold on top of them usually is not.",
                        "hi": "उन्हीं संख्याओं से गोचर का तर्क आप ख़ुद कर सकते हैं, और असल बात यही है। आज की चंद्र-राशि अपनी जन्म चंद्र-राशि से मिलाइए, या देखिए कि कोई धीमा ग्रह आपकी चंद्र-राशि से पहले और बाद वाली राशियों के सामने कहाँ है। माप मुफ़्त हैं; उन पर जो बेचा जाता है वह प्रायः नहीं।",
                    },
                ),
                aside={
                    "en": "A transit statement with no birth chart in it is a statement about the calendar. That is the whole test.",
                    "hi": "जिस गोचर-कथन में जन्म कुंडली है ही नहीं, वह पंचांग के बारे में कथन है। पूरी जाँच इतनी ही है।",
                },
            ),
        ),
        personalise=P.dasha_now,
    ),
    Chapter(
        slug="panchang-five-limbs",
        part=PART_TIME,
        title={"en": "Panchang: the five limbs", "hi": "पंचांग: पाँच अंग"},
        summary={
            "en": "The part of this tradition people actually use every day.",
            "hi": "इस परंपरा का वह हिस्सा जिसे लोग सचमुच रोज़ इस्तेमाल करते हैं।",
        },
        minutes=6,
        level="intermediate",
        sections=(
            Section(
                heading={"en": "Tithi, vara, nakshatra, yoga, karana", "hi": "तिथि, वार, नक्षत्र, योग, करण"},
                body=(
                    {
                        "en": "Panchang means “five limbs”. A tithi is the time the Moon takes to gain 12 degrees on the Sun; thirty make a lunar month, split into shukla (brightening) and krishna (darkening) paksha.",
                        "hi": "पंचांग का अर्थ है “पाँच अंग”। तिथि वह समय है जिसमें चंद्रमा सूर्य से 12 अंश आगे बढ़ता है; तीस तिथियों का एक चांद्र मास बनता है, जो शुक्ल (बढ़ते) और कृष्ण (घटते) पक्ष में बँटा है।",
                    },
                    {
                        "en": "Vara is the weekday, each ruled by a graha — the same rulerships that named the days in most languages. Yoga is derived from Sun and Moon together, and karana is half a tithi. All five are arithmetic on two longitudes.",
                        "hi": "वार सप्ताह का दिन है, हर एक का स्वामी एक ग्रह — वही स्वामित्व जिनसे अधिकांश भाषाओं में दिनों के नाम बने। योग सूर्य और चंद्र को जोड़कर निकलता है, और करण आधी तिथि है। पाँचों दो देशांतरों पर लगा गणित हैं।",
                    },
                    {
                        "en": "That last sentence is worth reading twice. The entire daily calendar of a civilisation — fasts, festivals, wedding dates, the timing of ceremonies — is computed from the longitude of the Sun and the longitude of the Moon. Nothing else enters, except the sunrise at your place, which decides which day a given moment belongs to.",
                        "hi": "आख़िरी वाक्य दो बार पढ़ने लायक़ है। एक पूरी सभ्यता का रोज़ का पंचांग — व्रत, त्योहार, विवाह की तिथियाँ, संस्कारों का समय — सूर्य के देशांतर और चंद्रमा के देशांतर से निकलता है। और कुछ नहीं आता, सिवाय आपकी जगह के सूर्योदय के, जो तय करता है कि कोई क्षण किस दिन का है।",
                    },
                ),
            ),
            Section(
                heading={"en": "The tithi in detail", "hi": "तिथि, विस्तार से"},
                body=(
                    {
                        "en": "Take the Moon's longitude, subtract the Sun's, divide by 12, and the quotient names the tithi. At zero you have Amavasya, the new moon; at 180 degrees, exactly halfway, Purnima. The fifteen names — Pratipada, Dwitiya, Tritiya and on to Chaturdashi — repeat in both halves of the month.",
                        "hi": "चंद्रमा का देशांतर लीजिए, सूर्य का घटाइए, 12 से भाग दीजिए — भागफल तिथि बता देगा। शून्य पर अमावस्या; ठीक आधे रास्ते, 180 अंश पर, पूर्णिमा। पंद्रह नाम — प्रतिपदा, द्वितीया, तृतीया और आगे चतुर्दशी तक — मास के दोनों पक्षों में दोहराए जाते हैं।",
                    },
                    {
                        "en": "This app reports the tithi, its number within the paksha, which paksha it is, and how far through it you are as a percentage. That last figure is the one that makes the next section make sense.",
                        "hi": "यह ऐप तिथि बताती है, पक्ष में उसका क्रमांक, कौन सा पक्ष है, और आप उसमें कितने प्रतिशत आगे हैं। यही आख़िरी आँकड़ा अगले खंड को समझने लायक़ बनाता है।",
                    },
                ),
            ),
            Section(
                heading={"en": "Vara, yoga and karana", "hi": "वार, योग और करण"},
                body=(
                    {
                        "en": "The vara looks like the simplest limb and hides the subtlest rule: the Vedic day runs sunrise to sunrise, not midnight to midnight. A birth at two in the morning belongs to the previous vara, and this app computes it from the actual sunrise at your coordinates rather than from the calendar date.",
                        "hi": "वार सबसे सीधा अंग दिखता है और सबसे बारीक नियम छिपाए बैठा है: वैदिक दिन सूर्योदय से सूर्योदय तक चलता है, आधी रात से आधी रात तक नहीं। रात दो बजे का जन्म पिछले वार का होता है, और यह ऐप उसे तारीख़ से नहीं, आपके निर्देशांकों के असली सूर्योदय से गिनती है।",
                    },
                    {
                        "en": "The seven vara lords — Sun for Ravivara, Moon for Somavara, Mars for Mangalvara, and so on — are the same sequence that named Sunday, Monday and Tuesday in English and in most European languages. That is not a coincidence or a borrowing in either direction; it is a shared inheritance from Hellenistic planetary hours.",
                        "hi": "सात वार-स्वामी — रविवार का सूर्य, सोमवार का चंद्र, मंगलवार का मंगल, और आगे — वही क्रम हैं जिनसे अंग्रेज़ी और अधिकांश यूरोपीय भाषाओं में संडे, मंडे और ट्यूज़डे के नाम बने। यह न संयोग है न किसी एक तरफ़ से उधार; यह हेलेनिस्टिक ग्रह-होरा की साझा विरासत है।",
                    },
                    {
                        "en": "Yoga adds the two longitudes instead of subtracting them and divides by 13°20', giving 27 named yogas. Karana halves the tithi arc, giving 60 karanas in a month — fifty-six of them from a repeating cycle of seven, and four fixed ones around the new moon. Both are used mainly for choosing times rather than reading charts.",
                        "hi": "योग दोनों देशांतर घटाने के बजाय जोड़ता है और 13°20' से भाग देता है, जिससे 27 नामित योग बनते हैं। करण तिथि के चाप को आधा करता है, जिससे मास में 60 करण बनते हैं — उनमें छप्पन सात के दोहराते चक्र से, और चार अमावस्या के आसपास स्थिर। दोनों का उपयोग मुख्यतः कुंडली पढ़ने में नहीं, समय चुनने में होता है।",
                    },
                ),
            ),
            Section(
                heading={"en": "Why a tithi can skip a day", "hi": "तिथि एक दिन क्यों लाँघ जाती है"},
                body=(
                    {
                        "en": "The Moon's speed varies, so a tithi is not a fixed number of hours — it runs from about 19 to 26. That is why a tithi can cover two sunrises or none, and why festival dates sometimes shift by a day between panchangs.",
                        "hi": "चंद्रमा की गति बदलती रहती है, इसलिए तिथि घंटों की कोई निश्चित संख्या नहीं होती — वह क़रीब 19 से 26 घंटे तक चलती है। इसी से कोई तिथि दो सूर्योदय ढँक लेती है या एक भी नहीं, और इसी से दो पंचांगों में त्योहार की तारीख़ कभी-कभी एक दिन खिसक जाती है।",
                    },
                    {
                        "en": "A tithi that spans two sunrises is called adhika and effectively repeats; one that fits entirely between two sunrises is kshaya and is skipped. Neither is an omen. Both are consequences of an elliptical orbit meeting a rule that assigns one tithi to each day.",
                        "hi": "जो तिथि दो सूर्योदय पर फैल जाए उसे अधिक तिथि कहते हैं और वह प्रभावतः दोहराई जाती है; जो दो सूर्योदयों के बीच पूरी समा जाए वह क्षय तिथि है और छोड़ दी जाती है। इनमें कोई शकुन नहीं। दोनों उस दीर्घवृत्ताकार कक्षा का नतीजा हैं जो “हर दिन एक तिथि” वाले नियम से टकराती है।",
                    },
                ),
            ),
            Section(
                heading={"en": "Why two panchangs disagree", "hi": "दो पंचांग क्यों नहीं मिलते"},
                body=(
                    {
                        "en": "Four ordinary reasons, none of them scandalous. Different ayanamsa. Different sunrise definition — upper limb or centre of the Sun, with or without refraction. Different rules for which sunrise a festival attaches to. And different places: a tithi begins at the same instant everywhere, but that instant falls on different sides of sunrise in Chennai and in Delhi.",
                        "hi": "चार सामान्य कारण, और इनमें कोई अनोखा नहीं। अलग अयनांश। सूर्योदय की अलग परिभाषा — सूर्य का ऊपरी किनारा या केंद्र, वायुमंडलीय अपवर्तन के साथ या बिना। त्योहार किस सूर्योदय से जुड़ेगा, इसके अलग नियम। और अलग स्थान: तिथि हर जगह एक ही क्षण शुरू होती है, पर वह क्षण चेन्नई और दिल्ली में सूर्योदय के अलग-अलग ओर पड़ता है।",
                    },
                    {
                        "en": "So when your family panchang and an app differ by a day, the useful question is which of those four they differ on — not which is authentic. This app computes the five limbs from the same longitudes it draws your chart from, and reports the moment, the place and the ayanamsa it used.",
                        "hi": "इसलिए घर के पंचांग और किसी ऐप में एक दिन का फ़र्क़ हो, तो काम का सवाल यह है कि वे इन चार में से किस पर अलग हैं — यह नहीं कि असली कौन है। यह ऐप पाँचों अंग उन्हीं देशांतरों से गिनती है जिनसे आपकी कुंडली बनाती है, और जो क्षण, स्थान और अयनांश उसने लिया वह बता देती है।",
                    },
                ),
                aside={
                    "en": "For religious observance, follow your family's or temple's panchang. This one is computed honestly, but a shared calendar is a social fact, not only an astronomical one.",
                    "hi": "धार्मिक अनुष्ठान के लिए अपने घर या मंदिर का पंचांग मानिए। यह वाला ईमानदारी से गिना गया है, पर साझा पंचांग केवल खगोलीय तथ्य नहीं, सामाजिक तथ्य भी है।",
                },
            ),
        ),
        personalise=P.birth_panchang,
    ),
)
