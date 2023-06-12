import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from movie_question_solve.preprocess_question import question
from django.shortcuts import render, redirect
from .models import User
from movie_question_solve.question_record import add_record,get_all_record,delete_all_record


# Create your views here.


def index(request):
    if 'account' not in request.COOKIES or not request.COOKIES['account']:
        return redirect('/login')
    return render(request, 'index.html')


@csrf_exempt  # post授权
def getreply(request):
    data = request.POST
    print(data)
    q = str(data.get("inputinfo"))  # 获得问题
    name = str(data.get("name"))
    print(q)
    tmp = question()
    tmp.question_process(q)
    ans = tmp.answer
    print(ans)
    add_record(name,q,ans)
    response = JsonResponse({"replyinfo": ans})
    return response

def download(request):
    name=request.GET.get('name')
    data=get_all_record(name)
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="record.txt"'
    response.write(data)
    return response


def delete_record(request):
    name = request.GET.get('name')
    delete_all_record(name)
    return render(request, 'index.html')


def register(request):
    if request.method == 'POST':
        account = request.POST['account']
        password = request.POST['password']
        user = User(account=account, password=password)
        user.save()
        return redirect('/login')
    return render(request, 'register.html')


def login(request):
    if request.method == 'POST':
        account = request.POST['account']
        password = request.POST['password']
        try:
            user = User.objects.get(account=account, password=password)
            print(account)
            response = redirect('index')  # 重定向到index页面
            response.set_cookie('account', user.account, samesite='Strict')
            return response
        except User.DoesNotExist:
            error_message = "登陆失败"
            return render(request, 'login.html', {'error_message': error_message})
    return render(request, 'login.html')
