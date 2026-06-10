from .models import ModulePermission


def user_permissions(request):

    permissions = {}

    if request.user.is_authenticated:

        perms = ModulePermission.objects.filter(
            user=request.user
        )

        for p in perms:
            permissions[p.module] = p

    return {
        'user_permissions': permissions
    }