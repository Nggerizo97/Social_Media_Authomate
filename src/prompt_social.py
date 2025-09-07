from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64
from PIL import Image
from io import BytesIO
import random
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
DRIVE_SERVICE_ACCOUNT_FILE = os.getenv("DRIVE_SERVICE_ACCOUNT_FILE")
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")

# --- 1. Realism Elements and Prompt Generation (Python version) ---
realism_elements = {
    "descriptors": [
        "human model hyper-detailed photorealistic portrait",
        "human model ultra-realistic cinematic character study",
        "human model high-fidelity realistic digital portrait",
        "human model 8K resolution realistic human depiction"
    ],
    "facial_features": [
        "natural subtle facial asymmetry",
        "soft skin with realistic pores and texture",
        "imperceptible vellus hair catching the light",
        "natural skin tone variations",
        "subtle signs of life like faint freckles or nearly invisible scars",
        "realistic eye reflections and moisture"
    ],
    "attire": [
        "form-fitting cotton t-shirt with visible fabric weave and slight pilling",
        "worn leather wristbands with authentic scuff marks and patina",
        "practical tactical pants with realistic stitching and pocket bulging",
        "slightly wrinkled linen shirt with natural fiber inconsistencies"
    ],
    "environments": [
        "misty forest with realistic atmospheric perspective and wet foliage",
        "urban alley with authentic trash, graffiti details, and worn textures",
        "sunlit meadow with accurately rendered botanical species and depth",
        "abandoned warehouse with peeling paint, rust, and dust motes in light rays"
    ],
    "lighting": [
        "natural diffuse overcast lighting creating soft shadows",
        "golden hour sunlight with accurate warm color temperature and long shadows",
        "cool moonlight with realistic light falloff and deep, soft shadows",
        "dappled forest light with authentic shadow softness and light patterns"
    ],
    "accessories": [
        "practical steel daggers with wear marks, minute scratches, and oil residue",
        "tactical belt with realistic weight distribution and gear sag",
        "weather-beaten leather satchel with stressed seams and buckle imprints",
        "scratched metal water flask with condensation droplets"
    ]
}

def get_random_element(array):
    return random.choice(array)

def generate_image_prompt():
    prompt = f"""
{get_random_element(realism_elements["descriptors"])} of a fierce young woman.
She has straight, shoulder-length dark brown hair with natural flyaways and individual strand definition.
Her face shows {get_random_element(realism_elements["facial_features"])} and {get_random_element(realism_elements["facial_features"])}. Ensure her eyes have lifelike catchlights and pupils react realistically to the described lighting.
She wears a {get_random_element(realism_elements["attire"])} and carries {get_random_element(realism_elements["accessories"])}. The clothing should show realistic folds, and material interaction with her form.
Location: {get_random_element(realism_elements["environments"])}.
Lighting: {get_random_element(realism_elements["lighting"])}. Pay close attention to how this light interacts with her skin, hair, and clothing materials, creating highlights and shadows that enhance realism.
Shot with a virtual 85mm lens at f/1.2 for authentic depth of field and bokeh.
Skin shows subtle capillary visibility, natural oil sheen, and micro-imperfections. The texture should not be overly smoothed.
Focus on extreme realism in textures, lighting, and human anatomy.
"""
    return "\n".join(line.strip() for line in prompt.splitlines() if line.strip())


# --- 2. Google Gemini Image Generation (Updated to new API) ---
def generate_image_with_gemini(prompt_text, output_filename="gemini_generated_image.png"):
    """Generates an image using Gemini with the new API and saves it locally."""
    try:
        if not API_KEY:
            print("Error: GOOGLE_API_KEY is not set in the .env file.")
            return None, None
        
        client = genai.Client(api_key=API_KEY)
        response = client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",
        contents=prompt_text,
        config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE']
    )
)
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                print(part.text)
            elif part.inline_data is not None:
                image = Image.open(BytesIO((part.inline_data.data)))
                image.save(output_filename)
                image.show()
                return output_filename, part.inline_data.data

    except Exception as e:
        print(f"An error occurred during Gemini image generation: {e}")
        return None, None

'''
# --- 3. Google Drive Upload (Remains the same) ---
def upload_to_drive(filepath, filename_on_drive, image_bytes, folder_id=None):
    """Uploads a file to Google Drive."""
    try:
        if not DRIVE_SERVICE_ACCOUNT_FILE or not os.path.exists(DRIVE_SERVICE_ACCOUNT_FILE):
            print(f"Error: DRIVE_SERVICE_ACCOUNT_FILE path not found or not set in .env: {DRIVE_SERVICE_ACCOUNT_FILE}")
            return None

        print(f"Uploading {filename_on_drive} to Google Drive...")
        creds = Credentials.from_service_account_file(
            DRIVE_SERVICE_ACCOUNT_FILE,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {'name': filename_on_drive}
        if folder_id and folder_id.strip():
            file_metadata['parents'] = [folder_id]

        media = MediaIoBaseUpload(BytesIO(image_bytes),
                                mimetype='image/png',
                                resumable=True)

        request = service.files().create(body=file_metadata,
                                     media_body=media,
                                     fields='id, webViewLink')
        file = request.execute()

        print(f"File '{filename_on_drive}' uploaded to Drive.")
        print(f"File ID: {file.get('id')}")
        print(f"View Link: {file.get('webViewLink')}")
        return file.get('webViewLink')

    except Exception as e:
        print(f"An error occurred during Google Drive upload: {e}")
        return None
'''

# --- Main Execution ---
if __name__ == "__main__":
    if not API_KEY:
        print("Startup Error: GOOGLE_API_KEY is not set in the .env file. Exiting.")
        exit()

    image_prompt = generate_image_prompt()
    print("--- Generated Prompt ---")
    print(image_prompt)
    print("------------------------\n")

    output_image_filename = "fierce_woman_realistic.png"
    local_image_path, image_bytes_data = generate_image_with_gemini(image_prompt, output_image_filename)
'''
    if local_image_path and image_bytes_data:
        print(f"\nImage '{local_image_path}' generated.")

        if DRIVE_SERVICE_ACCOUNT_FILE:
            drive_link = upload_to_drive(
                local_image_path,
                output_image_filename,
                image_bytes_data,
                DRIVE_FOLDER_ID
            )
            if drive_link:
                print(f"\nImage uploaded to Google Drive: {drive_link}")'''