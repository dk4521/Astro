"""The seventy-eight cards, written by a person.

Deliberately shaped like `meanings.py` rather than like `astro/`: nothing here
is measured, so nothing here is generated either. A card's meaning does not vary
by reader and does not change tomorrow, which makes it exactly the kind of text
that should be written once and shipped — not asked of a model on every draw,
where it would cost a request and could come back different.

House style, the same one the course and the dasha meanings keep:

- **Themes, not forecasts.** A card is a subject to think about, never a claim
  about what will happen.
- **No ranking.** No card is lucky or unlucky, good or bad. Death is an ending,
  the Tower is a weak foundation giving way, the Devil is a habit that charges
  more than it admits — described honestly and without menace, because
  frightening people is the one thing this product refuses to do.
- **Reversed is another angle, not a punishment.** The reversed line is written
  as the same theme seen from the other side — held back, overdone, or just
  beginning to loosen. It is never "the bad version of the card".
- **Something in their hands.** Where a line can name what the person could
  actually do, it does.

**On the Hindi.** Tarot has no settled Hindi vocabulary, so these are
translations rather than transliterations — नादान for The Fool, not "फ़ूल". A
reader who knows the English names can still find their card by its number and
suit, and a reader who does not gets a name that means something. The minor
arcana names are *composed* from the suit and the rank rather than listed, which
is what keeps "तीन तलवारें" and "तलवारों की रानी" from drifting apart over 56
cards.
"""

from __future__ import annotations

from dataclasses import dataclass

Text = dict[str, str]

LANGUAGES = ("en", "hi")


def pick(text: Text, language: str) -> str:
    """One language out of a `Text`, falling back to English."""
    return text.get(language) or text["en"]


@dataclass(frozen=True, slots=True)
class Card:
    """One card, in both languages.

    `arcana`, `suit` and `number` are the drawing instructions as much as they
    are facts: the app has no card art — 78 illustrations is a licensing problem
    and a 40 MB install — so it draws each face from these three fields. A major
    card gets its roman numeral, a minor card gets its suit mark repeated.
    """

    id: str
    arcana: str  # "major" | "minor"
    suit: str | None  # "wands" | "cups" | "swords" | "pentacles"
    #: 0–21 for the major arcana; 1–14 for a suit, where 11–14 are the court.
    number: int
    name: Text
    keywords: Text
    upright: Text
    reversed: Text


# --- Major arcana -----------------------------------------------------------


def _major(
    number: int,
    slug: str,
    name: tuple[str, str],
    keywords: tuple[str, str],
    upright: tuple[str, str],
    reversed_: tuple[str, str],
) -> Card:
    return Card(
        id=f"major-{slug}",
        arcana="major",
        suit=None,
        number=number,
        name={"en": name[0], "hi": name[1]},
        keywords={"en": keywords[0], "hi": keywords[1]},
        upright={"en": upright[0], "hi": upright[1]},
        reversed={"en": reversed_[0], "hi": reversed_[1]},
    )


MAJOR: tuple[Card, ...] = (
    _major(
        0, "fool",
        ("The Fool", "नादान"),
        ("beginning, trust, the first step", "शुरुआत, भरोसा, पहला क़दम"),
        (
            "A start made before you feel ready, and the nerve that makes it possible.",
            "तैयार महसूस करने से पहले उठाया गया क़दम, और वह हिम्मत जो उसे संभव बनाती है।",
        ),
        (
            "The same step, held back — by planning it once more, or asking one more person.",
            "वही क़दम, रुका हुआ — एक बार और योजना बनाकर, या एक और व्यक्ति से पूछकर।",
        ),
    ),
    _major(
        1, "magician",
        ("The Magician", "जादूगर"),
        ("focus, skill, what is at hand", "एकाग्रता, कौशल, हाथ में मौजूद साधन"),
        (
            "Everything this needs is already in front of you; the work is choosing where to point it.",
            "इसके लिए जो चाहिए वह सामने है; काम बस यह तय करना है कि उसे किस ओर लगाना है।",
        ),
        (
            "Energy spread across too many things to move any one of them.",
            "ऊर्जा इतनी जगह बँटी है कि किसी एक चीज़ को हिला नहीं पाती।",
        ),
    ),
    _major(
        2, "high-priestess",
        ("The High Priestess", "महापुरोहिता"),
        ("knowing, patience, the unsaid", "जानना, धैर्य, अनकहा"),
        (
            "Something you already know without being able to argue for it yet. Wait before you speak.",
            "कुछ जो आप जानते तो हैं पर अभी तर्क से समझा नहीं सकते। बोलने से पहले ठहरिए।",
        ),
        (
            "The quiet answer is there and being talked over — usually by your own noise.",
            "शांत उत्तर मौजूद है पर उसे दबाया जा रहा है — अक्सर आपके अपने शोर से।",
        ),
    ),
    _major(
        3, "empress",
        ("The Empress", "साम्राज्ञी"),
        ("care, growth, plenty", "देखभाल, वृद्धि, प्रचुरता"),
        (
            "Something you have been tending is ready to grow if you keep feeding it.",
            "जिसकी आप देखभाल कर रहे हैं वह बढ़ने को तैयार है — बस पोषण जारी रखिए।",
        ),
        (
            "Care poured outward until there is none left over for yourself.",
            "देखभाल बाहर इतनी बँटी कि अपने लिए कुछ नहीं बचा।",
        ),
    ),
    _major(
        4, "emperor",
        ("The Emperor", "सम्राट"),
        ("structure, authority, boundaries", "ढाँचा, अधिकार, सीमाएँ"),
        (
            "Order is what this needs — a rule, a schedule, a line you actually hold.",
            "यहाँ व्यवस्था चाहिए — एक नियम, एक समय-सारणी, एक सीमा जिस पर आप सचमुच टिके रहें।",
        ),
        (
            "Control applied where flexibility would work better, or a structure you never agreed to.",
            "जहाँ लचीलापन बेहतर था वहाँ नियंत्रण, या वह ढाँचा जिसके लिए आपने कभी हाँ नहीं कही।",
        ),
    ),
    _major(
        5, "hierophant",
        ("The Hierophant", "धर्मगुरु"),
        ("tradition, teaching, belonging", "परंपरा, शिक्षा, अपनापन"),
        (
            "The tried way, and someone who has walked it before you. Worth asking.",
            "आज़माया हुआ रास्ता, और कोई जो उस पर पहले चल चुका है। पूछ लेना ठीक रहेगा।",
        ),
        (
            "A rule followed because it is the rule, long after it stopped fitting you.",
            "नियम इसलिए निभाया जा रहा है कि वह नियम है, जबकि वह आप पर बैठना कब का बंद कर चुका।",
        ),
    ),
    _major(
        6, "lovers",
        ("The Lovers", "प्रेमी"),
        ("choice, values, meeting", "चुनाव, मूल्य, मेल"),
        (
            "A choice between two goods, settled by which one you actually want to be.",
            "दो अच्छी चीज़ों के बीच चुनाव, जो इस पर तय होगा कि आप असल में बनना क्या चाहते हैं।",
        ),
        (
            "Deciding by what is easier to explain to others rather than by what you mean.",
            "फ़ैसला इस आधार पर कि दूसरों को क्या समझाना आसान है, न कि इस पर कि आपका मन क्या कहता है।",
        ),
    ),
    _major(
        7, "chariot",
        ("The Chariot", "रथ"),
        ("drive, direction, holding course", "गति, दिशा, टिके रहना"),
        (
            "Momentum you have earned. Steering matters more than speed from here.",
            "गति आपने कमाई है। अब रफ़्तार से ज़्यादा दिशा मायने रखती है।",
        ),
        (
            "Pulling in two directions at once, so the effort shows and the distance does not.",
            "एक साथ दो दिशाओं में खिंचाव — मेहनत दिखती है, दूरी नहीं।",
        ),
    ),
    _major(
        8, "strength",
        ("Strength", "शक्ति"),
        ("patience, gentleness, nerve", "धैर्य, कोमलता, हिम्मत"),
        (
            "The kind of strength that stays calm instead of pushing harder.",
            "वह ताक़त जो और ज़ोर लगाने के बजाय शांत बनी रहती है।",
        ),
        (
            "Force where patience was needed, or patience worn thin and calling itself calm.",
            "जहाँ धैर्य चाहिए था वहाँ ज़ोर, या थका हुआ धैर्य जो ख़ुद को शांति कह रहा है।",
        ),
    ),
    _major(
        9, "hermit",
        ("The Hermit", "एकांतवासी"),
        ("solitude, reflection, your own counsel", "एकांत, चिंतन, अपनी सलाह"),
        (
            "Time alone with this, before it is discussed with anyone else.",
            "इस बात के साथ कुछ वक़्त अकेले, किसी और से चर्चा करने से पहले।",
        ),
        (
            "Solitude that has stopped being useful and become a place to hide.",
            "एकांत जो अब काम का नहीं रहा और छिपने की जगह बन गया है।",
        ),
    ),
    _major(
        10, "wheel",
        ("Wheel of Fortune", "भाग्यचक्र"),
        ("change, timing, what turns", "बदलाव, समय, जो घूमता है"),
        (
            "Circumstances are moving on their own. What you decide inside that movement is yours.",
            "हालात अपने आप बदल रहे हैं। उस बदलाव के भीतर जो आप तय करते हैं, वह आपका है।",
        ),
        (
            "Waiting for the turn instead of doing the part that does not depend on it.",
            "पलटने का इंतज़ार, बजाय उस हिस्से को करने के जो इस पलटने पर निर्भर ही नहीं।",
        ),
    ),
    _major(
        11, "justice",
        ("Justice", "न्याय"),
        ("fairness, consequence, clear sight", "निष्पक्षता, परिणाम, साफ़ नज़र"),
        (
            "Weigh it honestly, including the part that does not favour you.",
            "ईमानदारी से तौलिए — वह हिस्सा भी जो आपके पक्ष में नहीं है।",
        ),
        (
            "A version of the story kept in place because letting it go would cost something.",
            "कहानी का वह रूप जो इसलिए बना हुआ है कि उसे छोड़ने में कुछ खोना पड़ेगा।",
        ),
    ),
    _major(
        12, "hanged-man",
        ("The Hanged Man", "लटका हुआ मनुष्य"),
        ("pause, another angle, letting go of the controls", "ठहराव, दूसरा कोण, नियंत्रण छोड़ना"),
        (
            "Nothing moves for now, and the useful move is to look at it upside down.",
            "अभी कुछ नहीं हिलेगा; काम की बात यह है कि इसे उलटा करके देखा जाए।",
        ),
        (
            "A pause that has outlived its purpose and turned into stalling.",
            "ठहराव जिसका काम पूरा हो चुका और जो अब टालमटोल बन गया है।",
        ),
    ),
    _major(
        13, "death",
        ("Death", "मृत्यु"),
        ("ending, change, what you stop carrying", "अंत, बदलाव, जो अब नहीं ढोना"),
        (
            "Something is finished. Naming it as finished is what makes room for the next thing.",
            "कुछ पूरा हो चुका है। उसे पूरा हुआ मान लेना ही अगली चीज़ के लिए जगह बनाता है।",
        ),
        (
            "Holding on to something that has already ended, and paying the rent on it.",
            "उस चीज़ को पकड़े रहना जो ख़त्म हो चुकी है, और उसका किराया भरते रहना।",
        ),
    ),
    _major(
        14, "temperance",
        ("Temperance", "संतुलन"),
        ("balance, blending, the right dose", "संतुलन, मेल, सही मात्रा"),
        (
            "The middle setting. Neither all of it nor none of it — a mixture that can actually run.",
            "बीच का माप। न पूरा, न कुछ नहीं — एक ऐसा मिश्रण जो सचमुच चल सके।",
        ),
        (
            "Extremes taking turns, so nothing gets a chance to settle.",
            "बारी-बारी से दोनों छोर, इसलिए कुछ भी जम नहीं पाता।",
        ),
    ),
    _major(
        15, "devil",
        ("The Devil", "शैतान"),
        ("attachment, habit, what holds you", "लगाव, आदत, जो बाँधे है"),
        (
            "A habit or an arrangement that costs more than it admits. The chain is loose; look at it.",
            "कोई आदत या व्यवस्था जो जितना मानती है उससे ज़्यादा वसूलती है। ज़ंजीर ढीली है; उसे देखिए।",
        ),
        (
            "The first honest look at what it costs — which is where it starts to loosen.",
            "पहली बार ईमानदारी से यह देखना कि क़ीमत क्या है — यहीं से पकड़ ढीली होती है।",
        ),
    ),
    _major(
        16, "tower",
        ("The Tower", "मीनार"),
        ("sudden change, truth, what will not hold", "अचानक बदलाव, सच, जो टिकेगा नहीं"),
        (
            "Something built on a shaky footing gives way, and what is left standing is what was true.",
            "कमज़ोर नींव पर खड़ी चीज़ बैठ जाती है, और जो खड़ा रह जाता है वही सच था।",
        ),
        (
            "The crack is visible and is being patched rather than looked at.",
            "दरार दिख रही है और उसे देखने के बजाय ढका जा रहा है।",
        ),
    ),
    _major(
        17, "star",
        ("The Star", "तारा"),
        ("hope, repair, a clear night", "उम्मीद, मरम्मत, खुली रात"),
        (
            "The quiet after something hard, and the first honest reason to keep going.",
            "कठिन दौर के बाद की शांति, और आगे बढ़ते रहने की पहली सच्ची वजह।",
        ),
        (
            "Hope kept at arm's length, because believing it would mean risking it.",
            "उम्मीद दूर रखी हुई, क्योंकि उस पर भरोसा करने का मतलब है उसे दाँव पर लगाना।",
        ),
    ),
    _major(
        18, "moon",
        ("The Moon", "चंद्रमा"),
        ("uncertainty, imagination, half-light", "अनिश्चय, कल्पना, आधा उजाला"),
        (
            "Not everything here is what it looks like yet. Move slowly and check what is real.",
            "यहाँ सब कुछ अभी वैसा नहीं जैसा दिखता है। धीरे चलिए और जाँचिए कि असली क्या है।",
        ),
        (
            "The fog lifting, and the smaller, plainer truth underneath it.",
            "धुंध छँट रही है, और नीचे छोटा, सीधा सच निकल रहा है।",
        ),
    ),
    _major(
        19, "sun",
        ("The Sun", "सूर्य"),
        ("clarity, warmth, plain good", "स्पष्टता, गर्मी, सीधी भलाई"),
        (
            "Something straightforward and good, with nothing hidden in it. Let it be simple.",
            "कुछ सीधा और अच्छा, जिसमें कुछ छिपा नहीं है। इसे सरल ही रहने दीजिए।",
        ),
        (
            "Good news held at a distance by waiting for the catch.",
            "अच्छी ख़बर दूर रखी हुई है, इस इंतज़ार में कि कहीं कोई पेंच तो नहीं।",
        ),
    ),
    _major(
        20, "judgement",
        ("Judgement", "निर्णय"),
        ("reckoning, a call, honest review", "लेखा-जोखा, बुलावा, ईमानदार समीक्षा"),
        (
            "Looking back at the whole of it and deciding what you will do differently.",
            "पूरे मामले को पीछे मुड़कर देखना और यह तय करना कि अब क्या अलग करेंगे।",
        ),
        (
            "Rehearsing the verdict on yourself instead of acting on what you already concluded.",
            "अपने ही ऊपर फ़ैसला दोहराते रहना, जबकि जो समझ आ चुका उस पर काम करना बाक़ी है।",
        ),
    ),
    _major(
        21, "world",
        ("The World", "संसार"),
        ("completion, wholeness, a full circle", "पूर्णता, समग्रता, चक्र पूरा"),
        (
            "A chapter closes properly, and the next one starts from higher ground.",
            "एक अध्याय ठीक से बंद होता है, और अगला थोड़ी ऊँची ज़मीन से शुरू होता है।",
        ),
        (
            "Almost finished, and the last stretch is the one being avoided.",
            "लगभग पूरा, और आख़िरी हिस्सा ही वह है जिससे बचा जा रहा है।",
        ),
    ),
)


# --- Minor arcana -----------------------------------------------------------
#
# Names are composed rather than listed. Fifty-six names written out by hand is
# fifty-six chances for "तीन तलवारें" and "तलवारों की रानी" to disagree about how
# a suit is spelled, and the composition also carries the grammar a list cannot:
# Hindi inflects the suit for the oblique case and the particle for the rank's
# gender, so रानी takes की where राजा takes का.


@dataclass(frozen=True, slots=True)
class Suit:
    id: str
    name: Text
    #: What the suit is about, for the header above a card rather than for the
    #: reading itself.
    theme: Text
    #: Hindi plural ("तीन तलवारें") and oblique ("तलवारों की रानी").
    hi_plural: str
    hi_oblique: str


SUITS: tuple[Suit, ...] = (
    Suit(
        id="wands",
        name={"en": "Wands", "hi": "छड़ियाँ"},
        theme={"en": "drive, work, what you start", "hi": "ऊर्जा, काम, जो आप शुरू करते हैं"},
        hi_plural="छड़ियाँ",
        hi_oblique="छड़ियों",
    ),
    Suit(
        id="cups",
        name={"en": "Cups", "hi": "प्याले"},
        theme={"en": "feeling, closeness, what you care about", "hi": "भावना, नज़दीकी, जो आपको प्रिय है"},
        hi_plural="प्याले",
        hi_oblique="प्यालों",
    ),
    Suit(
        id="swords",
        name={"en": "Swords", "hi": "तलवारें"},
        theme={"en": "thought, speech, the truth of it", "hi": "विचार, वाणी, बात का सच"},
        hi_plural="तलवारें",
        hi_oblique="तलवारों",
    ),
    Suit(
        id="pentacles",
        name={"en": "Pentacles", "hi": "सिक्के"},
        theme={"en": "money, body, patient work", "hi": "पैसा, शरीर, धैर्य का काम"},
        hi_plural="सिक्के",
        hi_oblique="सिक्कों",
    ),
)

SUITS_BY_ID = {suit.id: suit for suit in SUITS}

_RANK_SLUG = (
    "ace", "two", "three", "four", "five", "six", "seven",
    "eight", "nine", "ten", "page", "knight", "queen", "king",
)

_RANK_EN = (
    "Ace", "Two", "Three", "Four", "Five", "Six", "Seven",
    "Eight", "Nine", "Ten", "Page", "Knight", "Queen", "King",
)

_NUMBER_HI = ("दो", "तीन", "चार", "पाँच", "छह", "सात", "आठ", "नौ", "दस")

#: The court, and the particle each one takes. रानी is feminine; the other three
#: are masculine, and Hindi will not let that be ignored.
_COURT_HI = {11: ("शिष्य", "का"), 12: ("अश्वारोही", "का"), 13: ("रानी", "की"), 14: ("राजा", "का")}


def _minor_name(suit: Suit, number: int) -> Text:
    english = f"{_RANK_EN[number - 1]} of {suit.name['en']}"

    if number == 1:
        hindi = f"{suit.hi_oblique} का इक्का"
    elif number <= 10:
        hindi = f"{_NUMBER_HI[number - 2]} {suit.hi_plural}"
    else:
        rank, particle = _COURT_HI[number]
        hindi = f"{suit.hi_oblique} {particle} {rank}"

    return {"en": english, "hi": hindi}


def _minor(
    suit_id: str,
    number: int,
    keywords: tuple[str, str],
    upright: tuple[str, str],
    reversed_: tuple[str, str],
) -> Card:
    suit = SUITS_BY_ID[suit_id]
    return Card(
        id=f"{suit_id}-{_RANK_SLUG[number - 1]}",
        arcana="minor",
        suit=suit_id,
        number=number,
        name=_minor_name(suit, number),
        keywords={"en": keywords[0], "hi": keywords[1]},
        upright={"en": upright[0], "hi": upright[1]},
        reversed={"en": reversed_[0], "hi": reversed_[1]},
    )


WANDS: tuple[Card, ...] = (
    _minor(
        "wands", 1,
        ("spark, an offer, new drive", "चिंगारी, प्रस्ताव, नई ऊर्जा"),
        (
            "A new thing worth starting, while the wanting is still fresh.",
            "कुछ नया शुरू करने लायक़, जब तक चाह ताज़ा है।",
        ),
        (
            "The spark is there and the first move keeps getting postponed.",
            "चिंगारी है, पर पहला क़दम टलता जा रहा है।",
        ),
    ),
    _minor(
        "wands", 2,
        ("planning, a direction, scope", "योजना, दिशा, दायरा"),
        (
            "The idea is real; now it needs a direction chosen and a date on it.",
            "विचार असली है; अब उसे एक दिशा और एक तारीख़ चाहिए।",
        ),
        (
            "Planning as a way of staying safely before the start line.",
            "योजना बनाना, ताकि शुरुआत की रेखा से पहले सुरक्षित खड़े रहा जा सके।",
        ),
    ),
    _minor(
        "wands", 3,
        ("progress, waiting on returns, a wider view", "प्रगति, प्रतिफल की प्रतीक्षा, चौड़ी नज़र"),
        (
            "The first work has gone out; this is the stretch where you watch and prepare.",
            "पहला काम निकल चुका है; यह वह दौर है जब आप देखते और तैयारी करते हैं।",
        ),
        (
            "Checking on it too often, which costs more than the waiting does.",
            "बार-बार जाँचना, जो इंतज़ार से ज़्यादा थका देता है।",
        ),
    ),
    _minor(
        "wands", 4,
        ("a milestone, home, rest earned", "पड़ाव, घर, कमाया हुआ आराम"),
        (
            "A milestone worth stopping at. Mark it before starting the next thing.",
            "रुकने लायक़ एक पड़ाव। अगली चीज़ शुरू करने से पहले इसे मनाइए।",
        ),
        (
            "Moving straight on to the next task, so nothing ever counts as done.",
            "सीधे अगले काम पर, इसलिए कुछ भी कभी पूरा नहीं गिना जाता।",
        ),
    ),
    _minor(
        "wands", 5,
        ("friction, competition, many voices", "रगड़, प्रतिस्पर्धा, कई आवाज़ें"),
        (
            "Everyone wants a slightly different thing, and it is noisy rather than serious.",
            "हर कोई थोड़ा अलग चाहता है — यह शोर है, गंभीर टकराव नहीं।",
        ),
        (
            "The argument dropped rather than settled, and it will come back.",
            "बहस सुलझी नहीं, छोड़ दी गई — और वह लौटेगी।",
        ),
    ),
    _minor(
        "wands", 6,
        ("recognition, a win, being seen", "पहचान, जीत, दिखना"),
        (
            "Something you did is noticed. Take the credit plainly.",
            "आपका किया हुआ काम दिखा है। श्रेय सीधे तरीक़े से ले लीजिए।",
        ),
        (
            "Waiting for the applause before believing the work was any good.",
            "काम को अच्छा मानने से पहले तालियों का इंतज़ार।",
        ),
    ),
    _minor(
        "wands", 7,
        ("holding your ground, standing firm", "अपनी जगह बचाना, डटे रहना"),
        (
            "Holding a position you have reason to hold, against pressure to fold.",
            "उस बात पर डटे रहना जिसके लिए आपके पास वजह है, झुकने के दबाव के बावजूद।",
        ),
        (
            "Defending something you no longer believe, out of the effort already spent on it.",
            "उस बात की रक्षा जिस पर अब यक़ीन नहीं, सिर्फ़ पहले लगाई मेहनत की वजह से।",
        ),
    ),
    _minor(
        "wands", 8,
        ("speed, news, things at once", "रफ़्तार, ख़बर, एक साथ चलती चीज़ें"),
        (
            "Things move quickly now. Answer the ones that matter and let the rest wait.",
            "अब चीज़ें तेज़ चलेंगी। जो ज़रूरी है उसका जवाब दीजिए, बाक़ी रुक सकता है।",
        ),
        (
            "Everything arriving at once and none of it in any order.",
            "सब एक साथ आ रहा है, और कुछ भी क्रम में नहीं।",
        ),
    ),
    _minor(
        "wands", 9,
        ("tiredness, guard up, nearly there", "थकान, सतर्कता, लगभग पहुँचे"),
        (
            "Tired and still standing, and closer to the end than it feels.",
            "थके हुए, फिर भी खड़े — और अंत जितना लगता है उससे पास है।",
        ),
        (
            "Guarding against a threat that has already passed.",
            "उस ख़तरे से बचाव जो बीत चुका है।",
        ),
    ),
    _minor(
        "wands", 10,
        ("overload, carrying too much", "बोझ, बहुत कुछ ढोना"),
        (
            "More is being carried than one person should. Some of it belongs to someone else.",
            "एक व्यक्ति के हिस्से से ज़्यादा ढोया जा रहा है। इसमें कुछ किसी और का है।",
        ),
        (
            "Putting one thing down, and finding that nothing collapses.",
            "एक चीज़ नीचे रखकर देखना — और पाना कि कुछ भी नहीं गिरा।",
        ),
    ),
    _minor(
        "wands", 11,
        ("curiosity, a first attempt, learning", "जिज्ञासा, पहला प्रयास, सीखना"),
        (
            "Beginner's energy — the freedom of not being good at it yet.",
            "नौसिखिए की ऊर्जा — अभी अच्छा न होने की आज़ादी।",
        ),
        (
            "Enthusiasm that has not yet met the boring middle of the work.",
            "उत्साह जो अभी काम के उबाऊ बीच तक नहीं पहुँचा।",
        ),
    ),
    _minor(
        "wands", 12,
        ("bold action, haste, going after it", "साहसी क़दम, जल्दबाज़ी, पीछे लगना"),
        (
            "Move now and adjust while moving; waiting will not improve this one.",
            "अभी चलिए और चलते-चलते सुधारिए; इंतज़ार से यह बेहतर नहीं होगा।",
        ),
        (
            "Speed without a direction, which is only motion.",
            "बिना दिशा की रफ़्तार, जो सिर्फ़ हलचल है।",
        ),
    ),
    _minor(
        "wands", 13,
        ("warmth, confidence, drawing people in", "गर्मजोशी, आत्मविश्वास, लोगों को जोड़ना"),
        (
            "Clear about what you want and warm about it, which is why people come along.",
            "अपनी चाह को लेकर स्पष्ट और गर्मजोश — यही वजह है कि लोग साथ आते हैं।",
        ),
        (
            "Certainty performed outward while the doubt stays private.",
            "बाहर आत्मविश्वास, और संदेह भीतर ही रखा हुआ।",
        ),
    ),
    _minor(
        "wands", 14,
        ("leadership, vision, seeing it through", "नेतृत्व, दृष्टि, अंत तक ले जाना"),
        (
            "Someone has to decide and then carry it. That role is available to you here.",
            "किसी को तय करके उसे निभाना होगा। यहाँ वह भूमिका आपके पास है।",
        ),
        (
            "Deciding for other people where they needed to be asked.",
            "दूसरों के लिए फ़ैसला, जहाँ उनसे पूछना ज़रूरी था।",
        ),
    ),
)


CUPS: tuple[Card, ...] = (
    _minor(
        "cups", 1,
        ("a feeling opening, an offer of closeness", "भावना का खुलना, नज़दीकी का प्रस्ताव"),
        (
            "A feeling arriving, or an offer of closeness. It asks only to be accepted.",
            "कोई भावना आ रही है, या नज़दीकी का प्रस्ताव। बस स्वीकार किए जाने की माँग है।",
        ),
        (
            "Feeling something and keeping it unsaid until the moment passes.",
            "महसूस करना और अनकहा रखना, जब तक वह पल निकल न जाए।",
        ),
    ),
    _minor(
        "cups", 2,
        ("mutual regard, a pair, agreement", "परस्पर आदर, जोड़ा, सहमति"),
        (
            "Two people meeting each other honestly, which is rarer than it sounds.",
            "दो लोग एक-दूसरे से ईमानदारी से मिलते हुए — जो सुनने में जितना आम लगता है, है नहीं।",
        ),
        (
            "One side doing most of the reaching.",
            "एक ही तरफ़ से ज़्यादातर हाथ बढ़ रहा है।",
        ),
    ),
    _minor(
        "cups", 3,
        ("friendship, celebration, company", "दोस्ती, जश्न, साथ"),
        (
            "The people who are glad for you. Let them be, and tell them so.",
            "वे लोग जो आपके लिए ख़ुश हैं। उन्हें रहने दीजिए, और कह भी दीजिए।",
        ),
        (
            "Company without closeness — a full room and nobody to say it to.",
            "साथ तो है पर नज़दीकी नहीं — भरा कमरा, और कहने को कोई नहीं।",
        ),
    ),
    _minor(
        "cups", 4,
        ("discontent, looking away, an unnoticed offer", "असंतोष, नज़र फेरना, अनदेखा प्रस्ताव"),
        (
            "Something is on offer and is being looked past — out of boredom rather than dislike.",
            "कुछ सामने रखा है और उसे अनदेखा किया जा रहा है — नापसंदगी से नहीं, ऊब से।",
        ),
        (
            "Interest returning, and the offer still being there.",
            "दिलचस्पी लौट रही है, और प्रस्ताव अब भी क़ायम है।",
        ),
    ),
    _minor(
        "cups", 5,
        ("loss, grief, what remains", "हानि, दुख, जो बचा है"),
        (
            "Grief for what did not work, with the part that survived still standing behind you.",
            "जो नहीं चला उसका दुख — और जो बचा है वह अब भी पीछे खड़ा है।",
        ),
        (
            "Turning around to count what is left.",
            "मुड़कर यह गिनना कि बचा क्या है।",
        ),
    ),
    _minor(
        "cups", 6,
        ("memory, kindness, the past", "स्मृति, नेकी, बीता हुआ"),
        (
            "Something from earlier comes back gently — a person, a place, an old kindness.",
            "पहले का कुछ धीरे से लौटता है — कोई व्यक्ति, कोई जगह, कोई पुरानी नेकी।",
        ),
        (
            "Living in a version of the past that memory has quietly edited.",
            "बीते हुए के उस रूप में रहना जिसे याद ने चुपचाप सुधार दिया है।",
        ),
    ),
    _minor(
        "cups", 7,
        ("options, imagination, too many wants", "विकल्प, कल्पना, बहुत सी चाहतें"),
        (
            "Many possibilities, most of them still pictures. Ask which one you would actually do.",
            "कई संभावनाएँ, जिनमें ज़्यादातर अभी तस्वीरें हैं। पूछिए कि आप असल में करेंगे कौन सी।",
        ),
        (
            "Choosing one, which is what makes the rest lose their pull.",
            "एक को चुन लेना — यही बाक़ी का खिंचाव ख़त्म करता है।",
        ),
    ),
    _minor(
        "cups", 8,
        ("walking away, looking for something truer", "छोड़कर चलना, कुछ सच्चा खोजना"),
        (
            "Leaving something that was fine, because fine is not what you came for.",
            "उस चीज़ को छोड़ना जो ठीक थी, क्योंकि आप 'ठीक' के लिए नहीं आए थे।",
        ),
        (
            "Half-leaving: gone in feeling, still present in fact.",
            "आधा जाना: मन से निकल चुके, हक़ीक़त में अब भी वहीं।",
        ),
    ),
    _minor(
        "cups", 9,
        ("contentment, a wish met", "संतोष, पूरी हुई चाह"),
        (
            "Something wanted for a long time is actually here. Notice it before wanting the next.",
            "जो देर से चाहा था वह सचमुच यहाँ है। अगली चाह से पहले इसे देख तो लीजिए।",
        ),
        (
            "Getting it, and finding that the wanting was the part you liked.",
            "मिल जाने पर यह पाना कि मज़ा चाहने में था।",
        ),
    ),
    _minor(
        "cups", 10,
        ("belonging, peace at home", "अपनापन, घर की शांति"),
        (
            "The ordinary version of happiness — people, routine, nothing dramatic about it.",
            "ख़ुशी का साधारण रूप — लोग, रोज़मर्रा, कुछ भी नाटकीय नहीं।",
        ),
        (
            "Measuring your own home against a picture of somebody else's.",
            "अपने घर को किसी और के घर की तस्वीर से नापना।",
        ),
    ),
    _minor(
        "cups", 11,
        ("tenderness, a message, a first feeling", "कोमलता, संदेश, पहली भावना"),
        (
            "A soft, unpractised feeling, or a message you were not expecting.",
            "एक कोमल, अनगढ़ भावना, या कोई संदेश जिसकी उम्मीद नहीं थी।",
        ),
        (
            "Feeling it and treating it as too small to mention.",
            "महसूस करना, और उसे कहने लायक़ न समझना।",
        ),
    ),
    _minor(
        "cups", 12,
        ("romance, an approach, following the heart", "प्रेम, पहल, दिल के पीछे"),
        (
            "Someone makes a move, or you do. It is sincere and a little theatrical.",
            "कोई पहल करता है, या आप करते हैं। यह सच्चा है और थोड़ा नाटकीय भी।",
        ),
        (
            "The gesture is beautiful and the following through is missing.",
            "इशारा सुंदर है, निभाना ग़ायब।",
        ),
    ),
    _minor(
        "cups", 13,
        ("empathy, holding others, deep feeling", "सहानुभूति, दूसरों को सँभालना, गहरी भावना"),
        (
            "The person others come to. Being that is a skill, and it uses you up.",
            "वह व्यक्ति जिसके पास लोग आते हैं। यह भी एक हुनर है, और यह ख़र्च कराता है।",
        ),
        (
            "Absorbing everyone's weather until you cannot find your own.",
            "सबका मौसम अपने भीतर ले लेना, यहाँ तक कि अपना मौसम मिलता ही नहीं।",
        ),
    ),
    _minor(
        "cups", 14,
        ("steadiness in feeling, calm care", "भावना में स्थिरता, शांत देखभाल"),
        (
            "Feeling deeply and staying steady — the two together, which is the hard part.",
            "गहराई से महसूस करना और स्थिर रहना — दोनों साथ, यही कठिन हिस्सा है।",
        ),
        (
            "Calm on the surface with nothing said, which is not the same as steady.",
            "ऊपर से शांति और भीतर कुछ कहा नहीं गया — यह स्थिरता नहीं है।",
        ),
    ),
)


# Swords are the suit a fear-selling deck would make the most of — Three, Nine
# and Ten are the three cards people are shown to frighten them. They are
# written here as what they actually are: a true thing said that hurt, a mind
# loud at night, and the bottom of something. Each one names the way out, and
# none of them predicts harm.
SWORDS: tuple[Card, ...] = (
    _minor(
        "swords", 1,
        ("clarity, a decision, cutting through", "स्पष्टता, निर्णय, काटकर आगे"),
        (
            "The thought that makes the rest fall into place. Write it down before it goes.",
            "वह विचार जिससे बाक़ी सब अपनी जगह बैठ जाता है। भूलने से पहले लिख लीजिए।",
        ),
        (
            "Clarity used as a weapon rather than as a way through.",
            "स्पष्टता को रास्ते की तरह नहीं, हथियार की तरह इस्तेमाल करना।",
        ),
    ),
    _minor(
        "swords", 2,
        ("stalemate, a choice avoided, a blindfold", "गतिरोध, टाला हुआ चुनाव, आँख पर पट्टी"),
        (
            "Two options, and a decision being kept at arm's length. You have enough to decide.",
            "दो रास्ते, और फ़ैसला दूर रखा हुआ। तय करने भर की जानकारी आपके पास है।",
        ),
        (
            "The blindfold coming off, and the choice turning out smaller than feared.",
            "पट्टी हटती है, और चुनाव डर से छोटा निकलता है।",
        ),
    ),
    _minor(
        "swords", 3,
        ("hurt, a plain truth, heartache", "चोट, सीधा सच, दिल का दर्द"),
        (
            "Something true and painful was said. The pain is honest, and it does pass.",
            "कुछ सच और तकलीफ़देह कहा गया। यह दर्द सच्चा है, और यह गुज़र भी जाता है।",
        ),
        (
            "Going over the same sentence again, which is what keeps the cut open.",
            "उसी वाक्य को बार-बार दोहराना, जो घाव को खुला रखता है।",
        ),
    ),
    _minor(
        "swords", 4,
        ("rest, recovery, stepping back", "विश्राम, उबरना, पीछे हटना"),
        (
            "Stop. Not giving up — the pause that makes the next attempt possible.",
            "रुकिए। हार नहीं — वह ठहराव जो अगली कोशिश को संभव बनाता है।",
        ),
        (
            "Rest deferred until the body takes it without asking.",
            "आराम तब तक टाला गया जब तक शरीर ने बिना पूछे उसे ले नहीं लिया।",
        ),
    ),
    _minor(
        "swords", 5,
        ("winning badly, the cost of being right", "बुरी जीत, सही साबित होने का ख़र्च"),
        (
            "A win that costs more than losing would have. Ask whether being right is the goal.",
            "ऐसी जीत जो हारने से महँगी है। पूछिए कि लक्ष्य सही साबित होना ही है क्या।",
        ),
        (
            "Putting the argument down first, which is not the same as conceding it.",
            "बहस पहले छोड़ देना — यह हार मान लेना नहीं है।",
        ),
    ),
    _minor(
        "swords", 6,
        ("moving on, a calmer crossing", "आगे बढ़ना, शांत पार होना"),
        (
            "Leaving rough water for quieter, carrying only what is needed.",
            "उथल-पुथल से शांत पानी की ओर, सिर्फ़ ज़रूरी सामान के साथ।",
        ),
        (
            "Making the crossing while still arguing with the shore behind you.",
            "पार होते हुए भी पीछे छूटे किनारे से बहस जारी।",
        ),
    ),
    _minor(
        "swords", 7,
        ("strategy, going alone, half-truths", "रणनीति, अकेले चलना, आधे सच"),
        (
            "Handling it quietly and alone. Check that quiet is not standing in for dishonest.",
            "इसे चुपचाप और अकेले सँभालना। जाँच लीजिए कि यह चुप्पी बेईमानी की जगह न ले रही हो।",
        ),
        (
            "The unsaid thing is about to be said, and it is better said by you.",
            "जो अनकहा है वह कहा जाने वाला है — और बेहतर है कि आप ही कहें।",
        ),
    ),
    _minor(
        "swords", 8,
        ("feeling stuck, a limit of your own making", "फँसा हुआ महसूस करना, अपनी बनाई सीमा"),
        (
            "It feels closed in, and part of the wall was built from the inside.",
            "लगता है रास्ता बंद है — और दीवार का कुछ हिस्सा भीतर से बना है।",
        ),
        (
            "Testing one wall, and finding it was a curtain.",
            "एक दीवार को छूकर देखना, और पाना कि वह परदा थी।",
        ),
    ),
    _minor(
        "swords", 9,
        ("worry, a sleepless night, the mind after dark", "चिंता, नींद न आना, रात का मन"),
        (
            "The worry is loudest at night and smaller in daylight. Say it out loud to someone.",
            "चिंता रात में सबसे ऊँची होती है और दिन में छोटी। इसे किसी से कह दीजिए।",
        ),
        (
            "Saying it out loud, which is where it stops growing.",
            "इसे ज़ुबान पर लाना — यहीं वह बढ़ना बंद करती है।",
        ),
    ),
    _minor(
        "swords", 10,
        ("an ending, the worst of it done", "अंत, सबसे बुरा बीत चुका"),
        (
            "This is the bottom of it, which means the direction from here is upward.",
            "यह सबसे निचला बिंदु है — यानी यहाँ से दिशा ऊपर की है।",
        ),
        (
            "Getting up slowly, and it does not have to look graceful.",
            "धीरे-धीरे उठना — और इसका सुंदर दिखना ज़रूरी नहीं।",
        ),
    ),
    _minor(
        "swords", 11,
        ("questions, watching, learning fast", "सवाल, निगरानी, तेज़ी से सीखना"),
        (
            "Ask the question directly. Curiosity is doing more work here than caution.",
            "सवाल सीधे पूछिए। यहाँ सतर्कता से ज़्यादा काम जिज्ञासा कर रही है।",
        ),
        (
            "Watching everyone closely and calling that understanding them.",
            "सबको ग़ौर से देखना और उसे समझ लेना मान लेना।",
        ),
    ),
    _minor(
        "swords", 12,
        ("directness, urgency, saying it", "सीधापन, तेज़ी, कह देना"),
        (
            "Straight at it, in plain words. Fast, and not always kind.",
            "सीधे, साफ़ शब्दों में। तेज़ — और हमेशा नरम नहीं।",
        ),
        (
            "Speed that leaves people behind, including the ones you needed.",
            "इतनी तेज़ी कि लोग पीछे छूट जाएँ, वे भी जिनकी ज़रूरत थी।",
        ),
    ),
    _minor(
        "swords", 13,
        ("clear sight, honest counsel, boundaries", "साफ़ नज़र, खरी सलाह, सीमाएँ"),
        (
            "Sees it accurately and says it without decoration. Find someone like that, or be them.",
            "जो है वैसा ही देखती है और बिना सजावट कह देती है। ऐसा कोई खोजिए, या ख़ुद बनिए।",
        ),
        (
            "Accuracy sharpened until it became distance.",
            "सटीकता इतनी तेज़ हुई कि वह दूरी बन गई।",
        ),
    ),
    _minor(
        "swords", 14,
        ("judgement, principle, deciding by reason", "विवेक, सिद्धांत, तर्क से तय करना"),
        (
            "Decide by the rule you would apply to anyone — including someone you dislike.",
            "उस नियम से तय कीजिए जो आप किसी पर भी लागू करते — उस पर भी जो पसंद न हो।",
        ),
        (
            "Principle used to avoid the harder, more human answer.",
            "सिद्धांत का इस्तेमाल उस कठिन, ज़्यादा इंसानी जवाब से बचने के लिए।",
        ),
    ),
)


PENTACLES: tuple[Card, ...] = (
    _minor(
        "pentacles", 1,
        ("an offer, a beginning with substance", "प्रस्ताव, ठोस शुरुआत"),
        (
            "Something solid on the table — work, money, a place. Small, and real.",
            "कुछ ठोस सामने है — काम, पैसा, कोई जगह। छोटा, पर असली।",
        ),
        (
            "An opportunity kept as an idea rather than acted on.",
            "अवसर को विचार बनाए रखना, उस पर काम न करना।",
        ),
    ),
    _minor(
        "pentacles", 2,
        ("juggling, balance, what comes in and goes out", "संतुलन साधना, आमद और ख़र्च"),
        (
            "Two demands, and enough for both if the timing is handled.",
            "दो माँगें, और दोनों के लिए काफ़ी — बशर्ते समय सँभाल लिया जाए।",
        ),
        (
            "One more thing added to a load that was already at its limit.",
            "पहले से भरे बोझ पर एक और चीज़।",
        ),
    ),
    _minor(
        "pentacles", 3,
        ("craft, working with others, being taught", "कारीगरी, मिलकर काम, सीखना"),
        (
            "The work gets better with other people in it. Show it before it is finished.",
            "दूसरों के शामिल होने से काम बेहतर होता है। पूरा होने से पहले दिखाइए।",
        ),
        (
            "Doing all of it alone to avoid being corrected.",
            "सब कुछ अकेले करना, ताकि कोई सुधार न सके।",
        ),
    ),
    _minor(
        "pentacles", 4,
        ("holding on, security, saving", "पकड़े रहना, सुरक्षा, बचत"),
        (
            "Keeping hold of what you have — sensible, up to the point where it becomes a grip.",
            "जो है उसे सँभालकर रखना — समझदारी, उस बिंदु तक जब तक वह जकड़ न बन जाए।",
        ),
        (
            "Loosening the hold, and finding you were safer than you thought.",
            "पकड़ ढीली करना, और यह पाना कि आप सोच से ज़्यादा सुरक्षित थे।",
        ),
    ),
    _minor(
        "pentacles", 5,
        ("a thin stretch, feeling outside, help nearby", "तंगी, बाहर होने का एहसास, पास ही मदद"),
        (
            "A thin stretch. Help is closer than it feels, and asking is the whole difficulty.",
            "तंगी का दौर। मदद जितनी लगती है उससे पास है, और पूछना ही पूरी मुश्किल है।",
        ),
        (
            "Asking, and the answer turning out ordinary and kind.",
            "पूछ लेना — और जवाब का साधारण और नेक निकलना।",
        ),
    ),
    _minor(
        "pentacles", 6,
        ("giving and receiving, a fair exchange", "देना और लेना, बराबर का लेन-देन"),
        (
            "Something passes between you and someone else. Watch that it can pass both ways.",
            "आपके और किसी के बीच कुछ आता-जाता है। ध्यान रहे कि यह दोनों तरफ़ चल सके।",
        ),
        (
            "Generosity that quietly keeps a ledger.",
            "उदारता जो चुपचाप हिसाब रखती है।",
        ),
    ),
    _minor(
        "pentacles", 7,
        ("patience, work not yet ripe, review", "धैर्य, काम का पकना, समीक्षा"),
        (
            "Planted and not yet ripe. This is the season for tending, not for harvesting.",
            "बोया जा चुका, पका नहीं। यह मौसम देखभाल का है, कटाई का नहीं।",
        ),
        (
            "Pulling it up to check the roots.",
            "जड़ें देखने के लिए पौधे को उखाड़ लेना।",
        ),
    ),
    _minor(
        "pentacles", 8,
        ("practice, repetition, getting good", "अभ्यास, दोहराव, माहिर होना"),
        (
            "Ordinary repetition is what turns into skill. Nothing clever is required today.",
            "साधारण दोहराव ही हुनर बनता है। आज किसी चतुराई की ज़रूरत नहीं।",
        ),
        (
            "Repetition without attention, which teaches nothing.",
            "बिना ध्यान का दोहराव, जो कुछ नहीं सिखाता।",
        ),
    ),
    _minor(
        "pentacles", 9,
        ("self-reliance, comfort you earned", "आत्मनिर्भरता, कमाया हुआ सुख"),
        (
            "Something you built yourself, enjoyed on your own terms.",
            "जो आपने ख़ुद खड़ा किया, और अपनी शर्तों पर भोग रहे हैं।",
        ),
        (
            "Independence held so tightly that company starts to look like debt.",
            "आत्मनिर्भरता इतनी कसकर पकड़ी कि साथ भी क़र्ज़ जैसा लगने लगे।",
        ),
    ),
    _minor(
        "pentacles", 10,
        ("family, the long term, what lasts", "परिवार, लंबी अवधि, जो रह जाता है"),
        (
            "The long view — what will still be standing after you, and who it is for.",
            "लंबी नज़र — आपके बाद भी जो खड़ा रहेगा, और वह किसके लिए है।",
        ),
        (
            "Inheriting an arrangement that nobody inside it chose.",
            "वह व्यवस्था विरासत में मिलना जिसे उसमें रहने वाले किसी ने चुना नहीं।",
        ),
    ),
    _minor(
        "pentacles", 11,
        ("study, a new venture, a first earning", "पढ़ाई, नया काम, पहली कमाई"),
        (
            "The beginning of something practical — a course, a job, a small first sum.",
            "किसी व्यावहारिक चीज़ की शुरुआत — कोई कोर्स, कोई नौकरी, पहली छोटी कमाई।",
        ),
        (
            "Studying the thing as a way of not yet doing it.",
            "उस चीज़ को पढ़ते रहना, ताकि उसे करना अभी न पड़े।",
        ),
    ),
    _minor(
        "pentacles", 12,
        ("steadiness, routine, slow reliable work", "स्थिरता, नियम, धीमा भरोसेमंद काम"),
        (
            "Unspectacular and dependable. This is the pace that actually finishes things.",
            "बिना चमक, भरोसे लायक़। असल में चीज़ें इसी रफ़्तार से पूरी होती हैं।",
        ),
        (
            "A routine that has stopped going anywhere.",
            "वह नियम जो अब कहीं नहीं ले जा रहा।",
        ),
    ),
    _minor(
        "pentacles", 13,
        ("practical care, resourcefulness", "व्यावहारिक देखभाल, साधन जुटाना"),
        (
            "Care shown as arrangements rather than as words — food, money, a lift, a room.",
            "देखभाल शब्दों में नहीं, इंतज़ाम में — खाना, पैसा, सवारी, एक कमरा।",
        ),
        (
            "Managing everyone's needs and skipping your own turn in the queue.",
            "सबकी ज़रूरतें सँभालना और अपनी बारी छोड़ देना।",
        ),
    ),
    _minor(
        "pentacles", 14,
        ("provision, stability, building", "प्रबंध, स्थिरता, खड़ा करना"),
        (
            "Built slowly, and it holds. There is enough here to be generous with.",
            "धीरे-धीरे बना, और टिका हुआ। यहाँ इतना है कि उदार हुआ जा सके।",
        ),
        (
            "Security counted so often that it stops feeling like security.",
            "सुरक्षा इतनी बार गिनी गई कि वह सुरक्षा लगनी ही बंद हो गई।",
        ),
    ),
)


# --- The deck ---------------------------------------------------------------

CARDS: tuple[Card, ...] = MAJOR + WANDS + CUPS + SWORDS + PENTACLES

CARDS_BY_ID: dict[str, Card] = {card.id: card for card in CARDS}

#: Seventy-eight, asserted at import rather than trusted. A card lost to a
#: copy-paste would not raise anything — it would quietly change every draw.
assert len(CARDS) == 78, f"the deck has {len(CARDS)} cards"
assert len(CARDS_BY_ID) == 78, "two cards share an id"
