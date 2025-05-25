from django.db import models

class User(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('seeker', 'Seeker'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email})"


class Books(models.Model):
    CONDITION_CHOICES = [
        ('New', 'New'),
        ('Good', 'Good'),
        ('Fair', 'Fair'),
    ]

    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Reserved', 'Reserved'),
        ('Not Available', 'Not Available'),
    ]

    title = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        help_text="Enter the book title",
    )
    author = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        help_text="Enter the book author",
    )
    genre = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        help_text="Enter the genre of the book",
    )
    condition = models.CharField(
        max_length=50,
        choices=CONDITION_CHOICES,
        null=False,
        blank=False,
        help_text="Select the condition of the book (New, Good, Fair)",
    )
    location = models.TextField(
        null=False,
        blank=False,
        help_text="Enter the location of the book owner",
    )
    photo_url = models.ImageField(
        upload_to='images/',
        null=True,
        blank=True,
        help_text="Upload an image of the book",
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='books',
        help_text="The user who owns the book",
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        null=False,
        blank=False,
        default='Available',
        help_text="Select the status of the book (Available, Reserved, Not Available)",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="The timestamp when the book was added",
    )
    external_url = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Enter an optional link to the book (Amazon, Daraz, etc.)",
    )

    def __str__(self):
        return f"{self.title} by {self.author} ({self.condition})"
    
from django.utils import timezone

class BookRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    book = models.ForeignKey(Books, on_delete=models.CASCADE, related_name='requests')
    seeker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='book_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Request {self.id} by {self.seeker.name} for {self.book.title} [{self.status}]"


from django.db import models
from django.utils import timezone

class Reviews(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    book = models.ForeignKey(Books, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField()  # 1 to 5
    comment = models.TextField(blank=True, null=True)
    reviewed_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Review by {self.reviewer.name} for {self.book.title}"

class Wishlists(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists')
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True, null=True)
    genre = models.CharField(max_length=255, blank=True, null=True)
    added_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Wishlist: {self.title} for {self.user.name}"
    
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', help_text="The user sending the message")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', help_text="The user receiving the message")
    book = models.ForeignKey(Books, on_delete=models.CASCADE, related_name='messages', blank=True, null=True, help_text="Optional: Book associated with the message")
    message_content = models.TextField(help_text="The content of the message")
    sent_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the message was sent")

    def __str__(self):
        return f"Message from {self.sender.name} to {self.receiver.name} on {self.sent_at}"

