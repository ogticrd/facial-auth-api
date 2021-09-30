import base64
import tempfile

def base64_to_webm(source: str) -> str:
    file_name: str = tempfile.mkstemp()[1] + '.webm'
    
    with open(file_name, 'wb') as video:
        video.write(base64.b64decode(source))
    
    return file_name