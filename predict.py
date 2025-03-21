import os
import sys
import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path as SystemPath
from typing import Any, List
import google.generativeai as genai
from cog import BasePredictor, Input, Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ComfyUI ve eklentiler için dizinler
COMFY_REPO = "https://github.com/comfyanonymous/ComfyUI.git"
IF_LLM_REPO = "https://github.com/if-ai/ComfyUI-IF_LLM.git"

class Predictor(BasePredictor):
    def setup(self):
        """
        Kurulum sırasında ComfyUI ve eklentileri yükler
        """
        # ComfyUI reposunu klonlama (yoksa)
        if not os.path.exists("ComfyUI"):
            subprocess.run(["git", "clone", COMFY_REPO], check=True)
        
        # ComfyUI ortamını kurma
        subprocess.run(["pip", "install", "-r", "ComfyUI/requirements.txt"], check=True)
        
        # IF_LLM eklentisini kurma
        os.makedirs("ComfyUI/custom_nodes", exist_ok=True)
        if not os.path.exists("ComfyUI/custom_nodes/ComfyUI-IF_LLM"):
            subprocess.run(["git", "clone", IF_LLM_REPO, "ComfyUI/custom_nodes/ComfyUI-IF_LLM"], check=True)
            subprocess.run(["pip", "install", "-r", "ComfyUI/custom_nodes/ComfyUI-IF_LLM/requirements.txt"], check=True)
        
        # Çalışma dizinleri oluşturma
        os.makedirs("input", exist_ok=True)
        os.makedirs("output", exist_ok=True)
        
        # ComfyUI'nin Python yolunu ekle
        sys.path.append("ComfyUI")

    def predict(
        self,
        jewelry_image: Path = Input(description="Takı resmi"),
        prompt: str = Input(description="Prompt (örn: 'woman wear this jewelry')", default="woman wear this jewelry"),
        api_key: str = Input(description="Gemini API Key", default=None),
        seed: int = Input(description="Seed değeri", default=1222),
    ) -> List[Path]:
        """
        Takı resmini alıp, Gemini API ile bir mankene giydirilmiş halini döndürür
        """
        # API anahtarını ayarla - önce parametreden, sonra .env'den
        gemini_api_key = api_key or os.getenv("GOOGLE_GEMINI_API_KEY")
        
        if not gemini_api_key:
            raise ValueError("API key is required. Please provide it either through the api_key parameter or set it in the .env file.")
            
        os.environ["GOOGLE_API_KEY"] = gemini_api_key

        # Giriş ve çıkış dizinlerini temizle
        for file in os.listdir("input"):
            os.remove(os.path.join("input", file))
        for file in os.listdir("output"):
            os.remove(os.path.join("output", file))
        
        # Takı resmini input dizinine kopyala
        input_path = os.path.join("input", f"jewelry_{int(time.time())}.png")
        shutil.copy(jewelry_image, input_path)
        
        # Workflow JSON oluştur
        workflow = {
            "6": {
                "inputs": {
                    "image": os.path.basename(input_path)
                },
                "class_type": "LoadImage",
                "_meta": {
                    "title": "Load Image"
                }
            },
            "7": {
                "inputs": {
                    "filename_prefix": "ComfyUI",
                    "images": [
                        "8",
                        4
                    ]
                },
                "class_type": "SaveImage",
                "_meta": {
                    "title": "Save Image"
                }
            },
            "8": {
                "inputs": {
                    "llm_provider": "gemini",
                    "llm_model": "gemini-2.0-flash-exp",
                    "base_ip": "localhost",
                    "port": "11434",
                    "user_prompt": prompt,
                    "strategy": "gemini2_create",
                    "profiles": "None",
                    "embellish_prompt": "None",
                    "style_prompt": "None",
                    "neg_prompt": "None",
                    "stop_string": "None",
                    "max_tokens": 2048,
                    "random": False,
                    "seed": seed,
                    "keep_alive": True,
                    "clear_history": True,
                    "history_steps": 10,
                    "aspect_ratio": "1:1",
                    "auto": False,
                    "batch_count": 1,
                    "external_api_key": gemini_api_key,
                    "attention": "sdpa",
                    "Store Auto Prompt": None,
                    "images": [
                        "6",
                        0
                    ]
                },
                "class_type": "IF_LLM",
                "_meta": {
                    "title": "IF LLM🎨"
                }
            }
        }
        
        # Workflow dosyasını oluştur
        with open("workflow.json", "w") as f:
            json.dump(workflow, f, indent=2)
        
        # ComfyUI'yi API modunda çalıştır ve workflow'u işle
        comfy_dir = os.path.abspath("ComfyUI")
        
        # API'yi başlat (arka planda)
        api_process = subprocess.Popen(
            [sys.executable, "main.py", "--port", "8188", "--listen", "0.0.0.0"],
            cwd=comfy_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # API'nin başlaması için bekle
        time.sleep(5)
        
        try:
            # Workflow'u gönder ve işle
            import requests
            
            # Prompt queue endpoint
            queue_url = "http://127.0.0.1:8188/prompt"
            
            # Workflow'u gönder
            response = requests.post(
                queue_url,
                json={"prompt": workflow}
            )
            
            if response.status_code != 200:
                raise RuntimeError(f"Error submitting workflow: {response.text}")
            
            # İşlem ID'sini al
            prompt_id = response.json()["prompt_id"]
            
            # İşlemin tamamlanmasını bekle
            while True:
                time.sleep(1)
                history_url = f"http://127.0.0.1:8188/history/{prompt_id}"
                history_response = requests.get(history_url)
                
                if history_response.status_code == 200:
                    history_data = history_response.json()
                    if history_data.get(prompt_id, {}).get("status", {}).get("status") == "success":
                        break
                    elif history_data.get(prompt_id, {}).get("status", {}).get("status") == "error":
                        error_msg = history_data.get(prompt_id, {}).get("status", {}).get("error", "Unknown error")
                        raise RuntimeError(f"Workflow failed: {error_msg}")
            
            # Oluşturulan görüntüleri bul
            output_images = []
            for filename in os.listdir("ComfyUI/output"):
                if filename.startswith("ComfyUI_"):
                    src_path = os.path.join("ComfyUI/output", filename)
                    dest_path = os.path.join("output", filename)
                    shutil.copy(src_path, dest_path)
                    output_images.append(Path(dest_path))
            
            return output_images
        
        finally:
            # API'yi kapat
            api_process.terminate()
            api_process.wait()

    def _cleanup_temp_files(self):
        """Geçici dosyaları temizle"""
        for dir_path in ["input", "output"]:
            if os.path.exists(dir_path):
                for file in os.listdir(dir_path):
                    os.remove(os.path.join(dir_path, file))