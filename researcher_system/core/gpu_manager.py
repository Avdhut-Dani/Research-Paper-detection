import torch

DEVICE="cuda" if torch.cuda.is_available() else "cpu"

def show_gpu():
    if DEVICE=="cuda":
        print("Using GPU:",torch.cuda.get_device_name(0))
    else:
        print("Using CPU")
