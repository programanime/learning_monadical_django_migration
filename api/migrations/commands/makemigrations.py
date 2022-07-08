from __future__ import absolute_import, unicode_literals

import os

from django.core.management.commands.makemigrations import (
    Command as MakeMigrationsCommand,
)
from django.db.migrations.loader import MigrationLoader

APP_NAME = "api"


class Command(MakeMigrationsCommand):
    """Cause git conflict when two migrations have the same parent."""

    def handle(self, *app_labels, **options):
        super(Command, self).handle(*app_labels, **options)
        loader = MigrationLoader(None, ignore_no_migrations=True)
        list_migrations = []
        current_migrations = None
        manifest_filename = f"migrations_{APP_NAME}.manifest"

        for migration in loader.disk_migrations:
            if migration[0] == APP_NAME:
                list_migrations.append(migration[1])

        list_migrations.sort()

        if os.path.exists(manifest_filename):
            with open(manifest_filename, encoding="utf-8") as f:
                current_migrations = f.read()

        with open(manifest_filename, "w", encoding="utf-8") as f:
            new_migrations = "\n".join(list_migrations)

            if not current_migrations or current_migrations != new_migrations:
                f.write(new_migrations)

            graph = loader.graph
            leaf_nodes = graph.leaf_nodes(APP_NAME)
            if len(leaf_nodes) != 1:
                f.write(f"{APP_NAME}: {leaf_nodes[0][1]}\n")
                raise Exception(f"App {APP_NAME} has multiple migrations!")
