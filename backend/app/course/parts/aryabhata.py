"""Part eight: The Aryabhatiya.

An exhaustive, encyclopedic deep dive into the 121 verses that changed Indian astronomy forever.
"""

from __future__ import annotations

from ..models import Chapter, Section
from . import PART_ARYABHATA

CHAPTERS: tuple[Chapter, ...] = (
    Chapter(
        slug="aryabhatiya-introduction-gitikapada",
        part=PART_ARYABHATA,
        title={"en": "Gitikapada: The Language of the Cosmos", "hi": "गीतिकापाद: ब्रह्मांड की भाषा"},
        summary={
            "en": "The invocation, the brilliant alphabetic numeral system, and the revolutionary Sine (Jya) table.",
            "hi": "मंगलाचरण, संख्याओं को लिखने की एक शानदार कूट-प्रणाली (Cryptography), और गणित की दुनिया बदलने वाली ज्या (Sine) तालिका।",
        },
        minutes=15,
        level="intermediate",
        sections=(
            Section(
                heading={"en": "The Illusion of Brevity", "hi": "छोटा होने का भ्रम"},
                body=(
                    {
                        "en": "The Aryabhatiya contains only 121 verses (Sutras), making it seem deceptively short. However, in the Indian tradition of 'Sutra' literature, knowledge was compressed into the absolute minimum number of syllables required, acting as memory aids (mnemonics) for scholars.",
                        "hi": "आर्यभटीय में कुल मिलाकर सिर्फ 121 श्लोक हैं, जिन्हें देखकर लगता है कि यह कोई बहुत छोटी सी किताब होगी। लेकिन भारत में 'सूत्र' साहित्य की यह परंपरा रही है कि अथाह ज्ञान को कम से कम अक्षरों में पिरो दिया जाता था, ताकि विद्वान उसे आसानी से याद (Memorize) रख सकें।"
                    },
                    {
                        "en": "Because of this extreme compression, the mathematics encoded within these 121 verses is so profound that subsequent astronomers, such as Bhaskara I (in his Aryabhatiya Bhasya) and Nilakantha Somayaji (in his Aryabhatiya Bhasya), had to write commentaries spanning thousands of pages to unpack the derivations, proofs, and working algorithms hidden inside.",
                        "hi": "चीजों को इतने छोटे रूप में समेटने की वजह से, इन 121 श्लोकों में छिपा गणित इतना गहरा हो गया कि बाद के खगोलविदों—जैसे भास्कर प्रथम और नीलकंठ सोमयाजी—को इसे डिकोड करने के लिए हज़ारों पन्नों के भाष्य (Commentaries) लिखने पड़े। तब जाकर दुनिया को समझ आया कि इन श्लोकों के भीतर कितने जटिल एल्गोरिदम और गणितीय प्रमाण (Proofs) छिपे थे।"
                    }
                ),
            ),
            Section(
                heading={"en": "The Alphabetic Numeral System (Katapayadi precursor)", "hi": "वर्णानुक्रमिक संख्या प्रणाली (अक्षरों में छिपा गणित)"},
                body=(
                    {
                        "en": "To fit massive astronomical numbers—like the number of times the moon revolves around the earth in 4.32 million years—into a poetic meter, Aryabhata invented a brilliant cryptographic number system.",
                        "hi": "अब चुनौती यह थी कि कविता के छोटे-छोटे छंदों में खगोल विज्ञान की उन विशाल संख्याओं (जैसे 43 लाख सालों में चाँद कितनी बार घूमेगा) को कैसे फिट किया जाए? इसका हल निकालने के लिए आर्यभट्ट ने संख्याओं को लिखने की एक शानदार कूट-प्रणाली (Cryptographic system) ईजाद की।"
                    },
                    {
                        "en": "Verse 2 explains the rule: Consonants represent numbers. The 'varga' (classified) consonants from 'ka' to 'ma' represent 1 to 25. The 'avarga' (unclassified) consonants like 'ya', 'ra', 'la', 'va' represent 30, 40, 50, 60, etc. Vowels act as multipliers (powers of 100). 'a' = 1, 'i' = 100, 'u' = 10,000, and so on.",
                        "hi": "श्लोक 2 में इसका नियम समझाया गया है: सभी व्यंजन (Consonants) किसी न किसी संख्या को दर्शाते हैं। 'क' से लेकर 'म' तक के 25 अक्षर 1 से 25 तक की संख्या बनते हैं। उसके आगे 'य', 'र', 'ल', 'व' जैसे अक्षर 30, 40, 50, 60 का काम करते हैं। वहीं जो स्वर (Vowels) हैं, वे 100 की घात (Powers of 100) के रूप में गुणा करने का काम करते हैं—जैसे 'अ' मतलब 1, 'इ' मतलब 100, 'उ' मतलब 10,000।"
                    },
                    {
                        "en": "Example Calculation: The word 'khyughṛ' (ख्युघृ) represents the number of revolutions of the Sun in a Mahayuga (4,320,000). \nHere is the exact mathematical decoding:\n1. 'kh' (ख) = 2. Attached to 'u' (10,000) = 20,000.\n2. 'y' (य) = 30. Attached to 'u' (10,000) = 300,000.\n3. 'gh' (घ) = 4. Attached to 'ṛ' (1,000,000) = 4,000,000.\nTotal = 4,000,000 + 300,000 + 20,000 = 4,320,000. \nThus, millions of years of celestial mechanics were compressed into two syllables.",
                        "hi": "ज़रा इस उदाहरण से समझिए: 'ख्युघृ' शब्द का मतलब है एक महायुग (43,20,000 साल) में सूर्य कितनी बार परिक्रमा करेगा। \nइसकी डिकोडिंग कुछ इस तरह होती है:\n1. 'ख' (यानी 2) के साथ 'उ' (10,000) लगा है = 20,000।\n2. 'य' (यानी 30) के साथ भी 'उ' (10,000) है = 3,00,000।\n3. 'घ' (यानी 4) के साथ 'ऋ' (10,00,000) लगा है = 40,00,000।\nकुल योग = 40,00,000 + 3,00,000 + 20,000 = 43,20,000। \nइस तरह, आसमान की चाल के लाखों-करोड़ों के आँकड़े सिर्फ दो अक्षरों के शब्द में सिमट गए।"
                    }
                ),
            ),
            Section(
                heading={"en": "The First Table of Sines (Jya)", "hi": "ज्या (Sine) की पहली तालिका"},
                body=(
                    {
                        "en": "Verse 12 contains the famous 'Jya' table. Aryabhata computed the sine of angles from 0 to 90 degrees at intervals of 3.75 degrees (225 minutes of arc).",
                        "hi": "श्लोक 12 में दुनिया की सबसे मशहूर 'ज्या' (Sine) की टेबल दी गई है। आर्यभट्ट ने 0 से 90 डिग्री के बीच के सभी कोणों (Angles) का मान 3.75 डिग्री के अंतराल पर नाप कर लिख दिया।"
                    },
                    {
                        "en": "He didn't just give the values; he gave the second-order difference equation used to generate them: \n\nR sin(n+1)A - R sin(n)A = [R sin(n)A - R sin(n-1)A] - [R sin(n)A / R sin(A)]\n\nThis recursive formula is mathematically equivalent to the modern differential equation d²(sin θ)/dθ² = -sin θ. It is the absolute bedrock of all trigonometric astronomy.",
                        "hi": "कमाल की बात यह है कि उन्होंने सिर्फ इन कोणों का मान ही नहीं बताया, बल्कि इन्हें निकालने का सूत्र (Second-order difference equation) भी दे दिया: \n\nR sin(n+1)A - R sin(n)A = [R sin(n)A - R sin(n-1)A] - [R sin(n)A / 225]\n\nयह सूत्र गणित की दुनिया में आज के मॉडर्न अवकल समीकरण (Differential equation) d²(sin θ)/dθ² = -sin θ के बिल्कुल बराबर है। आज के खगोल विज्ञान की पूरी त्रिकोणमिति इसी बुनियाद पर टिकी है।"
                    }
                ),
                aside={
                    "en": "When Arab scholars translated Jya, they wrote it as 'jiba'. Later Latin translators misread it as 'jaib' (meaning 'bay' or 'fold') and translated it to Latin as 'sinus', which is why we call it 'Sine' today. It all started with this verse.",
                    "hi": "रोचक बात यह है कि जब अरब के विद्वानों ने 'ज्या' का अनुवाद किया, तो उन्होंने इसे 'जीवा' लिखा। बाद में जब इसे लैटिन में अनुवाद किया गया, तो अनुवादक इसे गलती से 'जैब' (जिसका मतलब खाड़ी या मोड़ होता है) पढ़ गए और इसका लैटिन नाम 'sinus' (साइनस) रख दिया। आज जिसे पूरी दुनिया 'Sine' के नाम से जानती है, उसकी शुरुआत इसी एक श्लोक से हुई थी।"
                }
            )
        ),
    ),
    Chapter(
        slug="aryabhatiya-ganitapada-deep",
        part=PART_ARYABHATA,
        title={"en": "Ganitapada: The Arsenal of Mathematics", "hi": "गणितपाद: गणित का शस्त्रागार"},
        summary={
            "en": "The exact Sanskrit definition of Pi, geometric progressions, and a deep dive into the Kuttaka algorithm.",
            "hi": "पाई (π) की एकदम सटीक संस्कृत परिभाषा, ज्योमेट्रिक प्रोग्रेशन, और 'कुट्टक' एल्गोरिथ्म की पूरी पड़ताल।",
        },
        minutes=15,
        level="intermediate",
        sections=(
            Section(
                heading={"en": "The Irrationality of Pi (π)", "hi": "पाई (π) का सटीक मान और उसका रहस्य"},
                body=(
                    {
                        "en": "In verse 10, Aryabhata gives an incredibly accurate approximation for Pi (π), explicitly noting it as an approximation (āsanna).",
                        "hi": "श्लोक 10 में आर्यभट्ट पाई (π) का इतना सटीक मान बताते हैं कि आज भी हैरानी होती है। और सबसे बड़ी बात यह है कि वे खुद स्पष्ट रूप से कहते हैं कि यह मान केवल 'लगभग' (Approximation / आसन्न) है।"
                    },
                    {
                        "en": "The original Sanskrit verse:\n\"caturadhikam śatamaṣṭaguṇam dvāṣaṣṭistathā sahasrāṇām / \nayutadvayaviṣkambhasyāsanno vṛttapariṇāmaḥ\" \n\nLiteral Translation: \"Add four to 100, multiply by eight, and then add 62,000. By this rule the circumference of a circle with a diameter of 20,000 can be approached.\"",
                        "hi": "उनका मूल संस्कृत श्लोक कुछ इस तरह है:\n\"चतुरधिकं शतमष्टगुणं द्वाषष्टिस्तथा सहस्राणाम्।\nअयुतद्वयविष्कम्भस्यासन्नो वृत्तपरिणाहः॥\"\n\nइसका सीधा सा मतलब है: \"100 में 4 जोड़ें, 8 से गुणा करें, और फिर 62,000 जोड़ दें। इस नियम से 20,000 के व्यास (Diameter) वाले एक गोले की परिधि (Circumference) निकाली जा सकती है।\""
                    },
                    {
                        "en": "Mathematical derivation:\nCircumference = [(100 + 4) × 8] + 62,000 = 832 + 62,000 = 62,832.\nDiameter = 20,000.\nπ = Circumference / Diameter = 62,832 / 20,000 = 3.1416.\nThis was the most accurate value of Pi known in the ancient world, accurate to four decimal places.",
                        "hi": "अगर इसका गणितीय हिसाब लगाएं:\nपरिधि (Circumference) = [(100 + 4) × 8] + 62,000 = 832 + 62,000 = 62,832।\nव्यास (Diameter) = 20,000।\nπ = परिधि / व्यास = 62,832 / 20,000 = 3.1416।\nदशमलव के चार स्थानों तक एकदम सही उतरने वाला यह पाई (π) का दुनिया का सबसे सटीक मान था।"
                    }
                ),
            ),
            Section(
                heading={"en": "The Kuttaka (Pulverizer) Algorithm", "hi": "कुट्टक (Pulverizer) एल्गोरिथ्म"},
                body=(
                    {
                        "en": "Verses 32 and 33 present the 'Kuttaka' algorithm. In astronomy, finding when two planets will align perfectly (a conjunction) requires solving linear indeterminate equations (Diophantine equations) of the form ax + c = by.",
                        "hi": "श्लोक 32 और 33 में 'कुट्टक' एल्गोरिथ्म पेश किया गया है। खगोल विज्ञान में सबसे बड़ा सिरदर्द यह होता है कि अलग-अलग गति से चलने वाले दो ग्रह ठीक एक सीध में (Conjunction) कब आएंगे? इसे सुलझाने के लिए ax + c = by जैसे जटिल समीकरण (Diophantine equations) हल करने पड़ते हैं।"
                    },
                    {
                        "en": "For example, if Planet A takes 29 days to complete an orbit and Planet B takes 47 days, how many cycles before they meet at the exact same degree? \nAryabhata's method involves \"pulverizing\" (breaking down) the large coefficients by repeatedly dividing the larger by the smaller, finding the remainder, and substituting backward.",
                        "hi": "मान लीजिए कि ग्रह A को एक चक्कर लगाने में 29 दिन लगते हैं और ग्रह B को 47 दिन, तो कितने चक्करों के बाद वे आसमान में बिल्कुल एक ही जगह पर मिलेंगे?\nइसे हल करने के लिए आर्यभट्ट ने जो तरीका निकाला, उसे 'कुट्टक' (यानी तोड़ना/पीसना) कहा गया। इसमें बड़ी संख्याओं को छोटी संख्याओं से तब तक बार-बार भाग (Divide) दिया जाता है जब तक कि वे टूटकर एकदम छोटी न हो जाएँ, और फिर शेषफल के ज़रिए उल्टी गिनती करके जवाब निकाला जाता है।"
                    },
                    {
                        "en": "Step-by-step Kuttaka logic for (47x + c = 29y):\n1. Divide 47 by 29: Quotient 1, Remainder 18.\n2. Divide 29 by 18: Quotient 1, Remainder 11.\n3. Divide 18 by 11: Quotient 1, Remainder 7.\n4. Continue until the remainder is 1.\n5. Form a column of quotients, add the constant 'c', and multiply upward (the 'Valli' or creeper method) to find the integer solutions for x and y.",
                        "hi": "समीकरण (47x + c = 29y) के लिए कुट्टक विधि कैसे काम करती है:\n1. 47 को 29 से भाग दें: भागफल 1, शेष बचा 18।\n2. 29 को 18 से भाग दें: भागफल 1, शेष बचा 11।\n3. 18 को 11 से भाग दें: भागफल 1, शेष बचा 7।\n4. इसे तब तक दोहराते रहें जब तक शेष 1 न बच जाए।\n5. आखिर में इन सभी भागफलों की एक सीढ़ी (कॉलम) बनाएँ, उसमें स्थिरांक 'c' जोड़ें, और ऊपर की ओर गुणा करते हुए x और y का पक्का जवाब निकाल लें। इसे 'वल्ली' (लता) विधि भी कहते हैं।"
                    },
                    {
                        "en": "This algorithm predates the modern Extended Euclidean Algorithm by hundreds of years and was the primary tool used by Indian astronomers to compute the massive \"Ahargana\" (number of days elapsed since the start of the Kali Yuga) to pinpoint planetary positions.",
                        "hi": "यूरोप में जो 'Extended Euclidean Algorithm' बहुत बाद में आया, यह कुट्टक विधि उससे सैकड़ों साल पुरानी है। इसी कुट्टक के सहारे भारतीय खगोलविदों ने कलियुग की शुरुआत से बीते हुए दिनों (अहर्गण) की गिनती करके ग्रहों की बिल्कुल सटीक लोकेशन खोज निकाली थी।"
                    }
                ),
            )
        ),
    ),
    Chapter(
        slug="aryabhatiya-kalakriya-deep",
        part=PART_ARYABHATA,
        title={"en": "Kalakriya: Cosmic Gearboxes", "hi": "कालक्रिया: खगोलीय गियरबॉक्स"},
        summary={
            "en": "The mechanics of time, measuring the Yugas, and the brilliant Epicyclic theory for retrograde motion.",
            "hi": "समय का पहिया, युगों को नापने का तरीका, और ग्रहों के उल्टे चलने (वक्री गति) का शानदार गणितीय सिद्धांत।",
        },
        minutes=15,
        level="intermediate",
        sections=(
            Section(
                heading={"en": "Refining the Yugas", "hi": "युगों का असली गणित"},
                body=(
                    {
                        "en": "In the Kalakriyapada, Aryabhata departs radically from orthodox religious texts (Smritis) regarding the measurement of cosmic time. Traditional texts claimed the four Yugas (Satya, Treta, Dvapara, Kali) were of unequal, diminishing lengths (4:3:2:1 ratio).",
                        "hi": "कालक्रियापाद में पहुँचते ही आर्यभट्ट पुरानी धार्मिक मान्यताओं और स्मृतियों से बिल्कुल अलग रास्ता पकड़ लेते हैं। पुराने ग्रंथों का मानना था कि चार युग (सत्य, त्रेता, द्वापर, कलि) बराबर नहीं होते, बल्कि 4:3:2:1 के अनुपात में लगातार छोटे होते जाते हैं।"
                    },
                    {
                        "en": "Aryabhata, purely as a mathematical astronomer, rejected this. He stated that a Mahayuga is divided into four strictly equal quarters of 1,080,000 years each, completely stripping the Yuga system of its moral/mythological decline and reducing it to a pure mathematical least-common-multiple for planetary orbits.",
                        "hi": "लेकिन आर्यभट्ट ठहरे एक पक्के गणितज्ञ और खगोलशास्त्री, उन्होंने इस बात को सिरे से खारिज कर दिया। उन्होंने साफ कहा कि एक महायुग के चारों हिस्से बिल्कुल बराबर होते हैं—हर हिस्सा 10,80,000 साल का। उन्होंने युगों की इस व्यवस्था को 'नैतिक पतन' की पौराणिक कहानियों से बाहर निकाला और उसे ग्रहों की कक्षाओं के विशुद्ध गणितीय 'LCM' (लघुत्तम समापवर्त्य) में बदल कर रख दिया।"
                    }
                ),
            ),
            Section(
                heading={"en": "Epicycles: Explaining Retrograde Motion", "hi": "अधिचक्र (Epicycles): ग्रहों की वक्री गति का राज़"},
                body=(
                    {
                        "en": "Planets sometimes appear to stop, move backward (retrograde or 'Vakri'), and then move forward again. To mathematically predict this without a heliocentric telescope, Aryabhata perfected the system of Epicycles (Manda and Sighra).",
                        "hi": "आसमान में कभी-कभी ऐसा लगता है कि ग्रह चलते-चलते रुक गए हैं, फिर वे उल्टे (वक्री/Retrograde) चलने लगते हैं, और कुछ दिन बाद फिर से सीधे चलने लगते हैं। उस ज़माने में बिना किसी सूर्य-केंद्रित (Heliocentric) टेलिस्कोप के इस पहेली को गणित से सुलझाने के लिए, आर्यभट्ट ने 'अधिचक्र' (Epicycles) के सिद्धांत को बिल्कुल सटीक रूप दिया।"
                    },
                    {
                        "en": "He modeled planetary motion as a smaller circle (the epicycle) whose center moves along the circumference of a larger circle (the deferent) around the Earth.",
                        "hi": "उन्होंने समझाया कि ग्रह असल में एक बहुत बड़े घेरे (Deferent) पर नहीं चलते, बल्कि वे एक छोटे घेरे (Epicycle) पर घूम रहे होते हैं, और इस छोटे घेरे का केंद्र (Center) पृथ्वी के चारों ओर बने उस बड़े घेरे पर खिसकता रहता है।"
                    },
                    {
                        "en": "Aryabhata's equations for the 'Equation of Center' (Manda-phala) to correct the mean position of a planet:\nTrue Longitude = Mean Longitude ± (Radius of Epicycle / Radius of Deferent) × Sine(Mean Anomaly)",
                        "hi": "ग्रह की 'औसत स्थिति' (Mean position) को ठीक करके उसकी 'असली स्थिति' निकालने के लिए उन्होंने जो समीकरण दिया, वह कुछ ऐसा था:\nस्पष्ट रेखांश = मध्यम रेखांश ± (अधिचक्र की त्रिज्या / कक्षा की त्रिज्या) × ज्या (मध्यम विसंगति)"
                    },
                    {
                        "en": "By giving exact dimensions for these epicycles for Mars, Jupiter, Venus, Saturn, and Mercury in verses 17-21, he provided the exact code needed to compute planetary positions with stunning accuracy.",
                        "hi": "श्लोक 17 से 21 के बीच आर्यभट्ट ने मंगल, गुरु, शुक्र, शनि और बुध के लिए इन अधिचक्रों का बिल्कुल सटीक आकार (Dimensions) लिखकर दे दिया। इससे खगोलविदों के हाथ वह कोड लग गया जिससे वे किसी भी ग्रह की जगह अचूक सटीकता से बता सकते थे।"
                    }
                ),
            )
        ),
    ),
    Chapter(
        slug="aryabhatiya-golapada-deep",
        part=PART_ARYABHATA,
        title={"en": "Golapada: The Architecture of the Heavens", "hi": "गोलपाद: स्वर्ग की वास्तुकला"},
        summary={
            "en": "Spherical astronomy, the definitive proof of Earth's rotation, and the precise geometric calculation of eclipses.",
            "hi": "गोलीय खगोल विज्ञान, पृथ्वी के घूमने का सबसे बड़ा सबूत, और ग्रहण को नापने का सटीक ज्यामितीय गणित।",
        },
        minutes=20,
        level="intermediate",
        sections=(
            Section(
                heading={"en": "The Rotating Earth Analogy", "hi": "घूमती हुई पृथ्वी का उदाहरण"},
                body=(
                    {
                        "en": "The Golapada (50 verses) focuses on the celestial sphere. In verse 9, Aryabhata delivers one of the most famous analogies in the history of science to prove the Earth rotates on its axis.",
                        "hi": "गोलपाद (50 श्लोक) पूरी तरह से आसमान और खगोलीय गोले (Celestial sphere) की ज्यामिति पर टिका है। इसके श्लोक 9 में आर्यभट्ट विज्ञान के इतिहास का सबसे मशहूर उदाहरण देते हुए यह साबित करते हैं कि हमारी पृथ्वी अपनी धुरी पर घूम रही है।"
                    },
                    {
                        "en": "Sanskrit Verse 9:\n\"anulomagatirnausthaḥ paśyatyacalam vilomagam yadvat / \nacalāni bhāni tadvat samapaścimagāni lankāyām\"",
                        "hi": "संस्कृत श्लोक 9:\n\"अनुलोमगतिर्नौस्थः पश्यत्यचलं विलोमगं यद्वत्।\nअचलानि भानि तद्वत् समपश्चिमगानि लंकायाम्॥\""
                    },
                    {
                        "en": "Translation: \"Just as a man in a boat moving forward (anuloma) sees stationary objects on the bank moving backward (viloma), in exactly the same way, the stationary stars (acalāni bhāni) appear to move straight toward the west for a person on the equator (Lanka).\"\nThis insight replaced the mechanical nightmare of a spinning universe with the elegant reality of a spinning Earth.",
                        "hi": "अनुवाद: \"जिस तरह आगे की ओर (अनुलोम) बहती हुई नाव में बैठा इंसान किनारे की रुकी हुई चीज़ों को पीछे की ओर (विलोम) जाते हुए देखता है, ठीक उसी तरह, भूमध्य रेखा (लंका) पर खड़े इंसान को रुके हुए तारे (अचलानि भानि) सीधे पश्चिम की तरफ जाते हुए दिखाई देते हैं।\"\nइस एक शानदार सोच ने उस पुरानी गलतफहमी को हमेशा के लिए खत्म कर दिया कि पूरा ब्रह्मांड पृथ्वी के चक्कर लगा रहा है।"
                    }
                ),
            ),
            Section(
                heading={"en": "The Science of Shadows", "hi": "परछाइयों का विज्ञान (ग्रहण)"},
                body=(
                    {
                        "en": "Verses 37 to 48 are dedicated entirely to calculating eclipses. Aryabhata systematically dismantles the mythological idea of demons (Rahu and Ketu) causing eclipses.",
                        "hi": "श्लोक 37 से 48 पूरी तरह से ग्रहण (Eclipses) का गणित सुलझाने के लिए लिखे गए हैं। आर्यभट्ट ने राहु और केतु जैसे राक्षसों द्वारा सूरज-चाँद को निगलने वाली पुरानी पौराणिक कथाओं को जड़ से उखाड़ फेंका।"
                    },
                    {
                        "en": "Verse 37 translation: \"The Moon is of water, the Sun of fire, the Earth of soil, and its shadow of darkness. The Moon eclipses the Sun, and the great shadow of the Earth eclipses the Moon.\"",
                        "hi": "श्लोक 37 का अनुवाद: \"चंद्रमा पानी का है, सूर्य आग का है, पृथ्वी मिट्टी की है, और उसकी परछाईं अंधेरे की है। चंद्रमा सूर्य को ढकता है, और पृथ्वी की विशाल परछाईं चंद्रमा को ढकती है।\""
                    },
                    {
                        "en": "He doesn't just state this qualitatively; he gives the exact geometric formula to find the length of the Earth's shadow (Bhu-chhaya) cone:\n\nLength of Shadow = (Distance to Sun × Diameter of Earth) / (Diameter of Sun - Diameter of Earth)",
                        "hi": "वे सिर्फ अपनी बात कहकर नहीं रुकते; वे पृथ्वी की उस परछाईं (भू-छाया) की लंबाई नापने का बिल्कुल सटीक ज्यामितीय सूत्र देते हैं:\n\nछाया की लंबाई = (सूर्य की दूरी × पृथ्वी का व्यास) / (सूर्य का व्यास - पृथ्वी का व्यास)"
                    },
                    {
                        "en": "Once the length of the shadow cone is known, verse 40 gives the formula for the diameter of the shadow at the specific distance of the Moon's orbit. If the Moon's latitude brings it inside this geometric shadow, a lunar eclipse occurs. He even provided formulas to calculate the exact duration (Sthiti-ardha) of the total eclipse phase.",
                        "hi": "एक बार परछाईं की लंबाई पता चल जाए, तो श्लोक 40 चंद्रमा की कक्षा तक पहुँचते-पहुँचते उस परछाईं का व्यास (Diameter) निकालने का सूत्र देता है। जब चंद्रमा अपनी कक्षा में घूमता हुआ इस ज्यामितीय परछाईं के अंदर आ जाता है, तब चंद्र ग्रहण लगता है। इतना ही नहीं, उन्होंने पूर्ण ग्रहण कितनी देर तक चलेगा (स्थिति-अर्ध), इसका भी पक्का गणित दे दिया था।"
                    }
                ),
                aside={
                    "en": "The next time someone claims classical Indian texts were purely mythological, remember these 121 verses. They represent the moment mathematics definitively conquered the sky.",
                    "hi": "अगली बार जब कोई यह कहे कि पुराने भारतीय ग्रंथ सिर्फ कोरी पौराणिक कहानियों से भरे हैं, तो उन्हें इन 121 श्लोकों की याद दिलाइएगा। यह खगोल विज्ञान का वह क्षण था जब गणित ने आसमान के सारे रहस्यों को जीत लिया था।"
                }
            )
        ),
    ),
)
