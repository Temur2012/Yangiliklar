from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class News(models.Model):
    title      = models.CharField(max_length=300)
    slug       = models.SlugField(unique=True, blank=True)
    content    = models.TextField()
    category   = models.ForeignKey(Category, on_delete=models.CASCADE)
    image      = models.ImageField(upload_to='news/', blank=True, null=True)
    views      = models.IntegerField(default=0)
    is_breaking    = models.BooleanField(default=False)
    is_main_slider = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            slug = base
            n = 1
            while News.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)


class ContactMessage(models.Model):
    name       = models.CharField(max_length=100, verbose_name="Ism")
    email      = models.EmailField(verbose_name="Email")
    subject    = models.CharField(max_length=200, verbose_name="Mavzu")
    message    = models.TextField(verbose_name="Xabar")
    is_read    = models.BooleanField(default=False, verbose_name="O'qildi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yuborilgan vaqt")

    class Meta:
        verbose_name        = "Xabar"
        verbose_name_plural = "Xabarlar"
        ordering            = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.subject}"


class Comment(models.Model):
    news       = models.ForeignKey(News, on_delete=models.CASCADE, related_name='comments')
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    text       = models.TextField(verbose_name="Izoh")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Izoh"
        verbose_name_plural = "Izohlar"
        ordering            = ['created_at']

    def __str__(self):
        return f"{self.user.username}: {self.text[:50]}"