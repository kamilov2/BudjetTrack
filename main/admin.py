from django.contrib import admin
from .models import Profile, Limit, ExpenseCategory, Expense

class LimitInline(admin.TabularInline):
    model = Limit
    extra = 1

class ExpenseInline(admin.TabularInline):
    model = Expense
    extra = 1

class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('get_user_email', 'id', 'emoji', 'title', 'reg_date')
    list_filter = ('profile', 'reg_date')
    search_fields = ('profile__user__username', 'title')
    date_hierarchy = 'reg_date'

    def get_user_email(self, obj):
        return obj.profile.user.email if obj.profile.user else ''

    get_user_email.short_description = 'User Email'


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'id', 'reg_date')
    inlines = [LimitInline, ExpenseInline]

class LimitAdmin(admin.ModelAdmin):
    list_display = ('profile', 'limit', 'reg_date')
    list_filter = ('profile', 'reg_date')
    search_fields = ('profile__user__username',)
    date_hierarchy = 'reg_date'

class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('get_user_email', 'category', 'amount', 'reg_date')
    list_filter = ('profile', 'category', 'reg_date')
    search_fields = ('profile__user__username',)
    date_hierarchy = 'reg_date'

    def get_user_email(self, obj):
        return obj.profile.user.email if obj.profile.user else ''

    get_user_email.short_description = 'User Email'

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Limit, LimitAdmin)
admin.site.register(ExpenseCategory, ExpenseCategoryAdmin)
admin.site.register(Expense, ExpenseAdmin)
