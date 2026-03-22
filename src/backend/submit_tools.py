import io
import json
import zipfile

from fastapi import HTTPException

MAX_DECOMPRESSED_SIZE_MB = 200


def unzip_predictions_from_zip(zip_bytes: bytes) -> dict:
    """
    Reads predictions.json directly from the ZIP in memory.
    """
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        if "predictions.json" not in z.namelist():
            error_message = (
                "The uploaded ZIP file does not contains a predictions.json file."
            )
            raise HTTPException(400, error_message)
        info = z.getinfo("predictions.json")
        if info.file_size > MAX_DECOMPRESSED_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                413,
                f"Decompressed predictions.json exceeds {MAX_DECOMPRESSED_SIZE_MB}MB limit.",
            )
        with z.open("predictions.json") as f:
            return json.load(f)
