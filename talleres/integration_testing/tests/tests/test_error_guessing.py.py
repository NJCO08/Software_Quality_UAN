"""
Pruebas de Integración Avanzadas - Error Guessing (Puntos Extra)
Fuerza escenarios extremos y maliciosos basados en intuición de fallos comunes.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.service import TaskService
from src.storage import TaskStorage

# Stub neutral para evitar romper las pruebas con la red real
class NotifierMock:
    def send(self, message):
        pass

class TestErrorGuessing:
    GUESSING_FILE = "test_guessing_tasks.json"

    @pytest.fixture(autouse=True)
    def clean_environment(self):
        if os.path.exists(self.GUESSING_FILE):
            os.remove(self.GUESSING_FILE)
        yield
        if os.path.exists(self.GUESSING_FILE):
            os.remove(self.GUESSING_FILE)

    def test_guessing_spaces_only_title(self):
        """
        G1: ¿Qué pasa si el título no está vacío, pero son solo espacios en blanco? ("   ")
        El sistema debería tratarlo como un título vacío y rechazarlo en la lógica de negocio.
        """
        storage = TaskStorage(self.GUESSING_FILE)
        service = TaskService(storage, NotifierMock())

        # Intentar registrar una tarea con puros espacios
        result = service.add_task("   ")
        
        assert result is False, "Error: El servicio aceptó una tarea que solo contiene espacios en blanco."
        assert len(storage.load()) == 0

    def test_guessing_html_and_script_injection(self):
        """
        G2: Inyección de scripts/caracteres especiales.
        ¿El storage de bajo nivel corrompe el JSON si le enviamos etiquetas HTML o código?
        Debe serializar el string de forma segura sin romper la estructura del archivo.
        """
        storage = TaskStorage(self.GUESSING_FILE)
        service = TaskService(storage, NotifierMock())
        malicious_title = "<script>alert('XSS')</script> & @ # ¡!"

        result = service.add_task(malicious_title)

        assert result is True
        tasks = storage.load()
        assert len(tasks) == 1
        # Comprobar que el string JSON mantuvo los caracteres especiales intactos y seguros
        assert tasks[0]["title"] == malicious_title

    def test_guessing_case_insensitivity_duplicates(self):
        """
        G3: Duplicados con diferencias de mayúsculas y minúsculas (Case Insensitivity).
        Si ya existe "Estudiar", ¿el sistema bloquea "ESTUDIAR"? 
        La lógica de negocio debería sanitizar las entradas para evitar tareas idénticas duplicadas por texto.
        """
        storage = TaskStorage(self.GUESSING_FILE)
        service = TaskService(storage, NotifierMock())
        
        service.add_task("Estudiar Calidad")
        # Intento de sabotaje con mayúsculas sostenidas
        result_duplicate = service.add_task("ESTUDIAR CALIDAD")

        assert result_duplicate is False, "Error: Se permitió un duplicado debido a diferencias de mayúsculas/minúsculas."
        assert len(storage.load()) == 1