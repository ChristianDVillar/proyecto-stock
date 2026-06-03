"""Utilidades multi-tenant: aislamiento de datos por empresa."""
from flask_jwt_extended import get_jwt_identity

from .models import db, User, Tenant, Warehouse


def get_current_user():
    user_id = get_jwt_identity()
    if not user_id:
        return None
    try:
        return User.query.get(int(user_id))
    except (TypeError, ValueError):
        return None


def get_current_tenant_id():
    user = get_current_user()
    return user.tenant_id if user else None


def scope_tenant(query, model, tenant_id=None):
    """Filtra query por tenant_id si el modelo lo tiene."""
    tid = tenant_id if tenant_id is not None else get_current_tenant_id()
    if tid is not None and hasattr(model, 'tenant_id'):
        return query.filter(model.tenant_id == tid)
    return query


def ensure_default_tenant():
    """Crea tenant y almacén por defecto si no existen (para migraciones/init)."""
    tenant = Tenant.query.filter_by(slug='default').first()
    if not tenant:
        tenant = Tenant(name='Empresa Demo', slug='default', is_active=True)
        db.session.add(tenant)
        db.session.flush()
    wh = Warehouse.query.filter_by(tenant_id=tenant.id, code='MAIN').first()
    if not wh:
        wh = Warehouse(
            tenant_id=tenant.id,
            code='MAIN',
            name='Almacén Principal',
            city='Málaga',
            is_default=True,
        )
        db.session.add(wh)
    db.session.commit()
    return tenant, wh


def assign_user_tenant(user, tenant_id=None):
    if user.tenant_id:
        return user.tenant_id
    tenant, _ = ensure_default_tenant()
    user.tenant_id = tenant_id or tenant.id
    return user.tenant_id
