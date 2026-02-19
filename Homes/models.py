from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


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
    city = models.CharField( max_length=50, choices=CITIES, null=True)
    district = models.CharField(max_length=100)
    rooms = models.IntegerField(null=True)
    slug = models.SlugField(blank=True, null=True)
    bedrooms = models.IntegerField(null=True)
    bedrooms_descrip = models.TextField(null=True)
    bathrooms = models.IntegerField(null=True)
    bathrooms_descrip = models.TextField(null=True)
    livingroom_descrip = models.TextField(null=True)
    kitchen_descrip = models.TextField(null=True)
    area = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userhome")

    class Meta:
        ordering = ["-created_at"]


    def __str__(self):
        return self.name

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
        return f"{self.quantity} * {self.homes.name} in favcart {self.favcart.id}"