import json
import base64
import boto3
import cv2
import numpy as np

img_filename = '/tmp/inputimage.jpg'
output_bucket = 'kevin-fang'
s3_key_value = 'image.jpg'
boxed_img_filename = '/tmp/boxedimage.jpg'
boxed_s3_key_value = 'boxed_image.jpg'

s3_client = boto3.client('s3')
rekognition_client = boto3.client('rekognition')

def lambda_handler(event, context):
    requestMethod = event['httpMethod']
    if requestMethod == 'POST':
        requestBody = json.loads(event['body'])
        image_64_decode = base64.decodebytes(requestBody['key'].encode())
        
        # Save the image locally
        with open(img_filename, 'wb') as image_result:
            image_result.write(image_64_decode)
        
        # Upload the image to S3
        s3_client.upload_file(img_filename, output_bucket, s3_key_value, ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/jpeg'})
        s3_url = f'https://{output_bucket}.s3.amazonaws.com/{s3_key_value}'
        
        # Perform facial recognition
        with open(img_filename, 'rb') as image:
            response = rekognition_client.detect_faces(
                Image={'Bytes': image.read()},
                Attributes=['ALL']
            )
        
        # Get face details
        face_details = response['FaceDetails']
        
        # Read the image using OpenCV
        image = cv2.imread(img_filename)
        
        # Draw bounding boxes around faces
        height, width, _ = image.shape
        for face in face_details:
            box = face['BoundingBox']
            left = int(box['Left'] * width)
            top = int(box['Top'] * height)
            right = left + int(box['Width'] * width)
            bottom = top + int(box['Height'] * height)
            
            cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 3)
        
        # Save the image with bounding boxes locally
        cv2.imwrite(boxed_img_filename, image)
        
        # Upload the image with bounding boxes to S3
        s3_client.upload_file(boxed_img_filename, output_bucket, boxed_s3_key_value, ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/jpeg'})
        boxed_image_url = f'https://{output_bucket}.s3.amazonaws.com/{boxed_s3_key_value}'
        
        # Return the URLs
        return {
            'statusCode': 200,
            'body': json.dumps({
                'image_url': s3_url,
                'boxed_image_url': boxed_image_url,
                'face_details': face_details
            })
        }
    else:
        return {
            'statusCode': 400,
            'body': 'error'
        }
