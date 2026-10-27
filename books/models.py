from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.db.models import Avg, Count
from decimal import Decimal


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, default='')
    avatar_url = models.URLField(blank=True, default='')
    favorite_genres = models.CharField(max_length=255, blank=True, default='Fiction, Sci-Fi, Fantasy, Mystery')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    @property
    def display_avatar(self):
        if self.avatar_url:
            return self.avatar_url
        # Elegant SVG avatar using Dicebear or initials fallback
        return f"https://api.dicebear.com/7.x/bottts-neutral/svg?seed={self.user.username}"

    @property
    def genre_list(self):
        if self.favorite_genres:
            return [g.strip() for g in self.favorite_genres.split(',') if g.strip()]
        return ['Fiction']


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        # Also create default shelves for new user
        ReadList.create_default_shelves(instance)


class Friendship(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"{self.from_user.username} follows {self.to_user.username}"

    @classmethod
    def are_friends(cls, u1, u2):
        if not u1.is_authenticated or not u2.is_authenticated:
            return False
        return cls.objects.filter(from_user=u1, to_user=u2).exists()


class Book(models.Model):
    title = models.CharField(max_length=300, db_index=True)
    author = models.CharField(max_length=255, db_index=True)
    isbn = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    openlibrary_key = models.CharField(max_length=150, blank=True, null=True, unique=True, db_index=True)
    cover_url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, default='')
    first_publish_year = models.IntegerField(blank=True, null=True)
    genre = models.CharField(max_length=200, blank=True, default='General Fiction')
    page_count = models.IntegerField(blank=True, null=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0.00'))
    ratings_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-ratings_count', '-average_rating', 'title']

    def __str__(self):
        return f"{self.title} by {self.author}"

    def get_cover_image(self):
        if self.cover_url:
            return self.cover_url
        return "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&q=80&w=400"

    def update_rating_stats(self):
        stats = self.reviews.aggregate(avg=Avg('rating'), count=Count('id'))
        self.average_rating = Decimal(str(round(stats['avg'] or 0, 2)))
        self.ratings_count = stats['count'] or 0
        self.save(update_fields=['average_rating', 'ratings_count'])

    @property
    def star_display(self):
        # returns float rating
        return float(self.average_rating)


class ReadList(models.Model):
    LIST_TYPE_CHOICES = [
        ('want_to_read', 'Want to Read'),
        ('currently_reading', 'Currently Reading'),
        ('read', 'Read'),
        ('custom', 'Custom List'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='readlists')
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=160, blank=True)
    description = models.TextField(blank=True, default='')
    list_type = models.CharField(max_length=30, choices=LIST_TYPE_CHOICES, default='custom')
    is_default = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', 'created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or "list"
            slug = base_slug
            counter = 1
            while ReadList.objects.filter(user=self.user, slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    @classmethod
    def create_default_shelves(cls, user):
        defaults = [
            ('Want to Read', 'want_to_read', 'Books queued to read next'),
            ('Currently Reading', 'currently_reading', 'Books currently in progress'),
            ('Read', 'read', 'Books completed and logged'),
        ]
        for name, ltype, desc in defaults:
            cls.objects.get_or_create(
                user=user,
                list_type=ltype,
                defaults={
                    'name': name,
                    'description': desc,
                    'is_default': True,
                    'is_public': True,
                }
            )


class ReadListItem(models.Model):
    readlist = models.ForeignKey(ReadList, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='in_lists')
    notes = models.CharField(max_length=255, blank=True, default='')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('readlist', 'book')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.book.title} in {self.readlist.name}"


class RatingReview(models.Model):
    RATING_CHOICES = [
        (Decimal('1.0'), '1.0 - Poor'),
        (Decimal('1.5'), '1.5 - Mediocre'),
        (Decimal('2.0'), '2.0 - Okay'),
        (Decimal('2.5'), '2.5 - Average'),
        (Decimal('3.0'), '3.0 - Good'),
        (Decimal('3.5'), '3.5 - Very Good'),
        (Decimal('4.0'), '4.0 - Great'),
        (Decimal('4.5'), '4.5 - Outstanding'),
        (Decimal('5.0'), '5.0 - Masterpiece'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    rating = models.DecimalField(max_digits=2, decimal_places=1, choices=RATING_CHOICES)
    review_text = models.TextField(blank=True, default='')
    contains_spoilers = models.BooleanField(default=False)
    likes = models.ManyToManyField(User, blank=True, related_name='liked_reviews')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'book')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s review of {self.book.title} ({self.rating}/5)"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.book.update_rating_stats()

    def delete(self, *args, **kwargs):
        book = self.book
        super().delete(*args, **kwargs)
        book.update_rating_stats()


class ReviewComment(models.Model):
    review = models.ForeignKey(RatingReview, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_comments')
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.review}"


class Activity(models.Model):
    ACTIVITY_TYPES = [
        ('rated', 'rated a book'),
        ('reviewed', 'wrote a review for'),
        ('shelved', 'added to shelf'),
        ('friended', 'started following'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True, blank=True)
    review = models.ForeignKey(RatingReview, on_delete=models.CASCADE, null=True, blank=True)
    readlist = models.ForeignKey(ReadList, on_delete=models.CASCADE, null=True, blank=True)
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} {self.activity_type}"


class FAQ(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'General & Getting Started'),
        ('ratings', 'Ratings & Reviews'),
        ('shelves', 'Readlists & Shelves'),
        ('social', 'Friends & Community'),
        ('ai', 'AI Assistant & Recommendations'),
        ('technical', 'Error Codes & Technical'),
    ]

    question = models.CharField(max_length=350)
    answer = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='general')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question


class SupportTicket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    ticket_id = models.CharField(max_length=24, unique=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='support_tickets')
    guest_name = models.CharField(max_length=120, blank=True, default='')
    guest_email = models.EmailField(blank=True, default='')
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    created_by_ai = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.ticket_id}] {self.subject}"
