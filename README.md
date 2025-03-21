# ComfyUI Jewelry Model API

Bu Replicate modeli, ComfyUI ve Gemini 2.0 Flash API kullanarak bir takı resmini alıp, bu takıyı giymiş bir kadının görüntüsünü oluşturur.

## Kullanım

Model için aşağıdaki parametreleri kullanabilirsiniz:

- `jewelry_image`: Takı resmi (jpeg, png, vb.)
- `prompt`: Model için istek metni (varsayılan: "woman wear this jewelry")
- `api_key`: Gemini API anahtarı (opsiyonel)
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
        "api_key": "GEMINI_API_KEY",  # Opsiyonel
        "seed": 1234
    }
)

print(output)
```

## Gereksinimler

Model, IF_LLM eklentisinin 2.4.0 veya daha yeni sürümünü kullanır.

## Not

Bu API, Gemini'nin API sınırlamalarına tabidir. Kendi API anahtarınızı kullanmanız önerilir.