"""What the tradition associates with a dasha lord, written by a person.

Deliberately outside `astro/`. The engine computes and does not interpret — its
own modules say so — and this is interpretation: nine themes, each a claim about
meaning rather than a measurement. Keeping it here draws that line where a
reader can see it.

Equally deliberately outside `ai/`. Nothing here is generated, so nothing here
can hallucinate, cost a request, or come back different tomorrow. A dasha lord's
theme does not vary by reader, and asking a model to restate it every time would
buy nothing and risk something.

House style, the same as the course's:

- **Themes, not forecasts.** A period is a subject that keeps coming up, not a
  verdict on how it turns out.
- **No ranking.** No lord is lucky or unlucky, strong or weak, good or bad.
  Saturn is not a punishment and Jupiter is not a reward.
- **Something in their hands.** Each line names what the period asks of the
  person, because that is the half they can actually do something about.
"""

from __future__ import annotations

Text = dict[str, str]

DASHA_MEANINGS: dict[str, Text] = {
    "Sun": {
        "en": "Visibility and authority. Work that carries your own name on it.",
        "hi": "प्रकट होना और अधिकार। वह काम जिस पर आपका अपना नाम हो।",
    },
    "Moon": {
        "en": "Mind, mood and home. What you tend to, and who tends to you.",
        "hi": "मन, भाव और घर। जिसकी आप देखभाल करते हैं, और जो आपकी करता है।",
    },
    "Mars": {
        "en": "Drive and nerve. Starting things, and standing your ground.",
        "hi": "ऊर्जा और साहस। काम शुरू करना, और अपनी बात पर टिके रहना।",
    },
    "Mercury": {
        "en": "Communication and learning. Talking, writing, trading, figuring out.",
        "hi": "संवाद और सीखना। बोलना, लिखना, लेन-देन, समझ बनाना।",
    },
    "Jupiter": {
        "en": "Growth and meaning. Teaching, being taught, deciding what matters.",
        "hi": "विस्तार और अर्थ। सिखाना, सीखना, यह तय करना कि ज़रूरी क्या है।",
    },
    "Venus": {
        "en": "Relationship and craft. Comfort, beauty, and who you share it with.",
        "hi": "संबंध और कला। सुख, सौंदर्य, और वह जिसके साथ आप उसे बाँटते हैं।",
    },
    "Saturn": {
        "en": "Endurance and structure. Slow work that only time can finish.",
        "hi": "धैर्य और व्यवस्था। धीमा काम, जिसे सिर्फ़ समय पूरा कर सकता है।",
    },
    "Rahu": {
        "en": "Appetite and the unfamiliar. Wanting more, and where that takes you.",
        "hi": "आकांक्षा और अनजाना। और चाहना, और वह चाह आपको कहाँ ले जाती है।",
    },
    "Ketu": {
        "en": "Detachment and depth. Letting go of what you no longer need to hold.",
        "hi": "विरक्ति और गहराई। उसे छोड़ना जिसे अब पकड़े रखने की ज़रूरत नहीं।",
    },
}


def dasha_meaning(lord: str, language: str) -> str | None:
    """The theme of a dasha lord, or None for a lord we have not written."""
    text = DASHA_MEANINGS.get(lord)
    if text is None:
        return None
    return text.get(language) or text["en"]
