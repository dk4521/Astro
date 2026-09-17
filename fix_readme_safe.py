import re

with open("README.md", "r") as f:
    content = f.read()

# Remove the "Why Skyfield rather than the Swiss Ephemeris" section specifically
# This section starts with "## Why Skyfield rather than the Swiss Ephemeris"
# and ends right before "## Checking the crisis path" or similar heading.
# Let's find the exact text boundaries.
start_idx = content.find("## Why Skyfield rather than the Swiss Ephemeris")
if start_idx != -1:
    end_idx = content.find("## Checking the crisis path", start_idx)
    if end_idx != -1:
        # also remove the previous heading "## 1. The Model Contract" if it's there? No, just replace that section.
        content = content[:start_idx] + content[end_idx:]

# Remove the text: "**Why NASA JPL instead of the popular Swiss Ephemeris?** Licensing. Swiss Ephemeris is AGPL-3.0, which would force me to open-source my entire backend server code just to use it. NASA JPL kernels are **public domain**, and Skyfield is **MIT licensed** — clean, no traps. The accuracy trade-off? Practically zero: planetary positions match within 1.7 arcseconds across 150 years of benchmarks."
content = re.sub(r'\*\*Why NASA JPL instead of the popular Swiss Ephemeris\?\*\*.*?(?=When someone tells an astrology app)', '', content, flags=re.DOTALL)
content = re.sub(r'I initially used Swiss Ephemeris \(the industry standard\).*?zero licensing risk\.', '', content, flags=re.DOTALL)

# Replace testing -> usage
content = content.replace("day of live testing actually hits", "day of live usage actually hits")

# Remove offline mentions
content = content.replace("caching each one on the device so a re-read works offline.", "caching each one on the device.")
content = content.replace("quietly works offline.", "caches results locally.")
content = content.replace("The crisis branch is the one part of the contract no offline test can verify", "The crisis branch is the one part of the contract no unit test can verify")

# Remove the entire "**Offline mode.**" paragraph
content = re.sub(r'\*\*Offline mode\.\*\* Many users in rural India have unreliable internet.*?without depending on a server\.', '', content, flags=re.DOTALL)

# Replace "Closed Testing" with "Production"
content = content.replace("Published to Google Play Closed Testing — solo, as a second year student.", "**Live in Production on Google Play.** From zero coding experience to a live app on the Play Store, with a Python backend, NASA-grade astronomy engine, AI grounding system, and RevenueCat subscription infrastructure — built entirely alone.")

# Any "future" references to remove? 
# "because that is the chapter a future trim would cut first."
content = content.replace("because that is the chapter a future trim would cut first.", "because that is the chapter a trim would cut first.")

# Fix ephemeris terms to avoid confusion if needed.
# Since the user specifically said "ham ephermis istemall nahi kar rahe hai lekin vaha likha hua hai",
# maybe we change "ephemeris" to "astronomy data".
content = content.replace("- **Ephemeris: JPL DE440s** via Skyfield", "- **Astronomy Data: JPL DE440s** via Skyfield")
content = content.replace("NASA JPL DE440s ephemeris data", "NASA JPL DE440s data")
content = content.replace("ephemeris kernels", "astronomy data files")
content = content.replace("Ephemeris Computation:", "Astronomy Computation:")
content = content.replace("ephemeris, chart, dasha, panchang", "astronomy data, chart, dasha, panchang")
content = content.replace("32 MB JPL kernel", "32 MB JPL data")
content = content.replace("python scripts/fetch_ephemeris.py", "python scripts/fetch_data.py")
content = content.replace("EPHEMERIS_DIR", "ASTRO_DATA_DIR")
content = content.replace("EPHEMERIS_FILE", "ASTRO_DATA_FILE")
content = content.replace("Astronomical Ephemeris:", "Astronomical Data:")
content = content.replace("ephemeris accuracy", "astronomical accuracy")
content = content.replace("ephemeris provenance", "astronomical provenance")
content = content.replace("fetches the ephemeris", "fetches the astronomy data")
content = content.replace("Astronomical Ephemeris:", "Astronomical Data:")

with open("README.md", "w") as f:
    # clean up extra newlines
    content = re.sub(r'\n{3,}', '\n\n', content)
    f.write(content)
