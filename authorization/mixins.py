from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from authorization.utils.DBAudit import DBAudit


class AuthMixin:
    """ Class for process authorization users """
    template = ""

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("/office/")

        return render(request, self.template, context={})

    def post(self, request):
        user = authenticate(username=request.POST['username'], password=request.POST['password'])

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/office/')
            else:
                # Non active account
                return redirect('/')
        else:
            return render(request, self.template, context={"msg": "Логін або пароль не вірні"})


class RegisterMixin:
    """ Class for process registration new users """
    model = None
    template = ""
    href = "/auth/register/"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("/office/")
        return render(request, self.template, context={})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("/office/")

        data = request.POST

        if not DBAudit.check_email(data['email']) or not DBAudit.check_username(data['username']):
            return render(request, self.template, context={"msg": "Пошта або логін вже використовується"})

        User.objects.create_user(username=str(data['username']),
                                 email=str(data['email']),
                                 password=str(data['password']))

        self.create_profile(data)

        user = authenticate(username=data['username'], password=data['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/office/')
            else:
                return redirect('/')
        else:
            return redirect(self.href)

    def create_profile(self, data):
        profile = self.model.objects.get(user__username=str(data['username']))
        profile.name = str(data['name'])
        profile.surname = str(data['surname'])
        profile.last_name = str(data['last_name'])
        profile.save()


class LogoutMixin:
    """ Class for process logout users """
    href = ""

    def get(self, request):
        logout(request)
        return redirect(self.href)

    def post(self, request):
        logout(request)
        return redirect(self.href)
