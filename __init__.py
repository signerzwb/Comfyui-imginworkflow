# -*- coding: utf-8 -*-
from.nodes import Base64ImageProcessor

NODE_MAPPINGS = {
    'ImageUploadNode': ('imginworkflow工作流里存图片', Base64ImageProcessor)

}

NODE_CLASS_MAPPINGS = {k: v[1] for k, v in NODE_MAPPINGS.items()}
NODE_DISPLAY_NAME_MAPPINGS = {k: v[0] for k, v in NODE_MAPPINGS.items()}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']