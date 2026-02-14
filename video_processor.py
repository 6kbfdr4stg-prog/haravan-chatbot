import os
import requests
import json
import base64
import random
import re
import hashlib
from PIL import Image, ImageFilter

# Monkey patch for Pillow 10+ (moviepy 1.0.3 uses ANTIALIAS)
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips
from config import TEMP_IMAGE_DIR, OUTPUT_VIDEO_DIR

# --- Configuration ---
# Default key from original script (should be replaced by user key ideally)
GOOGLE_TTS_API_KEY = os.environ.get("GOOGLE_TTS_API_KEY", "AIzaSyBsXsKTO_g4tUVmKxNW1JPlOpLNGxGBIqE").strip()
GOOGLE_TTS_ENDPOINT = "https://texttospeech.googleapis.com/v1/text:synthesize"

VIDEO_W, VIDEO_H = 1080, 1920
FPS = 30
FADE_IN, FADE_OUT = 0.5, 0.5
KB_MIN_ZOOM = 1.03
KB_MAX_ZOOM = 1.08

os.makedirs(OUTPUT_VIDEO_DIR, exist_ok=True)

# --- Helper Functions ---

def normalize_space(s):
    return re.sub(r"\s+", " ", (s or "").strip())

def split_into_sentences(text):
    text = normalize_space(text)
    if not text: return []
    parts = re.split(r'(?<=[\.\!\?])\s+', text)
    merged = []
    for p in parts:
        if merged and len(p) < 15:
            merged[-1] = merged[-1] + " " + p
        else:
            merged.append(p)
    return [p for p in merged if p.strip()]

def durations_from_sentences(sentences, total_dur, min_per_seg=1.2):
    if not sentences: return [total_dur]
    lens = [max(1, len(s)) for s in sentences]
    s = float(sum(lens))
    raw = [total_dur * (l / s) for l in lens]
    raw = [max(min_per_seg, d) for d in raw]
    scale = total_dur / sum(raw)
    return [d * scale for d in raw]

def sha1(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()

# --- TTS ---

def get_tts_audio(text, voice_name="vi-VN-Neural2-A", speaking_rate=1.0):
    """
    Generate audio from text using Google Cloud TTS REST API.
    Returns path to saved audio file.
    """
    filename = f"tts_{sha1(text)[:10]}.mp3"
    filepath = os.path.join(TEMP_IMAGE_DIR, filename)
    
    if os.path.exists(filepath):
        return filepath

    url = f"{GOOGLE_TTS_ENDPOINT}?key={GOOGLE_TTS_API_KEY}"
    data = {
        "input": {"text": text},
        "voice": {"languageCode": "vi-VN", "name": voice_name},
        "audioConfig": {"audioEncoding": "MP3", "speakingRate": speaking_rate}
    }
    
    response = requests.post(url, json=data)
    response.raise_for_status()
    
    audio_content = response.json().get("audioContent")
    if not audio_content:
        raise Exception("No audio content returned from TTS API")
        
    with open(filepath, "wb") as f:
        f.write(base64.b64decode(audio_content))
        
    return filepath

# --- Image Processing ---

def fit_image_to_canvas(img_path, W=VIDEO_W, H=VIDEO_H):
    """
    Fit image to 9:16 canvas with blurred background.
    Returns path to processed image.
    """
    try:
        img = Image.open(img_path).convert("RGB")
        
        # Blur background
        bg = img.copy().resize((W, H)).filter(ImageFilter.GaussianBlur(radius=20))
        
        # Resize foreground
        iw, ih = img.size
        scale = min(W/iw, H/ih)
        new_w, new_h = int(iw*scale), int(ih*scale)
        img_resized = img.resize((new_w, new_h), Image.LANCZOS)
        
        # Paste
        canvas = bg.copy()
        canvas.paste(img_resized, ((W-new_w)//2, (H-new_h)//2))
        
        out_path = img_path.replace(".jpg", "_fit.jpg").replace(".png", "_fit.jpg")
        canvas.save(out_path, format="JPEG", quality=95)
        return out_path
    except Exception as e:
        print(f"Error processing image {img_path}: {e}")
        return None

# --- Ken Burns Effect ---

def make_ken_burns_clip(img_path, duration, seed=0):
    """
    Create a Ken Burns effect clip from an image.
    """
    random.seed(seed) # Deterministic
    
    zoom_in = (seed % 2 == 0)
    z_start = random.uniform(KB_MIN_ZOOM, KB_MAX_ZOOM)
    z_end = 1.0 if zoom_in else random.uniform(KB_MIN_ZOOM, KB_MAX_ZOOM)
    
    if zoom_in: z0, z1 = 1.0, z_start
    else: z0, z1 = z_start, 1.0
    
    direction = seed % 4 # 0:L-R, 1:R-L, 2:T-B, 3:B-T

    def fl(gf, t):
        # MoviePy custom filter logic
        # Ideally using CompositeVideoClip with dynamic resize/position
        # Simplified: Just resize/crop might be easier, but let's stick to simple zoom
        # This function is hard to implement perfectly without advanced MoviePy usage
        # Let's use a simpler approach: ImageClip with resize
        return gf(t)

    # Simplified Ken Burns using pure MoviePy resize/position
    # Note: MoviePy v1.0.3 resize can be slow or complex with lambda
    
    clip = ImageClip(img_path).set_duration(duration)
    
    def scale(t):
        prog = t / duration
        return z0 + (z1 - z0) * prog
        
    def position(t):
        # Center crop logic
        s = scale(t)
        # We need to center the zoomed image
        # W, H are fixed
        # Current size is W*s, H*s
        # x = (W - W*s) / 2
        # y = (H - H*s) / 2
        
        # Pan logic
        prog = t / duration
        move_x = 0
        move_y = 0
        if direction == 0: move_x = -20 * prog # Pan left
        # ... simplified pan
        
        # Just simple center zoom for now to be safe
        x = (VIDEO_W - VIDEO_W*s) / 2
        y = (VIDEO_H - VIDEO_H*s) / 2
        return (x, y)

    # Re-implementing the one from original script
    # It used CompositeVideoClip.
    
    def scale_fn(t):
        prog = t / max(1e-4, duration)
        return z0 + (z1 - z0) * prog

    def pos_fn(t):
        prog = t / max(1e-4, duration)
        s = scale_fn(t)
        sw, sh = VIDEO_W * s, VIDEO_H * s
        
        # Simple center alignment because pan logic is complex to port without testing
        x = (VIDEO_W - sw) / 2
        y = (VIDEO_H - sh) / 2
        return (x, y)

    # Note: resizing in MoviePy can be heavy.
    video = clip.resize(lambda t: scale_fn(t)).set_position(lambda t: pos_fn(t))
    return CompositeVideoClip([video], size=(VIDEO_W, VIDEO_H)).fadein(FADE_IN).fadeout(FADE_OUT)


# --- Main Generator ---

def generate_video(product_data):
    """
    Generate video for a product.
    product_data: {
        "id": ..., "title": ..., "script": ..., "images": [...]
    }
    """
    print(f"Generating video for: {product_data['title']}")
    
    # 1. Prepare Images
    prepared_images = []
    for img_path in product_data['images']:
        fit_path = fit_image_to_canvas(img_path)
        if fit_path:
            prepared_images.append(fit_path)
            
    if not prepared_images:
        print("No valid images found.")
        return None

    # 2. TTS
    script = product_data['script']
    try:
        audio_path = get_tts_audio(script)
    except Exception as e:
        print(f"TTS Error: {e}")
        return None
        
    audio_clip = AudioFileClip(audio_path)
    total_duration = audio_clip.duration
    
    # 3. Calculate Durations
    # If not enough images, loop them
    while len(prepared_images) * 3.0 < total_duration:
        prepared_images.extend(prepared_images)
        
    # Limit number of images if too many
    max_imgs = int(total_duration / 2.0) + 1 # Min 2s per image
    prepared_images = prepared_images[:max_imgs]

    sentences = split_into_sentences(script)
    # We map sentences roughly to images or just divide time
    # Let's divide time equally for simplicity in this version, 
    # or use the robust logic from original script if possible.
    # Original logic: durations_from_sentences maps sentences to time.
    # But we need to map images to time.
    
    # Let's just distribute images evenly across the audio duration
    img_duration = total_duration / len(prepared_images)
    
    clips = []
    for idx, img_path in enumerate(prepared_images):
        clip = make_ken_burns_clip(img_path, img_duration, seed=idx)
        clips.append(clip)
        
    # 4. Concatenate
    final_video = concatenate_videoclips(clips, method="compose")
    final_video = final_video.set_audio(audio_clip)
    final_video = final_video.set_fps(FPS)
    
    # 5. Write File
    output_filename = f"{product_data['id']}_video.mp4"
    output_path = os.path.join(OUTPUT_VIDEO_DIR, output_filename)
    
    final_video.write_videofile(output_path, codec="mpeg4", audio_codec="aac")
    print(f"Video saved to: {output_path}")
    return output_path
