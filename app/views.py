from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render,redirect, get_object_or_404
from .models import Product,Order,OrderDetail, Cart, CartItem, OrderReview
import json
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from .forms import ContactForm, ProductForm, AddressForm, OrderReviewForm
from rest_framework import viewsets
from .serializers import ProductSerializer
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime
# Create your views here.
class ProductViewset(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        products = Product.objects.all()
        name = self.request.GET.get('name')

        if name:
            products = products.filter(name__contains=name)
        return products

def home(req):
    products = Product.objects.all()
    return render(req, 'home/index.html', {'products': products})

def prodDetail(req,id):
    product = Product.objects.get(id=id)
    return render(req,'productDetail/index.html',{'product':product})

def registerV(req):
    if req.method=='POST':
        first_name = req.POST['first_name']
        last_name = req.POST['last_name']
        email = req.POST['email']
        password = req.POST['pass']
        confirm_password = req.POST.get('confirm_pass', '')
        
        # Validaciones
        if not all([first_name, last_name, email, password]):
            messages.error(req, 'Todos los campos son obligatorios')
            return render(req, 'register/index.html')
            
        if password != confirm_password:
            messages.error(req, 'Las contraseñas no coinciden')
            return render(req, 'register/index.html')
            
        if len(password) < 8:
            messages.error(req, 'La contraseña debe tener al menos 8 caracteres')
            return render(req, 'register/index.html')
            
        if User.objects.filter(email=email).exists():
            messages.error(req, 'Este correo electrónico ya está registrado')
            return render(req, 'register/index.html')
            
        try:
            username = email.split('@')[0]
            # Verificar si el username ya existe
            if User.objects.filter(username=username).exists():
                username = f"{username}{User.objects.count()}"
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            if user is not None:
                messages.success(req, '¡Registro exitoso! Por favor inicia sesión.')
                return redirect('login')
            else:
                messages.error(req, 'Error al crear el usuario')
                return render(req, 'register/index.html')
        except Exception as e:
            messages.error(req, f'Error en el registro: {str(e)}')
            return render(req, 'register/index.html')
        
    return render(req, 'register/index.html')

def loginV(req):
    if req.method=='POST':
        username = req.POST['username']
        password = req.POST['pass']

        if not username or not password:
            messages.error(req, 'Por favor ingresa tu usuario y contraseña')
            return render(req, 'login/index.html')

        # Intentar autenticar primero con el nombre de usuario
        user = authenticate(req, username=username, password=password)
        
        # Si falla, intentar con el correo electrónico
        if user is None and '@' in username:
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(req, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass

        if user is not None:
            login(req, user)
            messages.success(req, f'¡Bienvenido {user.first_name}!')
            return redirect('home')
        else:
            messages.error(req, 'Usuario o contraseña incorrectos. Recuerda que puedes usar tu correo electrónico o nombre de usuario.')
            return render(req, 'login/index.html')

    return render(req, 'login/index.html')

def logoutV(req):
    logout(req)
    return redirect('login')

@login_required
def pay(req):
    cart, created = Cart.objects.get_or_create(user=req.user)
    items = cart.items.all()
    total = sum(item.get_total_price() for item in items)
    if not items:
        messages.warning(req, "Tu carrito está vacío. Agrega productos antes de pagar.")
        return redirect('view_cart')

    # Dirección
    try:
        address = req.user.address
    except:
        address = None

    if req.method == 'POST':
        form = AddressForm(req.POST, instance=address)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = req.user
            address.save()
            messages.success(req, 'Dirección guardada correctamente.')
            return redirect('pay')
    else:
        form = AddressForm(instance=address)

    context = {
        'cart': cart,
        'items': items,
        'total': total,
        'form': form,
        'address': address
    }
    return render(req, 'pay/index.html', context)

@login_required
def customerData(req):
    user = req.user
    return render(req,'customerData/index.html',{'user' : user})

@login_required
def delete_user(req):
    if req.method == 'POST':
        user = req.user
        user.delete()
        messages.success(req, 'Tu cuenta ha sido eliminada con éxito.')
        
    return render(req, 'confirmDelete/index.html')

@login_required
def edit_user(req):
    if req.method == 'POST':
        method = req.POST.get('_method', '').upper()
        if method == 'PUT':
            user = req.user
            user.username = req.POST.get('username')
            user.first_name = req.POST.get('first_name')
            user.last_name = req.POST.get('last_name')
            user.email = req.POST.get('email')
            user.save()
            return redirect('customerData')  
    return render(req, 'edit_user.html')

@csrf_exempt
@login_required
def create_order(req):
    if req.method == 'POST':
        try:
            data = json.loads(req.body)
            products = data.get('products', [])
            
            # Crear la orden
            order = Order.objects.create(user=req.user, status='Pending', total_amount=0.00)

            total_amount = 0
            for item in products:
                product = Product.objects.get(id=item['id'])
                quantity = item['quantity']
                price = product.price

                OrderDetail.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=price
                )

                total_amount += quantity * price

            order.total_amount = total_amount
            order.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def order_history(req):
    orders = Order.objects.filter(user=req.user).order_by('-created_at')
    # Filtros
    estado = req.GET.get('estado', '')
    fecha_inicio = req.GET.get('fecha_inicio', '')
    fecha_fin = req.GET.get('fecha_fin', '')
    if estado:
        orders = orders.filter(status__iexact=estado)
    if fecha_inicio:
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            orders = orders.filter(created_at__date__gte=fecha_inicio_dt)
        except ValueError:
            pass
    if fecha_fin:
        try:
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
            orders = orders.filter(created_at__date__lte=fecha_fin_dt)
        except ValueError:
            pass
    paginator = Paginator(orders, 5)
    page_number = req.GET.get('page')
    page_obj = paginator.get_page(page_number)
    order_details = []
    # Manejo de review POST
    if req.method == 'POST' and req.POST.get('review_order_id'):
        order_id = req.POST.get('review_order_id')
        order = get_object_or_404(Order, id=order_id, user=req.user)
        try:
            review = order.review
            form = OrderReviewForm(req.POST, instance=review)
        except OrderReview.DoesNotExist:
            form = OrderReviewForm(req.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.order = order
            review.user = req.user
            review.save()
            messages.success(req, '¡Gracias por tu comentario!')
            return redirect('order_history')
    # Preparar detalles y forms
    for order in page_obj:
        details = OrderDetail.objects.filter(order=order)
        review_form = None
        try:
            review = order.review
            review_form = OrderReviewForm(instance=review)
        except OrderReview.DoesNotExist:
            review = None
            review_form = OrderReviewForm()
        order_details.append({
            'order': order,
            'details': details,
            'review': review,
            'review_form': review_form
        })
    context = {
        'order_details': order_details,
        'page_obj': page_obj,
        'estado': estado,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin
    }
    return render(req, 'orders/index.html', context)

def contact(req):
    data = {
        'form': ContactForm()
    }
    if req.method == 'POST':
        form = ContactForm(data=req.POST)
        if form.is_valid():
            form.save()
            messages.success(req, "Formulario enviado")
        else:
            data['form'] = form
    return render(req, 'contact/index.html', data)

@permission_required('app.add_product')
def addProduct(req):
    data = {
        'form': ProductForm()
    }
    if req.method == 'POST':
        form = ProductForm(data=req.POST, files=req.FILES)
        if form.is_valid():
            form.save()
            messages.success(req, "producto registrado")
        else:
            data['form'] = form
    return render(req, 'addProduct/index.html', data)

@permission_required('app.view_product')
def listProduct(req):
    Products = Product.objects.all()  
    data = { 
        'Products' : Products
    }
    return render(req, 'listProduct/index.html', data)

@permission_required('app.change_product')
def modifyProduct(req,id):
    product = Product.objects.get(id=id)
    data = {
        'form':ProductForm(instance=product)
    }
    if req.method == 'POST':
       form = ProductForm(data=req.POST, instance=product, files=req.FILES)
       if form.is_valid():
           form.save()
           messages.success(req, "producto modificado correctamente.")
           return redirect(to=listProduct)
       data['form'] = form
    return render(req, 'modifyProduct/index.html', data)

@permission_required('app.delete_product')
def deleteProduct(req,id):
    product = get_object_or_404(Product, id=id)
    product.delete()
    messages.success(req, "producto eliminado correctamente.")
    return redirect(to=listProduct)

@login_required
def view_cart(req):
    cart, created = Cart.objects.get_or_create(user=req.user)
    items = cart.items.all()
    total = sum(item.get_total_price() for item in items)
    
    context = {
        'cart': cart,
        'items': items,
        'total': total
    }
    return render(req, 'cart/index.html', context)

@login_required
def add_to_cart(req, product_id):
    if req.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        cart, created = Cart.objects.get_or_create(user=req.user)
        
        # Obtener la cantidad del formulario
        quantity = int(req.POST.get('quantity', 1))
        
        # Verificar stock
        if quantity > product.stock:
            messages.error(req, f'Solo hay {product.stock} unidades disponibles')
            return redirect('prodDetail', id=product_id)
        
        # Verificar si el producto ya está en el carrito
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'price': product.price, 'quantity': quantity}
        )
        
        if not created:
            # Si el producto ya existe, actualizar la cantidad
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.stock:
                messages.error(req, f'No hay suficiente stock. Solo quedan {product.stock} unidades')
                return redirect('prodDetail', id=product_id)
            cart_item.quantity = new_quantity
            cart_item.save()
        
        messages.success(req, f'Producto {product.name} agregado al carrito')
        return redirect('view_cart')
    
    return redirect('home')

@login_required
def update_cart_item(req, item_id):
    if req.method == 'POST':
        try:
            data = json.loads(req.body)
            quantity = int(data.get('quantity', 1))
            
            if quantity < 1:
                return JsonResponse({'success': False, 'message': 'La cantidad debe ser mayor a 0'})
            
            cart_item = get_object_or_404(CartItem, id=item_id, cart__user=req.user)
            cart_item.quantity = quantity
            cart_item.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Cantidad actualizada',
                'total': cart_item.get_total_price()
            })
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Datos inválidos'})
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Cantidad inválida'})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

@login_required
def remove_cart_item(req, item_id):
    if req.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=req.user)
        cart_item.delete()
        messages.success(req, "Producto eliminado del carrito")
        return redirect('view_cart')
    return redirect('view_cart')

@login_required
def change_cart_item_quantity(req, item_id, action):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=req.user)
    if req.method == 'POST':
        if action == 'add':
            if cart_item.quantity < cart_item.product.stock:
                cart_item.quantity += 1
                cart_item.save()
            else:
                messages.error(req, 'No hay más stock disponible.')
        elif action == 'subtract':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                messages.error(req, 'La cantidad mínima es 1.')
    return redirect('view_cart')

@csrf_exempt
@login_required
def paypal_complete(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart, _ = Cart.objects.get_or_create(user=request.user)
            items = cart.items.all()
            total = int(sum(item.get_total_price() for item in items))
            try:
                address = request.user.address
            except:
                address = None
            order = Order.objects.create(
                user=request.user,
                total_amount=total,
                address=address.street if address else '',
                addressNro=address.number if address else '',
                status='Pagado'
            )
            for item in items:
                OrderDetail.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.price
                )
            items.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    details = OrderDetail.objects.filter(order=order)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="boleta_pedido_{order.id}.pdf"'
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    y = height - 50
    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, y, f"Boleta Pedido #{order.id}")
    y -= 40
    p.setFont("Helvetica", 12)
    p.drawString(50, y, f"Fecha: {order.created_at.strftime('%d/%m/%Y %H:%M')}")
    y -= 20
    p.drawString(50, y, f"Cliente: {order.user.first_name} {order.user.last_name} ({order.user.email})")
    y -= 20
    p.drawString(50, y, f"Dirección: {order.address} {order.addressNro}")
    y -= 20
    p.drawString(50, y, f"Método de pago: PayPal")
    y -= 30
    p.setFont("Helvetica-Bold", 13)
    p.drawString(50, y, "Productos:")
    y -= 20
    p.setFont("Helvetica", 12)
    p.drawString(50, y, "Nombre")
    p.drawString(250, y, "Cantidad")
    p.drawString(350, y, "Precio")
    p.drawString(450, y, "Subtotal")
    y -= 15
    p.line(50, y, 550, y)
    y -= 15
    for detail in details:
        if y < 100:
            p.showPage()
            y = height - 50
        p.drawString(50, y, detail.product.name)
        p.drawString(250, y, str(detail.quantity))
        p.drawString(350, y, "${:,}".format(int(detail.price)))
        p.drawString(450, y, "${:,}".format(int(detail.get_total_price())))
        y -= 20
    y -= 10
    p.line(50, y, 550, y)
    y -= 25
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Total: ${:,}".format(int(order.total_amount)))
    p.showPage()
    p.save()
    return response