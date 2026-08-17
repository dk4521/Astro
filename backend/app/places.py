"""Built-in place lookup for birth coordinates.

Deliberately a small bundled dataset rather than a geocoding API call: birth
place search happens on the onboarding screen, where a network round trip per
keystroke is the difference between the app feeling instant and feeling like
every other astrology app. Swapping in a real geocoder later means replacing
`search()` alone — nothing else imports the table.

Coverage is India-first (all state capitals and major cities) plus the world
cities an Indian diaspora user is most likely to have been born in.
"""

from __future__ import annotations

import unicodedata
from functools import lru_cache

from .schemas import PlaceOut

# name, admin (state / region), country, latitude, longitude
_PLACES: tuple[tuple[str, str, str, float, float], ...] = (
    # --- India: metros and major cities ---
    ("Mumbai", "Maharashtra", "India", 19.0760, 72.8777),
    ("Delhi", "Delhi", "India", 28.6139, 77.2090),
    ("New Delhi", "Delhi", "India", 28.6139, 77.2090),
    ("Bengaluru", "Karnataka", "India", 12.9716, 77.5946),
    ("Hyderabad", "Telangana", "India", 17.3850, 78.4867),
    ("Ahmedabad", "Gujarat", "India", 23.0225, 72.5714),
    ("Chennai", "Tamil Nadu", "India", 13.0827, 80.2707),
    ("Kolkata", "West Bengal", "India", 22.5726, 88.3639),
    ("Pune", "Maharashtra", "India", 18.5204, 73.8567),
    ("Jaipur", "Rajasthan", "India", 26.9124, 75.7873),
    ("Surat", "Gujarat", "India", 21.1702, 72.8311),
    ("Lucknow", "Uttar Pradesh", "India", 26.8467, 80.9462),
    ("Kanpur", "Uttar Pradesh", "India", 26.4499, 80.3319),
    ("Nagpur", "Maharashtra", "India", 21.1458, 79.0882),
    ("Indore", "Madhya Pradesh", "India", 22.7196, 75.8577),
    ("Thane", "Maharashtra", "India", 19.2183, 72.9781),
    ("Bhopal", "Madhya Pradesh", "India", 23.2599, 77.4126),
    ("Visakhapatnam", "Andhra Pradesh", "India", 17.6868, 83.2185),
    ("Patna", "Bihar", "India", 25.5941, 85.1376),
    ("Vadodara", "Gujarat", "India", 22.3072, 73.1812),
    ("Ghaziabad", "Uttar Pradesh", "India", 28.6692, 77.4538),
    ("Ludhiana", "Punjab", "India", 30.9010, 75.8573),
    ("Agra", "Uttar Pradesh", "India", 27.1767, 78.0081),
    ("Nashik", "Maharashtra", "India", 19.9975, 73.7898),
    ("Faridabad", "Haryana", "India", 28.4089, 77.3178),
    ("Meerut", "Uttar Pradesh", "India", 28.9845, 77.7064),
    ("Rajkot", "Gujarat", "India", 22.3039, 70.8022),
    ("Varanasi", "Uttar Pradesh", "India", 25.3176, 82.9739),
    ("Srinagar", "Jammu and Kashmir", "India", 34.0837, 74.7973),
    ("Aurangabad", "Maharashtra", "India", 19.8762, 75.3433),
    ("Dhanbad", "Jharkhand", "India", 23.7957, 86.4304),
    ("Amritsar", "Punjab", "India", 31.6340, 74.8723),
    ("Allahabad", "Uttar Pradesh", "India", 25.4358, 81.8463),
    ("Prayagraj", "Uttar Pradesh", "India", 25.4358, 81.8463),
    ("Ranchi", "Jharkhand", "India", 23.3441, 85.3096),
    ("Howrah", "West Bengal", "India", 22.5958, 88.2636),
    ("Coimbatore", "Tamil Nadu", "India", 11.0168, 76.9558),
    ("Jabalpur", "Madhya Pradesh", "India", 23.1815, 79.9864),
    ("Gwalior", "Madhya Pradesh", "India", 26.2183, 78.1828),
    ("Vijayawada", "Andhra Pradesh", "India", 16.5062, 80.6480),
    ("Jodhpur", "Rajasthan", "India", 26.2389, 73.0243),
    ("Madurai", "Tamil Nadu", "India", 9.9252, 78.1198),
    ("Raipur", "Chhattisgarh", "India", 21.2514, 81.6296),
    ("Kota", "Rajasthan", "India", 25.2138, 75.8648),
    ("Chandigarh", "Chandigarh", "India", 30.7333, 76.7794),
    ("Guwahati", "Assam", "India", 26.1445, 91.7362),
    ("Solapur", "Maharashtra", "India", 17.6599, 75.9064),
    ("Bareilly", "Uttar Pradesh", "India", 28.3670, 79.4304),
    ("Moradabad", "Uttar Pradesh", "India", 28.8386, 78.7733),
    ("Mysuru", "Karnataka", "India", 12.2958, 76.6394),
    ("Tiruchirappalli", "Tamil Nadu", "India", 10.7905, 78.7047),
    ("Bhubaneswar", "Odisha", "India", 20.2961, 85.8245),
    ("Salem", "Tamil Nadu", "India", 11.6643, 78.1460),
    ("Thiruvananthapuram", "Kerala", "India", 8.5241, 76.9366),
    ("Bhiwandi", "Maharashtra", "India", 19.3002, 73.0586),
    ("Saharanpur", "Uttar Pradesh", "India", 29.9680, 77.5460),
    ("Gorakhpur", "Uttar Pradesh", "India", 26.7606, 83.3732),
    ("Guntur", "Andhra Pradesh", "India", 16.3067, 80.4365),
    ("Amravati", "Maharashtra", "India", 20.9320, 77.7523),
    ("Noida", "Uttar Pradesh", "India", 28.5355, 77.3910),
    ("Jamshedpur", "Jharkhand", "India", 22.8046, 86.2029),
    ("Bhilai", "Chhattisgarh", "India", 21.1938, 81.3509),
    ("Warangal", "Telangana", "India", 17.9689, 79.5941),
    ("Cuttack", "Odisha", "India", 20.4625, 85.8830),
    ("Firozabad", "Uttar Pradesh", "India", 27.1592, 78.3957),
    ("Kochi", "Kerala", "India", 9.9312, 76.2673),
    ("Dehradun", "Uttarakhand", "India", 30.3165, 78.0322),
    ("Durgapur", "West Bengal", "India", 23.5204, 87.3119),
    ("Ajmer", "Rajasthan", "India", 26.4499, 74.6399),
    ("Rourkela", "Odisha", "India", 22.2604, 84.8536),
    ("Nanded", "Maharashtra", "India", 19.1383, 77.3210),
    ("Kolhapur", "Maharashtra", "India", 16.7050, 74.2433),
    ("Siliguri", "West Bengal", "India", 26.7271, 88.3953),
    ("Jhansi", "Uttar Pradesh", "India", 25.4484, 78.5685),
    ("Ulhasnagar", "Maharashtra", "India", 19.2215, 73.1645),
    ("Nellore", "Andhra Pradesh", "India", 14.4426, 79.9865),
    ("Jammu", "Jammu and Kashmir", "India", 32.7266, 74.8570),
    ("Belagavi", "Karnataka", "India", 15.8497, 74.4977),
    ("Mangaluru", "Karnataka", "India", 12.9141, 74.8560),
    ("Tirunelveli", "Tamil Nadu", "India", 8.7139, 77.7567),
    ("Malegaon", "Maharashtra", "India", 20.5579, 74.5287),
    ("Gaya", "Bihar", "India", 24.7955, 85.0002),
    ("Udaipur", "Rajasthan", "India", 24.5854, 73.7125),
    ("Kozhikode", "Kerala", "India", 11.2588, 75.7804),
    ("Bhavnagar", "Gujarat", "India", 21.7645, 72.1519),
    ("Jalandhar", "Punjab", "India", 31.3260, 75.5762),
    ("Bikaner", "Rajasthan", "India", 28.0229, 73.3119),
    ("Patiala", "Punjab", "India", 30.3398, 76.3869),
    ("Bhagalpur", "Bihar", "India", 25.2425, 86.9842),
    ("Muzaffarpur", "Bihar", "India", 26.1209, 85.3647),
    ("Panaji", "Goa", "India", 15.4909, 73.8278),
    ("Shimla", "Himachal Pradesh", "India", 31.1048, 77.1734),
    ("Imphal", "Manipur", "India", 24.8170, 93.9368),
    ("Shillong", "Meghalaya", "India", 25.5788, 91.8933),
    ("Aizawl", "Mizoram", "India", 23.7271, 92.7176),
    ("Kohima", "Nagaland", "India", 25.6751, 94.1086),
    ("Agartala", "Tripura", "India", 23.8315, 91.2868),
    ("Itanagar", "Arunachal Pradesh", "India", 27.0844, 93.6053),
    ("Gangtok", "Sikkim", "India", 27.3389, 88.6065),
    ("Dispur", "Assam", "India", 26.1433, 91.7898),
    ("Puducherry", "Puducherry", "India", 11.9416, 79.8083),
    ("Haridwar", "Uttarakhand", "India", 29.9457, 78.1642),
    ("Mathura", "Uttar Pradesh", "India", 27.4924, 77.6737),
    ("Ujjain", "Madhya Pradesh", "India", 23.1765, 75.7885),
    ("Tirupati", "Andhra Pradesh", "India", 13.6288, 79.4192),
    ("Rishikesh", "Uttarakhand", "India", 30.0869, 78.2676),
    ("Pushkar", "Rajasthan", "India", 26.4897, 74.5511),
    ("Darbhanga", "Bihar", "India", 26.1542, 85.8918),
    ("Sonipat", "Haryana", "India", 28.9931, 77.0151),
    ("Gurugram", "Haryana", "India", 28.4595, 77.0266),
    ("Rohtak", "Haryana", "India", 28.8955, 76.6066),
    ("Hisar", "Haryana", "India", 29.1492, 75.7217),
    ("Karnal", "Haryana", "India", 29.6857, 76.9905),
    ("Ambala", "Haryana", "India", 30.3752, 76.7821),
    ("Panipat", "Haryana", "India", 29.3909, 76.9635),
    ("Alwar", "Rajasthan", "India", 27.5530, 76.6346),
    ("Bhilwara", "Rajasthan", "India", 25.3407, 74.6313),
    ("Sikar", "Rajasthan", "India", 27.6094, 75.1399),
    ("Satna", "Madhya Pradesh", "India", 24.5854, 80.8322),
    ("Rewa", "Madhya Pradesh", "India", 24.5362, 81.2961),
    ("Sagar", "Madhya Pradesh", "India", 23.8388, 78.7378),
    ("Ratlam", "Madhya Pradesh", "India", 23.3315, 75.0367),
    ("Korba", "Chhattisgarh", "India", 22.3595, 82.7501),
    ("Bilaspur", "Chhattisgarh", "India", 22.0797, 82.1409),
    ("Hubballi", "Karnataka", "India", 15.3647, 75.1240),
    ("Davanagere", "Karnataka", "India", 14.4644, 75.9218),
    ("Ballari", "Karnataka", "India", 15.1394, 76.9214),
    ("Shivamogga", "Karnataka", "India", 13.9299, 75.5681),
    ("Thrissur", "Kerala", "India", 10.5276, 76.2144),
    ("Kollam", "Kerala", "India", 8.8932, 76.6141),
    ("Alappuzha", "Kerala", "India", 9.4981, 76.3388),
    ("Kannur", "Kerala", "India", 11.8745, 75.3704),
    ("Erode", "Tamil Nadu", "India", 11.3410, 77.7172),
    ("Vellore", "Tamil Nadu", "India", 12.9165, 79.1325),
    ("Thoothukudi", "Tamil Nadu", "India", 8.7642, 78.1348),
    ("Dindigul", "Tamil Nadu", "India", 10.3624, 77.9695),
    ("Rajahmundry", "Andhra Pradesh", "India", 17.0005, 81.8040),
    ("Kakinada", "Andhra Pradesh", "India", 16.9891, 82.2475),
    ("Kurnool", "Andhra Pradesh", "India", 15.8281, 78.0373),
    ("Tirupur", "Tamil Nadu", "India", 11.1085, 77.3411),
    ("Karimnagar", "Telangana", "India", 18.4386, 79.1288),
    ("Nizamabad", "Telangana", "India", 18.6725, 78.0941),
    ("Asansol", "West Bengal", "India", 23.6739, 86.9524),
    ("Kharagpur", "West Bengal", "India", 22.3460, 87.2320),
    ("Berhampur", "Odisha", "India", 19.3150, 84.7941),
    ("Sambalpur", "Odisha", "India", 21.4669, 83.9812),
    ("Puri", "Odisha", "India", 19.8135, 85.8312),
    ("Junagadh", "Gujarat", "India", 21.5222, 70.4579),
    ("Jamnagar", "Gujarat", "India", 22.4707, 70.0577),
    ("Gandhinagar", "Gujarat", "India", 23.2156, 72.6369),
    ("Anand", "Gujarat", "India", 22.5645, 72.9289),
    ("Nadiad", "Gujarat", "India", 22.6916, 72.8634),
    ("Aligarh", "Uttar Pradesh", "India", 27.8974, 78.0880),
    ("Muzaffarnagar", "Uttar Pradesh", "India", 29.4727, 77.7085),
    ("Shahjahanpur", "Uttar Pradesh", "India", 27.8815, 79.9099),
    ("Rampur", "Uttar Pradesh", "India", 28.7983, 79.0250),
    ("Ayodhya", "Uttar Pradesh", "India", 26.7922, 82.1998),
    ("Solan", "Himachal Pradesh", "India", 30.9045, 77.0967),
    ("Dharamshala", "Himachal Pradesh", "India", 32.2190, 76.3234),
    ("Haldwani", "Uttarakhand", "India", 29.2183, 79.5130),
    # --- Neighbouring South Asia ---
    ("Kathmandu", "Bagmati", "Nepal", 27.7172, 85.3240),
    ("Pokhara", "Gandaki", "Nepal", 28.2096, 83.9856),
    ("Dhaka", "Dhaka", "Bangladesh", 23.8103, 90.4125),
    ("Chittagong", "Chattogram", "Bangladesh", 22.3569, 91.7832),
    ("Colombo", "Western", "Sri Lanka", 6.9271, 79.8612),
    ("Karachi", "Sindh", "Pakistan", 24.8607, 67.0011),
    ("Lahore", "Punjab", "Pakistan", 31.5204, 74.3587),
    ("Islamabad", "Islamabad", "Pakistan", 33.6844, 73.0479),
    ("Thimphu", "Thimphu", "Bhutan", 27.4728, 89.6390),
    ("Male", "Male", "Maldives", 4.1755, 73.5093),
    ("Kabul", "Kabul", "Afghanistan", 34.5553, 69.2075),
    # --- Gulf ---
    ("Dubai", "Dubai", "United Arab Emirates", 25.2048, 55.2708),
    ("Abu Dhabi", "Abu Dhabi", "United Arab Emirates", 24.4539, 54.3773),
    ("Sharjah", "Sharjah", "United Arab Emirates", 25.3463, 55.4209),
    ("Doha", "Doha", "Qatar", 25.2854, 51.5310),
    ("Kuwait City", "Al Asimah", "Kuwait", 29.3759, 47.9774),
    ("Muscat", "Muscat", "Oman", 23.5880, 58.3829),
    ("Manama", "Capital", "Bahrain", 26.2285, 50.5860),
    ("Riyadh", "Riyadh", "Saudi Arabia", 24.7136, 46.6753),
    ("Jeddah", "Makkah", "Saudi Arabia", 21.4858, 39.1925),
    # --- Rest of world ---
    ("London", "England", "United Kingdom", 51.5074, -0.1278),
    ("Birmingham", "England", "United Kingdom", 52.4862, -1.8904),
    ("Manchester", "England", "United Kingdom", 53.4808, -2.2426),
    ("Leicester", "England", "United Kingdom", 52.6369, -1.1398),
    ("New York", "New York", "United States", 40.7128, -74.0060),
    ("San Francisco", "California", "United States", 37.7749, -122.4194),
    ("San Jose", "California", "United States", 37.3382, -121.8863),
    ("Los Angeles", "California", "United States", 34.0522, -118.2437),
    ("Chicago", "Illinois", "United States", 41.8781, -87.6298),
    ("Houston", "Texas", "United States", 29.7604, -95.3698),
    ("Dallas", "Texas", "United States", 32.7767, -96.7970),
    ("Seattle", "Washington", "United States", 47.6062, -122.3321),
    ("Boston", "Massachusetts", "United States", 42.3601, -71.0589),
    ("Atlanta", "Georgia", "United States", 33.7490, -84.3880),
    ("Edison", "New Jersey", "United States", 40.5187, -74.4121),
    ("Toronto", "Ontario", "Canada", 43.6532, -79.3832),
    ("Vancouver", "British Columbia", "Canada", 49.2827, -123.1207),
    ("Brampton", "Ontario", "Canada", 43.7315, -79.7624),
    ("Calgary", "Alberta", "Canada", 51.0447, -114.0719),
    ("Sydney", "New South Wales", "Australia", -33.8688, 151.2093),
    ("Melbourne", "Victoria", "Australia", -37.8136, 144.9631),
    ("Brisbane", "Queensland", "Australia", -27.4698, 153.0251),
    ("Perth", "Western Australia", "Australia", -31.9505, 115.8605),
    ("Auckland", "Auckland", "New Zealand", -36.8485, 174.7633),
    ("Singapore", "Singapore", "Singapore", 1.3521, 103.8198),
    ("Kuala Lumpur", "Kuala Lumpur", "Malaysia", 3.1390, 101.6869),
    ("Bangkok", "Bangkok", "Thailand", 13.7563, 100.5018),
    ("Hong Kong", "Hong Kong", "China", 22.3193, 114.1694),
    ("Tokyo", "Tokyo", "Japan", 35.6762, 139.6503),
    ("Seoul", "Seoul", "South Korea", 37.5665, 126.9780),
    ("Beijing", "Beijing", "China", 39.9042, 116.4074),
    ("Shanghai", "Shanghai", "China", 31.2304, 121.4737),
    ("Jakarta", "Jakarta", "Indonesia", -6.2088, 106.8456),
    ("Manila", "Metro Manila", "Philippines", 14.5995, 120.9842),
    ("Paris", "Ile-de-France", "France", 48.8566, 2.3522),
    ("Berlin", "Berlin", "Germany", 52.5200, 13.4050),
    ("Frankfurt", "Hesse", "Germany", 50.1109, 8.6821),
    ("Amsterdam", "North Holland", "Netherlands", 52.3676, 4.9041),
    ("Zurich", "Zurich", "Switzerland", 47.3769, 8.5417),
    ("Rome", "Lazio", "Italy", 41.9028, 12.4964),
    ("Madrid", "Madrid", "Spain", 40.4168, -3.7038),
    ("Lisbon", "Lisbon", "Portugal", 38.7223, -9.1393),
    ("Dublin", "Leinster", "Ireland", 53.3498, -6.2603),
    ("Stockholm", "Stockholm", "Sweden", 59.3293, 18.0686),
    ("Oslo", "Oslo", "Norway", 59.9139, 10.7522),
    ("Moscow", "Moscow", "Russia", 55.7558, 37.6173),
    ("Istanbul", "Istanbul", "Turkey", 41.0082, 28.9784),
    ("Cairo", "Cairo", "Egypt", 30.0444, 31.2357),
    ("Nairobi", "Nairobi", "Kenya", -1.2921, 36.8219),
    ("Johannesburg", "Gauteng", "South Africa", -26.2041, 28.0473),
    ("Lagos", "Lagos", "Nigeria", 6.5244, 3.3792),
    ("Port Louis", "Port Louis", "Mauritius", -20.1609, 57.5012),
    ("Suva", "Central", "Fiji", -18.1416, 178.4419),
    ("Georgetown", "Demerara-Mahaica", "Guyana", 6.8013, -58.1551),
    ("Paramaribo", "Paramaribo", "Suriname", 5.8520, -55.2038),
    ("Sao Paulo", "Sao Paulo", "Brazil", -23.5505, -46.6333),
    ("Buenos Aires", "Buenos Aires", "Argentina", -34.6037, -58.3816),
    ("Mexico City", "Mexico City", "Mexico", 19.4326, -99.1332),
)


def _fold(text: str) -> str:
    """Casefold and strip accents so `Bengaluru` matches `bengaluru`."""
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    return stripped.casefold().strip()


@lru_cache(maxsize=1)
def _index() -> tuple[tuple[str, PlaceOut], ...]:
    """Pre-folded search keys paired with their place."""
    return tuple(
        (
            _fold(f"{name} {admin} {country}"),
            PlaceOut(
                name=name,
                admin=admin,
                country=country,
                latitude=lat,
                longitude=lon,
            ),
        )
        for name, admin, country, lat, lon in _PLACES
    )


def search(query: str, limit: int = 10) -> list[PlaceOut]:
    """Find places matching `query`, best matches first.

    Ranking is prefix-match on the city name, then any substring hit. That is
    enough for a picker over a few hundred entries and keeps the behaviour
    obvious; a real geocoder would replace this wholesale.
    """
    needle = _fold(query)
    if not needle:
        return []

    prefix: list[PlaceOut] = []
    contains: list[PlaceOut] = []

    for key, place in _index():
        city = _fold(place.name)
        if city.startswith(needle):
            prefix.append(place)
        elif needle in key:
            contains.append(place)

        if len(prefix) >= limit:
            break

    return (prefix + contains)[:limit]
