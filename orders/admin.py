from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # Don't show extra empty forms

    def get_queryset(self, request):
        # Get the base queryset
        qs = super().get_queryset(request)

        # If we're editing an existing order, filter items to only those for this order
        if request.resolver_match.url_name == 'orders_order_change':
            order_id = request.resolver_match.kwargs['object_id']
            return qs.filter(order_id=order_id)

        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # If we're adding a new order item, dynamically filter related fields
        if db_field.name == "product":  # assuming you have a product field
            if request.resolver_match.url_name == 'orders_order_change':
                order_id = request.resolver_match.kwargs['object_id']
                order = Order.objects.get(id=order_id)
                # You could filter products based on order.initiator or other criteria
                kwargs["queryset"] = db_field.remote_field.model.objects.filter(
                    # Add your filtering logic here
                    # For example, only show products that were in the user's basket
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'status', 'created')
    list_filter = ('status', 'created')
    inlines = [OrderItemInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Add any custom filtering for the Order admin list view
        if not request.user.is_superuser:
            # Example: only show orders for the current user if not superuser
            qs = qs.filter(initiator=request.user)
        return qs