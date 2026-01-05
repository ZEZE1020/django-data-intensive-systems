"""
Migration Audit Script.

This script inspects migration files to identify potentially dangerous or
destructive operations before they are applied to a production database.

Checks for:
  - `RunSQL` with raw, non-idempotent DDL (e.g., ALTER TABLE)
  - `DeleteModel`: Removing a model (and its table)
  - `RemoveField`: Removing a field (and its column)
  - `RenameField`: Renaming a field
  - `RenameModel`: Renaming a model

This helps enforce a policy of safe, backward-compatible migrations.

Usage:
    python scripts/migration_audit.py <app_name>
    python scripts/migration_audit.py --all
"""

import os
import ast
import argparse
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Potentially dangerous operation classes in django.db.migrations
DANGEROUS_OPS = {
    'DeleteModel',
    'RemoveField',
    'RenameField',
    'RenameModel',
    'RunSQL',  # RunSQL needs context, but is worth flagging
}

def audit_migration_file(file_path):
    """
    Audits a single migration file for dangerous operations.
    """
    print(f"INFO: Auditing {file_path}...")
    found_issues = []

    with open(file_path, 'r') as f:
        content = f.read()
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and hasattr(node.func, 'id'):
                    if node.func.id in DANGEROUS_OPS:
                        message = (
                            f"  - Found potentially dangerous operation "
                            f"'{node.func.id}' on line {node.lineno}."
                        )
                        found_issues.append(message)
                        if node.func.id == 'RunSQL':
                             message += " (Note: Review raw SQL for non-idempotent DDL)"
                             
        except SyntaxError as e:
            print(f"ERROR: Could not parse {file_path}: {e}")
            
    for issue in found_issues:
        print(f"WARNING:{issue}")
        
    return len(found_issues) > 0


def find_migrations(app_path):
    """
    Finds all migration files in a given app directory.
    """
    migrations_path = os.path.join(app_path, 'migrations')
    if not os.path.exists(migrations_path):
        return []

    migration_files = []
    for f in sorted(os.listdir(migrations_path)):
        if f.endswith('.py') and not f.startswith('__'):
            migration_files.append(os.path.join(migrations_path, f))
    return migration_files


def main():
    parser = argparse.ArgumentParser(description="Audit Django migration files for safety.")
    parser.add_argument(
        'app_name',
        nargs='?',
        default=None,
        help="Specific app name to audit (e.g., 'orders')."
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help="Audit all apps in the 'apps' directory."
    )
    args = parser.parse_args()

    apps_dir = os.path.join(project_root, 'apps')
    apps_to_audit = []

    if args.app_name:
        app_path = os.path.join(apps_dir, args.app_name)
        if os.path.exists(app_path):
            apps_to_audit.append(app_path)
        else:
            print(f"ERROR: App '{args.app_name}' not found at {app_path}")
            sys.exit(1)
            
    elif args.all:
        for item in os.listdir(apps_dir):
            path = os.path.join(apps_dir, item)
            if os.path.isdir(path):
                apps_to_audit.append(path)
    else:
        parser.print_help()
        sys.exit(1)

    print("--- Starting Migration Audit ---")
    total_issues = 0
    for app_path in apps_to_audit:
        print(f"\nAuditing app: {os.path.basename(app_path)}")
        migrations = find_migrations(app_path)
        if not migrations:
            print("  No migrations found.")
            continue
            
        for migration_file in migrations:
            if audit_migration_file(migration_file):
                total_issues += 1

    print("\n--- Migration Audit Complete ---")
    if total_issues > 0:
        print(f"\nFound issues in {total_issues} migration file(s). Please review carefully.")
        sys.exit(1)
    else:
        print("\nNo dangerous operations found. Looks safe.")
        sys.exit(0)


if __name__ == "__main__":
    main()
