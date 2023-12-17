from django import forms
from django.contrib.auth.forms import UserCreationForm

from myapp.models import Order, Review, Member


# Form for book search functionality
class SearchForm(forms.Form):
    CATEGORY_CHOICES = [
        ('S', 'Science&Tech'),
        ('F', 'Fiction'),
        ('B', 'Biography'),
        ('T', 'Travel'),
        ('O', 'Other')
    ]
    # Fields for searching books by name, category, and maximum price
    name = forms.CharField(max_length=100, required=False, label="Your Name")
    category = forms.ChoiceField(widget=forms.RadioSelect, choices=CATEGORY_CHOICES, required=False,
                                 label="Select a category:")
    max_price = forms.DecimalField(label="Maximum Price", required=True, min_value=0)


# Form for creating orders
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        # Fields for creating an order: books and order type
        fields = ['books', 'order_type']
        widgets = {'books': forms.CheckboxSelectMultiple(), 'order_type': forms.RadioSelect}


# Form for submitting reviews
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        # Fields for submitting a review: reviewer, book, rating, comments
        fields = ['reviewer', 'book', 'rating', 'comments']
        widgets = {'book': forms.RadioSelect}
        labels = {'reviewer': u'Please enter a valid email', 'rating': u'Rating: An integer between 1 (worst) and 5 ('
                                                                       u'best)'}

    # Validation for the rating field
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating < 1 or rating > 5:
            raise forms.ValidationError('You must enter a rating between 1 and 5!')
        return rating


# Form for user registration
class RegisterForm(UserCreationForm):
    class Meta:
        model = Member
        # Fields for user registration: username, passwords, profile image, personal details, and settings
        fields = ['username', 'password1', 'password2', 'profile_image', 'first_name', 'last_name', 'status', 'address',
                  'city', 'province', 'auto_renew']
