from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count, Q


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)

    def __str__(self):
        return self.user.username


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class QuestionManager(models.Manager):
    def popular(self):
        return self.annotate(
            likes_count=Count('likes', filter=Q(likes__is_like=True)),
            dislikes_count=Count('likes', filter=Q(likes__is_like=False)),
            like_difference=(
                    Count('likes', filter=Q(likes__is_like=True)) -
                    Count('likes', filter=Q(likes__is_like=False))
            )
        ).order_by('-like_difference', '-created_at')

    def newest(self):
        return self.annotate(
            likes_count=Count('likes', filter=Q(likes__is_like=True)),
            dislikes_count=Count('likes', filter=Q(likes__is_like=False)),
            like_difference=(
                    Count('likes', filter=Q(likes__is_like=True)) -
                    Count('likes', filter=Q(likes__is_like=False))
            )
        ).order_by('-created_at')


class Question(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="questions")
    tags = models.ManyToManyField(Tag, related_name="questions")

    objects = QuestionManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f"/question/{self.id}/"


class Answer(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Ответ на {self.question.title} от {self.author.username}"


class QuestionLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="question_likes")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)
    is_like = models.BooleanField(default=True)  # True - Like, False - Dislike

    class Meta:
        unique_together = ("user", "question")

    def __str__(self):
        return f"{self.user.username} лайкает {self.question.title}"


class AnswerLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="answer_likes")
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)
    is_like = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} лайков {self.answer.question.title}"
