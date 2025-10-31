from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Fan, Savol, Javob, Student, Sinf, UserResponse
from django.db.models import Q



@admin.register(Student)
class StudentAdmin(ImportExportModelAdmin):
    ordering = ('id',)
    list_display = ('id', 'FISh', 'seriya', 'raqami', 'sinf', 'school','jins')
    list_filter = ('sinf',)

    # ✅ Import orqali qo‘shilganda ishlaydi
    def after_import_instance(self, instance, new, **kwargs):
        if not instance.FISh or not instance.seriya or instance.raqami == 0 or not instance.sinf or not instance.school:
            instance.delete()


# ✅ Fan admin
@admin.register(Fan)
class FanAdmin(admin.ModelAdmin):
    list_display = ('id', 'nomi')
    search_fields = ('nomi',)


# ✅ Sinf admin (sizda hali yo‘q edi)
@admin.register(Sinf)
class SinfAdmin(admin.ModelAdmin):
    list_display = ('id', 'nomi')
    search_fields = ('nomi',)


class JavobInline(admin.TabularInline):
    model = Javob
    extra = 3  # 3 ta variant avtomatik chiqadi
    min_num = 3
    max_num = 5


@admin.register(Savol)
class SavolAdmin(admin.ModelAdmin):
    list_display = ('matn', 'fan', 'sinf')
    inlines = [JavobInline]

# ✅ UserResponse Admin (majburiy qo‘shildi)
@admin.register(UserResponse)
class UserResponseAdmin(admin.ModelAdmin):
    list_display = ('user', 'savol', 'javob', 'sinf')
    list_filter = ('sinf', 'savol__fan')
    search_fields = ('user', 'savol__matn')



