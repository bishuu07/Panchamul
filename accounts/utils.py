from .models import ModulePermission


def has_permission(user, module, action='can_view'):

    if user.role == 'SUPER_ADMIN':
        return True

    permission = ModulePermission.objects.filter(
        user=user,
        module=module
    ).first()

    if not permission:
        return False

    return getattr(permission, action)