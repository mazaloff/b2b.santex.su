from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from .models import Customer, Person, Order, OrderItem, Section, Product, Price, Store, Currency

admin.site.register(Customer)
admin.site.register(Person)


class ProductAdmin(admin.ModelAdmin):
    list_filter = ['section']


admin.site.register(Section)
admin.site.register(Product, ProductAdmin)
admin.site.register(Price)
admin.site.register(Store)
admin.site.register(Currency)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']


class OrderAdmin(admin.ModelAdmin):
    list_filter = ['date', 'customer', 'updated']
    inlines = [OrderItemInline]


# Unregister the provided model admin
admin.site.unregister(User)


# Register out own model admin, based on the default UserAdmin
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    readonly_fields = [
        'date_joined',
    ]

    def get_readonly_fields(self, request, obj=None):
        is_superuser = request.user.is_superuser
        disabled_fields = set()
        if not is_superuser:
            disabled_fields |= {
                'username',
                'password',
                'is_superuser',
                'user_permissions',
            }

        # Prevent non-superusers from editing their own permissions
        if (
                not is_superuser
                and obj is not None
                and obj == request.user
        ):
            disabled_fields |= {
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            }
        return disabled_fields


admin.site.register(Order, OrderAdmin)
