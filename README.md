# ComfyUI Jewelry Model API

Bu Replicate modeli, ComfyUI ve Gemini 2.0 Flash API kullanarak bir takı resmini alıp, bu takıyı giymiş bir kadının görüntüsünü oluşturur.

## Environment Setup (Required)

This project requires a Google Gemini API key to function. Set up your environment:

1. Copy the `.env.example` file to create your own `.env` file:
```bash
cp .env.example .env
```

2. Edit the `.env` file and add your Google Gemini API key:
```
GOOGLE_GEMINI_API_KEY=your_api_key_here
```

You can obtain a Gemini API key from [Google AI Studio](https://ai.google.dev/).

## Kullanım

Model için aşağıdaki parametreleri kullanabilirsiniz:

- `jewelry_image`: Takı resmi (jpeg, png, vb.)
- `prompt`: Model için istek metni (varsayılan: "woman wear this jewelry")
- `api_key`: Gemini API anahtarı (opsiyonel, .env dosyasında tanımlanabilir)
- `seed`: Sonuçların tutarlılığı için seed değeri (varsayılan: 1222)

## Nasıl Çalışır

1. Sisteme bir takı resmi yüklersiniz
2. ComfyUI ortamı yüklenen resmi alır
3. IF_LLM eklentisi aracılığıyla Gemini API'ye gönderir
4. Gemini API, takıyı bir modelin üzerinde gösterildiği bir resim oluşturur
5. Sonuç resmi size döndürülür

## API Örneği

```python
import replicate

output = replicate.run(
    "kullanıcıadı/model-adı:versiyon",
    input={
        "jewelry_image": open("takı.png", "rb"),
        "prompt": "woman wear this necklace",
        "api_key": "GEMINI_API_KEY",  # Opsiyonel, .env dosyasında tanımlanabilir
        "seed": 1234
    }
)

print(output)
```

## Gereksinimler

Model, IF_LLM eklentisinin 2.4.0 veya daha yeni sürümünü kullanır.

## Not

Bu API, Gemini'nin API sınırlamalarına tabidir. Kendi API anahtarınızı kullanmanız önerilir.

## Running the Project

To run the project:

```bash
cog predict -i jewelry_image=@your_image.png
```

You can also pass the API key directly as a parameter (overrides the .env file):
```bash
cog predict -i jewelry_image=@your_image.png -i api_key=your_api_key_here
```