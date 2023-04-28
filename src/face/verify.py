import boto3
from pydantic import BaseModel


class VerifyResult(BaseModel):
    isIdentical: bool
    confidence: float


def verify(target_path: str, source_path: str) -> VerifyResult:

    session = boto3.Session()
    client = session.client('rekognition')

    image_source = open(source_path, 'rb')
    image_target = open(target_path, 'rb')

    response = client.compare_faces(SimilarityThreshold=80,
                                    SourceImage={'Bytes': image_source.read()},
                                    TargetImage={'Bytes': image_target.read()})
    print(response)
    similarity = 0
    for faceMatch in response['FaceMatches']:
        position = faceMatch['Face']['BoundingBox']
        similarity = faceMatch['Similarity']
        print('The face at ' +
              str(position['Left']) + ' ' +
              str(position['Top']) +
              ' matches with ' + str(similarity) + '% confidence')
        if similarity > 90:
            faces_match = True
            break
    else:
        faces_match = False

    image_source.close()
    image_target.close()
    return VerifyResult(isIdentical=faces_match, confidence=similarity)
