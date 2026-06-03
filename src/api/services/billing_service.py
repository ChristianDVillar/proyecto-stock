"""Límites y uso por plan SaaS."""
from ..models import User, Warehouse, PurchaseOrder, Tenant, TenantPlanEnum
from ..tenant_utils import get_current_tenant_id

PLAN_LIMITS = {
    TenantPlanEnum.starter: {
        'price_eur': 19,
        'max_users': 3,
        'max_warehouses': 1,
        'max_orders_month': 50,
        'label': 'Starter',
    },
    TenantPlanEnum.pro: {
        'price_eur': 29,
        'max_users': 5,
        'max_warehouses': 2,
        'max_orders_month': 100,
        'label': 'Pro',
    },
    TenantPlanEnum.business: {
        'price_eur': 49,
        'max_users': 10,
        'max_warehouses': 3,
        'max_orders_month': 200,
        'label': 'Business',
    },
    TenantPlanEnum.enterprise: {
        'price_eur': 99,
        'max_users': None,
        'max_warehouses': None,
        'max_orders_month': None,
        'label': 'Enterprise',
    },
}


class BillingService:
    @staticmethod
    def get_plans():
        return [
            {
                'plan': plan.value,
                'label': cfg['label'],
                'price_eur': cfg['price_eur'],
                'max_users': cfg['max_users'],
                'max_warehouses': cfg['max_warehouses'],
                'max_orders_month': cfg['max_orders_month'],
            }
            for plan, cfg in PLAN_LIMITS.items()
        ]

    @staticmethod
    def get_tenant_usage(tenant_id=None):
        tid = tenant_id or get_current_tenant_id()
        tenant = Tenant.query.get(tid) if tid else None
        if not tenant:
            return None
        plan = tenant.plan if isinstance(tenant.plan, TenantPlanEnum) else TenantPlanEnum.starter
        limits = PLAN_LIMITS.get(plan, PLAN_LIMITS[TenantPlanEnum.starter])
        from datetime import datetime
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return {
            'tenant': tenant.to_dict(),
            'plan': plan.value,
            'limits': limits,
            'usage': {
                'users': User.query.filter_by(tenant_id=tid, is_active=True).count(),
                'warehouses': Warehouse.query.filter_by(tenant_id=tid, is_active=True).count(),
                'orders_this_month': PurchaseOrder.query.filter(
                    PurchaseOrder.tenant_id == tid,
                    PurchaseOrder.created_at >= month_start,
                ).count(),
            },
        }

    @staticmethod
    def check_limit(tenant_id, resource):
        usage = BillingService.get_tenant_usage(tenant_id)
        if not usage:
            return True, None
        limits = usage['limits']
        used = usage['usage']
        mapping = {
            'users': ('max_users', 'users'),
            'warehouses': ('max_warehouses', 'warehouses'),
            'orders': ('max_orders_month', 'orders_this_month'),
        }
        if resource not in mapping:
            return True, None
        max_key, use_key = mapping[resource]
        cap = limits.get(max_key)
        if cap is None:
            return True, None
        if used[use_key] >= cap:
            return False, f'Límite del plan alcanzado ({resource}: {cap})'
        return True, None
