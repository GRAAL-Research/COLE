import os


def omit_none(**kwargs):
    return {k:v for k,v in kwargs.items() if v is not None}

def create_directory( directory):
    try:
        os.makedirs(directory, exist_ok=True)
    except Exception as e:
        print(f" Couldn't create directory {directory} : {e}")
