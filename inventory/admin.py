from django.contrib import admin
from .models import Product, StockEntry, StockEntryItem

class StockEntryItemInline(admin.TabularInline):
    model = StockEntryItem
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('sku', 'name', 'current_stock', 'sale_price')
    search_fields = ('name', 'sku')

@admin.register(StockEntry)
class StockEntryAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'date')
    inlines = [StockEntryItemInline]