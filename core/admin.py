from django.contrib import admin
from .models import Category, Product, CarModel, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'slug']
    list_filter = ['department']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'years']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'phone', 'status', 'total', 'created_at']
    list_filter = ['status']
    list_editable = ['status']
    inlines = [OrderItemInline]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'price', 'in_stock', 'is_premium']
    list_filter = ['category__department', 'in_stock', 'is_premium']
    list_editable = ['price', 'in_stock']
    filter_horizontal = ['compatible_with']
    search_fields = ['title']