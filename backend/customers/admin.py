from django.contrib import admin
from customers.models import Customer, OwnerProfile, CompanyProfile, ContactPerson
from finance.models import BankAccount


# ✅ عرض الحسابات البنكية داخل صفحة العميل
class BankAccountInline(admin.TabularInline):
    model = BankAccount
    extra = 0
    fields = [
        'bank',
        'account_holder_name',
        'account_number',
        'iban_number',
        'iban_certificate_attachment'
    ]


# ✅ عرض ملف الشركة داخل العميل (كـ Inline اختياري)
class CompanyProfileInline(admin.StackedInline):
    model = CompanyProfile
    extra = 0
    can_delete = False
    verbose_name_plural = "Company Profile"
    fk_name = 'customer'
    show_change_link = True  # ✅ رابط لصفحة الشركة الكاملة


# ✅ عرض ملف المالك داخل العميل
class OwnerProfileInline(admin.StackedInline):
    model = OwnerProfile
    extra = 0
    can_delete = False
    verbose_name_plural = "Owner Profile"
    fk_name = 'customer'


# ✅ الأشخاص المتصلين بالشركة داخل ملف الشركة فقط (وليس العميل)
class ContactPersonInline(admin.TabularInline):
    model = ContactPerson
    extra = 0
    fields = [
        'name',
        'job_title',
        'email',
        'phone_number',
        'whatsapp_number',
        'is_primary'
    ]
    show_change_link = True


# ✅ إدارة العميل
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['full_name_english', 'email', 'customer_type', 'status']
    search_fields = ['full_name_english', 'email', 'customer_code', 'national_id_number']
    list_filter = ['customer_type', 'status', 'country']
    readonly_fields = ['created_at', 'updated_at']

    def get_inline_instances(self, request, obj=None):
        inline_instances = []
        if obj:
            if obj.customer_type == 'commercial' or obj.customer_type == 'consultant':
                inline_instances.append(CompanyProfileInline(self.model, self.admin_site))
            elif obj.customer_type == 'owner':
                inline_instances.append(OwnerProfileInline(self.model, self.admin_site))
            inline_instances.append(BankAccountInline(self.model, self.admin_site))
        return inline_instances


# ✅ إدارة ملف المالك (اختياري لو حبيت تفتحه مستقلًا)
@admin.register(OwnerProfile)
class OwnerProfileAdmin(admin.ModelAdmin):
    list_display = ['customer', 'authorized_person_name']
    search_fields = ['customer__full_name_english', 'authorized_person_name']
    list_filter = ['gender', 'nationality']


# ✅ إدارة ملف الشركة
@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ['customer', 'responsible_person_name', 'company_trade_license_number']
    search_fields = ['customer__full_name_english', 'responsible_person_name']
    list_filter = ['classification']
    inlines = [ContactPersonInline]  # ✅ مكانها الطبيعي


# ✅ إدارة الأشخاص المتصلين بالشركة (كـ Admin مستقل)
@admin.register(ContactPerson)
class ContactPersonAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone_number', 'company_profile']
    search_fields = ['name', 'email', 'company_profile__customer__full_name_english']
    list_filter = ['is_primary']
