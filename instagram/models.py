import re

# from accounts.models import User
# from django.conf import settings
from config.settings.common import AUTH_USER_MODEL
from django.db import models


class Post(models.Model):
    author = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to="instagram/post/%Y/%m/%d",)
    caption = models.TextField()
    tag_set = models.ManyToManyField("Tag", blank=True)
    location = models.CharField(max_length=100)

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

    # def get_absolute_url(self):
    #     return reverse("model_detail", kwargs={"pk": self.pk})


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name