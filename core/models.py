from django.db import models
from django.contrib.auth.models import User

DEPARTMENT_CHOICES = [
    ('stock',    'Сток запчасти — механизм'),
    ('interior', 'Салон и спорт товары'),
    ('body',     'Кузовные детали и тюнинг'),
    ('tuning',   'Тюнинг двигателя и мощность'),
    ('sport',    'Спорт и тюнинг'),
]

class Profile(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar     = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')
    phone      = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    city       = models.CharField(max_length=100, blank=True, verbose_name='Город')
    car_model  = models.CharField(max_length=100, blank=True, verbose_name='Модель Camry')
    bio        = models.TextField(blank=True, verbose_name='О себе')

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return f'Профиль {self.user.username}'


class Category(models.Model):
    name       = models.CharField(max_length=100, verbose_name='Название')
    slug       = models.SlugField(unique=True)
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES, default='stock', verbose_name='Отдел')
    description= models.TextField(blank=True, verbose_name='Описание')
    image      = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name='Фото')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return f'{self.get_department_display()} → {self.name}'


class CarModel(models.Model):
    name  = models.CharField(max_length=50, verbose_name='Поколение')
    years = models.CharField(max_length=50, verbose_name='Годы')
    code  = models.CharField(max_length=20, verbose_name='Кузов')

    class Meta:
        verbose_name = 'Модель Camry'
        verbose_name_plural = 'Модели Camry'

    def __str__(self):
        return f'{self.name} ({self.years})'


class Product(models.Model):
    category       = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Категория')
    compatible_with= models.ManyToManyField(CarModel, blank=True, verbose_name='Совместимость')
    title          = models.CharField(max_length=250, verbose_name='Название')
    description    = models.TextField(verbose_name='Описание')
    price          = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена (сом)')
    image          = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='Фото')
    in_stock       = models.BooleanField(default=True, verbose_name='В наличии')
    is_premium     = models.BooleanField(default=False, verbose_name='Премиум')
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.title


class Order(models.Model):
    STATUS_CHOICES = [
        ('new',        'Новый'),
        ('processing', 'В обработке'),
        ('ready',      'Готов к выдаче'),
        ('done',       'Выдан'),
        ('cancelled',  'Отменён'),
    ]
    user       = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Пользователь')
    name       = models.CharField(max_length=100, verbose_name='Имя')
    phone      = models.CharField(max_length=20, verbose_name='Телефон')
    comment    = models.TextField(blank=True, verbose_name='Комментарий')
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Статус')
    total      = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Итого')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ #{self.pk} — {self.name}'


class OrderItem(models.Model):
    order    = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product  = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price    = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f'{self.product.title} × {self.quantity}'