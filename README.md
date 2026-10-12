# ComfyUI-VRAMUnloadClip

更新日: 2026-10-13

## 目的

CLIP / Text Encoder による CONDITIONING 生成のあと、Text Encoder を VRAM からアンロードし、後段（KSampler など）で使える VRAM を増やします。

## 使い方

```text
Text Encode Positive ─┐
                      ├─ VRAM Unload CLIP → KSampler
Text Encode Negative ─┘
CLIP ─────────────────┘
```

Positive / Negative の両方のエンコードの後ろに置き、エンコードに使った CLIP を同じノードへ接続してください。

## enabled

- **True:** ComfyUI の model management 経由で CLIP / Text Encoder を VRAM からアンロードします。
- **False:** アンロードせず、CONDITIONING をそのまま通過させます。

既定値: **True**

## 動作

positive / negative の CONDITIONING は変更しません。ノードは通過のみ行い、enabled が True のとき CLIP モデルのアンロードを試みます。

## 注意

このノードより**後ろ**で同じ CLIP / Text Encoder を再度使うと、ComfyUI が VRAM へ再ロードする場合があります。

**テキストエンコードを行う最後のノードより後ろ**かつ、**サンプリングなど VRAM を多く使う処理より前**に配置してください。
