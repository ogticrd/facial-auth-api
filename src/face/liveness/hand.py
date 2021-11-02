import cv2 as cv
import mediapipe as mp
import numpy as np
from deepdiff import DeepDiff

from .types_utils import HandEnum
from .types_utils import HandSign
from .types_utils import HandSignDetectionResult

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

def _sign_detection(hand_sign: HandSign, results) -> HandSignDetectionResult:
    fingers_tips_ids = [mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                        mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.PINKY_TIP]
    
    fingers_statuses_right = HandSign(THUMB=False, INDEX=False, MIDDLE=False, RING=False, PINKY=False)
    
    fingers_statuses_left = HandSign(THUMB=False, INDEX=False, MIDDLE=False, RING=False, PINKY=False)
    
    for hand_index, hand_info in enumerate(results.multi_handedness):
        hand_label = hand_info.classification[0].label
        
        hand_landmarks =  results.multi_hand_landmarks[hand_index]
        
        for tip_index in fingers_tips_ids:
            finger_name = tip_index.name.split('_')[0]
            
            if (hand_landmarks.landmark[tip_index].y <= hand_landmarks.landmark[tip_index - 2].y):
                if hand_label == HandEnum.right:
                    temp_dict = dict(fingers_statuses_right)
                    temp_dict[finger_name] = True
                    fingers_statuses_right = HandSign(**temp_dict)
                else:
                    temp_dict = dict(fingers_statuses_left)
                    temp_dict[finger_name] = True
                    fingers_statuses_left = HandSign(**temp_dict)
        
        thumb_tip_x = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x
        thumb_mcp_x = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP - 1].x
        
        if (hand_label==HandEnum.right and (thumb_tip_x <= thumb_mcp_x)) or (hand_label==HandEnum.left and (thumb_tip_x >= thumb_mcp_x)):
            if hand_label == HandEnum.right:
                fingers_statuses_right.THUMB = True
            else:
                fingers_statuses_left.THUMB = True
        
        diff_right = DeepDiff(hand_sign, fingers_statuses_right)
        diff_left = DeepDiff(hand_sign, fingers_statuses_left)
        
        if not len(diff_right) or not len(diff_left):
            return HandSignDetectionResult(result=True, hand=hand_label)
        
    return HandSignDetectionResult(result=False, hand=hand_label)

def hand_sign_detection(image: np.ndarray, hand_sign: HandSign) -> HandSignDetectionResult:
    with mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
        image.flags.writeable = False
        image = cv.cvtColor(cv.flip(image, 1), cv.COLOR_BGR2RGB)
        results = hands.process(image)
        
        if results.multi_hand_landmarks:
            return _sign_detection(hand_sign, results)
        else:
            return HandSignDetectionResult(result=False, hand=HandEnum.right)
