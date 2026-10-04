from datetime import datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from django.conf import settings
from django.core.management.base import BaseCommand

EXCLUDED_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    "venv",
    "__pycache__",
}

EXCLUDED_FILES = {
    ".env",
    "db.sqlite3",
}

EXCLUDED_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".pyd",
}


class Command(BaseCommand):
    help = "Export the project source code as a clean ZIP archive."

    def handle(self, *args, **options):
        project_root = Path(settings.BASE_DIR)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_name = f"device-monitoring-api-{timestamp}.zip"
        output_path = project_root / output_name

        with ZipFile(output_path, "w", ZIP_DEFLATED) as zip_file:
            for path in project_root.rglob("*"):
                if path == output_path:
                    continue

                relative_path = path.relative_to(project_root)

                if self.should_exclude(relative_path):
                    continue

                if path.is_file():
                    zip_file.write(
                        path,
                        arcname=relative_path,
                    )

        self.stdout.write(
            self.style.SUCCESS(f"Project exported successfully: {output_path}")
        )

    def should_exclude(self, relative_path: Path) -> bool:
        parts = set(relative_path.parts)

        if parts & EXCLUDED_DIRS:
            return True

        if relative_path.name in EXCLUDED_FILES:
            return True

        if relative_path.suffix in EXCLUDED_SUFFIXES:
            return True

        if relative_path.suffix == ".zip":
            return True

        return False
