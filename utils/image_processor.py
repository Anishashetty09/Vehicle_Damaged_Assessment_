import io
import base64
import hashlib
import numpy as np
from PIL import Image, ImageStat, ImageEnhance
import torch
import torch.nn.functional as F
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

def check_image_quality(pil_image):
    """
    Analyzes brightness, contrast, and clarity of a PIL Image.
    Returns quality score (0-100), warnings list, and boolean indicator.
    """
    if pil_image.mode != "RGB":
        gray_img = pil_image.convert("L")
    else:
        gray_img = pil_image.convert("L")
        
    stat = ImageStat.Stat(gray_img)
    mean_brightness = stat.mean[0] # Average luminance (0-255)
    std_dev = stat.stddev[0]        # Standard deviation (measures contrast / variation)
    
    warnings = []
    quality_score = 100
    
    # 1. Darkness check
    if mean_brightness < 45:
        warnings.append("Low lighting / dark image detected.")
        quality_score -= 30
    elif mean_brightness > 230:
        warnings.append("Overexposed / extremely bright image detected.")
        quality_score -= 25
        
    # 2. Blur / low contrast check
    if std_dev < 20:
        warnings.append("Low contrast or potentially blurry image detected.")
        quality_score -= 35

    is_good_quality = len(warnings) == 0
    return {
        "is_good_quality": is_good_quality,
        "quality_score": max(0, min(100, int(quality_score))),
        "brightness": round(mean_brightness, 1),
        "contrast_std": round(std_dev, 1),
        "quality_warnings": warnings
    }

def compute_image_hash(pil_image):
    """
    Computes Difference Hashing (dHash) for rotational, scale, and lighting invariant duplicate detection.
    """
    gray = pil_image.convert("L").resize((9, 8), Image.Resampling.BILINEAR)
    pixels = np.array(gray, dtype=np.int32)
    # Difference between adjacent pixels
    diff = pixels[:, 1:] > pixels[:, :-1]
    # Convert boolean array to hex hash string
    decimal_val = 0
    hash_bits = []
    for bit in diff.flatten():
        hash_bits.append("1" if bit else "0")
    binary_str = "".join(hash_bits)
    return hex(int(binary_str, 2))[2:].zfill(16)

def process_image(image_input):
    """
    Accepts a PIL Image, binary bytes, or file path,
    converts to RGB, applies TorchVision transforms, and adds batch dimension (B=1, C=3, H=224, W=224).
    """
    if isinstance(image_input, str):
        pil_image = Image.open(image_input)
    elif isinstance(image_input, bytes):
        pil_image = Image.open(io.BytesIO(image_input))
    elif isinstance(image_input, Image.Image):
        pil_image = image_input
    else:
        raise ValueError("Unsupported image input type for processing.")
        
    if pil_image.mode != "RGB":
        pil_image = pil_image.convert("RGB")
        
    transform_fn = get_inference_transforms()
    tensor_img = transform_fn(pil_image)
    tensor_batch = tensor_img.unsqueeze(0)
    return tensor_batch, pil_image

def get_tta_tensors(pil_image):
    """
    Test-Time Augmentation (TTA):
    Returns 3 tensor variations (Standard, Horizontal Flip, Slightly Scaled)
    to eliminate angle/noise variance and improve prediction stability.
    """
    if pil_image.mode != "RGB":
        pil_image = pil_image.convert("RGB")

    transform_std = get_inference_transforms()
    
    transform_flip = transforms.Compose([
        transforms.Resize(256),
        transforms.RandomHorizontalFlip(p=1.0),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])
    
    transform_scale = transforms.Compose([
        transforms.Resize(280),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])

    t1 = transform_std(pil_image).unsqueeze(0)
    t2 = transform_flip(pil_image).unsqueeze(0)
    t3 = transform_scale(pil_image).unsqueeze(0)

    return torch.cat([t1, t2, t3], dim=0)

def generate_gradcam_heatmap(model, input_tensor, device, target_class=0):
    """
    Computes Grad-CAM (Gradient-weighted Class Activation Mapping) for ResNet-18 layer4.
    Returns a normalized 2D NumPy array heatmap (224x224, values 0.0 to 1.0).
    """
    model.eval()
    activations = []
    gradients = []

    def forward_hook(module, input, output):
        activations.append(output)

    def backward_hook(module, grad_in, grad_out):
        gradients.append(grad_out[0])

    # Hook into final conv layer (layer4) of ResNet-18
    target_layer = model.model.layer4
    h_fwd = target_layer.register_forward_hook(forward_hook)
    h_bwd = target_layer.register_full_backward_hook(backward_hook)

    try:
        input_var = input_tensor[:1].to(device).requires_grad_(True)
        logits = model(input_var)

        score = logits[0, target_class]
        model.zero_grad()
        score.backward()

        act = activations[0].detach().cpu().numpy()[0]   # Shape: (512, 7, 7)
        grad = gradients[0].detach().cpu().numpy()[0]    # Shape: (512, 7, 7)

        # Global Average Pooling on gradients -> alpha weights
        weights = np.mean(grad, axis=(1, 2))

        # Weighted combination of activation maps
        cam = np.zeros(act.shape[1:], dtype=np.float32)
        for i, w in enumerate(weights):
            cam += w * act[i]

        # ReLU activation (keep positive influences)
        cam = np.maximum(cam, 0)

        # Resize to 224x224 using PIL
        cam_img = Image.fromarray(cam)
        cam_resized = cam_img.resize((224, 224), Image.Resampling.BILINEAR)
        cam_arr = np.array(cam_resized)

        # Normalize to [0, 1]
        max_val = np.max(cam_arr)
        if max_val > 0:
            cam_arr = cam_arr / max_val
        else:
            cam_arr = np.zeros_like(cam_arr)

        return cam_arr

    except Exception as e:
        print(f"[WARNING] Grad-CAM computation failed: {e}")
        return np.zeros((224, 224), dtype=np.float32)
    finally:
        h_fwd.remove()
        h_bwd.remove()

def overlay_heatmap_on_image(original_pil, heatmap_2d):
    """
    Overlays a 2D float heatmap (0.0-1.0) on top of the original PIL image
    using JET colormap styling and returns a blended PIL Image.
    """
    resized_orig = original_pil.resize((224, 224), Image.Resampling.BILINEAR)
    orig_np = np.array(resized_orig, dtype=np.float32)

    # Apply JET colormap
    r = np.clip(1.5 - np.abs(heatmap_2d * 4.0 - 3.0), 0.0, 1.0)
    g = np.clip(1.5 - np.abs(heatmap_2d * 4.0 - 2.0), 0.0, 1.0)
    b = np.clip(1.5 - np.abs(heatmap_2d * 4.0 - 1.0), 0.0, 1.0)
    jet_np = np.stack([r, g, b], axis=-1) * 255.0

    # Blend original image (60%) with JET heatmap (40%)
    blended = 0.6 * orig_np + 0.4 * jet_np
    blended = np.clip(blended, 0, 255).astype(np.uint8)

    return Image.fromarray(blended)

def decode_base64_image(base64_str):
    """
    Decodes a base64 encoded data URI into a PIL RGB Image.
    """
    if "," in base64_str:
        base64_str = base64_str.split(",")[1]
    image_bytes = base64.b64decode(base64_str)
    pil_image = Image.open(io.BytesIO(image_bytes))
    if pil_image.mode != "RGB":
        pil_image = pil_image.convert("RGB")
    return pil_image


