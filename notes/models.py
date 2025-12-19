from django.db import models
from django.conf import settings

class Note(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    original_content = models.TextField()
    corrected_content = models.TextField(blank=True, null=True)
    truth_score = models.IntegerField(default=0, help_text="Score from 0 to 100")
    issues = models.JSONField(blank=True, null=True, help_text="List of detected truth/accuracy issues")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    truth_score = models.IntegerField(default=0)
    ai_feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Question by {self.user.username}: {self.content[:50]}"

class Answer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    content = models.TextField()
    truth_score = models.IntegerField(default=0)
    ai_feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-truth_score', '-created_at']

    def __str__(self):
        return f"Answer by {self.user.username} (Score: {self.truth_score})"

    @property
    def get_stroke_dashoffset(self):
        # Circumference is approx 125.6 (2 * pi * 20)
        # Offset = Circumference * (1 - score/100)
        return 125.6 * (1 - self.truth_score / 100)
