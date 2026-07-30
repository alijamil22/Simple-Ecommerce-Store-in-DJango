from django.contrib import admin
from .models import Category, Product, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price', 'stock', 'available', 'created', 'updated']
    list_filter = ['available', 'created', 'updated']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ['category']
    actions = ['make_available', 'make_unavailable']

    def make_available(self, request, queryset):
        queryset.update(available=True)
    make_available.short_description = "Mark selected products as available"

    def make_unavailable(self, request, queryset):
        queryset.update(available=False)
    make_unavailable.short_description = "Mark selected products as unavailable"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created', 'paid', 'payment_method']
    list_filter = ['paid', 'created', 'payment_method']
    inlines = [OrderItemInline]
