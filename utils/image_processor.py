import io
import base64
from PIL import Image
import torch
import torchvision.transforms as transforms

# Define ImageNet normalization standard matching model training setup
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

def get_inference_transforms():
    """
    Returns the standard TorchVision transform pipeline used for model evaluation.
    Resizes image to 256x256, crops center 224x224, converts to PyTorch tensor, 
    and normalizes with ImageNet mean and std.
    """
    return transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])

def process_image(image_input):
    """
    Accepts a PIL Image, binary bytes, or file path,
    converts to RGB, applies TorchVision transforms, and adds batch dimension (B=1, C=3, H=224, W=224).
    """
    if isinstance(image_input, str):
        # File path
        pil_image = Image.open(image_input)
    elif isinstance(image_input, bytes):
        # Bytes stream
        pil_image = Image.open(io.BytesIO(image_input))
    elif isinstance(image_input, Image.Image):
        pil_image = image_input
    else:
        raise ValueError("Unsupported image input type for processing.")
        
    # Ensure 3-channel RGB format
    if pil_image.mode != "RGB":
        pil_image = pil_image.convert("RGB")
        
    transform_fn = get_inference_transforms()
    tensor_img = transform_fn(pil_image)
    
    # Add batch dimension -> Shape: [1, 3, 224, 224]
    tensor_batch = tensor_img.unsqueeze(0)
    return tensor_batch, pil_image

def decode_base64_image(base64_str):
    """
    Decodes a base64 encoded data URI (e.g. from camera snapshot canvas)
    into a PIL RGB Image.
    """
    if "," in base64_str:
        base64_str = base64_str.split(",")[1]
    image_bytes = base64.b64decode(base64_str)
    pil_image = Image.open(io.BytesIO(image_bytes))
    if pil_image.mode != "RGB":
        pil_image = pil_image.convert("RGB")
    return pil_image
