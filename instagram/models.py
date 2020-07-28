import re

from django.db import models
from django.urls import reverse

# from accounts.models import User
# from django.conf import settings
from config.settings.common import AUTH_USER_MODEL


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# user
# -> Post.objects.filter(author=user)
# -> user.post_set.all()
class Post(BaseModel):
    author = models.ForeignKey(
        AUTH_USER_MODEL, related_name="my_post_set", on_delete=models.CASCADE
    )
    photo = models.ImageField(upload_to="instagram/post/%Y/%m/%d",)
    caption = models.TextField()
    tag_set = models.ManyToManyField("Tag", blank=True)
    location = models.CharField(max_length=100)
    like_user_set = models.ManyToManyField(
        AUTH_USER_MODEL, blank=True, related_name="like_post_set"
    )

    def __str__(self):
        return self.caption

    def extract_tag_list(self):
        # #문자 뒤의 숫자,문자를 긁어오는 정규식
        tag_name_list = re.findall(r"#([a-zA-Z\dㄱ-힣]+)", self.caption)
        tag_list = []
        for tag_name in tag_name_list:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            tag_list.append(tag)
        return tag_list

    def get_absolute_url(self):
        return reverse("instagram:post_detail", args=[self.pk])

    def is_like_user(self, user):
        return self.like_user_set.filter(pk=user.pk).exists()

    class Meta:
        ordering = ["-id"]


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# class LikeUser(models.Model):
#     post = models.ForeignKey(Post, on_delete=models.CASCADE)
#     user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
