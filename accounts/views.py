from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from app.models import Category, News


def base_ctx():
    return {
        'categories': Category.objects.all(),
        'latest_news': News.objects.all()[:5],
    }


# ── LOGIN ──────────────────────────────────────────────────
def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f"Xush kelibsiz, {user.username}!")
            return redirect(request.GET.get('next', 'home'))
        messages.error(request, "❌ Login yoki parol noto'g'ri!")
    return render(request, 'accounts/login.html', base_ctx())


# ── LOGOUT ─────────────────────────────────────────────────
def user_logout(request):
    logout(request)
    messages.success(request, "Tizimdan chiqdingiz.")
    return redirect('home')


# ── REGISTER ───────────────────────────────────────────────
def user_register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username  = request.POST.get('username', '').strip()
        email     = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        fname     = request.POST.get('first_name', '').strip()
        lname     = request.POST.get('last_name', '').strip()

        if not username or not password1:
            messages.error(request, "❌ Foydalanuvchi nomi va parol majburiy!")
        elif password1 != password2:
            messages.error(request, "❌ Parollar mos kelmadi!")
        elif len(password1) < 6:
            messages.error(request, "❌ Parol kamida 6 ta belgi bo'lishi kerak!")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "❌ Bu foydalanuvchi nomi band!")
        elif email and User.objects.filter(email=email).exists():
            messages.error(request, "❌ Bu email allaqachon ro'yxatdan o'tgan!")
        else:
            user = User.objects.create_user(
                username=username, email=email,
                password=password1, first_name=fname, last_name=lname
            )
            login(request, user)
            messages.success(request, f"✅ Xush kelibsiz, {user.username}!")
            return redirect('home')
    return render(request, 'accounts/register.html', base_ctx())


# ── PAROL O'ZGARTIRISH (login kerak) ──────────────────────
@login_required(login_url='/login/')
def change_password(request):
    if request.method == 'POST':
        old  = request.POST.get('old_password', '')
        new1 = request.POST.get('new_password1', '')
        new2 = request.POST.get('new_password2', '')

        if not request.user.check_password(old):
            messages.error(request, "❌ Joriy parol noto'g'ri!")
        elif new1 != new2:
            messages.error(request, "❌ Yangi parollar mos kelmadi!")
        elif len(new1) < 6:
            messages.error(request, "❌ Parol kamida 6 ta belgi bo'lishi kerak!")
        else:
            request.user.set_password(new1)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, "✅ Parol muvaffaqiyatli o'zgartirildi!")
            return redirect('change_password')
    return render(request, 'accounts/change_password.html', base_ctx())


# ── PAROLNI UNUTDIM — 1-qadam: username kiriting ──────────
def new_password(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        try:
            user = User.objects.get(username=username)
            # Token yaratish
            uid   = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = f"http://127.0.0.1:8000/new-password/reset/{uid}/{token}/"

            # Consolga chiqarish (email o'rniga)
            print("\n" + "=" * 60)
            print("  📧  PAROLNI TIKLASH HAVOLASI")
            print("=" * 60)
            print(f"  Foydalanuvchi : {user.username}")
            print(f"  Havola        : {reset_url}")
            print("=" * 60 + "\n")

            messages.success(
                request,
                "✅ Parolni tiklash havolasi consolga (terminelga) yuborildi! "
                "Termineldan havolani ko'rib, brauzerga kiriting."
            )
            return redirect('new_password')
        except User.DoesNotExist:
            messages.error(request, "❌ Bunday foydalanuvchi topilmadi!")

    return render(request, 'accounts/new_password.html', base_ctx())


# ── PAROLNI TIKLASH — 2-qadam: yangi parol ────────────────
def password_reset_confirm(request, uidb64, token):
    if request.user.is_authenticated:
        return redirect('home')

    # Token tekshirish
    try:
        uid  = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        messages.error(request, "❌ Havola noto'g'ri yoki muddati o'tgan!")
        return redirect('new_password')

    if request.method == 'POST':
        new1 = request.POST.get('new_password1', '')
        new2 = request.POST.get('new_password2', '')
        if new1 != new2:
            messages.error(request, "❌ Parollar mos kelmadi!")
        elif len(new1) < 6:
            messages.error(request, "❌ Parol kamida 6 ta belgi bo'lishi kerak!")
        else:
            user.set_password(new1)
            user.save()
            messages.success(request, "✅ Parol yangilandi! Tizimga kiring.")
            return redirect('login')

    ctx = base_ctx()
    ctx['username'] = user.username
    return render(request, 'accounts/password_reset_confirm.html', ctx)