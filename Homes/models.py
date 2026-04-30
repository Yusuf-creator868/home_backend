from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.contrib.postgres.indexes import GinIndex

ROLES = [
    ("RENTER/BUYER", "Rernter/Buyer"),
    ("SELLER", "Seller"),
    ("AGENT", "Agent"),
]

CITIES = [
    ("TASHKENT", "Tashkent"),
    ("SAMARKAND", "Samarkand"),
    ("BUKHARA", "Bukhara"),
    ("NUKUS", "Nukus"),
    ("ANDIJAN", "Andijan"),
    ("NAMANGAN", "Namangan"),
    ("GERGANA", "Fergana"),
    ("KOKAND", "Kokand"),
    ("KARSHI", "Karshi"),
    ("NAVOIY", "Navoiy"),
    ("TERMIZ", "Termiz"),
    ("JIZZAH", "Jizzah"),
]


class Profile(models.Model):
    phone_regex = RegexValidator(
        regex=r'^\d{9}$',
        message="Phone number must be entered in the format: '900000000'. Up to 9 digits allowed."
    )
    users = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=ROLES, blank=True)
    name_user = models.CharField(max_length=12, blank=False)
    phone_number = models.CharField(validators=[phone_regex], max_length=9, blank=True)
    city = models.CharField( max_length=50, choices=CITIES)


class Home(models.Model):
    
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
    ]
    TYPE = [
        ('rent', 'Rent'),
        ('sale', 'Sale'),
    ]
        
    city = models.CharField( max_length=50, choices=CITIES, null=True)
    type = models.CharField(max_length=50, choices=TYPE, null=True)
    district = models.CharField(max_length=100)
    rooms = models.IntegerField(null=True)
    slug = models.SlugField(blank=True, null=True)
    bedrooms = models.IntegerField(null=True)
    bathrooms = models.IntegerField(null=True)
    area = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userhome")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            GinIndex(
                name = "district_trgm",
                fields = ['district'],
                opclasses=['gin_trgm_ops']
            )
        ]
        
    def __str__(self):
        return self.district



# check later
    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.district)
            unique_slug = self.slug
            counter = 1
            if Home.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{self.slug}-{counter}"
                counter += 1
            self.slug = unique_slug

        super().save(*args, **kwargs)


class Images(models.Model):
    home = models.ForeignKey(Home, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="img")



class FavoriteCart(models.Model):
    fav_code = models.CharField(max_length=11, unique=True)

    def __str__(self):
        return self.fav_code
    


class FavoriteItems(models.Model):
    favcart = models.ForeignKey(FavoriteCart, related_name="items", on_delete=models.CASCADE)
    homes = models.ForeignKey(Home, on_delete=models.CASCADE)
    quantity = models.IntegerField(default = 1)

    def __str__(self):
        return f"{self.quantity} * {self.homes.district} in favcart {self.favcart.id}"
    
    
class PropertyView(models.Model):
    property = models.ForeignKey(Home, on_delete=models.CASCADE, related_name="views")
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'User {self.user} viewed home {self.property}'