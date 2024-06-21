from django.shortcuts import render,redirect
from .models import pet,customer,cart,order,payment,orderdetail
from django.views.generic import ListView,CreateView,DetailView,DeleteView,UpdateView
from django.http import HttpResponse
from django.template import loader
from django.db.models import Q
from django.contrib.auth.hashers import make_password,check_password
from datetime import date
from django.conf import settings
import razorpay
# Create your views here.
class petview(ListView):
    model= pet
    template_name = 'petview.html'
    context_object_name ='petobj'
    
    def get_context_data(self, **kwargs):
        data = self.request.session['sessionvalue']
        context = super().get_context_data(**kwargs)
        context['session'] = data
        return context

def search(request):
    if request.method=="POST":
        serachdata= request.POST.get('searchquery')
        petobj = pet.objects.filter(Q(name__icontains= serachdata)|Q(species__icontains= serachdata)|Q(breed__icontains= serachdata))
        return render(request,'petview.html',{'petobj':petobj})
    
def register(request):
    if request.method == 'GET':
        return render(request,'register.html')
    elif request.method == "POST":
        fname= request.POST.get('n')
        email= request.POST.get('e')
        phoneno= request.POST.get('pn')
        password= request.POST.get('pw')
        epassword= make_password(password)

        custobj= customer(name = fname,email=email,phoneno=phoneno,password=epassword)

        cust=customer.objects.filter(email=custobj.email)
        if cust:
            custobj = customer.objects.get(email=custobj.email)
            return render(request,'register.html',{'msg':"Email Already Exists"})
        custobj.save()

        
        return redirect('../login')

def login(request):
    if request.method =='GET':
        return render(request,'login.html')
    elif request.method == 'POST':
        user = request.POST.get('useremail')
        password=request.POST.get('pwd')

        cust=customer.objects.filter(email=user)
        if cust:
            custobj = customer.objects.get(email=user)
            flag=check_password(password,custobj.password)
            if flag:
                request.session['sessionvalue']=custobj.email
                return redirect('../petview')
            else:
                return render(request,'login.html',{'msg':'Incorrect Username or Password'})
        else:
            return render(request,'login.html',{'msg':'Incorrect Username or Password'})
        

class petdetails(DetailView):
    model = pet
    template_name = 'petdetail.html'
    context_object_name = 'i'

class petviewcm(ListView):
    template_name='petview.html'
    context_object_name='petobj'

def petviewscmfun(request):
    petdetail=pet.cpetobj.getdata('dog')
    return render(request,'petview.html',{'petobj':petdetail})

def addcart(request):
    productid=request.POST.get('productid')
    custsession=request.session['sessionvalue']#email of customer
    custobj=customer.objects.get(email=custsession)#fetch all record from database table using email
    pobj=pet.objects.get(id=productid)
    
    
    flag=cart.objects.filter(cid=custobj.id,pid=pobj.id)
    if flag:
        cartobj=cart.objects.get(cid=custobj.id,pid=pobj.id)
        cartobj.quantity=cartobj.quantity+1
        cartobj.total=pobj.price*cartobj.quantity
        cartobj.save()
        
    else:
        cartobj=cart(cid=custobj,pid=pobj,quantity=1,total=pobj.price*1)
        cartobj.save()
    return redirect('../petview')

def viewcart(request):
    custsession=request.session['sessionvalue']
    custobj=customer.objects.get(email=custsession)
    cartobj=cart.objects.filter(cid=custobj.id)

    return render(request,'cart.html',{'cartobj':cartobj})

def cq(request):
    cemail = request.session['sessionvalue']
    pid = request.POST.get('pid')
    custobj = customer.objects.get(email = cemail)
    pobj = pet.objects.get(id = pid)
    cartobj = cart.objects.get(cid = custobj.id,pid=pobj.id)

    if request.POST.get('changequantitybutton')=='+':
        cartobj.quantity = cartobj.quantity + 1
        cartobj.total = cartobj.quantity * pobj.price
        cartobj.save()

    elif request.POST.get('changequantitybutton')=='-':
        if cartobj.quantity == 1:
            cartobj.delete()
        else :
            cartobj.quantity = cartobj.quantity - 1
            cartobj.total = cartobj.quantity * pobj.price
            # print(cartobj.total)
            cartobj.save()

    return redirect('../viewcart')

def summary(request):
    custsession=request.session['sessionvalue']
    custobj=customer.objects.get(email=custsession)
    cartobj=cart.objects.filter(cid=custobj.id)
    totalbill=0
    for i in cartobj:
        totalbill = i.total + totalbill 

    return render(request,'summary.html',{'session':custsession,'cartobj':cartobj,'totalbill':totalbill})


def placeorder(request):
    firstname=request.POST.get('fn')
    lastname=request.POST.get('ln')
    address=request.POST.get('address')
    city=request.POST.get('city')
    state=request.POST.get('state')
    pincode=request.POST.get('pincode')
    phoneno=request.POST.get('phoneno')

    datev= date.today()
    print(datev)
    orderobj=order(firstname=firstname, lastname=lastname, phoneno=phoneno, address=address, city=city, state=state, pincode=pincode, orderdate=datev, orderstatus='pending')
    orderobj.save()
    ono=str(orderobj.id) + str(datev).replace('-','')
    orderobj.ordernumber=ono
    orderobj.save()

    custsession=request.session['sessionvalue']
    custobj=customer.objects.get(email=custsession)
    cartobj=cart.objects.filter(cid=custobj.id)
    

    totalbill=0
    for i in cartobj:
        totalbill=totalbill + i.total
    from django.core.mail import EmailMessage
    sm=EmailMessage('Order placed','order placed from pet store application.total bill for your order is'+str(totalbill),to=['Kushwahaaryan068@gmail.com'])
    sm.send()

       # authorize razorpay client with API Keys.
    razorpay_client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
 
 

    currency = 'INR'
    amount = 20000  # Rs. 200
 
    # Create a Razorpay Order
    razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                       currency=currency,
                                                       payment_capture='0'))
 
    # order id of newly created order.
    razorpay_order_id = razorpay_order['id']
    callback_url = '../petview'
 
    # we need to pass these details to frontend.
    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = settings.RAZORPAY_KEY_ID
    context['razorpay_amount'] = amount
    context['currency'] = currency
    context['callback_url'] = callback_url

    return render(request,'payment.html',{'orderobj':orderobj,'session':custsession,'cartobj':cartobj,'totalbill':totalbill,'context':context})


def paymentsuccess(request):
    oid = request.GET.get('order_id')
    tid = request.GET.get('payment_id')
    request.session['sessionvalue'] = request.GET.get('session')
    custsession=request.session['sessionvalue']
    custobj=customer.objects.get(email=custsession)
    cartobj=cart.objects.filter(cid=custobj.id)
    # paymentobj=payment.objects.get(tid=paymentobj.transactionid)
    orderobj=order.objects.get(ordernumber= oid )
    paymentobj=payment(customerid= custobj,oid=orderobj,paymentstatus='complete',transactionid=tid,paymentmode='paypal')
    paymentobj.save()
    oobj=order.objects.filter(ordernumber=oid).update(orderstatus='Orderplaced')
    for i in cartobj:
        orderdetailobj=orderdetail(ordernumber=oid,customerid=custobj,productid=i.pid,quantity=i.quantity,totalprice=i.total,paymentid=paymentobj)
        orderdetailobj.save()
    cartobj.delete()
    return render(request,'paymentsuccess.html',{'session':custsession,'payobj':paymentobj})


    
    



    


    

