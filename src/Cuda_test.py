import torch

def test_cuda():
    print("Checking CUDA availability...")
    cuda_available = torch.cuda.is_available()
    print(f"CUDA Available: {cuda_available}")

    if cuda_available:
        print(f"CUDA Version: {torch.version.cuda}")
        print(f"PyTorch version: {torch.__version__}")
        print(f"Device count: {torch.cuda.device_count()}")

        for i in range(torch.cuda.device_count()):
            print(f"Device {i}: {torch.cuda.get_device_name(i)}")

        # Simple tensor test
        print("Running a simple tensor operation on CUDA...")
        x = torch.tensor([1.0, 2.0, 3.0], device="cuda")
        y = torch.tensor([4.0, 5.0, 6.0], device="cuda")
        z = x + y
        print(f"Result (on CUDA): {z}")
    else:
        print("CUDA is not available on this system.")

if __name__ == "__main__":
    test_cuda()