from huggingface_hub import upload_folder

repo_id = "Yurhu/colle"  # Format: username/space_name
local_dir = "./"

upload_folder(
    repo_id=repo_id,
    folder_path=local_dir,
    repo_type="space",  # Important: this tells HF it's a Space
    commit_message="Push from a local computer",
)
