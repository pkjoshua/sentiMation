#!/usr/bin/env python3
"""
Simple API call test to verify Automatic1111 connection
"""
import requests
import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "generators"))
from sd_api_config import get_api_url

def test_txt2img():
    """Test a simple txt2img call"""
    url = get_api_url('txt2img')
    print(f"🎯 Testing txt2img: {url}")
    
    payload = {
        "prompt": "a simple test image",
        "negative_prompt": "",
        "steps": 1,
        "width": 512,
        "height": 512,
        "sampler_name": "Euler a",
        "cfg_scale": 7,
        "batch_size": 1
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            print("🎉 API call successful! Automatic1111 is processing the request.")
        else:
            print(f"⚠️  Response: {response.text[:200]}...")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_img2img():
    """Test a simple img2img call"""
    url = get_api_url('img2img')
    print(f"\n🎯 Testing img2img: {url}")
    
    # Create a simple test image (1x1 pixel)
    import base64
    from PIL import Image
    import io
    
    # Create a tiny test image
    img = Image.new('RGB', (1, 1), color='red')
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_str = base64.b64encode(img_buffer.getvalue()).decode()
    
    payload = {
        "init_images": [img_str],
        "prompt": "a simple test image",
        "negative_prompt": "",
        "steps": 1,
        "width": 512,
        "height": 512,
        "sampler_name": "Euler a",
        "cfg_scale": 7,
        "denoising_strength": 0.5
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            print("🎉 API call successful! Automatic1111 is processing the request.")
        else:
            print(f"⚠️  Response: {response.text[:200]}...")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Automatic1111 API Connection")
    print("=" * 40)
    
    # Test txt2img
    txt2img_success = test_txt2img()
    
    # Test img2img
    img2img_success = test_img2img()
    
    print(f"\n📊 Results:")
    print(f"  txt2img: {'✅ SUCCESS' if txt2img_success else '❌ FAILED'}")
    print(f"  img2img: {'✅ SUCCESS' if img2img_success else '❌ FAILED'}")
    
    if txt2img_success and img2img_success:
        print(f"\n🎉 All tests passed! Your generators should now work correctly.")
    else:
        print(f"\n⚠️  Some tests failed. Check your Automatic1111 configuration.") 