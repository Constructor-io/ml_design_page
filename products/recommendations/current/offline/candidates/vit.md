---
id: vit
title: "Image Similarity (ViT)"
position: 4
---

## ViT / Image Similarity

```
Model:          EfficientNet-B0 (default, pretrained ImageNet, S3 artifact)
                ViT-B/16 DINO (alternative)
                Marqo/marqo-fashionSigLIP (fashion OpenCLIP)
Input:          256x256 (EfficientNet), 224x224 (ViT/SigLIP)
Norm:           ImageNet mean/std
Embedding:      num_classes=0 (classifier head removed), feature layer output
Batch size:     256
Workers:        4
Hardware:       g5.2xlarge (scales to g5.8xlarge for catalogs >600K items)
Precision:      bfloat16 (CUDA AMP), channels-last memory format
```

No fine-tuning — pretrained features only.
