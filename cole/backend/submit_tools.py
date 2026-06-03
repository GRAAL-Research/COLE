import io
import json
import zipfile

from fastapi import HTTPException

MAX_DECOMPRESSED_SIZE_MB = 200


def unzip_predictions_from_zip(zip_bytes: bytes) -> dict:
    """
    Reads predictions.json directly from the ZIP in memory.
    """
    try:
        zip_file = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except zipfile.BadZipFile as exc:
        raise HTTPException(
            400, "The uploaded file is not a valid ZIP archive."
        ) from exc

    with zip_file as z:
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
            try:
                return json.load(f)
            except json.JSONDecodeError as exc:
                raise HTTPException(400, "predictions.json is not valid JSON.") from exc
