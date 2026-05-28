"""
Lógica de negocio del gestor de tareas.
Contiene errores de integración que las pruebas iniciales no detectan.
"""

from .storage import TaskStorage
from .notifier import Notifier

class TaskService:
    def __init__(self, storage: TaskStorage, notifier: Notifier):
        self.storage = storage
        self.notifier = notifier

    def add_task(self, title):
        """
        Agrega una nueva tarea.
        Retorna True si se agregó, False en caso de duplicado.
        Error de integración: no valida título vacío,
        y no revierte la operación si la notificación falla.
        """
        tasks = self.storage.load()
        if title in [t['title'] for t in tasks]:
            return False
        tasks.append({"title": title, "done": False})
        self.storage.save(tasks)
        # Error: no captura excepción de notifier
        self.notifier.send(f"Tarea '{title}' creada")
        return True

    def complete_task(self, title):
        """Marca una tarea como completada."""
        return True
 

    def list_tasks(self):
        return self.storage.load()