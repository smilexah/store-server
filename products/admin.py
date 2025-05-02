from django.contrib import admin
from django.utils.html import format_html
from .models import Product, ProductCategory, Basket

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    prepopulated_fields = {'name': ('name',)}  # Useful if you add slugs later


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'quantity', 'display_image', 'stripe_product_price_id')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    list_editable = ('price', 'quantity')  # Allow quick editing
    readonly_fields = ('stripe_product_price_id', 'image_preview')
    fieldsets = (
        (None, {
            'fields': ('name', 'category', 'description')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'quantity', 'stripe_product_price_id')
        }),
        ('Images', {
            'fields': ('image', 'image_preview')
        }),
    )

    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "-"
    display_image.short_description = 'Image Preview'

    def image_preview(self, obj):
        return self.display_image(obj)
    image_preview.short_description = 'Current Image'

    def save_model(self, request, obj, form, change):
        """Ensure Stripe product price is created if missing"""
        if not obj.stripe_product_price_id:
            stripe_product_price = obj.create_stripe_product_price()
            obj.stripe_product_price_id = stripe_product_price['id']
        super().save_model(request, obj, form, change)


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'created_timestamp')
    list_filter = ('user', 'created_timestamp')
    search_fields = ('user__username', 'product__name')
    readonly_fields = ('created_timestamp',)
    autocomplete_fields = ('user', 'product')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'product')