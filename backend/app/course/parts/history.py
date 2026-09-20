"""Part nine: the history of the astronomy.

How the mathematics grew.
"""

from __future__ import annotations

from ..models import Chapter, Section
from . import PART_HISTORY

CHAPTERS: tuple[Chapter, ...] = (
    Chapter(
        slug="history-calendars",
        part=PART_HISTORY,
        title={"en": "Time measurement and calendars", "hi": "समय का मापन और पंचांग"},
        summary={
            "en": "Before clocks, the sky was the only instrument. The logic of Luni-Solar calendars.",
            "hi": "जब घड़ियाँ नहीं थीं, तब आसमान ही इकलौता यंत्र था। चंद्र-सौर (Luni-Solar) पंचांग का असली तर्क।",
        },
        minutes=6,
        level="basic",
        sections=(
            Section(
                heading={"en": "The sky as a clock", "hi": "आसमान एक घड़ी के रूप में"},
                body=(
                    {
                        "en": "Ancient Indian astronomy began out of necessity. Before mechanical clocks existed, the sky provided the only reliable measure of time. The earliest astronomical texts, like the Vedanga Jyotisha (dating back to the late BCE era), were essentially manuals for keeping time to schedule seasonal agricultural activities and rituals.",
                        "hi": "प्राचीन भारतीय खगोल विज्ञान की शुरुआत एक गहरी ज़रूरत से हुई थी। जब मशीनी घड़ियाँ नहीं बनी थीं, तब समय नापने का एकमात्र भरोसेमंद ज़रिया आसमान ही था। 'वेदांग ज्योतिष' जैसे सबसे पुराने खगोलीय ग्रंथ असल में समय को बाँधने के तरीके थे, ताकि खेती-बाड़ी और मौसम के हिसाब से अनुष्ठानों का सही समय तय किया जा सके।"
                    },
                    {
                        "en": "Two natural rhythms dominate the sky: the Sun crossing the horizon (setting the day and the year) and the Moon cycling through its phases (setting the month). A solar year tracks the seasons perfectly, while a lunar month tracks the phases perfectly. The challenge of early astronomy was that these two do not divide evenly into one another.",
                        "hi": "आसमान में मुख्य तौर पर दो ही प्राकृतिक चक्र चलते हैं: पहला, सूर्य का उगना और डूबना (जो दिन और साल तय करता है) और दूसरा, चंद्रमा का घटना-बढ़ना (जिससे महीना तय होता है)। एक सौर वर्ष (Solar year) मौसम के साथ बिल्कुल सटीक बैठता है, जबकि चंद्र मास (Lunar month) चाँद की कलाओं के साथ। शुरुआती खगोल विज्ञान की सबसे बड़ी चुनौती यही थी कि ये दोनों चक्र आपस में कभी बराबर नहीं बैठते।"
                    }
                ),
            ),
            Section(
                heading={"en": "The Luni-Solar reconciliation", "hi": "सूर्य और चंद्रमा का तालमेल"},
                body=(
                    {
                        "en": "A lunar year of 12 full cycles is about 354 days long, falling 11 days short of the solar year. Without correction, the months would drift backward through the seasons, meaning a summer month would eventually arrive in winter.",
                        "hi": "12 महीनों का एक चंद्र वर्ष करीब 354 दिनों का होता है, जो सूर्य के साल से लगभग 11 दिन छोटा पड़ जाता है। अगर इसे सुधारा न जाए, तो महीने मौसम के हिसाब से पीछे खिसकने लगेंगे, और एक वक्त ऐसा आएगा जब गर्मियों का महीना कड़ाके की ठंड में पड़ने लगेगा।"
                    },
                    {
                        "en": "To reconcile them, ancient Indian astronomers developed a highly sophisticated Luni-Solar system. They tracked both orbits with mathematical precision and instituted an 'Adhik Maas' (leap month) roughly every three years. This intercalation acts as a mathematical gear, locking the lunar phases back into the solar seasons.",
                        "hi": "इस समस्या को सुलझाने के लिए प्राचीन भारतीय खगोलविदों ने एक बेहद शानदार 'चंद्र-सौर' (Luni-Solar) प्रणाली विकसित की। उन्होंने गणितीय सटीकता के साथ दोनों की चाल नापी और लगभग हर तीन साल में एक 'अधिक मास' (Leap month) जोड़ने का नियम बनाया। यह अतिरिक्त महीना एक गणितीय गियर (Gear) की तरह काम करता है, जो चंद्रमा की चाल को वापस मौसम (सूर्य) के साथ जोड़ देता है।"
                    },
                    {
                        "en": "Here is a mathematical representation of how the adjustment works over a 19-year cycle:\n\n[ Luni-Solar Cycle: 19 Solar Years ≈ 235 Lunar Months ]\n( 19 × 365.24 days = 6939.6 days )\n( 235 × 29.53 days = 6939.5 days )",
                        "hi": "यह समायोजन (Adjustment) 19 साल के चक्र में कैसे काम करता है, उसका गणित यहाँ देखा जा सकता है:\n\n[ चंद्र-सौर चक्र: 19 सौर वर्ष ≈ 235 चंद्र मास ]\n( 19 × 365.24 दिन = 6939.6 दिन )\n( 235 × 29.53 दिन = 6939.5 दिन )"
                    }
                ),
                aside={
                    "en": "This is why Indian festivals like Diwali shift their calendar dates every year but always occur in the same season. The math forces the alignment.",
                    "hi": "यही कारण है कि दिवाली जैसे भारतीय त्योहार हर साल तारीख तो बदलते हैं, लेकिन मौसम हमेशा वही रहता है। यह गणित ही उन्हें अपनी जगह पर बाँध कर रखता है।"
                }
            )
        ),
    ),
    Chapter(
        slug="history-siddhantas",
        part=PART_HISTORY,
        title={"en": "The era of the Siddhantas", "hi": "सिद्धांतों का युग"},
        summary={
            "en": "Varahamihira, Brahmagupta, interpolation, and the rules of zero.",
            "hi": "वराहमिहिर, ब्रह्मगुप्त, गणितीय अंतर्वेशन (Interpolation), और शून्य के नियम।",
        },
        minutes=7,
        level="intermediate",
        sections=(
            Section(
                heading={"en": "Varahamihira (6th Century)", "hi": "वराहमिहिर (छठी शताब्दी)"},
                body=(
                    {
                        "en": "Following Aryabhata, the next monumental figure was Varahamihira. His greatest contribution to the history of science was the Pancha-Siddhantika (The Treatise of the Five Astronomical Canons), compiled around 575 CE.",
                        "hi": "आर्यभट्ट के बाद खगोल विज्ञान में अगला बड़ा नाम वराहमिहिर का आता है। विज्ञान के इतिहास में उनका सबसे बड़ा योगदान 'पंचसिद्धान्तिका' है, जिसे उन्होंने लगभग 575 ईस्वी में संकलित किया था।"
                    },
                    {
                        "en": "This work summarized five major schools of astronomical thought that existed before him: the Surya, Romaka, Paulisa, Vasishtha, and Paitamaha Siddhantas. It is a vital historical text because it preserves the exchange of ideas in the ancient world.",
                        "hi": "इस महान ग्रंथ में उनसे पहले मौजूद पाँच प्रमुख खगोलीय विचारधाराओं का सार प्रस्तुत किया गया था: सूर्य, रोमक, पॉलिश, वशिष्ठ और पैतामह सिद्धांत। यह ऐतिहासिक रूप से एक बेहद अहम दस्तावेज़ है क्योंकि इसने प्राचीन विश्व में विचारों के आदान-प्रदान को सहेज कर रखा है।"
                    },
                    {
                        "en": "The Romaka and Paulisa Siddhantas directly incorporated Greek and Roman astronomical concepts, showing that early Indian astronomers actively studied foreign mathematics, integrated it with their own, and improved upon it.",
                        "hi": "'रोमक' और 'पॉलिश' सिद्धांतों में यूनानी (Greek) और रोमन खगोलीय ज्ञान को सीधे तौर पर शामिल किया गया था। इससे यह साबित होता है कि शुरुआती भारतीय खगोलविदों ने दूसरे देशों के गणित का भी खूब अध्ययन किया, उसे अपने ज्ञान के साथ जोड़ा और उसे और भी बेहतर बनाया।"
                    }
                ),
            ),
            Section(
                heading={"en": "Brahmagupta (7th Century)", "hi": "ब्रह्मगुप्त (7वीं शताब्दी)"},
                body=(
                    {
                        "en": "Working at the astronomical observatory in Ujjain, Brahmagupta authored the Brahmasphuta Siddhanta (Correctly Established Doctrine of Brahma) in 628 CE. This text pushed the boundaries of both arithmetic and astronomy.",
                        "hi": "उज्जैन की वेधशाला (Observatory) में काम करते हुए, ब्रह्मगुप्त ने 628 ईस्वी में 'ब्राह्मस्फुटसिद्धान्त' की रचना की। इस ग्रंथ ने न सिर्फ खगोल विज्ञान, बल्कि अंकगणित की सीमाओं को भी नई ऊंचाइयों तक पहुँचा दिया।"
                    },
                    {
                        "en": "His most famous mathematical achievement was formalizing the rules for computing with Zero. Before him, zero was merely a placeholder. Brahmagupta defined zero as the result of subtracting a number from itself, and wrote down the rules for adding, subtracting, and multiplying with zero and negative numbers.",
                        "hi": "गणित की दुनिया में उनकी सबसे बड़ी उपलब्धि 'शून्य' (Zero) के साथ गणना करने के नियम बनाना था। उनसे पहले शून्य सिर्फ जगह भरने (Placeholder) के काम आता था। ब्रह्मगुप्त ने बताया कि जब किसी संख्या को उसी में से घटाया जाए, तो शून्य मिलता है। उन्होंने शून्य और ऋणात्मक (Negative) संख्याओं को जोड़ने, घटाने और गुणा करने के पक्के नियम लिखे।"
                    },
                    {
                        "en": "In astronomy, estimating the exact position of planets required dealing with complex, non-linear speeds. Brahmagupta developed an advanced second-order interpolation formula to compute sines, allowing astronomers to calculate planetary positions with unprecedented precision.",
                        "hi": "खगोल विज्ञान में, ग्रहों की सटीक जगह का पता लगाने के लिए उनकी उलझी हुई और बदलती (Non-linear) गतियों को समझना ज़रूरी था। ब्रह्मगुप्त ने 'ज्या' (Sines) निकालने के लिए एक बेहद उन्नत 'सेकेंड-ऑर्डर इंटरपोलेशन' (Second-order interpolation) सूत्र बनाया, जिससे खगोलविद ग्रहों की स्थिति की अभूतपूर्व सटीकता से गणना कर सके।"
                    }
                ),
                aside={
                    "en": "Brahmagupta also made early observations resembling gravity, noting that it is the nature of the Earth to attract objects, just as it is the nature of water to flow.",
                    "hi": "ब्रह्मगुप्त ने गुरुत्वाकर्षण (Gravity) जैसी शुरुआती धारणाओं का भी ज़िक्र किया था। उनका मानना था कि जैसे बहना पानी का स्वभाव है, वैसे ही वस्तुओं को अपनी ओर खींचना पृथ्वी का स्वभाव है।"
                }
            )
        ),
    ),
    Chapter(
        slug="history-bhaskara",
        part=PART_HISTORY,
        title={"en": "Bhaskara II and mathematical mechanics", "hi": "भास्कराचार्य द्वितीय और गणितीय यांत्रिकी"},
        summary={
            "en": "The zenith of the Siddhanta school, early calculus, and spherical astronomy.",
            "hi": "सिद्धांत संप्रदाय का चरम, कैलकुलस की शुरुआत, और गोलीय खगोल विज्ञान।",
        },
        minutes=7,
        level="intermediate",
        sections=(
            Section(
                heading={"en": "The Siddhanta Shiromani (12th Century)", "hi": "सिद्धांत शिरोमणि (12वीं शताब्दी)"},
                body=(
                    {
                        "en": "Bhaskara II (also known as Bhaskaracharya) lived centuries later and is considered the zenith of the classical Siddhanta school. His magnum opus, the Siddhanta Shiromani (Head Jewel of Accuracy), was written in 1150 CE.",
                        "hi": "भास्कराचार्य द्वितीय (Bhaskara II) सदियों बाद हुए, और उन्हें शास्त्रीय सिद्धांत परंपरा का शिखर माना जाता है। उनकी सबसे महान रचना 'सिद्धांत शिरोमणि' 1150 ईस्वी में लिखी गई थी।"
                    },
                    {
                        "en": "The work is a massive, comprehensive treatise divided into four parts: Lilavati (arithmetic), Bijaganita (algebra), Grahaganita (mathematics of the planets), and Goladhyaya (spheres and the celestial globe).",
                        "hi": "यह ग्रंथ कोई छोटी-मोटी किताब नहीं, बल्कि एक विशाल और संपूर्ण महाग्रंथ है जो चार भागों में बंटा है: लीलावती (अंकगणित), बीजगणित, ग्रहगणित (ग्रहों का गणित), और गोलाध्याय (गोलीय खगोल विज्ञान)।"
                    }
                ),
            ),
            Section(
                heading={"en": "The roots of Calculus", "hi": "कैलकुलस (Calculus) की जड़ें"},
                body=(
                    {
                        "en": "Planets do not move at constant speeds; their speed changes every single day due to their elliptical orbits. To predict their exact positions, one must calculate their instantaneous speed at a specific moment.",
                        "hi": "ग्रह कभी भी एक जैसी गति से नहीं चलते; उनकी कक्षाएँ (Orbits) अण्डाकार होने के कारण उनकी चाल हर दिन बदलती रहती है। अगर आप उनकी सटीक स्थिति जानना चाहते हैं, तो आपको किसी एक खास पल में उनकी 'तात्कालिक गति' (Instantaneous speed) निकालनी होगी।"
                    },
                    {
                        "en": "In tackling this problem, Bhaskara II conceived early concepts of differential calculus. He understood that the differential coefficient vanishes at a function's extremum (its peak or trough), a principle that predated modern calculus by hundreds of years. This allowed him to precisely map the 'tatkalikagati' (instantaneous motion) of planets.",
                        "hi": "इस जटिल समस्या को सुलझाते हुए, भास्कराचार्य ने आधुनिक 'अवकलन कलन' (Differential calculus) की शुरुआती नींव रख दी थी। उन्होंने यह समझ लिया था कि किसी भी फलन (Function) के सबसे ऊंचे या निचले बिंदु (Extremum) पर उसका अवकल गुणांक (Differential coefficient) शून्य हो जाता है। यह सिद्धांत यूरोप में कैलकुलस आने से सैकड़ों साल पुराना है, और इसी के ज़रिए उन्होंने ग्रहों की 'तात्कालिक गति' को एकदम सटीकता से नापा था।"
                    },
                    {
                        "en": "By pushing the algebraic tools inherited from Brahmagupta to their absolute limits, Bhaskara II built the mathematical engine that powered Indian astronomy for the next several centuries.",
                        "hi": "ब्रह्मगुप्त से विरासत में मिले बीजगणित (Algebra) के औजारों को उनकी चरम सीमा तक ले जाकर, भास्कराचार्य ने एक ऐसा गणितीय इंजन तैयार किया जिसने आने वाली कई सदियों तक भारतीय खगोल विज्ञान को गति दी।"
                    }
                ),
            )
        ),
    ),
    Chapter(
        slug="history-kerala-school",
        part=PART_HISTORY,
        title={"en": "The Kerala School and infinite series", "hi": "केरल विद्यापीठ और अनंत श्रेणियाँ"},
        summary={
            "en": "Madhava, infinite expansions, Parameshvara, and the tradition of observation.",
            "hi": "माधव, अनंत विस्तार (Infinite expansions), परमेश्वर, और आसमान को देखने की परंपरा।",
        },
        minutes=8,
        level="intermediate",
        sections=(
            Section(
                heading={"en": "Madhava of Sangamagrama (14th Century)", "hi": "संगमग्राम के माधव (14वीं शताब्दी)"},
                body=(
                    {
                        "en": "The story of Indian astronomy did not stop in the north. Between the 14th and 16th centuries, the Kerala School of Astronomy and Mathematics flourished in South India, founded by the brilliant mathematician Madhava of Sangamagrama.",
                        "hi": "भारतीय खगोल विज्ञान की कहानी सिर्फ उत्तर भारत में ही खत्म नहीं हुई। 14वीं से 16वीं शताब्दी के बीच, दक्षिण भारत में खगोल विज्ञान और गणित का 'केरल विद्यापीठ' फला-फूला। इसकी स्थापना संगमग्राम के बेहद मेधावी गणितज्ञ माधव ने की थी।"
                    },
                    {
                        "en": "To compute the positions of planets, astronomers needed highly accurate tables of sine and cosine values. Madhava made a massive breakthrough: he moved beyond finite algebra and discovered infinite series expansions for trigonometric functions.",
                        "hi": "ग्रहों की स्थिति निकालने के लिए खगोलविदों को 'साइन' (Sine) और 'कोसाइन' (Cosine) की बेहद सटीक तालिकाओं की ज़रूरत पड़ती थी। माधव ने यहाँ एक बहुत बड़ी सफलता हासिल की: वह सीमित बीजगणित की दीवारों को लांघ गए और त्रिकोणमिति (Trigonometry) के लिए 'अनंत श्रेणी विस्तार' (Infinite series expansions) की खोज कर डाली।"
                    },
                    {
                        "en": "Madhava's Sine Series Expansion:\n\n  sin(x) = x - (x³/3!) + (x⁵/5!) - (x⁷/7!) + ...",
                        "hi": "माधव का ज्या (Sine) श्रेणी विस्तार:\n\n  sin(x) = x - (x³/3!) + (x⁵/5!) - (x⁷/7!) + ..."
                    },
                    {
                        "en": "He also developed infinite series for calculating Pi (π) to extraordinary precision. These discoveries foreshadowed the development of calculus in Europe (like the Taylor and Maclaurin series) by over two centuries.",
                        "hi": "उन्होंने पाई (π) का मान निकालने के लिए भी अनंत श्रेणियां बनाईं, जो अकल्पनीय रूप से सटीक थीं। उनकी इन खोजों ने यूरोप में 'टेलर' और 'मैक्लॉरिन' सीरीज़ के रूप में कैलकुलस विकसित होने से दो सदी पहले ही उसकी नींव रख दी थी।"
                    }
                ),
            ),
            Section(
                heading={"en": "Continuous observation: Parameshvara and Nilakantha", "hi": "लगातार प्रेक्षण: परमेश्वर और नीलकंठ"},
                body=(
                    {
                        "en": "The Kerala School did not just do abstract math; they were committed empirical scientists. Parameshvara (c. 1380–1460), a disciple in Madhava's lineage, conducted continuous naked-eye observations of eclipses and planetary positions for over 55 years.",
                        "hi": "केरल विद्यापीठ के लोग सिर्फ किताबों में उलझे रहने वाले गणितज्ञ नहीं थे; वे पक्के प्रायोगिक वैज्ञानिक (Empirical scientists) थे। माधव की ही परंपरा के एक शिष्य 'परमेश्वर' (लगभग 1380-1460 ईस्वी) ने पूरे 55 सालों तक नंगी आँखों से लगातार आसमान, ग्रहणों और ग्रहों की चाल का अध्ययन किया।"
                    },
                    {
                        "en": "When Parameshvara noticed that the classical formulas (from Aryabhata and others) began to diverge slightly from the actual observed sky, he did not ignore the sky. He corrected the math. He proposed a revised computational system known as Drgganita (Drigganita), which literally translates to 'computation based on observation'.",
                        "hi": "जब परमेश्वर ने देखा कि आर्यभट्ट और अन्य विद्वानों के पुराने सूत्र अब वास्तविक आसमान की चाल से थोड़ा-बहुत भटकने लगे हैं, तो उन्होंने आसमान को अनदेखा नहीं किया। इसके बजाय, उन्होंने अपने गणित को सुधारा। उन्होंने एक नई गणना प्रणाली का प्रस्ताव रखा जिसे 'दृग्गणित' कहा गया, जिसका सीधा सा मतलब है 'आँखों देखे प्रेक्षण (Observation) पर आधारित गणित'।"
                    },
                    {
                        "en": "Later, Nilakantha Somayaji (1444–1544) synthesized these findings in his Tantrasangraha, proposing highly sophisticated planetary models that remarkably mirrored geo-heliocentric structures.",
                        "hi": "बाद में, नीलकंठ सोमयाजी (1444-1544) ने इन सभी खोजों को अपने ग्रंथ 'तंत्रसंग्रह' में पिरोया। उन्होंने ग्रहों के ऐसे बेहद उन्नत मॉडल पेश किए जो आश्चर्यजनक रूप से आज के 'जियो-हीलियोसेंट्रिक' (Geo-heliocentric) ब्रह्मांड के काफी करीब थे।"
                    }
                ),
                aside={
                    "en": "The history of Indian astronomy proves that this tradition was never meant to be frozen in ancient texts. It was built on continuous measurement, mathematical innovation, and the willingness to correct old rules when they no longer matched the real sky.",
                    "hi": "भारतीय खगोल विज्ञान का यह इतिहास साबित करता है कि यह परंपरा कभी भी पुरानी किताबों में कैद होकर रह जाने के लिए नहीं बनी थी। इसकी बुनियाद लगातार आसमान नापने, गणित में नए प्रयोग करने, और जब पुराने नियम आसमान की असलियत से मेल न खाएँ, तो उन्हें बेझिझक सुधारने की हिम्मत पर टिकी थी।"
                }
            )
        ),
    ),
)
