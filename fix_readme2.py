import re

with open("README.md", "r") as f:
    content = f.read()

# Replace mentions of ephemeris
content = content.replace("- **Ephemeris: JPL DE440s** via Skyfield", "- **Astronomy Data: JPL DE440s** via Skyfield")
content = content.replace("NASA JPL DE440s ephemeris data", "NASA JPL DE440s data")
content = content.replace("ephemeris kernels", "astronomy data kernels")
content = content.replace("Ephemeris Computation:", "Astronomy Computation:")

# Swiss ephemeris leftovers in the intro paragraphs
content = re.sub(r'\*\*Why NASA JPL instead of the popular Swiss Ephemeris\?\*\*.*?benchmarks\.', '', content, flags=re.DOTALL)

# Mentions of testing in the context of live testing or closed testing
content = content.replace("day of live testing actually hits", "day of live usage actually hits")
content = content.replace("Closed Testing", "Production")

# Mentions of ephemeris fetching in render.yaml
content = content.replace("fetches the ephemeris", "fetches the astronomy data")

with open("README.md", "w") as f:
    f.write(content)
