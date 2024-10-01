from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Group
from django.contrib.auth import views as auth_views
from django.forms import BaseModelForm
from django.http.response import HttpResponse as HttpResponse
from django.utils import timezone
from django.contrib.auth import login as auth_login
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.db.models import Q, Sum, Max
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.conf import settings

from formset.views import FormViewMixin, FormView


# from web.mails import mail_password
from web import views as cviews
from web.decorators import superuser_required
from xauth import forms
from xauth import models


# Create your views here.

GENERATED_PASSWORD_LENGTH = getattr(settings, "GENERATED_PASSWORD_LENGTH", 10)
DEFAULT_FROM_EMAIL = getattr(settings, "DEFAULT_FROM_EMAIL")

# Users management


def has_permission_to_give_opinion(user):
    if hasattr(user, "assign") and user.assign:
        if user.assign.group_assign.name == "DRH":
            return True
    return False


def has_permission_to_validate(user):
    if hasattr(user, "assign") and user.assign:
        if user.assign.group_assign.name == "DRH":
            return True
    return False


@method_decorator(transaction.atomic, name="form_valid")
@method_decorator(
    permission_required("xauth.can_assign", raise_exception=True),
    name="dispatch",
)
class AssignCreateView(cviews.CustomCreateView):
    model = models.Assign
    name = "nomination"
    form_class = forms.AssignForm
    success_url = reverse_lazy("auth:user-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(models.User, pk=self.kwargs.get(self.pk_url_kwarg))
        card_title = (
            f"Nomination du {user.grade.label} {user.get_full_name()}"
            if user.grade
            else f"Nomination de {user.get_full_name()}"
        )
        context["card_title"] = card_title
        return context

    def form_valid(self, form):
        office = form.cleaned_data["group_assign"]
        user = get_object_or_404(models.User, pk=self.kwargs.get(self.pk_url_kwarg))
        form.instance.user = user
        form.instance.assigner = self.request.user

        print("hello", office.permissions.all())

        for permission in office.permissions.all():
            user.groups.add(permission)

        return super().form_valid(form)


@method_decorator(transaction.atomic, name="form_valid")
@method_decorator(
    permission_required("xauth.can_assign", raise_exception=True),
    name="dispatch",
)
class RoleCreateView(cviews.CustomCreateView):
    model = models.Assign
    name = "nomination"
    form_class = forms.RoleForm
    success_url = reverse_lazy("auth:user-list")

    def dispatch(self, request, *args, **kwargs):
        self.current_user = get_object_or_404(
            models.User, pk=self.kwargs.get(self.pk_url_kwarg)
        )
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.current_user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        card_title = (
            f"Attribution d'un rôle {self.current_user.grade.label} {self.current_user.get_full_name()}"
            if self.current_user.grade
            else f"Rôle de {self.current_user.get_full_name()}"
        )
        context["card_title"] = card_title
        return context

    def form_valid(self, form):
        office = form.cleaned_data["group_assign"]
        form.instance.user = self.current_user
        form.instance.assigner = self.request.user
        self.current_user.groups.add(office)
        return super().form_valid(form)


@method_decorator(transaction.atomic, name="form_valid")
@method_decorator(
    permission_required("xauth.can_assign", raise_exception=True),
    name="dispatch",
)
class AssignUpdateView(cviews.CustomUpdateView):
    model = models.Assign
    name = "nomination"
    form_class = forms.AssignForm
    success_url = reverse_lazy("auth:user-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(models.User, pk=self.kwargs.get(self.pk_url_kwarg))
        context["card_title"] = (
            f"Nomination du {user.grade.label} {user.get_full_name()}"
        )
        return context

    def form_valid(self, form):
        office = form.cleaned_data["office"]
        user = get_object_or_404(models.User, pk=self.kwargs.get(self.pk_url_kwarg))
        form.instance.user = user
        form.instance.assigner = self.request.user
        user.groups.add(office.permissions)
        return super().form_valid(form)


@method_decorator(transaction.atomic, name="get")
@method_decorator(
    permission_required("xauth.can_assign", raise_exception=True),
    name="dispatch",
)
class RemoveAssignView(View):
    def get(self, request, *args, **kwargs):
        user = get_object_or_404(models.User, pk=self.kwargs.get("pk"))

        if not hasattr(user, "assign"):
            messages.error(request, "Aucune nomination pour cette utilisateur")
            return redirect("xauth:user-list")

        assign = user.assign
        assign.unassigner = request.user
        assign.end_date = timezone.now()
        assign.save()

        user.groups.remove(**assign.office.permissions)
        user.assign.remove()
        models.HistoricalAssign.objects.create(assign=assign)

        messages.error(request, "Nomination retirer avec succès")
        return redirect("xauth:user-list")


@method_decorator(
    permission_required("xauth.list_user", raise_exception=True),
    name="dispatch",
)
class UserListView(cviews.CustomListView):
    model = models.User
    name = "user"
    template_name = "private/list-user.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_assign"] = self.request.user.has_perm("change_right_user")
        context["deactivate_user"] = self.request.user.has_perm("deactivate_user")
        # context["can_delete"] = False
        return context

    def get_queryset(self):
        queryset = super().get_queryset().order_by("first_name", "last_name")

        if hasattr(self.request.user, "assign"):
            queryset = queryset.filter(
                structure__in=self.request.user.assign.structure.get_children()
            )

        return queryset


@method_decorator(
    permission_required("xauth.list_user", raise_exception=True),
    name="dispatch",
)
class StaffListView(cviews.CustomListView):
    model = models.User
    name = "user"
    template_name = "private/list-staff.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_assign"] = self.request.user.has_perm("change_right_user")
        context["deactivate_user"] = self.request.user.has_perm("deactivate_user")
        context["card_title"] = "Liste du personnel militaire"
        return context

    def get_queryset(self):
        queryset = super().get_queryset().order_by("first_name", "last_name")

        if hasattr(self.request.user, "assign"):
            queryset = queryset.filter(
                structure__in=self.request.user.assign.structure.get_children(),
                structure__isnull=False,
            )

        return queryset


@method_decorator(transaction.atomic, name="form_valid")
@method_decorator(
    permission_required("xauth.add_user", raise_exception=True),
    name="dispatch",
)
class UserCreateView(cviews.CustomCreateView):
    model = models.User
    success_url = reverse_lazy("auth:user-list")
    form_class = forms.UserCreateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["card_title"] = "Ajout d'un nouvel utilisateur"
        return context

    def form_valid(self, form):
        form.instance.is_active = False
        return super().form_valid(form)


@method_decorator(transaction.atomic, name="form_valid")
@method_decorator(
    permission_required("xauth.change_user", raise_exception=True),
    name="dispatch",
)
class UserUpdateView(cviews.CustomUpdateView):
    model = models.User
    form_class = forms.UserChangeForm

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs["user"] = self.request.user
    #     return kwargs

    def dispatch(self, request, *args, **kwargs):
        user = self.get_object()
        if request.user.is_superuser or request.user.id == user.id:
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied

    def get_success_url(self):
        return reverse(
            "auth:user-detail", kwargs={"pk": self.kwargs.get(self.pk_url_kwarg)}
        )


@method_decorator(transaction.atomic, name="form_valid")
@method_decorator(
    permission_required("xauth.change_user", raise_exception=True),
    name="dispatch",
)
class UserProfilePhotoUpdateView(cviews.CustomUpdateView):
    model = models.User
    form_class = forms.UserChangeProfilePhotoForm

    def dispatch(self, request, *args, **kwargs):
        user = self.get_object()
        if request.user.is_superuser or request.user.id == user.id:
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied

    def get_success_url(self):
        return reverse(
            "auth:user-detail", kwargs={"pk": self.kwargs.get(self.pk_url_kwarg)}
        )


@method_decorator(
    permission_required("xauth.view_user", raise_exception=True),
    name="dispatch",
)
class UserDetailView(cviews.CustomDetailView):
    model = models.User

    def get_template_names(self):
        template_name = "private/user-profile.html"

        if self.request.user.is_staff:
            template_name = "private/user-profile-admin-view.html"

        return [template_name]


@method_decorator(transaction.atomic, name="render_to_response")
@method_decorator(
    permission_required("xauth.delete_user", raise_exception=True),
    name="dispatch",
)
class UserDeleteView(cviews.CustomDeleteView):
    model = models.User

    def get_success_url(self):
        return reverse("auth:user-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = forms.UserConfirmDeleteForm(user=self.get_object())
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        can_delete = True

        if self.object.is_superuser:
            can_delete = False
            messages.warning(
                request,
                "Impossible de supprimer cette utilisateur il s'agit de l'utilisateur principal de la plateforme.",
            )
            messages.info(
                request,
                "À défaut de pouvoir le supprimer, vous pouvez le désactiver. Notez qu'en le désactivant vous ne pourrez plus l'utiliser pour une connexion à cette plateforme. Vous pouvez le réactiver a tout instant.",
            )
            return HttpResponseRedirect(
                reverse("auth:user-detail", kwargs={"pk": self.object.pk})
            )

        if can_delete:
            return self.render_to_response(context)
        messages.warning(
            request,
            "Impossible de supprimer cette utilisateur car pourrait être l'autre d'une tâche/activité/commentaire et/ou le destinataire d'une tâche.",
        )
        messages.info(
            request,
            "À défaut de pouvoir le supprimer, vous pouvez le désactiver. Notez qu'en le désactivant cet utilisateur ne pourra plus ce connecter à cette plateforme. Vous pouvez le réactiver a tout instant.",
        )
        return HttpResponseRedirect(
            reverse("auth:user-detail", kwargs={"pk": self.object.pk})
        )


class UserUpdatePasswordView(auth_views.PasswordChangeView):
    template_name = "models/form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object = get_object_or_404(models.User, pk=self.kwargs.get("pk"))
        context["add_of"] = "Modification mot de passe"
        context["card_title"] = "Modification mot de passe"
        context["list_of"] = "Liste des utilisateurs"
        context["list_url"] = reverse("auth:user-list")
        context["detail_of"] = f"{self.object.get_full_name()}"
        context["detail_url"] = reverse(
            "auth:user-detail", kwargs={"pk": self.object.pk}
        )

        return context

    def get_success_url(self):
        return reverse_lazy("auth:user-detail", kwargs={"pk": self.kwargs.get("pk")})

    def form_valid(self, form):
        messages.success(self.request, "Votre mot de passe a été modifié avec succès")
        return super().form_valid(form)


class UserSendSecreteKey(View):
    def get_success_url(self):
        return reverse("auth:user-list")

    def get_object(self, pk):
        return get_object_or_404(models.User, pk=pk)

    def get(self, request, *args, **kwargs):
        from django.core.mail import send_mail

        pk = self.kwargs.get("pk")
        if pk is None:
            raise ImproperlyConfigured("pk non passé en paramètre de url")
        self.object = self.get_object(pk)

        if not self.object.is_active:
            activation = models.AccountActivationSecret.all_objects.filter(
                user=self.object
            )

            print("activation exists", activation.exists())
            if activation.exists():
                secret = activation.first().secret
            else:
                secret: str = models.User.objects.make_random_password(
                    length=GENERATED_PASSWORD_LENGTH
                )
                models.AccountActivationSecret.all_objects.create(
                    user=self.object, secret=secret
                )
            send_mail(
                "Clé d'activation de compte",
                secret,
                DEFAULT_FROM_EMAIL,
                [self.object.email],
            )
            messages.success(
                self.request,
                f"Le code d'activation de `{self.object.get_full_name()}` envoyé avec succès.",
            )
        else:
            messages.warning(
                self.request,
                f"Le compte de `{self.object.get_full_name()}` est déjà actif.",
            )

        return HttpResponseRedirect(self.get_success_url())


@method_decorator(
    permission_required("xauth.can_change_right", raise_exception=True),
    name="dispatch",
)
class UserAdminRightView(View):
    def get_success_url(self):
        return reverse("auth:user-detail", kwargs={"pk": self.kwargs.get("pk")})

    def get_object(self, pk):
        return get_object_or_404(models.User, pk=pk)

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        if pk is None:
            raise ImproperlyConfigured("pk non passé en paramètre de url")
        self.object = self.get_object(pk)

        if self.object.is_superuser:
            self.object.is_superuser = False
            self.object.save()
            messages.success(
                self.request,
                f"{self.object.get_full_name()} a été retiré des administrateurs de la plateforme.",
            )
        else:
            self.object.is_superuser = True
            self.object.save()
            messages.success(
                self.request,
                f"{self.object.get_full_name()} a été nommé administrateur de la plateforme..",
            )

        return HttpResponseRedirect(self.get_success_url())


@method_decorator(
    permission_required("auth.view_group", raise_exception=True),
    name="dispatch",
)
class GroupListView(cviews.CustomListView):
    model = Group
    template_name = "private/list-group.html"

    def get_queryset(self):
        return super().get_queryset().order_by("name")


@method_decorator(
    permission_required("auth.add_group", raise_exception=True),
    name="dispatch",
)
class GroupCreateView(cviews.CustomCreateView):
    model = Group
    form_class = forms.GroupForm
    success_url = reverse_lazy("auth:group-list")


@method_decorator(
    permission_required("auth.change_group", raise_exception=True),
    name="dispatch",
)
class GroupUpdateView(cviews.CustomUpdateView):
    model = Group
    form_class = forms.GroupForm
    success_url = reverse_lazy("auth:group-list")


@method_decorator(
    permission_required(["auth.view_group", "auth.change_group"], raise_exception=True),
    name="dispatch",
)
class GroupDetailView(cviews.CustomDetailView):
    model = Group
    template_name = "private/detail-group.html"


@method_decorator(
    permission_required("auth.delete_group", raise_exception=True),
    name="dispatch",
)
class GroupDeleteView(cviews.CustomDeleteView):
    model = Group

    def get_success_url(self):
        return reverse("auth:group-list")

    def get_can_delete(self):
        return not self.model.objects.filter(
            user__isnull=False, pk=self.object.id
        ).exists()


# Public authentication


class CustomLoginView(FormViewMixin, auth_views.LoginView):
    template_name = "public/login.html"
    # next_page = reverse_lazy("index-view")
    success_url = reverse_lazy("index-view")


class CustomLogoutView(auth_views.LogoutView):
    next_page = reverse_lazy("user-login")
    http_method_names = ["post", "options", "get"]

    def get(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomPasswordResetView(FormViewMixin, auth_views.PasswordResetView):
    template_name = "public/password-reset-request.html"
    success_url = reverse_lazy("password-reset-request-done")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["card_title"] = "Réinitialisation de votre mot de passe"
        return context

    def form_valid(self, form):
        self.request.session["password-reset-email"] = form.cleaned_data.get("email")
        return super().form_valid(form)


class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = "public/password-reset-request-done.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email = self.request.session["password-reset-email"]
        context["title"] += f" par mail au {email}"
        return context


class CustomPasswordResetConfirmView(
    FormViewMixin, auth_views.PasswordResetConfirmView
):
    template_name = "public/password-reset-confirm.html"
    success_url = reverse_lazy("password-reset-complete")
    form_class = forms.CustomSetPasswordForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["card_title"] = "Réinitialisation de votre mot de passe"
        return context


class SetPasswordView(FormView):
    template_name = "public/set-password.html"
    success_url = reverse_lazy("user-login")
    form_class = forms.CustomSetPasswordForm

    def dispatch(self, request, *args, **kwargs):
        self.user = get_object_or_404(models.User, pk=self.kwargs.get("pk"))
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["card_title"] = "Initialisation de votre mot de passe"
        return context

    def form_valid(self, form):
        form.save()
        models.AccountActivationSecret.objects.filter(user=self.user).first().delete(
            soft=False
        )
        messages.success(self.request, "Votre compte a été activé avec succès.")
        return super().form_valid(form)


class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "public/password-reset-complete.html"
    # success_url = reverse_lazy("password-reset-complete")


@method_decorator(transaction.atomic, name="form_valid")
class User2CreateView(FormView):
    form_class = forms.UserPublicActivationForm
    template_name = "public/signup.html"

    def get_success_url(self):
        return reverse("user-set-password", kwargs={"pk": self.user.pk})

    def form_valid(self, form):
        self.user = form.cleaned_data["user"]
        secret = form.cleaned_data["secret"]
        activation = models.AccountActivationSecret.all_objects.filter(
            user=self.user, secret=secret
        )
        print("activation existe", activation.exists())
        activation.update(is_active=False)
        return JsonResponse({"success_url": self.get_success_url()})
