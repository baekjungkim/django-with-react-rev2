from datetime import timedelta

from appdirs import user_cache_dir
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CommentForm, PostForm
from .models import Post, Comment


@login_required
def index(request):
    timesince = timezone.now() - timedelta(days=3)
    post_list = (
        Post.objects.all()
        .filter(Q(author=request.user) | Q(author__in=request.user.follower_set.all()))
        .filter(created_at__gte=timesince)
    )  # less than equal = lte, greater than equal = gte

    suggested_user_list = (
        get_user_model()
        .objects.all()
        .exclude(pk=request.user.pk)
        .exclude(pk__in=request.user.follower_set.all())[:3]
    )

    return render(
        request,
        "instagram/index.html",
        {"post_list": post_list, "suggested_user_list": suggested_user_list},
    )


@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            # post tag를 저장하기 위해 post pk 가 필요하기때문에 저장을 먼저 한다.
            # ManyToMany
            post.save()

            post.tag_set.add(*post.extract_tag_list())
            messages.success(request, "포스팅을 저장했습니다.")
            return redirect(post)  # TODO: get_absolute_url 활용
    else:
        form = PostForm()
    return render(request, "instagram/post_form.html", {"form": form})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)

    return render(request, "instagram/post_detail.html", {"post": post,})


def user_page(request, username):
    page_user = get_object_or_404(get_user_model(), username=username, is_active=True)

    post_list = Post.objects.filter(author=page_user)
    post_list_count = post_list.count()  # 실제 DB에 count 쿼리를 던지게 된다.
    # len(post_list) # post_list를 메모리에 올린 후 메모리에서 갯수를 반환해준다.

    is_follow = False
    # Login 했다면
    if request.user.is_authenticated:
        is_follow = request.user.follower_set.filter(
            pk=page_user.pk
        ).exists()  # User객체, AnonymousUser

    User = get_user_model()
    following = User.objects.filter(follower_set=page_user)

    # print("following: " + following)
    # print("follower: " + request.user.follower_set)

    return render(
        request,
        "instagram/user_page.html",
        {
            "page_user": page_user,
            "post_list": post_list,
            "post_list_count": post_list_count,
            "is_follow": is_follow,
            "following": following,
        },
    )


@login_required
def post_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.like_user_set.add(request.user)
    messages.success(request, f"{post}를 좋아합니다.")
    redirect_url = request.META.get("HTTP_REFERER", "instagram:index")
    return redirect(redirect_url)


@login_required
def post_unlike(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.like_user_set.remove(request.user)
    messages.success(request, f"{post}를 좋아요를 취소합니다.")
    redirect_url = request.META.get("HTTP_REFERER", "instagram:index")
    return redirect(redirect_url)


@login_required
def comment_new(request, post_pk):
    post = get_object_or_404(Post, id=post_pk)
    if request.method == "POST":
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()

            messages.success(request, "댓글을 저장했습니다.")
            redirect_url = request.META.get("HTTP_REFERER", "instagram:index")
            return redirect(redirect_url)
        else:
            messages.warning(request, "댓글 입력후 등록해주세요.")
            redirect_url = request.META.get("HTTP_REFERER", "instagram:index")
            return redirect(redirect_url)

