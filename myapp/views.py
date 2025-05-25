from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import login, logout
from django.contrib.sessions.models import Session
from .models import User , Reviews , Wishlists , BookRequest , Books , Message

from django.shortcuts import render
from django.db.models import Q
from .models import Books

def index(request):
    query = request.GET.get('q', '')
    books = Books.objects.all()
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(genre__icontains=query) |
            Q(location__icontains=query)
        )
    context = {
        'books': books,
        'query': query,
    }
    return render(request, 'index.html', context)



def register(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        password = make_password(request.POST['password'])
        location = request.POST['location']
        role = request.POST['role']
        phone = request.POST['phone']

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('register')

        User.objects.create(
            name=name, email=email, password_hash=password,
            location=location, role=role, phone=phone
        )
        messages.success(request, 'Registration successful. Please login.')
        return redirect('login')

    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = User.objects.get(email=email)
            if check_password(password, user.password_hash):
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                request.session['user_role'] = user.role
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid credentials.')
        except User.DoesNotExist:
            messages.error(request, 'Invalid credentials.')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('login')


from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Books, BookRequest, Wishlists

def dashboard(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = User.objects.get(id=user_id)

    if user.role == 'owner':
        requests = BookRequest.objects.filter(book__owner=user).order_by('-requested_at')

        if request.method == 'POST':
            request_id = request.POST.get('request_id')
            new_status = request.POST.get('status')
            if request_id and new_status in ['pending', 'approved', 'rejected']:
                book_request = get_object_or_404(BookRequest, id=request_id, book__owner=user)
                old_status = book_request.status
                book_request.status = new_status
                book_request.updated_at = timezone.now()
                book_request.save()

                if new_status == 'approved' and old_status != 'approved':
                    book = book_request.book
                    book.status = 'Not Available'
                    book.save()
                    BookRequest.objects.filter(book=book, status='pending').exclude(id=book_request.id).update(status='rejected')

                elif old_status == 'approved' and new_status != 'approved':
                    book = book_request.book
                    approved_exists = BookRequest.objects.filter(book=book, status='approved').exclude(id=book_request.id).exists()
                    if not approved_exists:
                        book.status = 'Available'
                        book.save()

                messages.success(request, f'Request status updated to {new_status}.')
            return redirect('dashboard')

        context = {
            'user': user,
            'requests': requests,
        }
        return render(request, 'dashboard_owner.html', context)

    else:  # seeker
        query = request.GET.get('q', '')
        books = Books.objects.filter(status='Available')
        if query:
            books = books.filter(
                Q(title__icontains=query) |
                Q(author__icontains=query) |
                Q(genre__icontains=query) |
                Q(location__icontains=query)
            )

        wishlist = Wishlists.objects.filter(user=user)
        matched_books = Books.objects.none()
        for wish in wishlist:
            matched_books |= Books.objects.filter(
                status='Available'
            ).filter(
                Q(title__icontains=wish.title) |
                Q(author__icontains=wish.author) |
                Q(genre__icontains=wish.genre)
            )

        matched_books = matched_books.distinct().exclude(id__in=books.values_list('id', flat=True))

        context = {
            'user': user,
            'books': books,
            'query': query,
            'matched_books': matched_books,
        }
        return render(request, 'dashboard_seeker.html', context)




from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Books, User
from django.core.exceptions import PermissionDenied

def book_list(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = User.objects.get(id=user_id)

    # Only show books owned by this user
    books = Books.objects.filter(owner=user).order_by('-created_at')

    return render(request, 'owner/book_list.html', {'books': books})


def book_create(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        title = request.POST['title']
        author = request.POST['author']
        genre = request.POST['genre']
        condition = request.POST['condition']
        location = request.POST['location']
        status = request.POST.get('status', 'Available')
        external_url = request.POST.get('external_url', None)
        photo = request.FILES.get('photo_url', None)

        book = Books(
            title=title,
            author=author,
            genre=genre,
            condition=condition,
            location=location,
            status=status,
            external_url=external_url,
            owner=user,
        )
        if photo:
            book.photo_url = photo

        book.save()
        messages.success(request, 'Book added successfully.')
        return redirect('book_list')

    return render(request, 'owner/book_form.html', {'action': 'Add'})


def book_edit(request, book_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    book = get_object_or_404(Books, id=book_id)

    # Permission check: only owner can edit
    if book.owner.id != user_id:
        raise PermissionDenied

    if request.method == 'POST':
        book.title = request.POST['title']
        book.author = request.POST['author']
        book.genre = request.POST['genre']
        book.condition = request.POST['condition']
        book.location = request.POST['location']
        book.status = request.POST.get('status', book.status)
        book.external_url = request.POST.get('external_url', book.external_url)

        photo = request.FILES.get('photo_url', None)
        if photo:
            book.photo_url = photo

        book.save()
        messages.success(request, 'Book updated successfully.')
        return redirect('book_list')

    return render(request, 'owner/book_form.html', {'book': book, 'action': 'Edit'})


def book_delete(request, book_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    book = get_object_or_404(Books, id=book_id)

    # Permission check: only owner can delete
    if book.owner.id != user_id:
        raise PermissionDenied

    book.delete()
    messages.success(request, 'Book deleted successfully.')
    return redirect('book_list')


def request_book(request, book_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = User.objects.get(id=user_id)
    if user.role != 'seeker':
        return redirect('dashboard')

    book = Books.objects.get(id=book_id)
    # Only allow request if status is 'Available'
    if book.status != 'Available':
        messages.error(request, 'Book is not available for request.')
        return redirect('dashboard')

    # Check if request already exists
    existing_request = BookRequest.objects.filter(book=book, seeker=user).first()
    if existing_request:
        messages.info(request, 'You have already requested this book.')
        return redirect('dashboard')

    BookRequest.objects.create(book=book, seeker=user, status='pending')
    messages.success(request, f'Request sent for "{book.title}".')
    return redirect('dashboard')

def seeker_requests(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = User.objects.get(id=user_id)
    if user.role != 'seeker':
        return redirect('dashboard')

    requests = BookRequest.objects.filter(seeker=user).order_by('-requested_at')

    context = {
        'user': user,
        'requests': requests,
    }
    return render(request, 'seeker_requests.html', context)

def delete_request(request, request_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = User.objects.get(id=user_id)
    if user.role != 'seeker':
        return redirect('dashboard')

    book_request = BookRequest.objects.filter(id=request_id, seeker=user).first()
    if book_request:
        book_request.delete()
        messages.success(request, 'Request deleted successfully.')
    else:
        messages.error(request, 'Request not found.')

    return redirect('seeker_requests')




from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

# Review page: View book details, reviews and add new review
def book_review(request, book_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = User.objects.get(id=user_id)
    book = get_object_or_404(Books, id=book_id)
    reviews = Reviews.objects.filter(book=book).order_by('-reviewed_at')

    if request.method == 'POST':
        rating = int(request.POST['rating'])
        comment = request.POST.get('comment', '')
        # Simple validation for rating
        if rating < 1 or rating > 5:
            messages.error(request, 'Rating must be between 1 and 5.')
        else:
            Reviews.objects.create(
                reviewer=user,
                book=book,
                rating=rating,
                comment=comment,
                reviewed_at=timezone.now()
            )
            messages.success(request, 'Review submitted successfully.')
            return redirect('book_review', book_id=book_id)

    context = {
        'user': user,
        'book': book,
        'reviews': reviews,
    }
    return render(request, 'book_review.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from .models import Wishlists, User, Books

# View wishlist and delete option
def wishlist_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = User.objects.get(id=user_id)
    wishlist_items = Wishlists.objects.filter(user=user)

    context = {
        'user': user,
        'wishlist_items': wishlist_items,
    }
    return render(request, 'wishlist.html', context)


def wishlist_delete(request, wishlist_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = User.objects.get(id=user_id)
    wishlist_item = get_object_or_404(Wishlists, id=wishlist_id, user=user)

    if request.method == 'POST':
        wishlist_item.delete()
        messages.success(request, 'Item removed from wishlist.')
        return redirect('wishlist_view')

    context = {
        'wishlist_item': wishlist_item,
        'user': user,
    }
    return render(request, 'wishlist_confirm_delete.html', context)


# Add wishlist manually (title, author, genre from form)
def add_to_wishlist_manual(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        author = request.POST.get('author', '').strip()
        genre = request.POST.get('genre', '').strip()

        user = User.objects.get(id=user_id)

        if title:
            # Prevent duplicates based on title and user
            if not Wishlists.objects.filter(user=user, title=title).exists():
                Wishlists.objects.create(
                    user=user,
                    title=title,
                    author=author if author else None,
                    genre=genre if genre else None,
                    added_at=timezone.now()
                )
                messages.success(request, f'Book "{title}" added to your wishlist.')
            else:
                messages.info(request, f'Book "{title}" is already in your wishlist.')
        else:
            messages.error(request, 'Title is required to add to wishlist.')

    return redirect('wishlist_view')


# Add book to wishlist from book list (with book_id)
def add_to_wishlist(request, book_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = User.objects.get(id=user_id)
    book = get_object_or_404(Books, id=book_id)

    # Prevent duplicates
    if not Wishlists.objects.filter(user=user, title=book.title).exists():
        Wishlists.objects.create(
            user=user,
            title=book.title,
            author=book.author,
            genre=book.genre,
            added_at=timezone.now()
        )
        messages.success(request, f'Book "{book.title}" added to your wishlist.')
    else:
        messages.info(request, f'Book "{book.title}" is already in your wishlist.')

    return redirect('dashboard')



def message_thread(request, owner_id, seeker_id, book_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = User.objects.get(id=user_id)
    book = get_object_or_404(Books, id=book_id)
    seeker = get_object_or_404(User, id=seeker_id)
    owner = get_object_or_404(User, id=owner_id)

    # Authorization check
    if user != owner and user != seeker:
        messages.error(request, "You are not authorized to view this conversation.")
        return redirect('dashboard')

    messages_qs = Message.objects.filter(
        Q(book=book) & 
        (Q(sender=owner, receiver=seeker) | Q(sender=seeker, receiver=owner))
    ).order_by('sent_at')

    if request.method == 'POST':
        message_content = request.POST.get('message_content')
        if message_content:
            Message.objects.create(
                sender=user,
                receiver=seeker if user == owner else owner,
                book=book,
                message_content=message_content,
                sent_at=timezone.now()
            )
            messages.success(request, "Message sent successfully.")
            return redirect('message_thread', owner_id=owner.id, seeker_id=seeker.id, book_id=book.id)
        else:
            messages.error(request, "Message content cannot be empty.")

    context = {
        'user': user,
        'book': book,
        'seeker': seeker,
        'owner': owner,
        'messages': messages_qs,
    }

    return render(request, 'message_thread.html', context)





from django.db.models import Q
from django.utils import timezone
from django.contrib import messages

def ownermessage_thread(request, owner_id, seeker_id, book_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = User.objects.get(id=user_id)
    owner = get_object_or_404(User, id=owner_id)
    seeker = get_object_or_404(User, id=seeker_id)
    book = get_object_or_404(Books, id=book_id)

    # Authorization: user must be either owner or seeker
    if user != owner and user != seeker:
        messages.error(request, "You are not authorized to view this conversation.")
        return redirect('dashboard')

    messages_qs = Message.objects.filter(
        book=book
    ).filter(
        Q(sender=owner, receiver=seeker) | Q(sender=seeker, receiver=owner)
    ).order_by('sent_at')

    if request.method == 'POST':
        message_content = request.POST.get('message_content')
        if message_content:
            Message.objects.create(
                sender=user,
                receiver=seeker if user == owner else owner,
                book=book,
                message_content=message_content,
                sent_at=timezone.now()
            )
            messages.success(request, "Message sent successfully.")
            return redirect('message_thread', owner_id=owner.id, seeker_id=seeker.id, book_id=book.id)
        else:
            messages.error(request, "Message content cannot be empty.")

    context = {
        'user': user,
        'owner': owner,
        'seeker': seeker,
        'book': book,
        'messages': messages_qs,
    }
    return render(request, 'owner/owner_message_thread.html', context)



from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User

def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            request.session['reset_user_id'] = user.id
            return redirect('password_reset_confirm')
        else:
            messages.error(request, 'Email not found.')
    return render(request, 'password_reset.html')

def password_reset_confirm(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('password_reset')

    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        new_password = request.POST.get('password')
        if new_password:
            from django.contrib.auth.hashers import make_password
            user.password_hash = make_password(new_password)
            user.save()
            messages.success(request, 'Password has been updated. You can now login.')
            del request.session['reset_user_id']
            return redirect('login')
        else:
            messages.error(request, 'Please enter a valid password.')

    return render(request, 'password_reset_confirm.html')
