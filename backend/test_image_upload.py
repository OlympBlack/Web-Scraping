import asyncio
from services.image_downloader import download_image
from services.supabase_client import upload_image

async def test_image_flow():
    # 1. Download a test image
    test_url = "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png"
    print(f"Downloading from {test_url}...")
    result = await download_image(test_url)
    
    if result:
        content, mime = result
        print(f"Downloaded {len(content)} bytes. Type: {mime}")
        
        # 2. Upload to Supabase
        filename = "test_google_logo.png"
        print(f"Uploading to {filename}...")
        public_url = upload_image(content, filename, content_type=mime)
        
        if public_url:
            print(f"Success! Public URL: {public_url}")
        else:
            print("Upload failed.")
    else:
        print("Download failed.")

if __name__ == "__main__":
    asyncio.run(test_image_flow())
