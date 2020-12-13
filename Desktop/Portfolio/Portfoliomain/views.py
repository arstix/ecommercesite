from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .models import *
from .forms import OrderForm, CreateUserForm
from .filters import OrderFilter
# Create your views here.
from .decorators import unauthenticated_user, allowed_users, admin_only


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                redirect('home')
            else:
                messages.info(request, "Username or password is incorrect")

        context = {}
        return render(request, 'Portfoliomain/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')

def userPage(request):
    orders = request.user.customer.order_set.all()

    total_orders = orders.count()
    context = {'orders': orders, 'total_orders':total_orders,
    'delivered':delivered,'pending':pending}
    return render(request, 'Portfoliomain/user.html', context)

def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:

        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                user = form.save()
                Customer.objects.create(user=user,)
                username = form.cleaned_data.get('username')
                group = Group.objects.get(name='customer')
                user.groups.add(group)
                messages.success(request, 'Account was created for' + user)
                return redirect('login')
        context = {'form':form}
        return render(request, 'Portfoliomain/register.html', context)

@login_required(login_url='login')
@admin_only
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()

    total_customers = customers.count()

    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()
    context = {'orders':orders, 'customers':customers, 'total_orders':total_orders,
    'delivered':delivered,'pending':pending}
    return render(request, 'Portfoliomain/dashboard.html', context)

def products(request):
    products = Product.objects.all()
    return render(request, 'Portfoliomain/products.html', {'products': products})

def customer(request, pk_test):
    customer = Customer.objects.get(id=pk_test)

    orders = customer.order_set.all()
    order_count = orders.count()

    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs

    context = {'customer': customer, 'orders':orders, 'order_count':order_count, 'myFilter':myFilter}
    return render(request, 'Portfoliomain/customer.html', context)
@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def createOrder(request, pk):
    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=10)
    customer = Customer.objects.get(id=pk)
    formset = OrderFormSet(instance=customer)
    #form = OrderForm(initial={'customer':customer})
    if request.method == 'POST':
        #print('Printing POST:', request.POST)
        formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')


    context = {'formset':formset}
    return render(request, 'Portfoliomain/order_form.html', context)
@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def updateOrder(request, pk):

    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)
    if request.method == 'POST':
        #print('Printing POST:', request.POST)
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')
    context = {'form': form}
    return render(request, 'Portfoliomain/order_form.html', context)
@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == "POST":
        order.delete()
    context = {'item':order}
    return render(request, 'Portfoliomain/delete.html', context)
