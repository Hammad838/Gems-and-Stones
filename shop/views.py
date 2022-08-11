from django.shortcuts import render
from .models import Product, Contact, Order, OrderUpdate
from math import ceil
import json
# Create your views here.
from django.http import HttpResponse

def index(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds':allProds}
    return render(request, 'shop/index.html', params)

def searchMatch(query, item):
    '''return true only if query matches the item'''
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False

def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]

        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds, "msg": ""}
    if len(allProds) == 0 or len(query)<4:
        params = {'msg': "Please make sure to enter relevant search query"}
    return render(request, 'shop/search.html', params)


def about(request):
    list = []
    list.append({'title': 'Mission', 'desc': '''
        "Our objectives are twofold. On the supply side, we aspire to
          be the world's leading environmentally responsible, human
          rights-minded, global supplier and discoverer of rare gems; to
          bridge income disparities throughout the gem industry by
          creating suitable working environments that will provide
          honorable livelihoods to employees at all levels of the supply
          chain. We aim to constantly develop and introduce new
          technologies to the gems' mining industry by being pioneers
          of innovation and technological advancements.
          On the demand side, we endeavor to provide our customers
          with the most profitable form of investment: one-of-a-kind,
          rare, and unique gems that serve as tangible, transportable,
          high-value assets that will always increase in value; and to
          serve our customers with the highest standards of honesty,
          integrity, and customer service".
    '''})
    list.append({'title': 'Geographical Region', 'desc': '''
        The mountains of Gilgit-Baltistan have an abundance of gemstones, such as
        emerald, aquamarine, peridot, spine, topaz, and garnet, among others. Gilgit. Baltistan is renowned for its assortment of colorful gemstones. Gilgit Baltistan
        features three well-known mountain ranges, including Himalaya, Hindu Kush,
        and Karakoram. Millions of years ago, two collisions between Asia and India
        created these mountain ranges. These collisions cause multiple phases of rock
        deformation. All of these geological processes created a separate mineral
        kingdom in GB. Mines & Minerals World Pvt. LTD's geographical position is one
        of its primary success factors, since it provides quick access to three well-known
        mountain ranges
    '''})
    list.append({'title': 'Value Chain Analysis', 'desc': '''
        The process of mining stones is the initial step in the gemstone route. There are
          several mining places accessible worldwide. However, in Pakistan, cutters and
          treaters are hard to come by, and only native miners are allowed to dig
          gemstones. Since there are no cutters or treaters nearby, the local miners sell
          their ore directly to marketers or raw dealers, who then send it to cutters in
          cutting centers. Ninety percent of the gems produced by our firm are sent to
          China, with the remaining ten percent going to Peshawar and other local
          markets
          '''})
    params = {'list': list}
    return render(request, 'shop/about.html', params)


def contact(request):
    thank = False
    if request.method=="POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        thank = True
    return render(request, 'shop/contact.html', {'thank': thank})


def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Order.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status":"success", "updates": updates, "itemsJson": order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')

    return render(request, 'shop/tracker.html')


def productView(request, myid):

    # Fetch the product using the id
    product = Product.objects.filter(id=myid)
    return render(request, 'shop/prodView.html', {'product':product[0]})


def checkout(request):
    if request.method=="POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amount', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        order = Order(items_json=items_json, name=name, email=email, address=address, city=city,
                       state=state, zip_code=zip_code, phone=phone, amount=amount)
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        update.save()
        # return render(request, 'shop/checkout.html', {'thank':thank, 'id': id})
        # Request paytm to transfer the amount to your account after payment by user
        param_dict = {
                'MID': 'Your-Merchant-Id-Here',
                'ORDER_ID': str(order.order_id),
                'TXN_AMOUNT': str(amount),
                'CUST_ID': email,
                'INDUSTRY_TYPE_ID': 'Retail',
                'WEBSITE': 'WEBSTAGING',
                'CHANNEL_ID': 'WEB',
                'CALLBACK_URL':'http://127.0.0.1:8000/shop/handlerequest/',

        }
        return render(request, 'shop/paytm.html', {'param_dict': param_dict})

    return render(request, 'shop/checkout.html')
