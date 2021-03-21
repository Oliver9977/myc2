import base64

def isBase64(s): #not a good idea .. but should work ... cannot be a "single word"
    try:
        #print(base64.b64decode(s))
        return base64.b64encode(base64.b64decode(s)).decode("utf-8","ignore") == s
    except:
        return False
    
def b64_decode(s):
    return base64.b64decode(s)

def b64_encode(s):
    return base64.b64encode(s.encode("utf-8","ignore")).decode("utf-8","ignore")
