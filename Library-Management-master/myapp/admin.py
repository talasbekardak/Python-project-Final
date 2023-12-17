from django.contrib import admin

from .models import Publisher, Book, Member, Order, Review


# Action to increase book prices by $10 in bulk
def increase_10_dollars(modeladmin, request, queryset):
    for book in queryset:
        price = book.price + 10
        book.price = price
        book.save()


class BookAdmin(admin.ModelAdmin):
    # Fields displayed in the Book admin panel
    fields = [('title', 'category', 'publisher'), ('num_pages', 'price', 'num_reviews')]
    list_display = ('title', 'category', 'price')  # Columns displayed in the book list
    actions = [increase_10_dollars]  # Action to increase book prices


class OrderAdmin(admin.ModelAdmin):
    fields = ['books', ('member', 'order_type', 'order_date')]  # Fields displayed in the Order admin panel
    list_display = ('id', 'member', 'order_type', 'order_date', 'total_items')  # Columns displayed in the order list


class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'city')  # Columns displayed in the Publisher admin panel


class MemberAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'status', 'books_title')  # Columns displayed in the
    # Member admin panel


# Register your models here.
admin.site.register(Publisher, PublisherAdmin)  # Register Publisher model
admin.site.register(Book, BookAdmin)  # Register Book model with customized admin view
admin.site.register(Member, MemberAdmin)  # Register Member model with customized admin view
admin.site.register(Order, OrderAdmin)  # Register Order model with customized admin view
admin.site.register(Review)  # Register Review model
