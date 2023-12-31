from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


# Define Django models with appropriate fields and relationships
class Publisher(models.Model):
    # Publisher details: name, website, location
    name = models.CharField(max_length=200)
    website = models.URLField()
    city = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=20, blank=False, default='USA')

    def __str__(self):
        return self.name


class Book(models.Model):
    # Book details: title, category, pages, price, publisher, description, reviews count
    CATEGORY_CHOICES = [
        ('S', 'Science&Tech'),
        ('F', 'Fiction'),
        ('B', 'Biography'),
        ('T', 'Travel'),
        ('O', 'Other')
    ]
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES, default='S')
    num_pages = models.PositiveIntegerField(default=100)
    price = models.DecimalField(max_digits=10, decimal_places=2,
                                validators=[MinValueValidator(0), MaxValueValidator(1000)])
    publisher = models.ForeignKey(Publisher, related_name='books', on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    num_reviews = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


class Member(User):
    # Extending Django's default User model with additional fields for library members
    STATUS_CHOICES = [
        (1, 'Regular member'),
        (2, 'Premium Member'),
        (3, 'Guest Member'),
    ]
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    address = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=20, default='Windsor')
    province = models.CharField(max_length=2, default='ON')
    last_renewal = models.DateField(default=timezone.now)
    auto_renew = models.BooleanField(default=True)
    borrowed_books = models.ManyToManyField(Book, blank=True)
    profile_image = models.ImageField(upload_to='profile_image/', blank=True)

    def __str__(self):
        return self.username

    def books_title(self):
        title = ""
        for book in self.borrowed_books.all():
            title = title + book.title + ", "
        return title[:-2]


class Order(models.Model):
    # Order details: books, member, order type, order date
    ORDER_TYPE_CHOICES = [
        (0, 'Purchase'),
        (1, 'Borrow')
    ]
    books = models.ManyToManyField(Book)
    member = models.ForeignKey(Member, related_name='member', on_delete=models.CASCADE)
    order_type = models.IntegerField(choices=ORDER_TYPE_CHOICES, default=1)
    order_date = models.DateField(default=timezone.now)

    def total_items(self):
        return self.books.count()

    def __str__(self):
        return self.member.username + " " + str(self.order_date)


class Review(models.Model):
    # Review details: reviewer email, book, rating, comments, review date
    reviewer = models.EmailField()
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comments = models.TextField(blank=True)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return self.reviewer + " for " + self.book.title + " : " + str(self.rating) + " stars"
