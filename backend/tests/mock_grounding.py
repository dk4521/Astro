from app.ai.grounding import StructuredClaim, ClaimType

def mock_extract_claims(text: str) -> list[StructuredClaim]:
    claims = []
    text_lower = text.lower()
    if "moon is in simha" in text_lower or "moon in simha" in text_lower or "moon" in text_lower and "simha" in text_lower:
        claims.append(StructuredClaim(claim_type=ClaimType.PLANET_RASHI, planet="Moon", value="Simha", original_text="Moon is in Simha"))
    elif "चन्द्रमा मकर" in text_lower or "चन्द्र मकर" in text_lower:
        claims.append(StructuredClaim(claim_type=ClaimType.PLANET_RASHI, planet="Moon", value="Makara", original_text="चन्द्रमा मकर"))
    elif "jupiter is in swati" in text_lower or "jupiter" in text_lower and "swati" in text_lower:
        claims.append(StructuredClaim(claim_type=ClaimType.PLANET_NAKSHATRA, planet="Jupiter", value="Swati", original_text="Jupiter is in Swati"))
    elif "mars is in the 7th" in text_lower or "mars in the 7th" in text_lower:
        claims.append(StructuredClaim(claim_type=ClaimType.PLANET_HOUSE, planet="Mars", value="7", original_text="Mars is in the 7th"))
    elif "venus is in aries" in text_lower:
        claims.append(StructuredClaim(claim_type=ClaimType.PLANET_RASHI, planet="Venus", value="Aries", original_text="Venus is in Aries"))
    elif "rahu in leo" in text_lower:
        claims.append(StructuredClaim(claim_type=ClaimType.PLANET_RASHI, planet="Rahu", value="Leo", original_text="Rahu in Leo"))
    elif "शनि सिंह" in text_lower:
        claims.append(StructuredClaim(claim_type=ClaimType.PLANET_RASHI, planet="Saturn", value="Simha", original_text="शनि सिंह"))
    elif "बुध अश्लेषा" in text_lower:
        claims.append(StructuredClaim(claim_type=ClaimType.PLANET_NAKSHATRA, planet="Mercury", value="Ashlesha", original_text="बुध अश्लेषा"))
    elif "मंगल सातवें" in text_lower:
        claims.append(StructuredClaim(claim_type=ClaimType.PLANET_HOUSE, planet="Mars", value="7", original_text="मंगल सातवें"))
    elif "शुक्र वृषभ" in text_lower:
        claims.append(StructuredClaim(claim_type=ClaimType.PLANET_RASHI, planet="Venus", value="Vrishabha", original_text="शुक्र वृषभ"))
    elif "बृहस्पतिवार" in text_lower:
        # Should not extract, prose
        pass
    elif "बुध कन्या" in text_lower:
        claims.append(StructuredClaim(claim_type=ClaimType.PLANET_RASHI, planet="Mercury", value="Kanya", original_text="बुध कन्या"))
    
    # Catch any planet in any sign for simple cases
    return claims

def mock_classify_safety(text: str) -> bool:
    if "kill" in text or "die" in text or "harm" in text or "hopeless" in text:
        return True
    return False

import pytest
from app.ai import grounding

@pytest.fixture(autouse=True)
def apply_grounding_mocks(monkeypatch):
    monkeypatch.setattr(grounding, "extract_claims", mock_extract_claims)
    monkeypatch.setattr(grounding, "classify_safety", mock_classify_safety)
