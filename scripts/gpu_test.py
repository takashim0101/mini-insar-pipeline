# import torch
# 
# if torch.cuda.is_available():
#     print("PyTorch: CUDA is available!")
#     
#     # Get the number of GPUs
#     num_gpus = torch.cuda.device_count()
#     print(f"PyTorch: Found {num_gpus} GPU(s).")
#     
#     # Print details for each GPU
#     for i in range(num_gpus):
#         print(f"  - GPU {i}: {torch.cuda.get_device_name(i)}")
#     
#     # Create a tensor and move it to the GPU
#     print("\nCreating a tensor on the CPU...")
#     cpu_tensor = torch.randn(3, 3)
#     print(cpu_tensor)
#     
#     print("\nMoving the tensor to the GPU (cuda:0)...")
#     gpu_tensor = cpu_tensor.to("cuda:0")
#     print(gpu_tensor)
#     
#     print("\nPerforming a simple operation on the GPU...")
#     result_tensor = gpu_tensor * gpu_tensor
#     print(result_tensor)
#     
#     print("\nGPU usage test successful!")
# else:
#     print("PyTorch: CUDA is not available. The GPU is not being used.")


import torch

if torch.cuda.is_available():
    print("PyTorch: CUDA is available!")
    num_gpus = torch.cuda.device_count()
    print(f"PyTorch: Found {num_gpus} GPU(s).")
    for i in range(num_gpus):
        print(f"  - GPU {i}: {torch.cuda.get_device_name(i)}")

    print("\nCreating a tensor on the CPU...")
    cpu_tensor = torch.randn(3, 3)
    print(cpu_tensor)

    print("\nMoving the tensor to the GPU (cuda:0)...")
    gpu_tensor = cpu_tensor.to("cuda:0")
    print(gpu_tensor)

    print("\nPerforming a simple operation on the GPU...")
    result_tensor = gpu_tensor * gpu_tensor
    print(result_tensor)

    print("\nGPU usage test successful!")
else:
    print("PyTorch: CUDA is not available.")
