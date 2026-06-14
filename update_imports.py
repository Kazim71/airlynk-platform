import os
import glob

BASE_DIR = r"d:\Projects\AirLynk\backend"

import_mappings = {
    "backend.services.api.app.api.dependencies.deps": "backend.shared.api.dependencies",
    "backend.services.api.app.api.routes.health": "backend.shared.api.routes.health",
    "backend.services.api.app.api.routes.metrics": "backend.shared.api.routes.metrics",
    "backend.services.api.app.api.routes.auth": "backend.services.auth.api.routes",
    "backend.services.api.app.services.auth_service": "backend.services.auth.service.auth_service",
    "backend.services.api.app.repositories.auth_repository": "backend.services.auth.repository.auth_repository",
    "backend.services.api.app.models.auth": "backend.services.auth.models.user",
    "backend.services.api.app.models.booking": "backend.services.booking.models.booking",
    "backend.services.api.app.models.location": "backend.services.booking.models.location",
    "backend.services.api.app.models.fleet": "backend.services.fleet.models.fleet",
    "backend.services.api.app.models.base": "backend.shared.database.base",
    "backend.services.api.app.main": "backend.main",
    "backend.services.worker.celery_app": "backend.worker.celery_app",
    "backend.services.worker": "backend.worker",
    "backend.shared.schemas.auth": "backend.services.auth.schemas.auth",
}

def replace_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content
    for old, new in import_mappings.items():
        new_content = new_content.replace(old, new)
        
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath}")

for root, _, files in os.walk(BASE_DIR):
    for file in files:
        if file.endswith('.py') or file.endswith('.mako'):
            replace_in_file(os.path.join(root, file))

print("Import replacements complete.")
