from rest_framework import permissions



class IsAdminOrSelf(permissions.BasePermission):
    """
    Admins can access everything.
    Users can only access their own profile (retrieve/update).
    """

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj == request.user
