import sys
import os
# Asegura que Python encuentre el módulo 'src' desde la carpeta 'tests'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.storage import TaskStorage
from src.service import TaskService
from src.notifier import Notifier

# =====================================================================
# Pruebas  de Integración Iniciales
# =====================================================================

class TestServiceIntegration:
    def test_add_task_happy_path(self):
        storage = TaskStorage("test_tasks.json")
        notifier = Notifier()
        service = TaskService(storage, notifier)
        result = service.add_task("Comprar leche")
        assert result is True

    def test_complete_task(self):
        storage = TaskStorage("test_tasks.json")
        notifier = Notifier()
        service = TaskService(storage, notifier)
        service.add_task("Aprender pytest")
        assert service.complete_task("Aprender pytest") is True


# =====================================================================
# PARTE 4.1: Enfoque Top-Down (Aislamiento con Stubs Manuales)
# =====================================================================

class StorageStub:
    """
    Stub manual para TaskStorage.
    Simula el almacenamiento en memoria y actúa como sensor para auditoría.
    """
    def __init__(self, preset_tasks=None):
        # Permite precargar tareas en el almacenamiento simulado
        self.tasks = preset_tasks if preset_tasks is not None else []
        self.save_called = False
        self.last_saved_tasks = None

    def load(self):
        return self.tasks

    def save(self, tasks):
        self.save_called = True
        self.last_saved_tasks = tasks


class NotifierStub:
    """
    Stub manual para Notifier.
    Evita fallos aleatorios de red/simulación y registra las llamadas recibidas.
    """
    def __init__(self):
        self.send_called = False
        self.last_message = None

    def send(self, message):
        self.send_called = True
        self.last_message = message


class TestTopDown:
    def test_add_task_top_down_success(self):
        """
        Valida el camino feliz: el servicio interactúa correctamente con las
        capas inferiores enviando los parámetros adecuados a los Stubs.
        """
        # Arreglar (Arrange)
        storage_stub = StorageStub(preset_tasks=[])
        notifier_stub = NotifierStub()
        service = TaskService(storage_stub, notifier_stub)
        task_title = "Estudiar para el parcial"

        # Actuar (Act)
        result = service.add_task(task_title)

        # Afirmar (Assert)
        # 1. El servicio debe reportar éxito en su ejecución
        assert result is True
        
        # 2. Verificación de Integración: ¿Se invocó el almacenamiento con los datos correctos?
        assert storage_stub.save_called is True
        assert len(storage_stub.last_saved_tasks) == 1
        assert storage_stub.last_saved_tasks[0]["title"] == task_title
        
        # 3. Verificación de Comunicación: ¿Se notificó la creación con el mensaje esperado?
        assert notifier_stub.send_called is True
        assert notifier_stub.last_message == f"Tarea '{task_title}' creada"

    def test_add_task_top_down_duplicate(self):
        """
        Valida que el servicio lea el almacenamiento y rechace tareas duplicadas,
        frenando llamadas innecesarias al Notificador y al método Save.
        """
        # Arreglar (Arrange)
        existing_task = {"title": "Comprar leche", "done": False}
        storage_stub = StorageStub(preset_tasks=[existing_task])
        notifier_stub = NotifierStub()
        service = TaskService(storage_stub, notifier_stub)

        # Actuar (Act)
        result = service.add_task("Comprar leche")

        # Afirmar (Assert)
        # 1. El servicio debe retornar False al detectar el duplicado
        assert result is False
        
        # 2. Auditoría de comportamiento: No debe alterarse el almacenamiento ni enviar alertas
        assert storage_stub.save_called is False
        assert notifier_stub.send_called is False