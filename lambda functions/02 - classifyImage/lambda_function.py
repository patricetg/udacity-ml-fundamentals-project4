import subprocess
import sys

# https://stackoverflow.com/questions/60311148/pip-install-python-package-within-aws-lambda
# pip install custom package to /tmp/ and add to path
subprocess.call('pip install sagemaker -t /tmp/ --no-cache-dir'.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
sys.path.insert(1, '/tmp/')

import json
import sagemaker
import base64
from sagemaker.serializers import IdentitySerializer

# Fill this in with the name of your deployed model
ENDPOINT = "image-classification-2023-09-05-10-24-54-478" ## TODO: fill in

def lambda_handler(event, context):
    """
        Input eg:
        
        "image_data": "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",
        "s3_bucket": "sagemaker-us-west-2-659095202386",
        "s3_key": "train/bicycle_s_000017.png",
        "inferences": [],
        "prefix": "udacity-project-4"

        Output eg:
        {
            "statusCode": 200,
            "body": {
                "image_data": "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",
                "s3_bucket": "sagemaker-us-west-2-659095202386",
                "s3_key": "test/ordinary_bicycle_s_000431.png",
                "inferences": [
                    0.46814629435539246,
                    0.5318536758422852
                ],
                "prefix": "udacity-project-4"
            }
        }



    """

    b64encoded_image=event.get("image_data")

    # Decode the image data
    image = base64.b64decode(b64encoded_image)

    # Instantiate a Predictor
    predictor = sagemaker.predictor.Predictor(ENDPOINT)

    # For this model the IdentitySerializer needs to be "image/png"
    predictor.serializer = IdentitySerializer("image/png")
    
    # predictor.serializer = IdentitySerializer("image/png")
    # with open("./test/bicycle_s_001789.png", "rb") as f:
    #     payload = f.read()
    # inference = predictor.predict(payload)

    # Make a prediction:
    inferences = predictor.predict(image) #eg. b'[0.91, 0.09]'
    inferences = inferences.decode("utf-8") #eg. '[0.91, 0.09]'
    
    # We return the data back to the Step Function    
    event["inferences"] = eval(inferences) #eg. [0.91, 0.09]
    return {
        'statusCode': 200,
        'body': event #json.dumps(event)
    }