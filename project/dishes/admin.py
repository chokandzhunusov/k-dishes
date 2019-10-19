from django.contrib import admin
from .models import Order, Dish, UniqueDish


class OrderAdmin(admin.ModelAdmin):
    fields = ('date', 'buyer')


class DishAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Dish._meta.get_fields()]

class UniqueDishAdmin(admin.ModelAdmin):
    list_display = [field.name for field in UniqueDish._meta.get_fields()]


admin.site.register(Order, OrderAdmin)
admin.site.register(Dish, DishAdmin)
admin.site.register(UniqueDish, UniqueDishAdmin)
