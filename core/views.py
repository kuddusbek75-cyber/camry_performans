from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Category, Product, Order, OrderItem, Profile

DEPARTMENTS = [
    {'key': 'stock',    'label': 'Сток механизм',   'desc': 'Оригинальные и аналоговые запчасти двигателя, подвески, трансмиссии'},
    {'key': 'interior', 'label': 'Салон и спорт',   'desc': 'Спортивные сиденья, руль, педали, мультимедиа, тюнинг салона'},
    {'key': 'body',     'label': 'Кузов и обвесы',  'desc': 'Бамперы, пороги, спойлеры, капоты, накладки, оптика'},
    {'key': 'tuning',   'label': 'Тюнинг мощности', 'desc': 'Чип-тюнинг, впуск, выхлоп, турбо, интеркулер, форсунки'},
    {'key': 'sport',    'label': 'Спорт и тюнинг',  'desc': 'Диски, койловеры, Brembo, аэродинамика, спортивная подвеска'},
]

def index(request):
    categories = Category.objects.all()
    featured_products = Product.objects.filter(in_stock=True)[:8]
    return render(request, 'index.html', {
        'categories': categories,
        'departments': DEPARTMENTS,
        'featured_products': featured_products,
    })

def department(request, dept_key):
    dept = next((d for d in DEPARTMENTS if d['key'] == dept_key), None)
    if not dept:
        return redirect('index')
    categories = Category.objects.filter(department=dept_key)
    products = Product.objects.filter(category__department=dept_key, in_stock=True)
    return render(request, 'department.html', {
        'dept': dept,
        'categories': categories,
        'products': products,
    })

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.all()
    return render(request, 'category_detail.html', {'category': category, 'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    related = Product.objects.filter(category=product.category).exclude(pk=pk)[:4]
    return render(request, 'product_detail.html', {'product': product, 'related': related})

def search(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        results = Product.objects.filter(title__icontains=query, in_stock=True)
    return render(request, 'search.html', {'results': results, 'query': query})

def get_cart(request):
    return request.session.get('cart', {})

def cart_view(request):
    cart = get_cart(request)
    items = []
    total = 0
    for pid, qty in cart.items():
        try:
            p = Product.objects.get(pk=int(pid))
            subtotal = p.price * qty
            total += subtotal
            items.append({'product': p, 'qty': qty, 'subtotal': subtotal})
        except Product.DoesNotExist:
            pass
    return render(request, 'cart.html', {'items': items, 'total': total})

def cart_add(request, pk):
    cart = get_cart(request)
    key = str(pk)
    cart[key] = cart.get(key, 0) + 1
    request.session['cart'] = cart
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'count': sum(cart.values())})
    return redirect('cart')

def cart_remove(request, pk):
    cart = get_cart(request)
    cart.pop(str(pk), None)
    request.session['cart'] = cart
    return redirect('cart')

def cart_count(request):
    cart = get_cart(request)
    return JsonResponse({'count': sum(cart.values())})

def checkout(request):
    cart = get_cart(request)
    if not cart:
        return redirect('cart')
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        comment = request.POST.get('comment', '')
        if name and phone:
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                name=name, phone=phone, comment=comment
            )
            total = 0
            for pid, qty in cart.items():
                try:
                    p = Product.objects.get(pk=int(pid))
                    OrderItem.objects.create(order=order, product=p, quantity=qty, price=p.price)
                    total += p.price * qty
                except Product.DoesNotExist:
                    pass
            order.total = total
            order.save()
            request.session['cart'] = {}
            messages.success(request, f'Заказ #{order.pk} оформлен! Мы свяжемся с вами.')
            return redirect('index')
    items = []
    total = 0
    for pid, qty in cart.items():
        try:
            p = Product.objects.get(pk=int(pid))
            subtotal = p.price * qty
            total += subtotal
            items.append({'product': p, 'qty': qty, 'subtotal': subtotal})
        except Product.DoesNotExist:
            pass
    return render(request, 'checkout.html', {'items': items, 'total': total})

@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    total_spent = sum(o.total for o in orders)
    total_orders = orders.count()
    total_items = sum(item.quantity for o in orders for item in o.items.all())

    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        profile.phone = request.POST.get('phone', '')
        profile.city = request.POST.get('city', '')
        profile.car_model = request.POST.get('car_model', '')
        profile.bio = request.POST.get('bio', '')
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        profile.save()
        messages.success(request, 'Профиль обновлён!')
        return redirect('profile')

    return render(request, 'profile.html', {
        'profile': profile,
        'orders': orders,
        'total_spent': total_spent,
        'total_orders': total_orders,
        'total_items': total_items,
    })

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Аккаунт создан!')
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')