from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.views import View
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from foodcartapp.forms.AuthForms import Login
from foodcartapp.forms.AuthForms import Signup


class SignUpView(View):
    def get(self, request, *args, **kwargs):
        form = Signup()
        return render(request, "sign_up.html", context={'title': 'SignUp', 'form': form})

    def post(self, request):
        form = Signup(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = User.objects.create_user(username=username, password=password)
            user.customuser.phone_number = form.cleaned_data['phone_number']
            user.customuser.address = form.cleaned_data['address']
            user.customuser.pincode = form.cleaned_data['pincode']

            staff = Group.objects.get(name="HotelAdmins")
            staff.user_set.add(user)
            user.is_staff = True
            user.save()
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('foodcartapp:HotelView')
            else:
                raise PermissionDenied


class LoginView(View):
    def get(self, request, *args, **kwargs):
        if(request.user.is_authenticated):
            if request.user.is_staff:
                return redirect("foodcartapp:HotelView")
            raise PermissionDenied

        form = Login()
        return render(request, "login.html", context={'title': 'Login | User', 'form': form})

    def post(self, request):
        form = Login(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_staff:
                    return redirect("foodcartapp:HotelView")
            raise PermissionDenied


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("foodcartapp:Login")
