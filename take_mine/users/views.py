from django.contrib.auth import get_user_model, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from app.utils import get_page_context
from .forms import UserRegisterForm

User = get_user_model()  # Правильный способ получения модели пользователя

def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get("username")
            # Явный вход пользователя после регистрации
            login(request, user)
            messages.success(
                request, f"Аккаунт создан для {username}! Теперь вы можете войти."
            )
            return redirect("app:index")
    else:
        form = UserRegisterForm()
    return render(request, "users/register.html", {"form": form})
@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    items = user.items.select_related("category").order_by("-created_at")
    context = {"items": items, "author": user}
    context.update(get_page_context(items, request))
    return render(request, "users/profile.html", context)