import base64
import io
import torch
import numpy as np
from PIL import Image
import binascii

class Base64ImageProcessor:
    def __init__(self):
        self.last_b64 = ""  # 状态保持

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "compress_level": ("INT", {"default": 4, "min": 0, "max": 9}),
            },
            "optional": {
                "images": ("IMAGE",),
                "manual_base64": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "dynamicPrompts": False
                }),
            },
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("images", "base64_str")
    FUNCTION = "process"
    CATEGORY = "Image Processing"

    def process(self, compress_level=4, images=None, manual_base64=""):
        try:
            # 优先级：图像输入 > 手动输入
            if images is not None:
                # 图像编码模式
                encoded_b64 = self.encode_images(images, compress_level)
                return (images, encoded_b64)
            elif manual_base64.strip():
                # Base64解码模式
                img_tensor, processed_b64 = self.decode_base64(manual_base64)
                return (img_tensor, processed_b64)
            else:
                raise ValueError("需要提供图像输入或Base64字符串")

        except Exception as e:
            error_msg = f"❗ 错误: {str(e)}"
            return (None, error_msg)

    def decode_base64(self, base64_str):
        """强化版Base64解码方法"""
        try:
            if "base64," in base64_str:
                header, data = base64_str.split(",", 1)
                mime_type = header.split(":")[1].split(";")[0]
            else:
                data = base64_str
                mime_type = "image/png"

            if not data:
                raise ValueError("空Base64内容")
            
            decoded = base64.b64decode(data, validate=True)
            
            img = Image.open(io.BytesIO(decoded))
            img.verify()
            
            img = Image.open(io.BytesIO(decoded))
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")
            
            img_np = np.array(img).astype(np.float32) / 255.0
            if img_np.ndim == 2:
                img_np = np.expand_dims(img_np, axis=-1)
                img_np = np.repeat(img_np, 3, axis=-1)
                
            tensor_out = torch.from_numpy(img_np).unsqueeze(0)
            
            processed_b64 = f"data:{mime_type};base64,{data}"
            return tensor_out, processed_b64

        except binascii.Error as e:
            raise ValueError(f"Base64解码失败: {str(e)}")
        except (IOError, Image.DecompressionBombError) as e:
            raise ValueError(f"图像解析失败: {str(e)}")

    def encode_images(self, images, compress_level):
        """图像编码方法（自动覆盖manual_base64）"""
        if not isinstance(images, torch.Tensor) or images.dim() != 4:
            raise ValueError(f"输入应为4D张量，实际维度: {images.dim()}")
        
        images = torch.clamp(images, 0.0, 1.0)
        
        b64_list = []
        for i in range(images.size(0)):
            img_np = (images[i].cpu().numpy() * 255).astype(np.uint8)
            
            # 通道标准化
            if img_np.shape[-1] == 1:
                img_np = np.repeat(img_np, 3, axis=-1)
            elif img_np.shape[-1] == 4:
                img_np = img_np[..., :3]
            
            buffer = io.BytesIO()
            Image.fromarray(img_np).save(
                buffer,
                format="PNG",
                compress_level=compress_level,
                optimize=compress_level > 0
            )
            b64 = base64.b64encode(buffer.getvalue()).decode()
            b64_list.append(f"data:image/png;base64,{b64}")
            
        return "\n".join(b64_list)

NODE_CLASS_MAPPINGS = {"Base64ImageProcessor": Base64ImageProcessor}
NODE_DISPLAY_NAME_MAPPINGS = {"Base64ImageProcessor": "🔄 Base64双向处理器"}
