from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User, EmailVerification


class EmailVerificationInline(admin.TabularInline):
    model = EmailVerification
    extra = 0
    readonly_fields = ('code', 'created', 'expiration', 'status')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name',
                    'is_staff', 'is_verified_email', 'image_preview')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_verified_email')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined', 'image_preview')
    inlines = [EmailVerificationInline]

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'image', 'image_preview')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified_email', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.image.url)
        return "No image"

    image_preview.short_description = 'Profile Image'


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created', 'expiration', 'status', 'is_expired')
    list_filter = ('status', 'created')
    search_fields = ('user__username', 'user__email', 'code')
    readonly_fields = ('code', 'created', 'expiration', 'status', 'is_expired')
    raw_id_fields = ('user',)

    def is_expired(self, obj):
        return obj.is_expired()

    is_expired.boolean = True
    is_expired.short_description = 'Expired?'

    def send_verification_action(self, request, queryset):
        for verification in queryset:
            verification.send_verification_email()
        self.message_user(request, f"Verification emails sent for {queryset.count()} records")

    send_verification_action.short_description = "Resend verification email"

    actions = ['send_verification_action']