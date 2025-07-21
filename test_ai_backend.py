#!/usr/bin/env python3
"""
Comprehensive AI Backend Testing Script
Tests both Basic Pitch and Coqui TTS services
"""

import requests
import base64
import json
import time
import librosa
import numpy as np
import io
import sys
from typing import Dict, Any

class AIBackendTester:
    def __init__(self):
        self.basic_pitch_url = "http://localhost:8001"
        self.coqui_tts_url = "http://localhost:8002"
        
    def test_basic_pitch_health(self) -> Dict[str, Any]:
        """Test Basic Pitch service health"""
        try:
            response = requests.get(f"{self.basic_pitch_url}/health", timeout=5)
            return {
                "status": "success" if response.status_code == 200 else "failed",
                "data": response.json() if response.status_code == 200 else None,
                "error": None
            }
        except Exception as e:
            return {"status": "failed", "data": None, "error": str(e)}
    
    def test_coqui_tts_health(self) -> Dict[str, Any]:
        """Test Coqui TTS service health"""
        try:
            response = requests.get(f"{self.coqui_tts_url}/health", timeout=5)
            return {
                "status": "success" if response.status_code == 200 else "failed",
                "data": response.json() if response.status_code == 200 else None,
                "error": None
            }
        except Exception as e:
            return {"status": "failed", "data": None, "error": str(e)}
    
    def generate_test_audio(self, duration=2, sample_rate=22050) -> str:
        """Generate a simple test audio (sine wave) and return as base64"""
        t = np.linspace(0, duration, int(sample_rate * duration))
        # Create a simple melody: C4 (261.63 Hz) for 1 second, then E4 (329.63 Hz) for 1 second
        frequency1, frequency2 = 261.63, 329.63
        audio = np.concatenate([
            np.sin(2 * np.pi * frequency1 * t[:sample_rate]),
            np.sin(2 * np.pi * frequency2 * t[sample_rate:])
        ])
        
        # Normalize audio
        audio = audio / np.max(np.abs(audio))
        
        # Convert to bytes
        buffer = io.BytesIO()
        import soundfile as sf
        sf.write(buffer, audio, sample_rate, format='WAV')
        buffer.seek(0)
        
        # Encode to base64
        audio_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        return audio_base64
    
    def test_melody_extraction(self) -> Dict[str, Any]:
        """Test Basic Pitch melody extraction with generated audio"""
        try:
            # Generate test audio
            audio_base64 = self.generate_test_audio()
            
            payload = {"audio": audio_base64}
            response = requests.post(
                f"{self.basic_pitch_url}/extract-melody",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success",
                    "data": result,
                    "error": None
                }
            else:
                return {
                    "status": "failed",
                    "data": None,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {"status": "failed", "data": None, "error": str(e)}
    
    def test_text_to_speech(self, text="Hello, this is a test of the TTS service") -> Dict[str, Any]:
        """Test Coqui TTS text-to-speech"""
        try:
            payload = {"text": text}
            response = requests.post(
                f"{self.coqui_tts_url}/synthesize",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success",
                    "data": result,
                    "error": None
                }
            else:
                return {
                    "status": "failed",
                    "data": None,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {"status": "failed", "data": None, "error": str(e)}
    
    def run_comprehensive_test(self):
        """Run all tests and provide a comprehensive report"""
        print("🎵 AI SINGER BACKEND COMPREHENSIVE TEST 🎵")
        print("=" * 50)
        
        # Test 1: Basic Pitch Health
        print("\n1. Testing Basic Pitch Service Health...")
        bp_health = self.test_basic_pitch_health()
        if bp_health["status"] == "success":
            print("✅ Basic Pitch service is healthy!")
            print(f"   Response: {bp_health['data']}")
        else:
            print("❌ Basic Pitch service health check failed!")
            print(f"   Error: {bp_health['error']}")
        
        # Test 2: Coqui TTS Health  
        print("\n2. Testing Coqui TTS Service Health...")
        tts_health = self.test_coqui_tts_health()
        if tts_health["status"] == "success":
            print("✅ Coqui TTS service is healthy!")
            print(f"   Response: {tts_health['data']}")
        else:
            print("❌ Coqui TTS service health check failed!")
            print(f"   Error: {tts_health['error']}")
        
        # Test 3: Melody Extraction (only if Basic Pitch is healthy)
        if bp_health["status"] == "success":
            print("\n3. Testing Melody Extraction...")
            melody_test = self.test_melody_extraction()
            if melody_test["status"] == "success":
                print("✅ Melody extraction working!")
                data = melody_test["data"]
                if "notes" in data:
                    print(f"   Extracted {len(data['notes'])} notes")
                if "midi_data" in data:
                    print(f"   MIDI data size: {len(data['midi_data'])} bytes")
            else:
                print("❌ Melody extraction failed!")
                print(f"   Error: {melody_test['error']}")
        
        # Test 4: Text-to-Speech (only if TTS is healthy)
        if tts_health["status"] == "success":
            print("\n4. Testing Text-to-Speech...")
            tts_test = self.test_text_to_speech()
            if tts_test["status"] == "success":
                print("✅ Text-to-speech working!")
                data = tts_test["data"]
                if "audio" in data:
                    print(f"   Generated audio data size: {len(data['audio'])} bytes")
            else:
                print("❌ Text-to-speech failed!")
                print(f"   Error: {tts_test['error']}")
        
        # Final Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        services_status = {
            "Basic Pitch Health": bp_health["status"],
            "Coqui TTS Health": tts_health["status"]
        }
        
        if bp_health["status"] == "success":
            melody_result = self.test_melody_extraction()
            services_status["Melody Extraction"] = melody_result["status"]
            
        if tts_health["status"] == "success":
            tts_result = self.test_text_to_speech()
            services_status["Text-to-Speech"] = tts_result["status"]
        
        for service, status in services_status.items():
            icon = "✅" if status == "success" else "❌"
            print(f"{icon} {service}: {status.upper()}")
        
        total_tests = len(services_status)
        passed_tests = sum(1 for status in services_status.values() if status == "success")
        
        print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL SYSTEMS GO! AI Singer backend is fully operational!")
        elif passed_tests > 0:
            print("⚠️  Partial functionality - some services are working")
        else:
            print("🚨 System down - all services are failing")

if __name__ == "__main__":
    try:
        import soundfile as sf
    except ImportError:
        print("Installing required dependency: soundfile")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "soundfile"])
        import soundfile as sf
    
    tester = AIBackendTester()
    tester.run_comprehensive_test()
