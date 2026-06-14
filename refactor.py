import os
import shutil

BASE_DIR = r"d:\Projects\AirLynk\backend"

moves = [
    # 1. Entrypoints
    (r"services\api\app\main.py", r"main.py"),
    (r"services\worker", r"worker"),
    
    # 2. Shared API
    (r"services\api\app\api\dependencies\deps.py", r"shared\api\dependencies.py"),
    (r"services\api\app\api\routes\health.py", r"shared\api\routes\health.py"),
    (r"services\api\app\api\routes\metrics.py", r"shared\api\routes\metrics.py"),
    
    # 3. Auth Domain
    (r"services\api\app\api\routes\auth.py", r"services\auth\api\routes.py"),
    (r"services\api\app\services\auth_service.py", r"services\auth\service\auth_service.py"),
    (r"services\api\app\repositories\auth_repository.py", r"services\auth\repository\auth_repository.py"),
    (r"services\api\app\models\auth.py", r"services\auth\models\user.py"),
    (r"shared\schemas\auth.py", r"services\auth\schemas\auth.py"),
    (r"tests\api\test_auth_api.py", r"services\auth\tests\api\test_auth_api.py"),
    (r"tests\unit\test_auth_service.py", r"services\auth\tests\unit\test_auth_service.py"),
    
    # 4. Booking Domain
    (r"services\api\app\models\booking.py", r"services\booking\models\booking.py"),
    (r"services\api\app\models\location.py", r"services\booking\models\location.py"),
    
    # 5. Fleet Domain
    (r"services\api\app\models\fleet.py", r"services\fleet\models\fleet.py"),
    
    # Base model handling (Delete later, but move for now)
    (r"services\api\app\models\base.py", r"shared\database\base_reexport.py"), 
    
    # Move conftest.py
    (r"tests\conftest.py", r"conftest.py"),
]

for src, dst in moves:
    src_path = os.path.join(BASE_DIR, src)
    dst_path = os.path.join(BASE_DIR, dst)
    
    if os.path.exists(src_path):
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        if os.path.isdir(src_path):
            shutil.move(src_path, dst_path)
        else:
            shutil.move(src_path, dst_path)
        print(f"Moved {src} -> {dst}")
    else:
        print(f"Skipping {src_path}, does not exist")

# Touch __init__.py files where needed
def touch(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'a'):
        pass

dirs_to_init = [
    r"shared\api", r"shared\api\routes",
    r"services\auth", r"services\auth\api", r"services\auth\service", 
    r"services\auth\repository", r"services\auth\models", r"services\auth\schemas", 
    r"services\auth\tests", r"services\auth\tests\api", r"services\auth\tests\unit",
    r"services\booking", r"services\booking\models",
    r"services\fleet", r"services\fleet\models",
]

for d in dirs_to_init:
    touch(os.path.join(BASE_DIR, d, "__init__.py"))

print("Done moving files and creating __init__.py")
