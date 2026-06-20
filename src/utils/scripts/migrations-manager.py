#!/usr/bin/env python3

## This script manages database migrations by creating new migration.

## usage:
# To create a new migration:
#   python src/utils/scripts/migrations-manager.py create <migration_name>

import datetime
from pathlib import Path


def make_migration(name: str) -> str:
    now = datetime.datetime.now()
    migration_name = f"{now.strftime('%Y%m%d%H%M%S')}_{name}.sql"

    script_dir = Path(__file__).resolve().parent

    migration_folder = script_dir.parent.parent / "database" / "migrations"

    migration_path = migration_folder / migration_name

    migration_path.parent.mkdir(parents=True, exist_ok=True)

    with open(migration_path, "w", encoding="utf-8") as f:
        f.write(f"-- Migration: {name}\n")

    return f"Sucesso! Migration criada: {migration_path.relative_to(script_dir.parent.parent.parent)}"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Manage database migrations.")
    subparsers = parser.add_subparsers(dest="command")

    create_parser = subparsers.add_parser("create", help="Create a new migration.")
    create_parser.add_argument("name", type=str, help="Name of the migration.")

    args = parser.parse_args()

    if args.command == "create":
        print(make_migration(args.name))
    else:
        parser.print_help()
