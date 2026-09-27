import shutil
from pathlib import Path

from fastapi import UploadFile


UPLOAD_DIR = (
    Path(__file__).resolve().parents[2]
    / "uploads"
)


def ensure_upload_dir_exists() -> None:
    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


def save_uploaded_file(
    file: UploadFile
) -> str:

    ensure_upload_dir_exists()

    file_path = (
        UPLOAD_DIR
        / file.filename
    )

    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    return str(file_path)