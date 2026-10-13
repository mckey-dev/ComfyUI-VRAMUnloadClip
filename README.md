# ComfyUI-VRAMUnloadClip

更新日: 2026-10-14

## 目的

CLIP / Text Encoder 利用後に Text Encoder を VRAM からアンロードし、後段（KSampler など）で使える VRAM を増やします。出力データ（CONDITIONING または生成テキスト）は変更しません。

## ノード

| 表示名 | 用途 |
|--------|------|
| **VRAM Unload CLIP (Prompt)** | `CLIP Text Encode` 後の positive / negative CONDITIONING |
| **VRAM Unload CLIP (Text)** | `Generate Text` / `Generate LTX2 Prompt` 後の generated_text / thinking |

## CLIP Text Encode（Prompt）

```text
Text Encode Positive ─┐
                      ├─ VRAM Unload CLIP (Prompt) → KSampler
Text Encode Negative ─┘
CLIP ─────────────────┘
```

Positive / Negative の両方のエンコードの後ろに置き、エンコードに使った CLIP を同じノードへ接続してください。

## Generate Text（Text）

```text
CLIP ── Generate Text ── VRAM Unload CLIP (Text) ── CLIP Text Encode（prompt に generated_text）
  └────────────────────────────────────────────────┘
```

`Generate Text` の直後に置き、同じ CLIP を Text ノードへ接続してください。`thinking` は使う場合のみ接続します。

## enabled

- **True:** ComfyUI の model management 経由で CLIP / Text Encoder を VRAM からアンロードします。
- **False:** アンロードせず、入力をそのまま通過させます。

既定値: **True**

## 注意

このノードより**後ろ**で同じ CLIP / Text Encoder を再度使うと、ComfyUI が VRAM へ再ロードする場合があります。

**CLIP / Generate Text を行う最後のノードより後ろ**かつ、**サンプリングなど VRAM を多く使う処理より前**に配置してください。
