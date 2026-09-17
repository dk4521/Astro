import re

with open("backend/app/ai/grounding.py", "r") as f:
    content = f.read()

content = content.replace("def classify_safety(text: str) -> bool:", "def classify_safety(text: str) -> str:")
content = content.replace("return SafetyCheckResult(**data).is_crisis", "return \"CRISIS\" if SafetyCheckResult(**data).is_crisis else \"SAFE\"")
content = content.replace("return False", "return \"UNKNOWN\"")

with open("backend/app/ai/grounding.py", "w") as f:
    f.write(content)

with open("backend/app/ai/interpret.py", "r") as f:
    content = f.read()

old_logic = """    is_crisis = False
    if session_id and crisis.is_in_crisis(session_id):
        is_crisis = True
    elif grounding.classify_safety(question):
        is_crisis = True
        if session_id:
            crisis.mark_crisis(session_id)
            
    if is_crisis:
        # Deterministic safe path
        request = Request(
            messages=[{"role": "user", "content": question}],
            suffix="The user is in crisis. Generate a short, empathetic response and provide standard helplines. Do not mention astrology, charts, planets, or predictions at all.",
        )
    else:"""

new_logic = """    safety_status = "SAFE"
    if session_id and crisis.is_in_crisis(session_id):
        safety_status = "CRISIS"
    else:
        safety_status = grounding.classify_safety(question)
        if safety_status == "CRISIS" and session_id:
            crisis.mark_crisis(session_id)
            
    if safety_status == "CRISIS":
        # Deterministic safe path
        request = Request(
            messages=[{"role": "user", "content": question}],
            suffix="The user is in crisis. Generate a short, empathetic response and provide standard helplines. Do not mention astrology, charts, planets, or predictions at all.",
        )
    elif safety_status == "UNKNOWN":
        yield "I'm having trouble connecting right now. Please try again later."
        return
    else:"""

content = content.replace(old_logic, new_logic)

with open("backend/app/ai/interpret.py", "w") as f:
    f.write(content)

