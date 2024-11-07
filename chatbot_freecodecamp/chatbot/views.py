from django.shortcuts import render,redirect
from django.http import JsonResponse
import openai
from transformers import pipeline
from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat
from django.utils import timezone
# Create your views here.

# open_api_key = "your_open_api_key"
# openai.api_key = open_api_key

# def ask_openai(message):
#     response = openai.completions.create(
#         model = "gpt-4o-mini",
#         prompt = message,
#         max_tokens = 150,
#         n=1,
#         stop=None,
#         temperature=0.7,
#     )
#     print(response)
#     answer = response.choices[0].text.strip()
#     return answer

def ask_trasformer(message):
    generator = pipeline("text-generation", model="distilgpt2")
    response = generator(message, max_length=30, num_return_sequences=1)
    print(response)
    return response[0]["generated_text"]


def chatbot(request):
    chats = Chat.objects.filter(user=request.user)
    if request.method == "POST":
        message = request.POST.get('message')
        # response = "Hi, this is my response"   #This is where the repsonse from LLM should be pasted.
        response = ask_trasformer(message)
        # print(response)

        chat = Chat(user=request.user,message=message,response=response,created_at=timezone.now)
        chat.save()

        return JsonResponse({'message':message,'response':response}) 
    return render(request,'chatbot.html',{"chats":chats})


def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(request,username=username,password=password)
        if user is not None:
            auth.login(request,user)
            return redirect('chatbot')
        else:
            error_message = "Invalid Username or password"
            return render(request,'login.html',{'error_message':error_message})
    else:
        return render(request,'login.html')

def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        passowrd1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if passowrd1 == password2:
            try:
                user =  User.objects.create_user(username,email,passowrd1)
                user.save()
                auth.login(request,user)
                return redirect('chatbot')
            except:
                error_message = 'Error creating account'
                return render(request,'register.html',{'error_message':error_message})    
        else:
            error_message = "Password dont match"
            return render(request,'register.html',{'error_message':error_message})
    return render(request,'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login')
    # return render(request)