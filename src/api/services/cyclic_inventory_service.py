"""Inventarios cíclicos programados."""
from datetime import date, datetime, timedelta

from ..models import db, CyclicInventorySchedule, CyclicInventoryTask, Stock
from ..tenant_utils import get_current_tenant_id, scope_tenant

WEEKDAY_NAMES = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']


class CyclicInventoryService:
    @staticmethod
    def list_schedules(tenant_id=None):
        tid = tenant_id or get_current_tenant_id()
        q = CyclicInventorySchedule.query.filter_by(is_active=True)
        if tid:
            q = q.filter_by(tenant_id=tid)
        return [s.to_dict() for s in q.order_by(CyclicInventorySchedule.weekday).all()]

    @staticmethod
    def create_schedule(tenant_id, name, weekday, device_type=None, warehouse_id=None):
        if weekday < 0 or weekday > 6:
            return None, {'error': 'weekday debe ser 0-6 (lunes-domingo)', 'status': 400}
        s = CyclicInventorySchedule(
            tenant_id=tenant_id,
            name=name,
            weekday=weekday,
            device_type=device_type,
            warehouse_id=warehouse_id,
        )
        db.session.add(s)
        return s, None

    @staticmethod
    def list_tasks(tenant_id=None, status=None):
        tid = tenant_id or get_current_tenant_id()
        q = CyclicInventoryTask.query
        if tid:
            q = q.filter_by(tenant_id=tid)
        if status:
            q = q.filter_by(status=status)
        return [t.to_dict() for t in q.order_by(CyclicInventoryTask.due_date.desc()).limit(100).all()]

    @staticmethod
    def generate_tasks_for_today(tenant_id=None):
        """Genera tareas según schedules del día actual."""
        tid = tenant_id or get_current_tenant_id()
        today = date.today()
        weekday = today.weekday()
        q = CyclicInventorySchedule.query.filter_by(is_active=True, weekday=weekday)
        if tid:
            q = q.filter_by(tenant_id=tid)
        created = []
        for sched in q.all():
            exists = CyclicInventoryTask.query.filter_by(
                schedule_id=sched.id, due_date=today
            ).first()
            if exists:
                continue
            count = 0
            stock_q = scope_tenant(
                Stock.query.filter(Stock.deleted_at.is_(None)), Stock, sched.tenant_id
            )
            if sched.device_type:
                from ..models import StockTypeEnum
                try:
                    dtype = StockTypeEnum[sched.device_type]
                    stock_q = stock_q.filter(Stock.dispositivo == dtype)
                except KeyError:
                    pass
            if sched.warehouse_id:
                stock_q = stock_q.filter_by(warehouse_id=sched.warehouse_id)
            count = stock_q.count()
            title = f'{sched.name} — {WEEKDAY_NAMES[weekday]} ({count} ítems)'
            task = CyclicInventoryTask(
                tenant_id=sched.tenant_id,
                schedule_id=sched.id,
                title=title,
                due_date=today,
                status='pendiente',
            )
            db.session.add(task)
            created.append(task)
        return created

    @staticmethod
    def complete_task(task_id, user_id, notes=None):
        task = CyclicInventoryTask.query.get(task_id)
        if not task:
            return None, {'error': 'Tarea no encontrada', 'status': 404}
        task.status = 'completada'
        task.completed_at = datetime.utcnow()
        task.assigned_to = user_id
        if notes:
            task.notes = notes
        return task, None
