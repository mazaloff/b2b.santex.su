from django.contrib import admin
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
    list_filter = ['person', 'created', 'updated']
    inlines = [OrderItemInline]

admin.site.register(Order, OrderAdmin)