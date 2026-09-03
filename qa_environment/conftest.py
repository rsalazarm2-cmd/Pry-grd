import os
import sys
import pytest
from datetime import datetime
from pathlib import Path

# Agregar el directorio raíz del backend al sys.path para poder importar modulos
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

# Configurar logs de pytest a un archivo en qa_environment/logs
@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    logs_dir = ROOT_DIR / "qa_environment" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"test_run_{timestamp}.log"
    
    config.option.log_file = str(log_file)
    config.option.log_file_level = "INFO"
    config.option.log_file_format = "%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)"
    config.option.log_file_date_format = "%Y-%m-%d %H:%M:%S"

@pytest.fixture(autouse=True)
def set_django_settings():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

@pytest.fixture
def test_data_dir():
    """Retorna la ruta al directorio de datos de prueba."""
    d = ROOT_DIR / "qa_environment" / "test_data"
    d.mkdir(parents=True, exist_ok=True)
    return d
