import importlib.util
import inspect
import logging
from pathlib import Path

from dmp_af.validation.rules.base import BaseModelValidator, BaseProjectValidator

logger = logging.getLogger(__name__)


def load_custom_rules(
    folder_path: Path,
) -> tuple[list[BaseModelValidator], list[BaseProjectValidator]]:
    """
    Load custom validation rules from a folder.

    :param folder_path: Path to folder containing Python files with custom validators
    :return: Tuple of (model_validators, project_validators)
    """
    model_validators = []
    project_validators = []

    if not folder_path.exists():
        logger.warning(f'Custom rules path does not exist: {folder_path}')
        return model_validators, project_validators

    if not folder_path.is_dir():
        logger.warning(f'Custom rules path is not a directory: {folder_path}')
        return model_validators, project_validators

    # Import all .py files in the folder
    for py_file in folder_path.glob('*.py'):
        if py_file.name.startswith('_'):
            continue

        try:
            # Load module dynamically
            # WARNING: This executes arbitrary Python code from the custom validator file
            # Only load validators from trusted sources
            spec = importlib.util.spec_from_file_location(py_file.stem, py_file)
            if spec is None or spec.loader is None:
                logger.warning(f'Could not load module spec for {py_file}')
                continue

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find validator classes
            for name, obj in inspect.getmembers(module, inspect.isclass):
                # Skip base classes
                if obj in (BaseModelValidator, BaseProjectValidator):
                    continue

                # Check if it's a model validator
                if issubclass(obj, BaseModelValidator):
                    try:
                        instance = obj()  # Will fail if abstract methods not implemented
                        model_validators.append(instance)
                        logger.info(f'Loaded model validator: {instance.name} from {py_file.name}')
                    except TypeError as e:
                        logger.error(f'Cannot instantiate {name}: {e}')
                        continue
                    except Exception as e:
                        logger.error(f'Failed to instantiate {name} from {py_file}: {e}')
                        continue

                # Check if it's a project validator
                elif issubclass(obj, BaseProjectValidator):
                    try:
                        instance = obj()  # Will fail if abstract methods not implemented
                        project_validators.append(instance)
                        logger.info(f'Loaded project validator: {instance.name} from {py_file.name}')
                    except TypeError as e:
                        logger.error(f'Cannot instantiate {name}: {e}')
                        continue
                    except Exception as e:
                        logger.error(f'Failed to instantiate {name} from {py_file}: {e}')
                        continue

        except Exception as e:
            logger.error(f'Failed to load custom rules from {py_file}: {e}')
            continue

    return model_validators, project_validators
