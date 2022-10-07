import qrcode 
import random
import smtplib
from django.conf import settings
from .models import VerificationCodes
import mpld3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  
import numpy as np

def send_email(to_email, message):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(settings.FROM_EMAIL, settings.EMAIL_PASSWORD)
    s.sendmail('Test message',to_email, message)


def send_otp(email):
    rand=random.randint(1000,9999)
    
    # To add the random otp in our table 
    VerificationCodes.objects.create(
            email = email,
            otp = rand,
        )
    msg=f"Your One Time Password(OTP) is {rand}"

    send_email(to_email=email, message=msg)

def feedback_type(overall,servicing,behaviour):
    rating = int(overall) + int(servicing) + int(behaviour)
    if rating >= 9 :
        return "positive"
    else:
        return "negative"

def generate_qrcode(loc):

    features = qrcode.QRCode(version = 1, box_size = 40, border = 3)

    features.add_data(f'127.0.0.1:8000/feedback?city={loc}')

    features.make(fit = True)

    generated = features.make_image()
    generated.save(f"mainapp/static/images/qrcodes/{loc}.png")


def generate_graph(cities, negative_points, positive_points):
    x=np.arange(len(cities))
    plt.bar(x -0.2,positive_points,0.4,color='g',edgecolor='green',label="postive feedbacks")
    plt.bar(x +0.2,negative_points,0.4,color='r',edgecolor='red',label="negative feedbacks")
    plt.xlabel("City")
    plt.ylabel("Number of feedbacks")
    plt.title("Type of feedback")
    plt.legend()
    plt.xticks(np.arange(len(cities)) +1 ,5.0,cities)
    plt.savefig('mainapp/static/images/graphs/feedback_graph.png')
    plt.close()


def generate_piechart(city,pos,neg):
    feedback = ["positive","Negative"]
    feed=[pos,neg]
    fig = plt.figure(figsize = (10 , 7))
    #fig2=plt.figure(figsize = (10,7))
    plt.pie(feed, labels = feedback,autopct='%1.1f%%')
    plt.title(city)
    plt.savefig('mainapp/static/images/graphs/feedback_graph.png')
    plt.close()

