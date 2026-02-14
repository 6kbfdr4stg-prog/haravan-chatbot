import sys
import os
import json
import base64
from unittest.mock import MagicMock

# Define the function as it is in the file (simplified for testing)
# We just want to test the chunking logic

CACHE_TTS_DIR = "/tmp/cache_tts"
os.makedirs(CACHE_TTS_DIR, exist_ok=True)
GOOGLE_TTS_API_KEY = "dummy_key"
GOOGLE_TTS_ENDPOINT = "dummy_url"
HTTP_TIMEOUT = 30
SESSION = MagicMock()
import hashlib

def sha1(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()

def split_into_sentences(text):
    import re
    _SENT_SPLIT_RE = re.compile(r'(?<=[\.\!\?…])\s+|\n+')
    text = text.strip()
    if not text: return []
    parts = [p.strip() for p in _SENT_SPLIT_RE.split(text) if p and p.strip()]
    return parts

def vbee_tts_get_audio_path_test(input_text):
    # Mocking the function logic
    MAX_BYTES = 4500
    chunks = []
    text_bytes_len = len(input_text.encode('utf-8'))
    
    if text_bytes_len < MAX_BYTES:
        chunks.append(input_text)
    else:
        sentences = split_into_sentences(input_text)
        current_chunk = ""
        for s in sentences:
            next_chunk = (current_chunk + " " + s).strip()
            if len(next_chunk.encode('utf-8')) < MAX_BYTES:
                current_chunk = next_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = s
        if current_chunk:
            chunks.append(current_chunk)
    
    # Check chunks size
    print(f"Original len: {text_bytes_len} bytes")
    print(f"Chunks: {len(chunks)}")
    for i, c in enumerate(chunks):
        clen = len(c.encode('utf-8'))
        print(f"  Chunk {i}: {clen} bytes")
        if clen > MAX_BYTES:
            print(f"  ❌ FAIL: Chunk {i} is {clen} bytes > {MAX_BYTES}")
            return False
            
    return True

# Test cases
long_text = "This is a sentence. " * 500 # ~ 10000 bytes
print("Testing long text...")
vbee_tts_get_audio_path_test(long_text)

print("\nTesting short text...")
vbee_tts_get_audio_path_test("Short text.")

