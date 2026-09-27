import argparse
import asyncio
import logging
from pathlib import Path
import shutil


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


async def copy_file(file_path: Path, output_folder: Path) -> None:
    """
    Копіює файл у підпапку, назва якої відповідає його розширенню.
    """
    try:
        extension = file_path.suffix.lower().lstrip(".")

        if not extension:
            extension = "no_extension"

        target_folder = output_folder / extension

        await asyncio.to_thread(
            target_folder.mkdir,
            parents=True,
            exist_ok=True,
        )

        target_file = target_folder / file_path.name

        await asyncio.to_thread(
            shutil.copy2,
            file_path,
            target_file,
        )

        logging.info(
            "Copied %s -> %s",
            file_path,
            target_file,
        )

    except Exception as error:
        logging.error(
            "Error copying file %s: %s",
            file_path,
            error,
        )


async def read_folder(
    source_folder: Path,
    output_folder: Path,
) -> None:
    """
    Рекурсивно читає всі файли у source folder
    та асинхронно копіює їх у output folder.
    """
    try:
        if not source_folder.exists():
            logging.error(
                "Source folder does not exist: %s",
                source_folder,
            )
            return

        if not source_folder.is_dir():
            logging.error(
                "Source path is not a directory: %s",
                source_folder,
            )
            return

        await asyncio.to_thread(
            output_folder.mkdir,
            parents=True,
            exist_ok=True,
        )

        files = await asyncio.to_thread(
            lambda: [
                path
                for path in source_folder.rglob("*")
                if path.is_file()
            ]
        )

        tasks = [
            copy_file(file_path, output_folder)
            for file_path in files
        ]

        await asyncio.gather(*tasks)

    except Exception as error:
        logging.exception(
            "Error while reading folder: %s",
            error,
        )


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "Sort files from source folder "
            "into subfolders by file extension."
        )
    )

    parser.add_argument(
        "source",
        type=str,
        help="Path to source folder",
    )

    parser.add_argument(
        "output",
        type=str,
        help="Path to output folder",
    )

    return parser.parse_args()


async def main():
    args = parse_arguments()

    source_folder = Path(args.source)
    output_folder = Path(args.output)

    await read_folder(
        source_folder,
        output_folder,
    )

    logging.info("File sorting completed.")


if __name__ == "__main__":
    asyncio.run(main())