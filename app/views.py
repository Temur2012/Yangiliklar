from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import F
from django.contrib.auth.decorators import login_required
from .models import News, Category, ContactMessage, Comment


def base_ctx():
    return {
        'categories': Category.objects.all(),
        'latest_news': News.objects.all()[:5],
    }


# ── BOSH SAHIFA ──────────────────────────────────────────────
def home(request):
    ctx = base_ctx()
    ctx.update({
        'slider_news':      News.objects.filter(is_main_slider=True).exclude(image='')[:5],
        'breaking_news':    News.objects.filter(is_breaking=True)[:5],
        'latest_news':      News.objects.all()[:8],
        'trending_news':    News.objects.order_by('-views')[:5],
        'latest_news_main': News.objects.exclude(image='').order_by('-created_at')[:4],  # ✅ SHU QATOR
    })
    return render(request, 'index.html', ctx)


# ── YANGILIK DETAIL ──────────────────────────────────────────

def news_detail(request, pk):
    news = get_object_or_404(News, pk=pk)

    # Faqat bir marta hisoblash
    session_key = f'viewed_news_{pk}'
    if not request.session.get(session_key):
        if not request.user.is_superuser:
            News.objects.filter(pk=pk).update(views=F('views') + 1)
        request.session[session_key] = True

    news.refresh_from_db()  # yangilangan views ni olish
    ctx = base_ctx()
    ctx.update({
        'news': news,
        'related': News.objects.filter(category=news.category).exclude(id=news.id)[:4],
        'comments': news.comments.all(),
    })
    return render(request, 'news_detail.html', ctx)



# ── YANGILIK YARATISH (faqat superuser) ─────────────────────
@login_required(login_url='/login/')
def news_create(request):
    if not request.user.is_superuser:
        messages.error(request, "❌ Bu sahifaga kirish huquqingiz yo'q!")
        return redirect('home')

    ctx = base_ctx()
    if request.method == 'POST':
        title          = request.POST.get('title', '').strip()
        content        = request.POST.get('content', '').strip()
        category_id    = request.POST.get('category')
        image          = request.FILES.get('image')
        is_breaking    = bool(request.POST.get('is_breaking'))
        is_main_slider = bool(request.POST.get('is_main_slider'))

        if not title or not content or not category_id:
            messages.error(request, "❌ Sarlavha, matn va kategoriya majburiy!")
        else:
            category = get_object_or_404(Category, pk=category_id)
            news = News(
                title=title,
                content=content,
                category=category,
                is_breaking=is_breaking,
                is_main_slider=is_main_slider,
            )
            if image:
                news.image = image
            news.save()
            messages.success(request, "✅ Yangilik muvaffaqiyatli qo'shildi!")
            return redirect('news_detail', pk=news.pk)

    return render(request, 'news_create.html', ctx)


# ── YANGILIK TAHRIRLASH (faqat superuser) ───────────────────
@login_required(login_url='/login/')
def news_edit(request, pk):
    if not request.user.is_superuser:
        messages.error(request, "❌ Bu sahifaga kirish huquqingiz yo'q!")
        return redirect('home')

    news = get_object_or_404(News, pk=pk)
    ctx = base_ctx()
    ctx['news'] = news

    if request.method == 'POST':
        title          = request.POST.get('title', '').strip()
        content        = request.POST.get('content', '').strip()
        category_id    = request.POST.get('category')
        image          = request.FILES.get('image')
        is_breaking    = bool(request.POST.get('is_breaking'))
        is_main_slider = bool(request.POST.get('is_main_slider'))

        if not title or not content or not category_id:
            messages.error(request, "❌ Sarlavha, matn va kategoriya majburiy!")
        else:
            category = get_object_or_404(Category, pk=category_id)
            news.title          = title
            news.content        = content
            news.category       = category
            news.is_breaking    = is_breaking
            news.is_main_slider = is_main_slider
            if image:
                news.image = image
            news.save()
            messages.success(request, "✅ Yangilik yangilandi!")
            return redirect('news_detail', pk=news.pk)

    return render(request, 'news_edit.html', ctx)


# ── YANGILIK O'CHIRISH (faqat superuser) ────────────────────
@login_required(login_url='/login/')
def news_delete(request, pk):
    if not request.user.is_superuser:
        messages.error(request, "❌ Bu sahifaga kirish huquqingiz yo'q!")
        return redirect('home')

    news = get_object_or_404(News, pk=pk)
    if request.method == 'POST':
        news.delete()
        messages.success(request, "✅ Yangilik o'chirildi!")
        return redirect('home')

    ctx = base_ctx()
    ctx['news'] = news
    return render(request, 'news_delete.html', ctx)


# ── IZOH QO'SHISH (login kerak) ─────────────────────────────
@login_required(login_url='/login/')
def add_comment(request, pk):
    news = get_object_or_404(News, pk=pk)
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text:
            Comment.objects.create(news=news, user=request.user, text=text)
            messages.success(request, "✅ Izohingiz qo'shildi!")
        else:
            messages.error(request, "❌ Izoh bo'sh bo'lishi mumkin emas!")
    return redirect('news_detail', pk=pk)


# ── IZOH O'CHIRISH ───────────────────────────────────────────
@login_required(login_url='/login/')
def delete_comment(request, pk):
    comment  = get_object_or_404(Comment, pk=pk)
    news_pk  = comment.news.pk
    if request.user == comment.user or request.user.is_superuser:
        comment.delete()
        messages.success(request, "Izoh o'chirildi.")
    else:
        messages.error(request, "❌ Sizda bu izohni o'chirish huquqi yo'q!")
    return redirect('news_detail', pk=news_pk)


# ── KATEGORIYA ───────────────────────────────────────────────
def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    ctx = base_ctx()
    ctx.update({
        'category':  category,
        'news_list': News.objects.filter(category=category),
    })
    return render(request, 'category.html', ctx)


# ── QIDIRUV ──────────────────────────────────────────────────
def search(request):
    query   = request.GET.get('q', '').strip()
    results = News.objects.filter(title__icontains=query) if query else News.objects.none()
    ctx = base_ctx()
    ctx.update({'query': query, 'results': results, 'count': results.count()})
    return render(request, 'search.html', ctx)


# ── ALOQA ────────────────────────────────────────────────────
def contact(request):
    ctx = base_ctx()
    if request.method == 'POST':
        name    = request.POST.get('name', '').strip()
        email   = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        if name and email and subject and message:
            ContactMessage.objects.create(
                name=name, email=email, subject=subject, message=message
            )
            messages.success(request, f"✅ Rahmat {name}! Xabaringiz yuborildi.")
        else:
            messages.error(request, "❌ Barcha maydonlarni to'ldiring!")
        return redirect('contact')
    return render(request, 'contact.html', ctx)