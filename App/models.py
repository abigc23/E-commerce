from django.db import models

class author(models.Model):
    author_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    bio = models.TextField()
    birth_date = models.DateField()
    nationality = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'author'

class genre(models.Model):
    genre_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class book(models.Model):
    book_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    publication_date = models.DateField()
    isbn = models.CharField(max_length=13, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    cover_image = models.ImageField(upload_to='book_covers/')
    author = models.ForeignKey(author, on_delete=models.CASCADE)
    language = models.CharField(max_length=100)
    dimensions = models.ForeignKey(Dimensions, on_delete=models.SET_NULL, null=True, blank=True)
    page_count = models.IntegerField(null=True)
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True)  

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'book'

class bookgenre(models.Model):
    bookgenre_id = models.AutoField(primary_key=True)
    book = models.ForeignKey(book, on_delete=models.CASCADE)
    genre = models.ForeignKey(genre, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('book', 'genre')
        db_table = 'bookgenre'

    def __str__(self):
        return f"{self.book.title} - {self.genre.name}"

class customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.city}, {self.country}'

    class Meta:
        db_table = 'customer'

class order(models.Model):
    order_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(customer, on_delete=models.CASCADE)
    order_date = models.DateTimeField()
    status = models.CharField(max_length=50)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order #{self.order_id} - {self.customer}"

    class Meta:
        db_table = 'order'

class orderitem(models.Model):
    orderitem_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(order, on_delete=models.CASCADE)
    book = models.ForeignKey(book, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.book.title} - Quantity: {self.quantity}"

    class Meta:
        db_table = 'orderitem'


class cartitem(models.Model):
     cartitem_id = models.AutoField(primary_key=True)
     customer = models.ForeignKey(customer, on_delete=models.CASCADE)
     book = models.ForeignKey(book, on_delete=models.CASCADE)
     quantity = models.IntegerField()
     def __str__(self):
         return f"{self.customer} - {self.book.title} - Quantity: {self.quantity}"
     
class payment(models.Model):
     payment_id = models.AutoField(primary_key=True)
     order = models.ForeignKey(order, on_delete=models.CASCADE)
     payment_date = models.DateTimeField()
     amount = models.DecimalField(max_digits=10, decimal_places=2)
     payment_method = models.CharField(max_length=50)
     def __str__(self):
         return f"Payment for Order #{self.order.order_id} - Amount: {self.amount}"
