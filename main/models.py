from django.db import models
from django.contrib.auth.models import User 



class Profile(models.Model):
    user = models.OneToOneField(User, verbose_name="User", on_delete=models.CASCADE)
    email = models.EmailField(verbose_name="Email", default="" , unique=True)  
    reg_date = models.DateField(verbose_name="Registration Date", auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.id} | {self.user.get_full_name} | {self.reg_date}"




    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'             

class Limit(models.Model):
    profile = models.ForeignKey(Profile , verbose_name = "Client" , on_delete = models.CASCADE)
    limit = models.DecimalField(max_digits=15 , verbose_name="Client limit" , decimal_places=2 , null=True, blank=True)
    reg_date = models.DateField(auto_now_add=True)


    def __str__(self) -> str:
        return f"{self.profile.id} | {self.reg_date}"

    class Meta:
        verbose_name = "Limit"
        verbose_name_plural = "Limits"

class ExpenseCategory(models.Model):
    profile = models.ForeignKey(Profile , verbose_name="Profile" , on_delete=models.CASCADE)
    emoji = models.CharField(verbose_name = "Category Emoji" , max_length=50)
    title = models.CharField(verbose_name = "Category Title" , max_length=100 , blank=True)
    reg_date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.profile.id} | {self.reg_date}"
    
    class Meta:
        verbose_name = "Expense Category"
        verbose_name_plural = "Expense Categorys"

    
class Expense(models.Model):
    profile = models.ForeignKey(Profile , verbose_name="Profile" , on_delete=models.CASCADE)
    category = models.ForeignKey(ExpenseCategory , verbose_name="Expense Category" , on_delete=models.CASCADE)
    amount = models.DecimalField(verbose_name="Expense Amount" , max_digits=25 , decimal_places=2)
    description = models.TextField(verbose_name="Description field" , blank=True)
    reg_date = models.DateField(auto_now_add=True)


    def __str__(self) -> str:
        return f"{self.profile.id} | {self.reg_date}"
    
    class Meta:
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"


