"""CONDITIONING 生成後に CLIP / Text Encoder を VRAM から安全にアンロードする ComfyUI ノード。"""

import time

import comfy.model_management as model_management


def _free_vram_mib(device):
    """指定デバイスの空き VRAM を MiB で返す。取得に失敗した場合は None。"""
    try:
        return model_management.get_free_memory(device) / (1024 * 1024)
    except Exception:
        return None


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
            print("[VRAMUnloadClip] Disabled. Passing conditioning through.")
            return (positive, negative)

        print("[VRAMUnloadClip] Enabled.")
        print("[VRAMUnloadClip] Requesting CLIP/Text Encoder unload...")

        patcher = getattr(clip, "patcher", None)
        if patcher is None:
            print("[VRAMUnloadClip] CLIP patcher not found. Skipping unload.")
            return (positive, negative)

        device = getattr(patcher, "load_device", None)
        if device is None:
            device = model_management.get_torch_device()

        free_before = _free_vram_mib(device)
        if free_before is not None:
            print(f"[VRAMUnloadClip] Free VRAM before: {free_before:.0f} MiB")

        try:
            model_management.unload_model_and_clones(patcher)
        except Exception as e:
            print(f"[VRAMUnloadClip] WARNING: unload failed: {e}")
            return (positive, negative)

        free_after = _free_vram_mib(device)
        if free_after is not None:
            print(f"[VRAMUnloadClip] Free VRAM after : {free_after:.0f} MiB")
            if free_before is not None:
                freed = free_after - free_before
                print(f"[VRAMUnloadClip] Freed approximately: {freed:.0f} MiB")

        print("[VRAMUnloadClip] Unload completed.")
        return (positive, negative)


NODE_CLASS_MAPPINGS = {
    "VRAMUnloadClip": VRAMUnloadClip,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VRAMUnloadClip": "VRAM Unload CLIP",
}
