import re

with open("README.md", "r") as f:
    content = f.read()

# Remove Swiss Ephemeris section (Lines ~122 to ~146)
content = re.sub(r'## Why Skyfield rather than the Swiss Ephemeris.*?(?=## 1. The Model Contract)', '', content, flags=re.DOTALL)

# Replace "offline test" -> "unit test"
content = content.replace("no offline test can verify", "no unit test can verify")

# Remove offline mentions
content = content.replace("caching each one on the device so a re-read works offline.", "caching each one on the device.")
content = content.replace("quietly works offline.", "caches results locally.")

# Remove Offline mode section entirely
content = re.sub(r'\*\*Offline mode\.\*\* Many users in rural India.*?depending on a server\.', '', content, flags=re.DOTALL)

# Update Closed Testing -> Production
content = content.replace("Published to Google Play Closed Testing — solo, as a second year student.", "Published on Google Play — solo, as a second year student.")

# Future references
content = content.replace('because that is the chapter a future trim would cut first.', 'because that is the chapter a trim would cut first.')

# Fix "ephemeris" usages
content = content.replace("NASA JPL DE440s ephemeris kernels", "NASA JPL DE440s data")
content = content.replace("NASA JPL DE440s ephemeris data", "NASA JPL DE440s data")
content = content.replace("ephemeris accuracy", "astronomical accuracy")
content = content.replace("ephemeris provenance", "astronomical provenance")
# We still keep the word where it makes sense, but the user said "ham ephermis istemall nahi kar rahe hai lekin vaha likha hua hai"
# They probably meant Swiss Ephemeris which was repeatedly mentioned in the README.
content = re.sub(r'I initially used Swiss Ephemeris.*?zero licensing risk\.', '', content, flags=re.DOTALL)
content = content.replace("Astrology engine (ephemeris, chart, dasha, panchang)", "Astrology engine (astronomy data, chart, dasha, panchang)")
content = content.replace("32 MB JPL kernel", "32 MB JPL data")
content = content.replace("python scripts/fetch_ephemeris.py", "python scripts/fetch_data.py")
content = content.replace("EPHEMERIS_DIR", "ASTRO_DATA_DIR")
content = content.replace("EPHEMERIS_FILE", "ASTRO_DATA_FILE")
content = content.replace("Astronomical Ephemeris:", "Astronomical Data:")

with open("README.md", "w") as f:
    # also remove empty lines left by regex
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    f.write(content)
