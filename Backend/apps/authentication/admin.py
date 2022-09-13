from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.utils import unquote
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import (
    AdminPasswordChangeForm,
    UserChangeForm,
    UserCreationForm,
)
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.db import router, transaction
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.template.loader import render_to_string

from import_export.admin import ImportExportActionModelAdmin
from import_export import resources

from apps.authentication.models import ModeloPersonas


csrf_protect_m = method_decorator(csrf_protect)
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())

class AdminResourcePersonas(resources.ModelResource):
    save_points = []
    
    def before_import_row(self, row, **kwargs):
        password = row['password']
        row['password'] = make_password(password)
    
    def after_save_instance(self, instance:ModeloPersonas, using_transactions:bool, dry_run:bool):
        TEMPLATE_CODE_VERIFICATION_EMAIL_TEXT = 'authentication/email/verification_code.txt'
        TEMPLATE_CODE_VERIFICATION_EMAIL_HTML = 'authentication/email/verification_code.html'
        
        send_date = timezone.now
        user_id = instance.id
        user_email = instance.email
        user_url = f"{settings.BASE_URL}/authentication/verification/{user_id}"
        v_code = instance.cod_verificacion
        
        email_text = render_to_string(
            TEMPLATE_CODE_VERIFICATION_EMAIL_TEXT,
            {'code': v_code, 'time': send_date, 'url': user_url}
        )
        
        email_html = render_to_string(
            TEMPLATE_CODE_VERIFICATION_EMAIL_HTML,
            {'code': v_code, 'time': send_date, 'url': user_url}
        )
        
        if using_transactions and dry_run:
            con = transaction.get_connection()
            for sid in self.save_points:
                con.run_on_commint = [
                    (sids, func) for (sids, func) in con.run_on_commit if sid not in sids
                ]
            print("Lo envie 1 vez xD", v_code, user_id, user_email)
            
            ModeloPersonas.objects.filter(
                id=instance.id
            ).update(
                verification_code = v_code
            )
            
            send_mail(
                subject=f"Verifica tu dirección de correo electrónico | Ecommerce | {settings.BASE_URL}",
                message=email_text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user_email],
                html_message=email_html,
            )
        
        super().after_saveinstance(instance, using_transactions, dry_run)
        
        
        class Meta:
            model = ModeloPersonas
            fields = (
                'id',
                'username',
                'email',
                'tipo_identificacion',
                'identificacion',
                'pais',
                'ciudad',
                'direccion',
                'anotaciones_direccion',
                'termsYcond',
                'cod_verificacion',
                'is_staff',
                'nombres',
                'apellidos',
                'password',
                'celular',
                'rol',
                'is_active',
                'created',
                'updated',
                'order'
            )
            export_order = fields
            
@admin.register(ModeloPersonas)
class AdminPersonas(ImportExportActionModelAdmin, admin.ModelAdmin):
    resource_class = AdminResourcePersonas
    
    fieldsets = (
        ("Información de usuario", {
            "fields": (
                "username",
                "email",
                "password",
                "cod_verificacion",
                "rol",
                "created",
                "updated",
                "last_login"
            )
        }),
        
        ("Permisos", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
                "termsYcond",
            )
        }),
        
        ("Información personal", {
            "fields": (
                "nombres",
                "apellidos",
                "celular",
                "tipo_identificacion",
                "identificacion",
                "pais",
                "ciudad",
                "direccion",
                "anotaciones_direccion",
            )
        })
    )
    
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2"),
            },
        ),
    )
    
    filter_horizontal = (
        'groups',
        'user_permissions'
    )
    
    list_display = (
        "id",
        "username",
        "nombre_completo",
        "email",
        "rol",
        "is_active",
    )
    
    list_display_links = (
        "username",
        "nombre_completo",
        "email",
    )
    
    readonly_fields = (
        "created",
        "updated",
        "last_login"
    )
    
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
    )
    
    search_fields = (
        "username",
        "email",
        "nombres",
        "apellidos",
        "celular",
        "tipo_identificacion",
        "identificacion",
    )
    
    # Lo siguiente es de Django:
    add_form_template = "admin/auth/user/add_form.html"
    
    change_user_password_template = None
    
    form = UserChangeForm
    
    add_form = UserCreationForm
    
    change_password_form = AdminPasswordChangeForm
    
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        if obj is None:
            defaults["form"] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)

    def get_urls(self):
        return [
            path(
                "<id>/password/",
                self.admin_site.admin_view(self.user_change_password),
                name="auth_user_password_change",
            ),
        ] + super().get_urls()

    def lookup_allowed(self, lookup, value):
        # Don't allow lookups involving passwords.
        return not lookup.startswith("password") and super().lookup_allowed(
            lookup, value
        )

    @sensitive_post_parameters_m
    @csrf_protect_m
    def add_view(self, request, form_url="", extra_context=None):
        with transaction.atomic(using=router.db_for_write(self.model)):
            return self._add_view(request, form_url, extra_context)

    def _add_view(self, request, form_url="", extra_context=None):
        # It's an error for a user to have add permission but NOT change
        # permission for users. If we allowed such users to add users, they
        # could create superusers, which would mean they would essentially have
        # the permission to change users. To avoid the problem entirely, we
        # disallow users from adding users if they don't have change
        # permission.
        if not self.has_change_permission(request):
            if self.has_add_permission(request) and settings.DEBUG:
                # Raise Http404 in debug mode so that the user gets a helpful
                # error message.
                raise Http404(
                    'Your user does not have the "Change user" permission. In '
                    "order to add users, Django requires that your user "
                    'account have both the "Add user" and "Change user" '
                    "permissions set."
                )
            raise PermissionDenied
        if extra_context is None:
            extra_context = {}
        username_field = self.model._meta.get_field(self.model.USERNAME_FIELD)
        defaults = {
            "auto_populated_fields": (),
            "username_help_text": username_field.help_text,
        }
        extra_context.update(defaults)
        return super().add_view(request, form_url, extra_context)

    @sensitive_post_parameters_m
    def user_change_password(self, request, id, form_url=""):
        user = self.get_object(request, unquote(id))
        if not self.has_change_permission(request, user):
            raise PermissionDenied
        if user is None:
            raise Http404(
                _("%(name)s object with primary key %(key)r does not exist.")
                % {
                    "name": self.model._meta.verbose_name,
                    "key": escape(id),
                }
            )
        if request.method == "POST":
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                change_message = self.construct_change_message(
                    request, form, None)
                self.log_change(request, user, change_message)
                msg = gettext("Password changed successfully.")
                messages.success(request, msg)
                update_session_auth_hash(request, form.user)
                return HttpResponseRedirect(
                    reverse(
                        "%s:%s_%s_change"
                        % (
                            self.admin_site.name,
                            user._meta.app_label,
                            user._meta.model_name,
                        ),
                        args=(user.pk,),
                    )
                )
        else:
            form = self.change_password_form(user)

        fieldsets = [(None, {"fields": list(form.base_fields)})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            "title": _("Change password: %s") % escape(user.get_username()),
            "adminForm": adminForm,
            "form_url": form_url,
            "form": form,
            "is_popup": (IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET),
            "is_popup_var": IS_POPUP_VAR,
            "add": True,
            "change": False,
            "has_delete_permission": False,
            "has_change_permission": True,
            "has_absolute_url": False,
            "opts": self.model._meta,
            "original": user,
            "save_as": False,
            "show_save": True,
            **self.admin_site.each_context(request),
        }

        request.current_app = self.admin_site.name

        return TemplateResponse(
            request,
            self.change_user_password_template
            or "admin/auth/user/change_password.html",
            context,
        )

    def response_add(self, request, obj, post_url_continue=None):
        """
        Determine the HttpResponse for the add_view stage. It mostly defers to
        its superclass implementation but is customized because the User model
        has a slightly different workflow.
        """
        # We should allow further modification of the user just added i.e. the
        # 'Save' button should behave like the 'Save and continue editing'
        # button except in two scenarios:
        # * The user has pressed the 'Save and add another' button
        # * We are adding a user in a popup
        if "_addanother" not in request.POST and IS_POPUP_VAR not in request.POST:
            request.POST = request.POST.copy()
            request.POST["_continue"] = 1
        return super().response_add(request, obj, post_url_continue)    