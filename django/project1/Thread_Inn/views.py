import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from functools import wraps
import os
from django.conf import settings

from .models import Product, Cart
from .forms import ProductForm, CustomUserCreationForm


API_BASE_URL = 'http://127.0.0.1:7000/api/products'

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def api_add_product(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Validate required fields
            required_fields = ['name', 'desc', 'price', 'category']
            if not all(field in data for field in required_fields):
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            # Optional: Handle image upload or path
            image_path = data.get('image') if data.get('image') else None

            # Create product
            Product.objects.create(
                name=data['name'],
                description=data['desc'],
                price=data['price'],
                image=image_path,
                category=data['category'],
                added_by=request.user if request.user.is_authenticated else None  # Optional fallback
            )
            return JsonResponse({'message': 'Product added successfully'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
def product(request):
    response = requests.get(API_BASE_URL)
    if response.status_code == 200:
        products = response.json()
    else:
        products = []
        messages.error(request, "Could not fetch products.")
    return render(request, 'product.html', {'products': products})


def create_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        image_file = request.FILES.get('image')
        image_url = request.POST.get('image_url')

        if image_file:
            image = image_file.name
        elif image_url:
            image = image_url
        else:
            image = 'default.jpg'
        data = {
            'name': name,
            'desc': description,
            'price': int(float(price)),
            'image': image
        }
        response = requests.post(API_BASE_URL, json=data)
        
        if response.status_code == 201:
            messages.success(request, "Product added successfully!")
            return redirect('product')
        
        messages.error(request, "Failed to add product")
    
    return render(request, 'addproduct.html')

def product_detail(request, product_id):
    response = requests.get(f"{API_BASE_URL}/{product_id}")
    if response.status_code == 200:
        product_data = response.json()
        return render(request, 'product_detail.html', {'product': product_data})
    else:
        messages.error(request, {product_id})
        return redirect('product')

def update_product(request, product_id):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        image = request.POST.get('image')
        product_data = {
            'name': name,
            'desc': description,
            'price': price,
            'image': image
        }
        response = requests.put(f"{API_BASE_URL}/{product_id}", json=product_data)
        if response.status_code == 200:
            messages.success(request, "Product updated successfully!")
            return redirect('product_detail', product_id=product_id)
        else:
            messages.error(request, "Update failed.")
            return redirect('product')
    else:
        response = requests.get(f"{API_BASE_URL}/{product_id}")
        if response.status_code == 200:
            return render(request, 'updateproduct.html', {'product': response.json()})
        else:
            messages.error(request, f"Product not found (ID: {product_id})")
            return redirect('product')

@login_required
def delete_product_view(request, product_id):
    if request.method == 'POST':
        response = requests.delete(f"{API_BASE_URL}/{product_id}")
        if response.status_code == 200:
            messages.success(request, "Product deleted successfully!")
        else:
            messages.error(request, "Could not delete product.")
    return redirect('product')


def home(request):
    users_list = User.objects.all()
    return render(request, 'index.html', {'user': request.user, 'users_list': users_list})


@login_required
def dashboard(request):
    return render(request, "dashboard.html", {'user': request.user})


@login_required
def profile(request):
    return render(request, 'profile.html', {'user': request.user})


def purchase(request):
    return render(request, 'purchase.html')


def men(request):
    products = Product.objects.filter(category='men')
    cart_items = Cart.objects.filter(user=request.user) if request.user.is_authenticated else []
    return render(request, 'men.html', {
        'products': products,
        'cart_items': cart_items,
        'total_price': total_price(request)
    })


def women(request):
    products = Product.objects.filter(category='women')
    cart_items = Cart.objects.filter(user=request.user) if request.user.is_authenticated else []
    return render(request, 'women.html', {
        'products': products,
        'cart_items': cart_items,
        'total_price': total_price(request)
    })

def bottom(request):
    products = Product.objects.filter(category='bottom')
    cart_items = Cart.objects.filter(user=request.user) if request.user.is_authenticated else []
    return render(request, 'bottom.html', {
        'products': products,
        'cart_items': cart_items,
        'total_price': total_price(request)
    })

def shoes(request):
    products = Product.objects.filter(category='shoes')
    cart_items = Cart.objects.filter(user=request.user) if request.user.is_authenticated else []
    return render(request, 'shoes.html', {
        'products': products,
        'cart_items': cart_items,
        'total_price': total_price(request)
    })

def tshirt(request):
    products = Product.objects.filter(category='tshirt')
    cart_items = Cart.objects.filter(user=request.user) if request.user.is_authenticated else []
    return render(request, 'tshirt.html', {
        'products': products,
        'cart_items': cart_items,
        'total_price': total_price(request)
    })

def kids(request):
    products = Product.objects.filter(category='kids')
    cart_items = Cart.objects.filter(user=request.user) if request.user.is_authenticated else []
    return render(request, 'kids.html', {
        'products': products,
        'cart_items': cart_items,
        'total_price': total_price(request)
    })


def total_price(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        return sum(item.product.price * item.quantity for item in cart_items)
    return 0


@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_cost = sum(item.total_price() for item in cart_items)
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_cost': total_cost,
    })



@user_passes_test(lambda u: u.is_staff or u.is_superuser)
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    user = request.user
    cart_item, created = Cart.objects.get_or_create(user=user, product=product)
    if not created:
        cart_item.quantity += 1
    else:
        cart_item.quantity = 1
    cart_item.save()
    

    return redirect(product.category)  


@login_required
def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart_item = Cart.objects.filter(user=request.user, product=product).first()
    
    if cart_item:
        cart_item.delete()
        messages.success(request, "Item removed from cart successfully!")
    else:
        messages.error(request, "This item is not in your cart.")
    
    return redirect('cart')

@login_required
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_cost = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_cost': total_cost
    })


def role_required(role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            messages.error(request, "Role-based access is not supported currently.")
            return redirect('dashboard')
        return _wrapped_view
    return decorator


@login_required
def role_assign(request):
    messages.warning(request, "Role assignment not supported with default User model.")
    return redirect('home')


@role_required('admin')
def admin_panel(request):
    return render(request, 'admin.html', {'user': request.user})


def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not username or not email or not password1 or not password2:
            messages.error(request, "All fields are required.")
            return redirect('register')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()

        logout(request)
        messages.success(request, "Account created successfully! You can now log in.")
        return redirect('login')

    return render(request, 'register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = AuthenticationForm()

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('home')
            else:
                messages.error(request, "Invalid email or password.")
        except User.DoesNotExist:
            messages.error(request, "No account found with this email!")

    return render(request, 'login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect('register')


# Product Creation View (Restricted to Staff and Superadmins)
@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully!")
            return redirect('product_list')  # Redirect to your product list page after adding a product
    else:
        form = ProductForm()

    return render(request, 'add_product.html', {'form': form})


from django.core.exceptions import PermissionDenied

# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Product
from django.contrib.auth.decorators import user_passes_test

def is_admin(user):
    return user.is_superuser or user.is_staff

def add_product_view(request):
    if request.method == 'POST':
        name = request.POST.get('product_name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')  
        image = request.POST.get('image')  
        category = request.POST.get('category')

        if name and description and price and category:
            try:
                if image and not image.startswith("images/"):
                    image = f"images/{image}"

                Product.objects.create(
                    name=name,
                    description=description,
                    price=price,
                    image=image,
                    category=category,
                    added_by=request.user
                )
                messages.success(request, "Product added successfully!")
                return redirect('add_product')
            except Exception as e:
                messages.error(request, f"Something went wrong: {e}")
        else:
            messages.error(request, "All required fields must be filled.")

    return render(request, 'add_product.html')




# Product List View
@login_required
def product_list(request):
    if not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied

    if request.user.is_superuser:
        products = Product.objects.all()
    else:
        products = Product.objects.filter(added_by=request.user)

    total_products = Product.objects.all().count()

    return render(request, 'product_list.html', {
        'products': products,
        'total_products': total_products,
    })



# Edit Product View
@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if not (request.user.is_superuser or (request.user.is_staff and product.added_by == request.user)):
        messages.error(request, "You don't have permission to edit this product.")
        return redirect('product_list')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            if 'image' in request.FILES:
                product.image = request.FILES['image']
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect('product_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProductForm(instance=product)

    return render(request, 'edit_product.html', {
        'form': form,
        'product': product,
        'current_image': product.image  # Pass current image to template
    })


# Delete Product View
@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if not (request.user.is_superuser or (request.user.is_staff and product.added_by == request.user)):
        raise PermissionDenied

    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted successfully!")
        return redirect('product_list')

    return render(request, 'confirm_delete.html', {'product': product})
