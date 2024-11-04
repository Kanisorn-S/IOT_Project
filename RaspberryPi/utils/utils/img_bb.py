import requests

def upload_image_to_imgbb(image_path, api_key):
    # Open the image file in binary mode
    with open(image_path, "rb") as image_file:
        # Prepare the image data to upload
        files = {
            'image': image_file.read()
        }
        
        # API endpoint to upload the image
        url = "https://api.imgbb.com/1/upload"
        
        # Payload with API key and expiration time (optional)
        payload = {
            'key': api_key,
            'expiration': 600  # Expiration time in seconds (optional)
        }
        
        # Send POST request to upload the image
        response = requests.post(url, files=files, data=payload)
        
        # Check if the upload was successful
        if response.status_code == 200:
            # Extract the image URL from the response
            image_url = response.json()['data']['url']
            print("Image URL:", image_url)
            return image_url
        else:
            print("Error:", response.status_code, response.text)
            return None