"""CLIP / Text Encoder を VRAM から安全にアンロードする ComfyUI ノード（Prompt / Text 用）。"""

import time

import comfy.model_management as model_management

_LOG_PREFIX = "[VRAMUnloadClip]"


def _free_vram_mib(device):
    """指定デバイスの空き VRAM を MiB で返す。取得に失敗した場合は None。"""
    try:
        return model_management.get_free_memory(device) / (1024 * 1024)
    except Exception:
        return None


def _unload_clip_from_vram(clip, log_prefix=_LOG_PREFIX):
    """clip.patcher を model management 経由でアンロードする。成功時 True。"""
    print(f"{log_prefix} Requesting CLIP/Text Encoder unload...")

    patcher = getattr(clip, "patcher", None)
    if patcher is None:
        print(f"{log_prefix} CLIP patcher not found. Skipping unload.")
        return False

    device = getattr(patcher, "load_device", None)
    if device is None:
        device = model_management.get_torch_device()

    free_before = _free_vram_mib(device)
    if free_before is not None:
        print(f"{log_prefix} Free VRAM before: {free_before:.0f} MiB")

    try:
        model_management.unload_model_and_clones(patcher)
    except Exception as e:
        print(f"{log_prefix} WARNING: unload failed: {e}")
        return False

    free_after = _free_vram_mib(device)
    if free_after is not None:
        print(f"{log_prefix} Free VRAM after : {free_after:.0f} MiB")
        if free_before is not None:
            freed = free_after - free_before
            print(f"{log_prefix} Freed approximately: {freed:.0f} MiB")

    print(f"{log_prefix} Unload completed.")
    return True


class VRAMUnloadClip:
    """CONDITIONING を変更せず通過させ、任意で clip.patcher をアンロードする。"""

    NOT_IDEMPOTENT = True

    @classmethod
    def INPUT_TYPES(cls):
        """ノード入力ソケット定義。"""
        return {
            "required": {
                "enabled": ("BOOLEAN", {"default": True}),
                "positive": ("CONDITIONING",),
                "negative": ("CONDITIONING",),
                "clip": ("CLIP",),
            }
        }

    RETURN_TYPES = ("CONDITIONING", "CONDITIONING")
    RETURN_NAMES = ("positive", "negative")
    FUNCTION = "unload"
    CATEGORY = "VRAM Tools/Unload"

    @classmethod
    def IS_CHANGED(cls, enabled, positive, negative, clip):
        """Queue ごとに実行されるようキャッシュキーを毎回変える。"""
        return time.time()

    def unload(self, enabled, positive, negative, clip):
        """enabled に応じて CLIP アンロードを行い、入力 CONDITIONING をそのまま返す。"""
        if not enabled:
            print(f"{_LOG_PREFIX} Disabled. Passing conditioning through.")
            return (positive, negative)

        print(f"{_LOG_PREFIX} Enabled.")
        _unload_clip_from_vram(clip)
        return (positive, negative)


class VRAMUnloadClipText:
    """Generate Text の STRING を通過させ、任意で clip.patcher をアンロードする。"""

    NOT_IDEMPOTENT = True

    @classmethod
    def INPUT_TYPES(cls):
        """ノード入力ソケット定義。"""
        return {
            "required": {
                "enabled": ("BOOLEAN", {"default": True}),
                "clip": ("CLIP",),
                "generated_text": ("STRING", {"forceInput": True}),
            },
            "optional": {
                "thinking": ("STRING", {"forceInput": True}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("generated_text", "thinking")
    FUNCTION = "unload"
    CATEGORY = "VRAM Tools/Unload"

    @classmethod
    def IS_CHANGED(cls, enabled, clip, generated_text, thinking=""):
        """Queue ごとに実行されるようキャッシュキーを毎回変える。"""
        return time.time()

    def unload(self, enabled, clip, generated_text, thinking=""):
        """enabled に応じて CLIP アンロードを行い、入力文字列をそのまま返す。"""
        if not enabled:
            print(f"{_LOG_PREFIX} Disabled. Passing text through.")
            return (generated_text, thinking)

        print(f"{_LOG_PREFIX} Enabled.")
        _unload_clip_from_vram(clip)
        return (generated_text, thinking)


NODE_CLASS_MAPPINGS = {
    "VRAMUnloadClip": VRAMUnloadClip,
    "VRAMUnloadClipText": VRAMUnloadClipText,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VRAMUnloadClip": "VRAM Unload CLIP (Prompt)",
    "VRAMUnloadClipText": "VRAM Unload CLIP (Text)",
}
