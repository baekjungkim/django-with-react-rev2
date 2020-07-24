from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Post


def index(request):
    return render(request, "instagram/index.html")


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


def post_list(request):
    post_list = Post.objects.all()

    return render(request, "instagram/post_list.html", {"post_list": post_list})


def user_page(request, username):
    page_user = get_object_or_404(get_user_model(), username=username, is_active=True)
    post_list = Post.objects.filter(author=page_user)
    post_list_count = post_list.count()  # 실제 DB에 count 쿼리를 던지게 된다.
    # len(post_list) # post_list를 메모리에 올린 후 메모리에서 갯수를 반환해준다.
    return render(
        request,
        "instagram/user_page.html",
        {
            "page_user": page_user,
            "post_list": post_list,
            "post_list_count": post_list_count,
        },
    )
