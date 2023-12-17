import random
from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from .forms import SearchForm, OrderForm, ReviewForm, RegisterForm
from .models import Book, Member, Order, Review
import logging

logger = logging.getLogger(__name__)


# Index view function
def index(request):
    try:
        # Retrieves the last login from the session and fetches a list of books
        last_login = request.session.get('last_login', '')
        book_list = Book.objects.all().order_by('id')[:10]
        return render(request, 'myapp/index.html', {'booklist': book_list, 'last_login': last_login})
    except Exception as e:
        # Logs an error if an exception occurs while rendering the index view
        logger.error(f"An error occurred in index view: {e}")
        return render(request, 'myapp/error.html', {'message': 'Something went wrong! Please try again later.'})


# Index view class-based
class IndexView(View):
    template_name = 'myapp/index.html'
    last_login_cookie = 'last_login'

    def get(self, request):
        try:
            # Retrieves the last login from the session and fetches a list of books using a class-based approach
            last_login = request.session.get(self.last_login_cookie, '')
            book_list = Book.objects.all().order_by('id')[:10]
            return render(request, self.template_name, {'booklist': book_list, 'last_login': last_login})
        except Exception as e:
            # Logs an error if an exception occurs while rendering the index view (class-based)
            logger.error(f"An error occurred in IndexView: {e}")
            return render(request, 'myapp/error.html', {'message': 'Something went wrong! Please try again later.'})


# Function-based view for book detail
def detail(request, book_id):
    try:
        # Retrieves the book with the given ID or raises a 404 error
        book = get_object_or_404(Book, id=book_id)
        return render(request, 'myapp/detail.html', {'book': book})
    except Book.DoesNotExist as e:
        # Logs an error if the book does not exist and returns an HTTP 500 error response
        logger.error(f"Book with ID {book_id} does not exist: {e}")
        return HttpResponseServerError("Sorry, the book you requested does not exist.")


# Class-based view for detailed book information
class DetailView(View):
    template_name = 'myapp/detail.html'

    def get(self, request, book_id):
        try:
            # Retrieves the book with the given ID or raises a 404 error
            book = get_object_or_404(Book, id=book_id)
            reviews = Review.objects.filter(book=book)

            # Calculates average rating for the book's reviews
            avg_rating = -1
            if reviews.exists():
                total_rating = sum(review.rating for review in reviews)
                avg_rating = total_rating / len(reviews)

            # Renders the book detail template with book info and average rating
            return render(request, self.template_name, {'book': book, 'avg_rating': avg_rating, 'reviews': reviews})
        except Book.DoesNotExist as e:
            # Logs an error if the book does not exist and returns an HTTP 500 error response
            logger.error(f"Book with ID {book_id} does not exist: {e}")
            return HttpResponseServerError("Sorry, the book you requested does not exist.")


# View to handle book searching
def findbooks(request):
    try:
        if request.method == 'POST':
            # Handles form submission via POST method
            form = SearchForm(request.POST)
            if form.is_valid():
                # Extracts cleaned form data
                name = form.cleaned_data['name']
                category = form.cleaned_data['category']
                max_price = form.cleaned_data['max_price']

                # Filters books based on category and maximum price
                if not category:
                    booklist = Book.objects.filter(price__lte=max_price)
                else:
                    booklist = Book.objects.filter(price__lte=max_price, category=category)

                # Logs the resulting book list and search parameters
                logger.info(f"Book list: {booklist}")
                logger.info(f"Search results - Name: {name}, Category: {category}, Max Price: {max_price}")

                # Logs individual book details in the list
                for book in booklist:
                    logger.info(f"Book: {book.title}, Category: {book.category}")

                # Renders the results page with booklist and search parameters
                return render(request, 'myapp/results.html', {'booklist': booklist, 'name': name, 'category': category})
            else:
                # Handles form validation errors
                logger.error(f"Form errors: {form.errors}")
                return render(request, 'myapp/findbooks.html', {'form': form})
        else:
            # Handles GET requests, provides an empty search form
            form = SearchForm()
            return render(request, 'myapp/findbooks.html', {'form': form})
    except Exception as e:
        # Catches any unexpected errors during book search
        logger.error(f"An error occurred: {e}")
        return HttpResponseServerError("An error occurred during book search.")


@login_required(login_url='/myapp/login/')
def place_order(request):
    try:
        if request.method == 'POST':
            # Handles POST requests for order placement
            form = OrderForm(request.POST)
            if form.is_valid():
                # Validates the submitted form
                books = form.cleaned_data['books']
                order = form.save(commit=False)
                member = get_object_or_404(Member, id=request.user.id)
                order.member = member
                order.save()
                order.books.set(books)

                # Updates user's borrowed books if it's a borrow order type
                order_type = order.order_type
                if order_type == 1:
                    for book in order.books.all():
                        member.borrowed_books.add(book)

                # Renders a response page with order details
                return render(request, 'myapp/order_response.html', {'books': books, 'order': order})
            else:
                # If form is invalid, re-renders the place order form
                return render(request, 'myapp/placeorder.html', {'form': form})
        else:
            # Handles GET requests, provides an empty order form
            form = OrderForm()
            return render(request, 'myapp/placeorder.html', {'form': form})
    except Exception as e:
        # Logs and handles any unexpected errors during order placement
        logger.error(f"An error occurred: {e}")
        return HttpResponseServerError("An error occurred while placing the order.")


@login_required(login_url='/myapp/login/')
def review(request):
    try:
        # Retrieves the member based on the logged-in user
        member = Member.objects.get(pk=request.user.pk)

        # Checks if the member has eligible status for reviewing
        if member.status == 1 or member.status == 2:
            if request.method == 'POST':
                # Handles POST requests for submitting reviews
                form = ReviewForm(request.POST)
                if form.is_valid():
                    # Saves the review and updates book review count
                    review = form.save()
                    book = review.book
                    book.num_reviews += 1
                    book.save()
                    review.save()
                    return HttpResponseRedirect('/myapp')
            else:
                # For GET requests, provides an empty review form
                form = ReviewForm()
            return render(request, 'myapp/review.html', {'form': form})
        else:
            # Renders an invalid page for ineligible members
            return render(request, 'myapp/invalid.html', {'message': 'You are not eligible to view this page'})
    except Member.DoesNotExist as e:
        # Logs and handles member not found scenarios
        logger.error(f"Member not found: {e}")
        return render(request, 'myapp/invalid.html', {'message': 'You are not eligible to view this page'})
    except Exception as e:
        # Logs and handles unexpected errors during review submission
        logger.error(f"An error occurred: {e}")
        return render(request, 'myapp/error.html', {'message': 'An error occurred while processing your request'})


def user_login(request):
    try:
        # If the user is already authenticated, redirects to the index page
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('myapp:index'))

        # Handles POST requests when the user submits the login form
        if request.method == 'POST':
            # Retrieves the 'next' value if provided in the form
            valuenext = request.POST.get('next')
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)

            if user:
                # Checks if the user account is active
                if user.is_active:
                    login(request, user)
                    # Saves last login time in the session and sets its expiration time
                    request.session['last_login'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    request.session.set_expiry(3600)
                    # Redirects to the next URL or index page if 'next' is empty
                    if valuenext == '':
                        return HttpResponseRedirect(reverse('myapp:index'))
                    else:
                        return HttpResponseRedirect(valuenext)
                else:
                    # Renders an invalid page for disabled user accounts
                    return render(request, 'myapp/invalid.html', {'message': 'Your account is disabled.'})
            else:
                # Renders an invalid page for invalid login details
                return render(request, 'myapp/invalid.html', {'message': 'Invalid login details.'})
        else:
            # Renders the login form for GET requests
            return render(request, 'myapp/login.html')

    except Exception as e:
        # Logs and renders an error page for unexpected errors during login
        logger.error(f"An error occurred: {e}")
        return render(request, 'myapp/error.html', {'message': 'An error occurred while processing your request'})


@login_required(login_url='/myapp/login/')  # Requires login to access this view
def user_logout(request):
    logout(request)  # Logs out the user
    return HttpResponseRedirect(reverse('myapp:index'))  # Redirects to the index page after logout


@login_required(login_url='/myapp/login/')
def chk_reviews(request, book_id):
    try:
        # Retrieves the book with the given ID
        selected_book = get_object_or_404(Book, pk=book_id)

        # Checks if there are no reviews for the book
        if selected_book.num_reviews == 0:
            return render(request, 'myapp/chk_reviews.html', {'book': selected_book, 'avg_rating': -1})

        # Retrieves reviews for the book and calculates the average rating
        reviews = Review.objects.filter(book=selected_book)
        total_rating = sum(review.rating for review in reviews)
        avg_rating = total_rating / len(reviews)

        # Renders the template with book information and average rating
        return render(request, 'myapp/chk_reviews.html', {'book': selected_book, 'avg_rating': avg_rating})

    except Book.DoesNotExist as e:
        # Handles the case where the book with the given ID does not exist
        logger.error(f"Book with ID {book_id} does not exist: {e}")
        return render(request, 'myapp/error.html', {'error_message': 'The book does not exist.'})

    except ZeroDivisionError as e:
        # Handles the case where there are no reviews for the book (division by zero error)
        logger.error(f"Error calculating average rating: {e}")
        return render(request, 'myapp/error.html', {'error_message': 'No reviews available for this book.'})

    except Exception as e:
        # Handles any other unexpected errors that may occur
        logger.error(f"An error occurred: {e}")
        return render(request, 'myapp/error.html', {'error_message': 'An unexpected error occurred.'})


def register(request):
    try:
        # If the request method is POST, it attempts to process the registration form
        if request.method == 'POST':
            form = RegisterForm(request.POST, request.FILES)
            if form.is_valid():
                # Saves the valid form data to create a new user
                form.save()
                return HttpResponseRedirect(reverse('myapp:login'))
            else:
                # If the form is invalid, logs the error and renders an error message
                logger.error(f"Invalid registration form data: {form.errors}")
                return render(request, 'myapp/error.html',
                              {'error_message': 'Invalid registration form data. Please check your input.'})
        else:
            # If it's a GET request, it renders the registration form
            form = RegisterForm()
        return render(request, 'myapp/register.html', {'form': form})

    except Exception as e:
        # Handles any unexpected errors during the registration process
        logger.error(f"An error occurred during registration: {e}")
        return render(request, 'myapp/error.html',
                      {'error_message': 'An unexpected error occurred during registration.'})


@login_required(login_url='/myapp/login/')
def my_orders(request):
    try:
        # Attempt to retrieve the logged-in user
        logged_in_user = Member.objects.get(pk=request.user.pk)

        # Fetch orders associated with the logged-in user
        orders = Order.objects.filter(member=logged_in_user)

        # Initialize an empty list to store book titles corresponding to each order
        book_list = []

        # Iterate through each order to retrieve associated books and concatenate their titles
        for order in orders:
            books = order.books.all()
            book_title = ''
            for book in books:
                book_title = book_title + book.title + ', '

            # Append concatenated book titles (excluding the trailing comma and space) to book_list
            book_list.append(book_title[:-2])

        # Zip orders with their respective book titles for display in the template
        new_list = zip(orders, book_list)

        # Render the 'myapp/myorders.html' template with retrieved data for display
        return render(request, 'myapp/myorders.html', {'orders': orders, 'book_list': book_list, 'new_list': new_list})

    except Member.DoesNotExist:
        # Log an error if the logged-in user is not found and render a corresponding message for the user
        error_message = 'There are no available orders!'
        logger.error(f"Error retrieving orders: {error_message}")
        return render(request, 'myapp/invalid.html', {'message': error_message})

    except Exception as e:
        # Log any unexpected errors and render a general error message for the user
        error_message = 'An unexpected error occurred while retrieving orders.'
        logger.error(f"Unexpected error in my_orders view: {e}")
        return render(request, 'myapp/error.html', {'error_message': error_message})
