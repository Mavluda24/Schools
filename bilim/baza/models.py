from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver



class Sinf(models.Model):
    nomi = models.CharField(max_length=50)

    def __str__(self):
        return self.nomi

    class Meta:
        verbose_name_plural = "Sinf"


class Fan(models.Model):
    sinf = models.ManyToManyField(Sinf, related_name="sinflar")
    nomi = models.CharField(max_length=100)
    rasmi = models.ImageField(upload_to="images/")

    def __str__(self):
        return self.nomi

    class Meta:
        verbose_name_plural = "Fan"


class Savol(models.Model):
    fan = models.ForeignKey(Fan, on_delete=models.CASCADE, related_name='savollar', null=True, blank=True)
    sinf = models.ForeignKey(Sinf, on_delete=models.CASCADE, related_name='savollar', null=True, blank=True)
    matn = models.TextField("Savol matni")

    def __str__(self):
        return self.matn[:50]
    class Meta:
        verbose_name_plural = "Savol"


class Javob(models.Model):
    savol = models.ForeignKey(Savol, on_delete=models.CASCADE, related_name='javoblar')
    matn = models.CharField("Javob matni", max_length=255)
    togri = models.BooleanField("To'g'ri javob", default=False)

    def __str__(self):
        return f"{self.matn} ({'Toʻgʻri' if self.togri else 'Notoʻgʻri'})"


class UserResponse(models.Model):
    user = models.CharField(max_length=100)
    savol = models.ForeignKey(Savol, on_delete=models.CASCADE)
    javob = models.ForeignKey(Javob, on_delete=models.CASCADE,null=True, blank=True)
    sinf = models.ForeignKey(Sinf, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} - {self.savol.matn[:30]}"


class Student(models.Model):
    GENDER_CHOICES = [
        ('o\'g\'il bola', 'o\'g\'il bola'),
        ('qiz bola', 'qiz bola'),
    ]

    id = models.AutoField(primary_key=True)
    FISh = models.CharField(max_length=100)
    seriya = models.CharField(max_length=100)
    raqami = models.IntegerField(default=0)
    sinf = models.CharField(max_length=100)
    school = models.CharField(max_length=100)
    jins = models.CharField(max_length=100, choices=GENDER_CHOICES, default='qiz bola')



    def __str__(self):
        return self.FISh

    class Meta:
        verbose_name_plural = 'Student'

