from django.db import models
from django.core.validators import MinValueValidator
from phonenumber_field import modelfields
from django.db.models import F, Sum


class Restaurant(models.Model):
    name = models.CharField('название', max_length=50)
    address = models.CharField('адрес', max_length=100, blank=True)
    contact_phone = models.CharField('контактный телефон', max_length=50, blank=True)

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )

        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(verbose_name='название', max_length=50)
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        verbose_name='цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        verbose_name='картинка'
    )
    special_status = models.BooleanField(
        verbose_name='спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        verbose_name='описание',
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return '{} - {}'.format(self.restaurant.name, self.product.name)


class StatusOrder(models.TextChoices):
    unprocessed = 'Необработанный заказ', 'Необработанный заказ'
    in_work = 'Готовиться рестораном', 'Готовиться рестораном'
    delivery = 'Передан курьеру', 'Передан курьеру'
    completed = 'Заказ завершён', 'Заказ завершён'


class OrderQuerySet(models.QuerySet):
    def total_price(self):
        return self.annotate(price=Sum(F('quantity__price') * F('quantity__quantity'))).exclude(
            status=StatusOrder.completed).order_by('-status')

    def get_restaurants(self):
        restaurant_menu_items = RestaurantMenuItem.objects.select_related(
            'restaurant', 'product'
        ).filter(availability=True)

        for order in self:
            order_restaurants = []
            for order_product in order.quantity.all():
                product_restaurants = set()
                for restaurant_item in restaurant_menu_items:
                    if order_product.product == restaurant_item.product:
                        product_restaurants.add(restaurant_item.restaurant)
                order_restaurants.append(product_restaurants)

            get_restaurants = set.intersection(*order_restaurants)
            order.get_restaurants = get_restaurants

        return self


class StatusOrder(models.TextChoices):
    unprocessed = 'unprocessed', 'Необработанный заказ'
    in_work = 'in_work', 'Готовится рестораном'
    delivery = 'delivery', 'Передан курьеру'
    completed = 'completed', 'Заказ завершён'


class ChoicePay(models.TextChoices):
    cash = 'cash', 'Наличные'
    card = 'card', 'Карта'


class Order(models.Model):
    firstname = models.CharField(
        max_length=100,
        verbose_name='Имя')
    lastname = models.CharField(
        max_length=160,
        verbose_name='Фамилия')
    phonenumber = modelfields.PhoneNumberField(
        verbose_name='Номер телефона')
    address = models.CharField(
        max_length=255,
        verbose_name='Адрес',
        db_index=True)
    status = models.CharField(
        max_length=21,
        verbose_name='Статус заказа',
        choices=StatusOrder.choices,
        default=StatusOrder.unprocessed,
        db_index=True)
    comment = models.TextField(
        verbose_name='Комментарий',
        blank=True)
    created_at = models.DateTimeField(
        auto_created=True,
        auto_now_add=True,
        verbose_name='Дата создания заказа',
        db_index=True)
    called_at = models.DateTimeField(
        db_index=True,
        null=True,
        blank=True,
        verbose_name='Время звонка с клиентом')
    delivery_at = models.DateTimeField(
        db_index=True,
        null=True,
        blank=True,
        verbose_name='Время когда доставлен заказ')
    payment_method = models.CharField(
        max_length=8,
        verbose_name='Форма оплаты',
        choices=ChoicePay.choices,
        db_index=True)
    cooking_restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='Ресторан',
        related_name='orders')

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return '{}-{} {}'.format(self.firstname, self.lastname, self.address)


class ProductQuantity(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='quantity',
        verbose_name='Товар')
    quantity = models.PositiveSmallIntegerField(
        verbose_name='Кол-во',
        validators=[MinValueValidator(1)])
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='quantity',
        verbose_name='Товар, Кол-во')
    price = models.DecimalField(
        verbose_name='цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = 'Товар, Кол-во'
        verbose_name_plural = 'Товары, Кол-во'

    def __str__(self):
        return self.order.firstname
