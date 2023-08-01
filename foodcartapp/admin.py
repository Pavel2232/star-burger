from django.contrib import admin
from django.shortcuts import reverse
from django.templatetags.static import static
from django.utils.html import format_html
from .models import Product, Order, ProductQuantity, StatusOrder
from .models import ProductCategory
from .models import Restaurant
from .models import RestaurantMenuItem
from django import forms
from django.http import HttpResponseRedirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.encoding import iri_to_uri
class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html('<img src="{url}" style="max-height: 200px;"/>', url=obj.image.url)

    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html('<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>', edit_url=edit_url,
                           src=obj.image.url)

    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class ProductAdmin(admin.ModelAdmin):
    pass


class OrderQuantityForms(forms.ModelForm):
    price = forms.IntegerField(required=False)

    class Meta:
        model = ProductQuantity
        fields = '__all__'


class ProductQuantityInline(admin.TabularInline):
    form = OrderQuantityForms
    model = ProductQuantity
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', ]

    def response_change(self, request, obj):
        admin_page = super(OrderAdmin, self).response_change(request, obj)
        if url_has_allowed_host_and_scheme(request.GET.get('next'), None):
            url = iri_to_uri(request.GET.get('next'))
            return HttpResponseRedirect(url)
        else:
            return admin_page

    def get_form(self, request, order: Order=None, change=False, **kwargs):
        form = super().get_form(request, order, **kwargs)
        if order is None:
            return form
        name_restaurants = []
        for custom in Order.objects.filter(id=order.id).get_restaurants():
            for restaurant in custom.get_restaurants:
                name_restaurants.append(restaurant.name)
        form.base_fields['restaurant'].queryset = Restaurant.objects.filter(name__in=name_restaurants)
        order.status = StatusOrder.in_work
        return form
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.price = instance.product.price
            instance.save()
        formset.save()

    inlines = [
        ProductQuantityInline
    ]


