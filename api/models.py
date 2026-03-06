from django.db import models

class User(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.email

class SkincareProduct(models.Model):
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    ingredients = models.TextField(blank=True, null=True)
    how_to_use = models.TextField(blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., 50ml, 100g")

    def __str__(self):
        return self.name

class UserRoutine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='routines')
    product = models.ForeignKey(SkincareProduct, on_delete=models.CASCADE)
    frequency = models.CharField(max_length=100, help_text="e.g., Morning, Night, Twice daily")
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.product.name}"

class SkinProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress_entries')
    image = models.ImageField(upload_to='progress/')
    note = models.TextField(blank=True, null=True)
    logged_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Progress for {self.user.email} at {self.logged_at}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255)
    age = models.IntegerField(blank=True, null=True)
    gender = models.CharField(max_length=50, blank=True, null=True)
    skin_type = models.CharField(max_length=100, help_text="Step 2")
    concerns = models.TextField(blank=True, null=True, help_text="Step 3")
    sensitivity_level = models.CharField(max_length=100, blank=True, null=True, help_text="Step 4")
    climate = models.CharField(max_length=100, blank=True, null=True, help_text="Step 5")
    ingredient_preferences = models.TextField(blank=True, null=True, help_text="Step 6")
    allergies = models.TextField(blank=True, null=True, help_text="Step 7")
    other_allergies = models.TextField(blank=True, null=True, help_text="Step 7 custom")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile for {self.user.email}"

class SkinAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analyses')
    image = models.ImageField(upload_to='analyses/')
    hydration_level = models.IntegerField(help_text="Percentage 0-100")
    sun_damage = models.CharField(max_length=100)
    acne_status = models.CharField(max_length=100)
    fine_lines = models.CharField(max_length=100)
    overall_score = models.IntegerField()
    recommendation_summary = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis for {self.user.email} - {self.overall_score}/100"

class SkinHealthScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='health_scores')
    score = models.IntegerField()
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Score {self.score} for {self.user.email} at {self.recorded_at}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(SkincareProduct, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Processing')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.order_id} - {self.user.email}"

class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(SkincareProduct, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(help_text="1 to 5 stars")
    comment = models.TextField()
    is_verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.email} for {self.product.name}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=100, help_text="e.g., Score, Order, Reminder")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.email}: {self.title}"

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    category = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.question