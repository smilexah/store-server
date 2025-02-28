from django.urls import path

from products.views import ProductListView, basket_add, basket_remove

# from django.views.decorators.cache import cache_page

app_name = 'products'

urlpatterns = [
    path('', ProductListView.as_view(), name='index'),
    # path('', cache_page(30)(ProductListView.as_view()), name='index') - cache_page example
    path('baskets/add/<int:product_id>/', basket_add, name='basket_add'),
    path('baskets/remove/<int:basket_id>/', basket_remove, name='basket_remove'),
    path('category/<int:category_id>/', ProductListView.as_view(), name='category'),
    path('page/<int:page>/', ProductListView.as_view(), name='paginator'),
]
