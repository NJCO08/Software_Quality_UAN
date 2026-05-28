import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.storage import TaskStorage
from src.service import TaskService
from src.notifier import Notifier

# ==========================================
# STUBS MANUALES PARA EL ENFOQUE TOP-DOWN
# ==========================================

class StorageStub:
    """Stub que simula el almacenamiento en memoria y registra llamadas."""
    def __init__(self):
        self.tasks_in_memory = []
        self.save_called_with = None
        self.load_called_count = 0

    def load(self):
        self.load_called_count += 1
        return self.tasks_in_memory

    def save(self, tasks):
        self.save_called_with = tasks
        self.tasks_in_memory = tasks


class NotifierStub:
    """Stub que simula el notificador y registra los mensajes enviados."""
    def __init__(self):
        self.send_called_with = None

    def send(self, message):
        self.send_called_with = message


# ==========================================
# CLASES DE PRUEBAS
# ==========================================

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


class TestTopDown:
    """Parte 4.1: Pruebas de integración con enfoque Top-Down."""

    def test_add_task_top_down_flow(self):
        # 1. Inicializar los Stubs aislados
        storage_stub = StorageStub()
        notifier_stub = NotifierStub()
        
        # 2. Inyectar stubs en el servicio (Módulo de nivel superior)
        service = TaskService(storage_stub, notifier_stub)
        
        # 3. Ejecutar la acción
        result = service.add_task("Estudiar Calidad de Software")
        
        # 4. VALIDACIONES DE LOGICA Y FLUJO (Contratos de comunicación)
        assert result is True
        
        # Verificar que se cargó el storage y se guardó la estructura correcta
        assert storage_stub.load_called_count == 1
        assert storage_stub.save_called_with == [{"title": "Estudiar Calidad de Software", "done": False}]
        
        # Verificar que el Notifier recibió el mensaje exacto esperado por el contrato
        assert notifier_stub.send_called_with == "Tarea 'Estudiar Calidad de Software' creada"

    def test_add_duplicate_task_top_down(self):
        storage_stub = StorageStub()
        notifier_stub = NotifierStub()
        
        # Pre-cargar el stub con una tarea existente
        storage_stub.tasks_in_memory = [{"title": "Tarea Duplicada", "done": False}]
        
        service = TaskService(storage_stub, notifier_stub)
        
        # Intentar añadir el mismo título
        result = service.add_task("Tarea Duplicada")
        
        # Validar que retorna False, NO guarda cambios y NO genera notificación
        assert result is False
        assert storage_stub.save_called_with is None  # No debió llamar a save()
        assert notifier_stub.send_called_with is None  # No debió notificar