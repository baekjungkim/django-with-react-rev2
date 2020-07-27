from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.views import PasswordChangeView as AuthPasswordChangeView
from django.contrib.auth.views import logout_then_login
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from .forms import PasswordChangeForm, ProfileForm, SignupForm

login = LoginView.as_view(template_name="accounts/login_form.html")


# 로그아웃 하자마자 로그인으로 보냄
def logout(request):
    messages.success(request, "로그아웃 되었습니다.")
    return logout_then_login(request)


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            signed_user = form.save()
            auth_login(request, signed_user)
            messages.success(request, "회원가입 환영합니다.")
            signed_user.send_welcome_email()  # FIXME: Celery로 처리하는것을 추천
            next_url = request.GET.get("next", "/")
            return redirect(next_url)
    else:
        form = SignupForm()
    return render(request, "accounts/signup_form.html", {"form": form})


@login_required
def profile_edit(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "프로필을 수정/저장 했습니다.")
            return redirect("profile_edit")
    else:
        form = ProfileForm(instance=request.user)

    return render(request, "accounts/profile_edit_form.html", {"form": form})


class PasswordChangeView(LoginRequiredMixin, AuthPasswordChangeView):
    success_url = reverse_lazy("password_change")
    template_name = "accounts/password_change_form.html"
    form_class = PasswordChangeForm

    def form_valid(self, form):
        messages.success(self.request, "암호를 변경했습니다.")
        return super().form_valid(form)


password_change = PasswordChangeView.as_view()


@login_required
def user_follow(request, username):
    follow_user = get_object_or_404(get_user_model(), username=username, is_active=True)

    # request.user => following
    request.user.following_set.add(follow_user)
    # follow_user => follower
    follow_user.follower_set.add(request.user)

    messages.success(request, f"{follow_user}님을 팔로우했습니다.")
    redirect_url = request.META.get("HTTP_REFERER", "instagram:index")
    return redirect(redirect_url)


@login_required
def user_unfollow(request, username):
    unfollow_user = get_object_or_404(
        get_user_model(), username=username, is_active=True
    )

    # request.user => unfollowing
    request.user.following_set.remove(unfollow_user)
    # follow_user => unfollower
    unfollow_user.follower_set.remove(request.user)

    messages.success(request, f"{unfollow_user}님을 언팔로우했습니다.")
    redirect_url = request.META.get("HTTP_REFERER", "instagram:index")
    return redirect(redirect_url)
