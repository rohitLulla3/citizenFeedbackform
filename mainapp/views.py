from pstats import Stats
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.contrib import messages
from .utils import generate_graph, generate_piechart, generate_qrcode, send_otp,feedback_type
from mainapp.forms import MyLoginForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required



from .models import Feedback, VerificationCodes

# Create your views here.

def home(request):
    if request.method == "POST":
        email = request.POST['email']
        request.session['email'] = email
        send_otp(email)
        return HttpResponseRedirect("/otp")

    return render(request,'home.html')
    
def otp_verify(request):
    if not request.session.get("email"):
        return HttpResponseRedirect("/")

    if request.method == 'POST':
        otp = request.POST['otp']
        email = request.session['email']
        print("➡ email :", email)
        verification_code = VerificationCodes.objects.filter(email=email,otp = otp).last()
        print("➡ verification_code :", verification_code)

        if verification_code:
            verification_code.delete()
            messages.info(request, "You are successfully logged in.")
            request.session["otp_verified"] = True
            del request.session['email']
            return HttpResponseRedirect("/feedback")
    return render(request, 'otp.html')

def adm(request):
    form=MyLoginForm()
    if request.method=="POST":
      form=MyLoginForm(request.POST)
      if form.is_valid():
        username = request.POST['username']
        passwd = request.POST['pass']
        user = authenticate(request,username=username,password = passwd)
        if user is not None:
            login(request,user)
            messages.success(request, "Success")
            return HttpResponseRedirect("/stats")

      else:
        print(form.errors)
        print("fail")
        messages.error(request, " Invalid Captcha")
    return render(request,"admin_login.html",{"form":form})

@login_required
def mainadm(request):
    display_qr=False
    if request.method == 'POST':

        city = request.POST['site']
        print("➡ city :", city)
        generate_qrcode(city)
        display_qr=False
        if city:
            display_qr = True
        context = {"city":city,'show_qr':display_qr}
    else:
        context = {'show_qr':display_qr}    

    return render(request,'admin.html',context)
    

def feedback(request):

    data = request.GET
    city = data.get("city")
    if city:
        request.session["city"] = city


    if not request.session.get("otp_verified"):
        return HttpResponseRedirect("/")

    if request.method == 'POST':
        how_do_you_come = request.POST.get('site',None)
        waiting_time = request.POST.get('waiting_time',None)
        overall = request.POST.get('rating1',None)
        servicing = request.POST.get('rating2',None)
        behaviour = request.POST.get('rating3',None)
        feedback = request.POST.get('description',None)
        police_name = request.POST.get('police_name',None)
        type_feedback = feedback_type(overall,servicing,behaviour)
        rec = Feedback(reason_to_come = how_do_you_come,waiting_time= waiting_time, overall=overall, behaviour=behaviour, servicing = servicing, type_feedback=type_feedback, city=request.session["city"],police_name=police_name, feedback=feedback)
        rec.save()
        del request.session["otp_verified"]
        messages.success(request,"Form Successfully submitted!!")

    return render(request,'feedback.html')

# def feedbacks(request):
#     data = Feedback.objects.all().filter(type_feedback = 'positive')
#     print(data)
#     return HttpResponse(data)

def bar_graph(request):

    feedbacks = Feedback.objects.all()
    neg_points = []
    pos_points = []
    cities = []
    if request.method == 'POST':
        cities = request.POST.getlist('site')
        pie_city = request.POST['city']
    
        for city in cities:
            negative = feedbacks.filter(city__icontains=city.lower(), type_feedback="negative")
            neg_points.append(negative.count())

            positive = feedbacks.filter(city__icontains=city.lower(), type_feedback="positive")
            pos_points.append(positive.count())

        generate_graph(cities=cities, negative_points=neg_points, positive_points=pos_points)
        generate_piechart(pie_city,)

    return render(request, "graph.html")
