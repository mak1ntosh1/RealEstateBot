import importlib
import sys
from pathlib import Path

from aiogram import Router

from config import settings


def setup_all_routers(dispatcher):
    print(f"Поиск роутеров в папке: {settings.PathSettings.HANDLERS_DIR}")

    for file_path in settings.PathSettings.HANDLERS_DIR.rglob("*.py"):
        if file_path.name == "__init__.py":
            continue

        relative_path = file_path.relative_to(Path(__file__).parent.parent)
        module_name = str(relative_path).replace("/", ".")[:-3]

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None:
            print(f"Не удалось получить спецификацию для {file_path.name}")
            continue

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        if hasattr(module, "router") and isinstance(module.router, Router):
            dispatcher.include_router(module.router)
            print(f"✔️ Роутер из {module_name} ({file_path.name}) успешно добавлен.")
        else:
            print(
                f"❌ В файле {file_path.name} (модуль: {module_name}) не найден объект 'router' типа aiogram.Router."
            )

    print(f"\nВсего роутеров добавлено в диспетчер: {len(dispatcher.sub_routers)}")
