from django.db import models
from django.contrib.auth.models import User


post_types = [("AR", "article"), ("NW", "news")]


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        score = 0
        posts = Post.objects.filter(author=self)
        score += (posts.aggregate(models.Sum("rating"))["rating__sum"] or 0) * 3
        score += posts.aggregate(models.Sum("comment__rating"))["comment__rating__sum"] or 0
        score += Comment.objects.filter(user=self.user).aggregate(models.Sum("rating"))["rating__sum"] or 0
        self.rating = score
        self.save()
        return self

    def __str__(self):
        return f'{self.user.username}'


class Category(models.Model):
    name = models.CharField(unique=True, max_length=255)
    subscribers = models.ManyToManyField(User, through="CategoryUser")

    def __str__(self):
        return f'{self.name}'


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    type = models.CharField(max_length=2, choices=post_types)
    creation_time = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through="PostCategory")
    header = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.IntegerField(default=0)

    def preview(self):
        return self.text[0:124] + "..."

    def like(self):
        self.rating += 1
        self.save()
        return self

    def dislike(self):
        self.rating -= 1
        self.save()
        return self


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class CategoryUser(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="posted_comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    creation_time = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()
        return self

    def dislike(self):
        self.rating -= 1
        self.save()
        return self
