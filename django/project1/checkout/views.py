# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.http import JsonResponse
# from .forms import CheckoutForm, PaymentForm
# from .models import Order, OrderItem, PaymentMethod
# from decimal import Decimal

# def checkout(request):
#     # Sample order data - in a real app, this would come from your cart/session
#     order_items = [
#         {'brand': 'Prada', 'name': 'Leather mini bag', 'price': Decimal('1850.00')},
#         # Add more items as needed
#     ]
    
#     shipping_cost = Decimal('370.00')
#     discount = Decimal('0.00')
    
#     # Calculate total
#     subtotal = sum(item['price'] for item in order_items)
#     total = subtotal + shipping_cost - discount
    
#     # Create context with sample data for saved cards
#     context = {
#         'checkout_form': CheckoutForm(initial={'name': ''}),
#         'payment_form': PaymentForm(),
#         'saved_cards': [
#             {
#                 'id': 1,
#                 'logo': 'M',
#                 'last_four': '8232',
#                 'full_number': '4441 2354 3266 5655',
#                 'type': 'mastercard',
#                 'selected': True
#             },
#             {
#                 'id': 2,
#                 'logo': 'V',
#                 'last_four': '5442',
#                 'full_number': '4111 1111 1111 1111',
#                 'type': 'visa',
#                 'selected': False
#             }
#         ],
#         'order_items': order_items,
#         'shipping_cost': shipping_cost,
#         'discount': discount,
#         'subtotal': subtotal,
#         'total': total
#     }
    
#     if request.method == 'POST':
#         checkout_form = CheckoutForm(request.POST)
#         payment_form = PaymentForm(request.POST)
        
#         if checkout_form.is_valid() and payment_form.is_valid():
#             # In a real application, process payment here
            
#             # Save the order
#             order = checkout_form.save(commit=False)
#             order.total_amount = total
#             order.save()
            
#             # Save order items
#             for item in order_items:
#                 OrderItem.objects.create(
#                     order=order,
#                     product_name=item['name'],
#                     brand=item['brand'],
#                     price=item['price']
#                 )
            
#             # For AJAX requests, return JSON response
#             if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#                 return JsonResponse({'success': True, 'redirect': '/checkout/confirmation/'})
            
#             messages.success(request, 'Your order has been placed successfully!')
#             return redirect('order_confirmation')
#         else:
#             context['checkout_form'] = checkout_form
#             context['payment_form'] = payment_form
            
#             # For AJAX requests, return validation errors
#             if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#                 return JsonResponse({
#                     'success': False,
#                     'checkout_errors': checkout_form.errors,
#                     'payment_errors': payment_form.errors
#                 })
    
#     return render(request, 'checkout/checkout.html', context)

# def order_confirmation(request):
#     # Simple confirmation page
#     return render(request, 'checkout/confirmation.html')

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .forms import CheckoutForm, PaymentForm
from .models import Order, OrderItem, PaymentMethod
from decimal import Decimal
# Import your Cart model
from Thread_Inn.models import Cart  # Replace 'your_cart_app' with your actual cart app name

def checkout(request):
    # Get cart items using your existing code
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        total_cost = sum(item.product.price * item.quantity for item in cart_items)
    else:
        # Handle anonymous users if needed
        messages.warning(request, "Please log in to checkout")
        return redirect('login')  # Replace with your login URL name
    
    # Use the cart items for checkout
    order_items = []
    for item in cart_items:
        order_items.append({
            'brand': getattr(item.product, 'brand', 'N/A'),  # Use getattr in case some attributes don't exist
            'name': item.product.name,
            'price': item.product.price,
            'quantity': item.quantity,
            'total_price': item.product.price * item.quantity,
            'product_id': item.product.id,
        })
          
    # Calculate totals
    subtotal = total_cost
    shipping_cost = Decimal('20.00')
    discount = Decimal('0.00')
    tax= total_cost * Decimal('0.05')  # Example tax calculation
    total = subtotal + shipping_cost +tax - discount
          
    # Create context
    context = {
        'checkout_form': CheckoutForm(initial={'name': ''}),
        'payment_form': PaymentForm(),
        'saved_cards': [
            {
                'id': 1,
                'logo': 'M',
                'last_four': '8232',
                'full_number': '4441 2354 3266 5655',
                'type': 'mastercard',
                'selected': True
            },
            {
                'id': 2,
                'logo': 'V',
                'last_four': '5442',
                'full_number': '4111 1111 1111 1111',
                'type': 'visa',
                'selected': False
            }
        ],
        'cart_items': cart_items,  # Pass the original cart items
        'order_items': order_items,
        'shipping_cost': shipping_cost,
        'discount': discount,
        'tax':tax,
        'subtotal': subtotal,
        'total': total
    }
          
    if request.method == 'POST':
        checkout_form = CheckoutForm(request.POST)
        payment_form = PaymentForm(request.POST)
                  
        if checkout_form.is_valid() and payment_form.is_valid():
            # Save the order
            order = checkout_form.save(commit=False)
            order.total_amount = total
            order.user = request.user  # Associate order with user
            order.save()
                          
            # Save order items from cart
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product_name=item.product.name,
                    brand=getattr(item.product, 'brand', 'N/A'),
                    price=item.product.price,
                    quantity=item.quantity
                )
                          
            # Clear the cart after successful checkout
            cart_items.delete()
                          
            # For AJAX requests, return JSON response
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'redirect': '/checkout/confirmation'})
                          
            messages.success(request, 'Your order has been placed successfully!')
            return redirect('order_confirmation')
        else:
            context['checkout_form'] = checkout_form
            context['payment_form'] = payment_form
                          
            # For AJAX requests, return validation errors
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'checkout_errors': checkout_form.errors,
                    'payment_errors': payment_form.errors
                })
          
    return render(request, 'checkout/checkout.html', context)

def order_confirmation(request):
    # Simple confirmation page
    return render(request, 'Thread_Inn/index.html')
    # return redirect('order_confirmation')