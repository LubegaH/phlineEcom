from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Item, OrderItem, Order
from django.views.generic import ListView, DetailView
from django.utils import timezone


def checkout(request):
    return render(request, 'checkout-page.html')


class HomeView(ListView):
    model = Item
    template_name = "home.html"


# class CollectionsView(ListView):
#     model = Item
#     template_name = "collections.html"


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"


# Add to Shopping cart logic
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        # Check if order_item is in the order
        if order.item.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Item quantity has been updated")

        else:
            order.item.add(order_item)
            messages.info(request, "This item has been added to your cart")
            return redirect("core:product", slug=slug)

    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item has been added to your cart")
    return redirect("core:product", slug=slug)


# Remove from shopping cart logic
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )

    if order_qs.exists():
        order = order_qs[0]
        # Check if order_item is in the order
        if order.item.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.item.remove(order_item)
            messages.info(request, "This item has been removed from your cart")
            return redirect("core:product", slug=slug)
        else:
            # Message stating order does not contain this order item
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)


    else:
        # Message indicating user has no order
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)
