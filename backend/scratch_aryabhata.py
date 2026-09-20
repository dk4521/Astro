content = '''"""Part eight: The Aryabhatiya.

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
            "hi": "मंगलाचरण, शानदार वर्णानुक्रमिक संख्या प्रणाली, और क्रांतिकारी ज्या (Sine) तालिका।",
        },
        minutes=15,
        level="intermediate",
        sections=(
            Section(
                heading={"en": "The Illusion of Brevity", "hi": "संक्षिप्तता का भ्रम"},
                body=(
                    {
                        "en": "The Aryabhatiya contains only 121 verses (Sutras), making it seem deceptively short. However, in the Indian tradition of 'Sutra' literature, knowledge was compressed into the absolute minimum number of syllables required, acting as memory aids (mnemonics) for scholars.",
                        "hi": "आर्यभटीय में केवल 121 श्लोक (सूत्र) हैं, जिससे यह भ्रामक रूप से छोटा लगता है। हालाँकि, 'सूत्र' साहित्य की भारतीय परंपरा में, ज्ञान को याद रखने (Mnemonics) के लिए न्यूनतम संभव अक्षरों में संकुचित (Compress) किया जाता था।"
                    },
                    {
                        "en": "Because of this extreme compression, the mathematics encoded within these 121 verses is so profound that subsequent astronomers, such as Bhaskara I (in his Aryabhatiya Bhasya) and Nilakantha Somayaji (in his Aryabhatiya Bhasya), had to write commentaries spanning thousands of pages to unpack the derivations, proofs, and working algorithms hidden inside.",
                        "hi": "इस अत्यधिक संपीड़न (Compression) के कारण, इन 121 श्लोकों में कूटबद्ध गणित इतना गहरा है कि बाद के खगोलविदों, जैसे भास्कर प्रथम (उनके आर्यभटीय भाष्य में) और नीलकंठ सोमयाजी को इसके अंदर छिपे हुए प्रमेयों, प्रमाणों और एल्गोरिदम को खोलने के लिए हज़ारों पन्नों के भाष्य (Commentaries) लिखने पड़े।"
                    }
                ),
            ),
            Section(
                heading={"en": "The Alphabetic Numeral System (Katapayadi precursor)", "hi": "वर्णानुक्रमिक संख्या प्रणाली"},
                body=(
                    {
                        "en": "To fit massive astronomical numbers—like the number of times the moon revolves around the earth in 4.32 million years—into a poetic meter, Aryabhata invented a brilliant cryptographic number system.",
                        "hi": "विशाल खगोलीय संख्याओं—जैसे कि 43.2 लाख वर्षों में चंद्रमा कितनी बार पृथ्वी की परिक्रमा करता है—को काव्यात्मक छंद में फिट करने के लिए, आर्यभट्ट ने एक शानदार क्रिप्टोग्राफिक संख्या प्रणाली का आविष्कार किया।"
                    },
                    {
                        "en": "Verse 2 explains the rule: Consonants represent numbers. The 'varga' (classified) consonants from 'ka' to 'ma' represent 1 to 25. The 'avarga' (unclassified) consonants like 'ya', 'ra', 'la', 'va' represent 30, 40, 50, 60, etc. Vowels act as multipliers (powers of 100). 'a' = 1, 'i' = 100, 'u' = 10,000, and so on.",
                        "hi": "श्लोक 2 नियम की व्याख्या करता है: व्यंजन (Consonants) संख्याओं का प्रतिनिधित्व करते हैं। 'क' से 'म' तक के 'वर्ग' व्यंजन 1 से 25 का प्रतिनिधित्व करते हैं। 'य', 'र', 'ल', 'व' जैसे 'अवर्ग' व्यंजन 30, 40, 50, 60 आदि का प्रतिनिधित्व करते हैं। स्वर गुणक (100 की घातों) के रूप में कार्य करते हैं। 'अ' = 1, 'इ' = 100, 'उ' = 10,000, इत्यादि।"
                    },
                    {
                        "en": "Example Calculation: The word 'khyughṛ' (ख्युघृ) represents the number of revolutions of the Sun in a Mahayuga (4,320,000). \nHere is the exact mathematical decoding:\n1. 'kh' (ख) = 2. Attached to 'u' (10,000) = 20,000.\n2. 'y' (य) = 30. Attached to 'u' (10,000) = 300,000.\n3. 'gh' (घ) = 4. Attached to 'ṛ' (1,000,000) = 4,000,000.\nTotal = 4,000,000 + 300,000 + 20,000 = 4,320,000. \nThus, millions of years of celestial mechanics were compressed into two syllables.",
                        "hi": "उदाहरण गणना: 'ख्युघृ' शब्द एक महायुग (4,320,000) में सूर्य की परिक्रमाओं की संख्या को दर्शाता है। \nयहाँ सटीक गणितीय डिकोडिंग है:\n1. 'ख' (2) 'उ' (10,000) के साथ = 20,000।\n2. 'य' (30) 'उ' (10,000) के साथ = 300,000।\n3. 'घ' (4) 'ऋ' (1,000,000) के साथ = 4,000,000।\nकुल = 4,000,000 + 300,000 + 20,000 = 4,320,000। \nइस प्रकार, लाखों वर्षों के खगोलीय यांत्रिकी को सिर्फ दो अक्षरों में संकुचित कर दिया गया।"
                    }
                ),
            ),
            Section(
                heading={"en": "The First Table of Sines (Jya)", "hi": "ज्या (Sine) की पहली तालिका"},
                body=(
                    {
                        "en": "Verse 12 contains the famous 'Jya' table. Aryabhata computed the sine of angles from 0 to 90 degrees at intervals of 3.75 degrees (225 minutes of arc).",
                        "hi": "श्लोक 12 में प्रसिद्ध 'ज्या' (Sine) तालिका है। आर्यभट्ट ने 0 से 90 डिग्री तक के कोणों की ज्या की गणना 3.75 डिग्री (225 मिनट आर्क) के अंतराल पर की।"
                    },
                    {
                        "en": "He didn't just give the values; he gave the second-order difference equation used to generate them: \n\nR sin(n+1)A - R sin(n)A = [R sin(n)A - R sin(n-1)A] - [R sin(n)A / R sin(A)]\n\nThis recursive formula is mathematically equivalent to the modern differential equation d²(sin θ)/dθ² = -sin θ. It is the absolute bedrock of all trigonometric astronomy.",
                        "hi": "उन्होंने केवल मूल्य नहीं दिए; उन्होंने उन्हें उत्पन्न करने के लिए उपयोग किए जाने वाले द्वितीय-क्रम अंतर समीकरण (Second-order difference equation) को दिया: \n\nR sin(n+1)A - R sin(n)A = [R sin(n)A - R sin(n-1)A] - [R sin(n)A / 225]\n\nयह पुनरावर्ती सूत्र (Recursive formula) गणितीय रूप से आधुनिक अवकल समीकरण d²(sin θ)/dθ² = -sin θ के समतुल्य है। यह सभी त्रिकोणमितीय खगोल विज्ञान का पूर्ण आधार है।"
                    }
                ),
                aside={
                    "en": "When Arab scholars translated Jya, they wrote it as 'jiba'. Later Latin translators misread it as 'jaib' (meaning 'bay' or 'fold') and translated it to Latin as 'sinus', which is why we call it 'Sine' today. It all started with this verse.",
                    "hi": "जब अरब विद्वानों ने 'ज्या' का अनुवाद किया, तो उन्होंने इसे 'जीवा' लिखा। बाद के लैटिन अनुवादकों ने इसे गलती से 'जैब' (जिसका अर्थ है खाड़ी या मोड़) पढ़ लिया और इसका लैटिन में अनुवाद 'sinus' (साइनस) कर दिया, यही कारण है कि आज हम इसे 'Sine' कहते हैं। यह सब इसी श्लोक से शुरू हुआ था।"
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
            "hi": "Pi (π) की सटीक संस्कृत परिभाषा, गुणोत्तर श्रेढ़ी, और कुट्टक एल्गोरिथ्म का गहन अध्ययन।",
        },
        minutes=15,
        level="intermediate",
        sections=(
            Section(
                heading={"en": "The Irrationality of Pi (π)", "hi": "पाई (π) की अपरिमेयता"},
                body=(
                    {
                        "en": "In verse 10, Aryabhata gives an incredibly accurate approximation for Pi (π), explicitly noting it as an approximation (āsanna).",
                        "hi": "श्लोक 10 में, आर्यभट्ट पाई (π) का अविश्वसनीय रूप से सटीक अनुमान देते हैं, स्पष्ट रूप से इसे एक सन्निकटन (आसन्न / Approximation) के रूप में नोट करते हैं।"
                    },
                    {
                        "en": "The original Sanskrit verse:\n\"caturadhikam śatamaṣṭaguṇam dvāṣaṣṭistathā sahasrāṇām / \nayutadvayaviṣkambhasyāsanno vṛttapariṇāmaḥ\" \n\nLiteral Translation: \"Add four to 100, multiply by eight, and then add 62,000. By this rule the circumference of a circle with a diameter of 20,000 can be approached.\"",
                        "hi": "मूल संस्कृत श्लोक:\n\"चतुरधिकं शतमष्टगुणं द्वाषष्टिस्तथा सहस्राणाम्।\nअयुतद्वयविष्कम्भस्यासन्नो वृत्तपरिणाहः॥\"\n\nशाब्दिक अनुवाद: \"100 में चार जोड़ें, आठ से गुणा करें, और फिर 62,000 जोड़ें। इस नियम से 20,000 के व्यास वाले वृत्त की परिधि जानी जा सकती है (आसन्न)।\""
                    },
                    {
                        "en": "Mathematical derivation:\nCircumference = [(100 + 4) × 8] + 62,000 = 832 + 62,000 = 62,832.\nDiameter = 20,000.\nπ = Circumference / Diameter = 62,832 / 20,000 = 3.1416.\nThis was the most accurate value of Pi known in the ancient world, accurate to four decimal places.",
                        "hi": "गणितीय व्युत्पत्ति:\nपरिधि = [(100 + 4) × 8] + 62,000 = 832 + 62,000 = 62,832।\nव्यास = 20,000।\nπ = परिधि / व्यास = 62,832 / 20,000 = 3.1416।\nयह प्राचीन विश्व में ज्ञात पाई का सबसे सटीक मान था, जो दशमलव के चार स्थानों तक सटीक था।"
                    }
                ),
            ),
            Section(
                heading={"en": "The Kuttaka (Pulverizer) Algorithm", "hi": "कुट्टक (तोड़ने वाला) एल्गोरिथ्म"},
                body=(
                    {
                        "en": "Verses 32 and 33 present the 'Kuttaka' algorithm. In astronomy, finding when two planets will align perfectly (a conjunction) requires solving linear indeterminate equations (Diophantine equations) of the form ax + c = by.",
                        "hi": "श्लोक 32 और 33 'कुट्टक' एल्गोरिथ्म प्रस्तुत करते हैं। खगोल विज्ञान में, यह पता लगाने के लिए कि दो ग्रह पूरी तरह से एक सीध में (Conjunction) कब आएंगे, ax + c = by के रूप के रैखिक अनिश्चित समीकरणों (Diophantine equations) को हल करना आवश्यक है।"
                    },
                    {
                        "en": "For example, if Planet A takes 29 days to complete an orbit and Planet B takes 47 days, how many cycles before they meet at the exact same degree? \nAryabhata's method involves \"pulverizing\" (breaking down) the large coefficients by repeatedly dividing the larger by the smaller, finding the remainder, and substituting backward.",
                        "hi": "उदाहरण के लिए, यदि ग्रह A को कक्षा पूरी करने में 29 दिन लगते हैं और ग्रह B को 47 दिन लगते हैं, तो वे कितने चक्रों के बाद बिल्कुल उसी डिग्री पर मिलेंगे?\nआर्यभट्ट की विधि में बड़े गुणांकों (Coefficients) को \"कुट्टक\" (तोड़ना) शामिल है, जिसमें बड़ी संख्या को छोटी संख्या से बार-बार विभाजित किया जाता है, शेषफल निकाला जाता है, और पीछे की ओर प्रतिस्थापित किया जाता है।"
                    },
                    {
                        "en": "Step-by-step Kuttaka logic for (47x + c = 29y):\n1. Divide 47 by 29: Quotient 1, Remainder 18.\n2. Divide 29 by 18: Quotient 1, Remainder 11.\n3. Divide 18 by 11: Quotient 1, Remainder 7.\n4. Continue until the remainder is 1.\n5. Form a column of quotients, add the constant 'c', and multiply upward (the 'Valli' or creeper method) to find the integer solutions for x and y.",
                        "hi": "(47x + c = 29y) के लिए कुट्टक तर्क (Step-by-step):\n1. 47 को 29 से विभाजित करें: भागफल 1, शेष 18।\n2. 29 को 18 से विभाजित करें: भागफल 1, शेष 11।\n3. 18 को 11 से विभाजित करें: भागफल 1, शेष 7।\n4. तब तक जारी रखें जब तक शेष 1 न हो जाए।\n5. भागफल का एक कॉलम बनाएं, स्थिरांक 'c' जोड़ें, और x और y के लिए पूर्णांक समाधान खोजने के लिए ऊपर की ओर गुणा करें (वल्ली या लता विधि)।"
                    },
                    {
                        "en": "This algorithm predates the modern Extended Euclidean Algorithm by hundreds of years and was the primary tool used by Indian astronomers to compute the massive \"Ahargana\" (number of days elapsed since the start of the Kali Yuga) to pinpoint planetary positions.",
                        "hi": "यह एल्गोरिथ्म आधुनिक विस्तारित यूक्लिडियन एल्गोरिथ्म (Extended Euclidean Algorithm) से सैकड़ों साल पहले का है और ग्रहों की स्थिति का पता लगाने के लिए विशाल \"अहर्गण\" (कलियुग की शुरुआत के बाद से बीते दिनों की संख्या) की गणना करने के लिए भारतीय खगोलविदों द्वारा उपयोग किया जाने वाला प्राथमिक उपकरण था।"
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
            "hi": "समय का तंत्र, युगों को मापना, और वक्री गति (Retrograde) के लिए शानदार अधिचक्र (Epicyclic) सिद्धांत।",
        },
        minutes=15,
        level="intermediate",
        sections=(
            Section(
                heading={"en": "Refining the Yugas", "hi": "युगों का संशोधन"},
                body=(
                    {
                        "en": "In the Kalakriyapada, Aryabhata departs radically from orthodox religious texts (Smritis) regarding the measurement of cosmic time. Traditional texts claimed the four Yugas (Satya, Treta, Dvapara, Kali) were of unequal, diminishing lengths (4:3:2:1 ratio).",
                        "hi": "कालक्रियापाद में, आर्यभट्ट ब्रह्मांडीय समय के मापन के संबंध में रूढ़िवादी धार्मिक ग्रंथों (स्मृतियों) से मौलिक रूप से अलग हो जाते हैं। पारंपरिक ग्रंथों का दावा था कि चार युग (सत्य, त्रेता, द्वापर, कलि) असमान, घटती हुई लंबाई (4:3:2:1 अनुपात) के थे।"
                    },
                    {
                        "en": "Aryabhata, purely as a mathematical astronomer, rejected this. He stated that a Mahayuga is divided into four strictly equal quarters of 1,080,000 years each, completely stripping the Yuga system of its moral/mythological decline and reducing it to a pure mathematical least-common-multiple for planetary orbits.",
                        "hi": "आर्यभट्ट ने विशुद्ध रूप से एक गणितीय खगोलशास्त्री के रूप में इसे खारिज कर दिया। उन्होंने कहा कि एक महायुग को 1,080,000 वर्षों के चार बिल्कुल समान तिमाहियों में विभाजित किया गया है, जिसने युग प्रणाली को उसके नैतिक/पौराणिक पतन से पूरी तरह मुक्त कर दिया और इसे ग्रहों की कक्षाओं के लिए एक शुद्ध गणितीय लघुत्तम-समापवर्त्य (LCM) में बदल दिया।"
                    }
                ),
            ),
            Section(
                heading={"en": "Epicycles: Explaining Retrograde Motion", "hi": "अधिचक्र (Epicycles): वक्री गति की व्याख्या"},
                body=(
                    {
                        "en": "Planets sometimes appear to stop, move backward (retrograde or 'Vakri'), and then move forward again. To mathematically predict this without a heliocentric telescope, Aryabhata perfected the system of Epicycles (Manda and Sighra).",
                        "hi": "ग्रह कभी-कभी रुकते हुए, पीछे की ओर चलते हुए (वक्री गति), और फिर आगे बढ़ते हुए दिखाई देते हैं। सूर्य-केंद्रित टेलीस्कोप के बिना गणितीय रूप से इसकी भविष्यवाणी करने के लिए, आर्यभट्ट ने अधिचक्र (Epicycles - मंद और शीघ्र) की प्रणाली को परिपूर्ण किया।"
                    },
                    {
                        "en": "He modeled planetary motion as a smaller circle (the epicycle) whose center moves along the circumference of a larger circle (the deferent) around the Earth.",
                        "hi": "उन्होंने ग्रहीय गति को एक छोटे वृत्त (अधिचक्र/Epicycle) के रूप में तैयार किया, जिसका केंद्र पृथ्वी के चारों ओर एक बड़े वृत्त (कक्षा) की परिधि के साथ चलता है।"
                    },
                    {
                        "en": "Aryabhata's equations for the 'Equation of Center' (Manda-phala) to correct the mean position of a planet:\nTrue Longitude = Mean Longitude ± (Radius of Epicycle / Radius of Deferent) × Sine(Mean Anomaly)",
                        "hi": "ग्रह की मध्यम स्थिति (Mean position) को ठीक करने के लिए 'केंद्र के समीकरण' (मंद-फल) के लिए आर्यभट्ट के समीकरण:\nस्पष्ट रेखांश (True Longitude) = मध्यम रेखांश ± (अधिचक्र की त्रिज्या / कक्षा की त्रिज्या) × ज्या (मध्यम विसंगति / Mean Anomaly)"
                    },
                    {
                        "en": "By giving exact dimensions for these epicycles for Mars, Jupiter, Venus, Saturn, and Mercury in verses 17-21, he provided the exact code needed to compute planetary positions with stunning accuracy.",
                        "hi": "श्लोक 17-21 में मंगल, गुरु, शुक्र, शनि और बुध के लिए इन अधिचक्रों के सटीक आयाम (Dimensions) देकर, उन्होंने ग्रहों की स्थिति की आश्चर्यजनक सटीकता के साथ गणना करने के लिए आवश्यक सटीक कोड प्रदान किया।"
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
            "hi": "गोलीय खगोल विज्ञान, पृथ्वी के घूर्णन का निश्चित प्रमाण, और ग्रहणों की सटीक ज्यामितीय गणना।",
        },
        minutes=20,
        level="intermediate",
        sections=(
            Section(
                heading={"en": "The Rotating Earth Analogy", "hi": "घूमती हुई पृथ्वी का सादृश्य"},
                body=(
                    {
                        "en": "The Golapada (50 verses) focuses on the celestial sphere. In verse 9, Aryabhata delivers one of the most famous analogies in the history of science to prove the Earth rotates on its axis.",
                        "hi": "गोलपाद (50 श्लोक) खगोलीय गोले (Celestial sphere) पर केंद्रित है। श्लोक 9 में, आर्यभट्ट विज्ञान के इतिहास में सबसे प्रसिद्ध उपमाओं में से एक देते हैं यह साबित करने के लिए कि पृथ्वी अपनी धुरी पर घूमती है।"
                    },
                    {
                        "en": "Sanskrit Verse 9:\n\"anulomagatirnausthaḥ paśyatyacalam vilomagam yadvat / \nacalāni bhāni tadvat samapaścimagāni lankāyām\"",
                        "hi": "संस्कृत श्लोक 9:\n\"अनुलोमगतिर्नौस्थः पश्यत्यचलं विलोमगं यद्वत्।\nअचलानि भानि तद्वत् समपश्चिमगानि लंकायाम्॥\""
                    },
                    {
                        "en": "Translation: \"Just as a man in a boat moving forward (anuloma) sees stationary objects on the bank moving backward (viloma), in exactly the same way, the stationary stars (acalāni bhāni) appear to move straight toward the west for a person on the equator (Lanka).\"\nThis insight replaced the mechanical nightmare of a spinning universe with the elegant reality of a spinning Earth.",
                        "hi": "अनुवाद: \"जिस प्रकार आगे की ओर (अनुलोम) जाती हुई नाव में बैठा व्यक्ति किनारे की स्थिर वस्तुओं को पीछे की ओर (विलोम) जाते हुए देखता है, ठीक उसी प्रकार, भूमध्य रेखा (लंका) पर बैठे व्यक्ति को स्थिर तारे (अचलानि भानि) सीधे पश्चिम की ओर जाते हुए दिखाई देते हैं।\"\nइस अंतर्दृष्टि ने एक घूमते हुए ब्रह्मांड के यांत्रिक दुःस्वप्न को एक घूमती हुई पृथ्वी की सुरुचिपूर्ण वास्तविकता से बदल दिया।"
                    }
                ),
            ),
            Section(
                heading={"en": "The Geometry of Eclipses", "hi": "ग्रहणों की ज्यामिति"},
                body=(
                    {
                        "en": "Verses 37 to 48 are dedicated entirely to calculating eclipses. Aryabhata systematically dismantles the mythological idea of demons (Rahu and Ketu) causing eclipses.",
                        "hi": "श्लोक 37 से 48 पूरी तरह से ग्रहणों की गणना के लिए समर्पित हैं। आर्यभट्ट ने व्यवस्थित रूप से राक्षसों (राहु और केतु) के कारण ग्रहण होने के पौराणिक विचार को नष्ट कर दिया।"
                    },
                    {
                        "en": "Verse 37 translation: \"The Moon is of water, the Sun of fire, the Earth of soil, and its shadow of darkness. The Moon eclipses the Sun, and the great shadow of the Earth eclipses the Moon.\"",
                        "hi": "श्लोक 37 अनुवाद: \"चंद्रमा जल का है, सूर्य अग्नि का है, पृथ्वी मिट्टी की है, और उसकी छाया अंधकार की है। चंद्रमा सूर्य पर ग्रहण लगाता है, और पृथ्वी की महान छाया चंद्रमा पर ग्रहण लगाती है।\""
                    },
                    {
                        "en": "He doesn't just state this qualitatively; he gives the exact geometric formula to find the length of the Earth's shadow (Bhu-chhaya) cone:\n\nLength of Shadow = (Distance to Sun × Diameter of Earth) / (Diameter of Sun - Diameter of Earth)",
                        "hi": "वह इसे केवल गुणात्मक (Qualitatively) रूप से नहीं कहते हैं; वह पृथ्वी के छाया शंकु (भू-छाया) की लंबाई ज्ञात करने के लिए सटीक ज्यामितीय सूत्र देते हैं:\n\nछाया की लंबाई = (सूर्य की दूरी × पृथ्वी का व्यास) / (सूर्य का व्यास - पृथ्वी का व्यास)"
                    },
                    {
                        "en": "Once the length of the shadow cone is known, verse 40 gives the formula for the diameter of the shadow at the specific distance of the Moon's orbit. If the Moon's latitude brings it inside this geometric shadow, a lunar eclipse occurs. He even provided formulas to calculate the exact duration (Sthiti-ardha) of the total eclipse phase.",
                        "hi": "एक बार छाया शंकु की लंबाई ज्ञात हो जाने के बाद, श्लोक 40 चंद्रमा की कक्षा की विशिष्ट दूरी पर छाया के व्यास (Diameter) का सूत्र देता है। यदि चंद्रमा का अक्षांश (Latitude) उसे इस ज्यामितीय छाया के अंदर लाता है, तो चंद्र ग्रहण होता है। उन्होंने पूर्ण ग्रहण चरण की सटीक अवधि (स्थिति-अर्ध) की गणना करने के लिए सूत्र भी प्रदान किए।"
                    }
                ),
                aside={
                    "en": "The next time someone claims classical Indian texts were purely mythological, remember these 121 verses. They represent the moment mathematics definitively conquered the sky.",
                    "hi": "अगली बार जब कोई यह दावा करे कि शास्त्रीय भारतीय ग्रंथ विशुद्ध रूप से पौराणिक थे, तो इन 121 श्लोकों को याद रखें। वे उस क्षण का प्रतिनिधित्व करते हैं जब गणित ने निश्चित रूप से आकाश पर विजय प्राप्त की।"
                }
            )
        ),
    ),
)
'''

with open('/home/deepak/Documents/astrology app/backend/app/course/parts/aryabhata.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("aryabhata.py written successfully.")
