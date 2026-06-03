import io
import json
import zipfile
from unittest import TestCase

from fastapi import HTTPException

from cole.backend.submit_tools import (
    MAX_DECOMPRESSED_SIZE_MB,
    unzip_predictions_from_zip,
)


def _zip_with(name: str, payload: bytes) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w") as z:
        z.writestr(name, payload)
    return buf.getvalue()


class UnzipPredictionsFromZipTest(TestCase):
    def test_valid_zip_returns_parsed_dict(self):
        content = {"model_name": "m", "tasks": []}
        zip_bytes = _zip_with("predictions.json", json.dumps(content).encode("utf-8"))

        actual = unzip_predictions_from_zip(zip_bytes)

        self.assertEqual(content, actual)

    def test_missing_predictions_json_raises_400(self):
        zip_bytes = _zip_with("other.json", b"{}")

        with self.assertRaises(HTTPException) as ctx:
            unzip_predictions_from_zip(zip_bytes)
        self.assertEqual(400, ctx.exception.status_code)
        self.assertIn("predictions.json", ctx.exception.detail)

    def test_non_zip_bytes_raises_400_not_500(self):
        # Previously raised zipfile.BadZipFile -> 500 server error.
        with self.assertRaises(HTTPException) as ctx:
            unzip_predictions_from_zip(b"this is not a zip file")
        self.assertEqual(400, ctx.exception.status_code)

    def test_invalid_json_inside_zip_raises_400_not_500(self):
        zip_bytes = _zip_with("predictions.json", b"{ this is not json }")

        with self.assertRaises(HTTPException) as ctx:
            unzip_predictions_from_zip(zip_bytes)
        self.assertEqual(400, ctx.exception.status_code)
        self.assertIn("JSON", ctx.exception.detail)

    def test_oversized_decompressed_payload_raises_413(self):
        oversized = b"x" * (MAX_DECOMPRESSED_SIZE_MB * 1024 * 1024 + 1)
        zip_bytes = _zip_with("predictions.json", oversized)

        with self.assertRaises(HTTPException) as ctx:
            unzip_predictions_from_zip(zip_bytes)
        self.assertEqual(413, ctx.exception.status_code)
