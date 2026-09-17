import re

with open("README.md", "r") as f:
    content = f.read()

# Line 26: | Astrology engine (ephemeris, chart, dasha, panchang) | Built, 216 tests passing |
content = re.sub(r'Built, \d+ tests passing', 'Built, 69 tests passing', content)

# Line 31: 36 tests -> 37 tests
content = re.sub(r'Pro\. \d+ tests', 'Pro. 37 tests', content)

# Line 51: tests/          251 tests, including known-chart, grounding, cache, entitlement and tarot
content = re.sub(r'tests/\s+\d+ tests', 'tests/          237 tests', content)

# Line 74: ./.venv/bin/python -m pytest          # 153 tests
content = re.sub(r'python -m pytest\s+# \d+ tests', 'python -m pytest          # 237 tests', content)

# Line 798: **250+ automated tests passing.**
content = re.sub(r'\*\*\d+\+ automated tests passing\.\*\*', '**237 automated tests passing.**', content)

# Add explicit breakdown where it says "The pytest suite covers..."
# I'll replace the existing sentence.
old_sentence = "The pytest suite covers ephemeris accuracy against known historical charts, grounding logic across three scripts, entitlement gate enforcement, crisis detection across English/Hindi/Hinglish, and reproducible tarot shuffles. Every push is tested before it can break a user's reading."
new_sentence = """The pytest suite covers ephemeris accuracy against known historical charts, grounding logic, entitlement gate enforcement, crisis detection, and reproducible tarot shuffles. Every push is tested before it can break a user's reading.

**Test Suites Breakdown:**
- **Total automated tests:** 237
- **Astro Engine & Matching tests:** 69
- **AI Grounding & Tarot tests:** 87
- **Backend API & Subscriptions tests:** 81"""

content = content.replace(old_sentence, new_sentence)

with open("README.md", "w") as f:
    f.write(content)
