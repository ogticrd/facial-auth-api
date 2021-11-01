from face.liveness import HandSign

HANDS_ACTIONS = [
    HandSign(THUMB=False, INDEX=False, MIDDLE=False, RING=False, PINKY=False),
    HandSign(THUMB=True, INDEX=False, MIDDLE=False, RING=False, PINKY=False),
    HandSign(THUMB=False, INDEX=True, MIDDLE=True, RING=False, PINKY=False),
    HandSign(THUMB=True, INDEX=True, MIDDLE=True, RING=False, PINKY=False),
    HandSign(THUMB=True, INDEX=True, MIDDLE=True, RING=True, PINKY=True)
]