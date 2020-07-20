from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import Tag

from .forms import PostForm


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
            return redirect("/")  # TODO: get_absolute_url 활용
    else:
        form = PostForm()
    return render(request, "instagram/post_form.html", {"form": form})
