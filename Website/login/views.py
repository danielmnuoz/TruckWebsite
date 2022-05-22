import datetime

from django.contrib import messages
from django.contrib.auth import authenticate
from django.db import connection
from django.shortcuts import render, redirect

from .models import AuditLog
from .models import GeneralUser


# Create your views here.

def base(request):
    return render(request, 'base.html')


def create_account(request):
    if request.method == 'POST':
        # print('reachable code')
        username = request.POST.get('username')
        password = request.POST.get('password')
        type = request.POST.get('users')
        sqlCode = 'INSERT INTO GENERAL_USER(EMAIL,PASSWORD,USER_TYPE,POINTS) VALUES(%s, %s, %s, 0)'
        # print(username, password, type)
        if username and password and type:
            # add to audit log
            strToAdd = "Created " + username + "."
            date = datetime.datetime.now().date()
            AuditLog.objects.create(date=date, event=strToAdd)

            connection.cursor().execute(
                sqlCode,
                [username, password, type])
            return redirect('/user_login/')
    return render(request, 'createAccount.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        exists = 0
        usertype = 0

        # Parameterized SQL queries prevent SQL injection
        sqlUser = 'SELECT * FROM GENERAL_USER WHERE EMAIL = %s and PASSWORD = %s'
        sqlStoreRequest = 'INSERT INTO LOGINS(DATE, EMAIL, PASSFAIL) VALUES(now(), %s, %s)'
        user = authenticate(username=username, password=password)
        if user is not None:
            print("A backend authenticated the credentials")
        else:
            print("No backend authenticated credentials ")

        # Run a query. If the user exists, they are in the database
        for p in GeneralUser.objects.raw(sqlUser, [username, password]):
            exists = 1
            usertype = p.user_type
            ID = p.user_id

        # Store all requests to the database
        connection.cursor().execute(sqlStoreRequest, [username, exists])

        if exists:
            request.session['username'] = ID
            if usertype == 0:
                return redirect('/dashboard/admin/')
            elif usertype == 1:
                return redirect('/dashboard/sponsor/')
            elif usertype == 2:
                return redirect('/dashboard/user/')

        # The user does not exist in database. Redirect them to the same page.
        else:
            messages.error(request, 'username or password not correct')
            return redirect('/')


    else:
        return redirect('/')


def changePassword(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        try:
            if password == password2:
                if GeneralUser.objects.filter(email=username).exists():
                    GeneralUser.objects.update_or_create(email=username, defaults={'password': password})
                    return base(request)
            else:
                messages.error(request, 'Passwords do not match')
                # changePassword(request)
        except Exception:
            pass

        base(request)

    return render(request, "changePassword.html")
