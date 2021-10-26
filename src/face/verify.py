import os
from typing import Dict
from typing import TypedDict
import requests

from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials

class VerifyResult(TypedDict):
    isIdentical: bool
    confidence: float

def verify(target_path: str, source_path: str) -> VerifyResult:
    face_client = FaceClient(os.environ.get('FACE_API_ENDPOINT'), CognitiveServicesCredentials(os.environ.get('FACE_API_KEY', '')))

    test_image_array = [target_path, source_path]
    face_ids = []
    for image in test_image_array:
        image_io = open(image, 'r+b')
        face_ids.append(face_client.face.detect_with_stream(image_io, detection_model='detection_03')[0].face_id)

    headers: Dict[str, str] = {
        'Ocp-Apim-Subscription-Key': os.environ.get('FACE_API_KEY', ''),
        'Content-Type': 'application/json'
    }

    data: Dict[str, str] = {
        "faceId1": face_ids[0],
        "faceId2": face_ids[1]
    }

    results = requests.post(f'{os.environ.get("FACE_API_ENDPOINT")}/face/v1.0/verify', headers=headers, json=data)
    json_results = results.json()
    return VerifyResult(isIdentical=json_results['isIdentical'], confidence=json_results['confidence'])