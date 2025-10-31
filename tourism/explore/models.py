# chatbot/models.py
from django.db import models


class Intent(models.Model):
    """
    High level grouping (maps to category in your dataset).
    """
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Rule(models.Model):
    """
    A matching rule: exact question, regex, or keywords.
    priority: lower number = higher priority
    """
    MATCH_TYPE_CHOICES = [
        ('exact', 'Exact'),
        ('regex', 'Regex'),
        ('keyword', 'Keyword'),
    ]

    intent = models.ForeignKey(Intent, on_delete=models.CASCADE, related_name='rules')
    match_type = models.CharField(max_length=20, choices=MATCH_TYPE_CHOICES, default='keyword')
    pattern = models.TextField(help_text="Exact text (for exact), regex pattern (for regex), or comma-separated keywords (for keyword)")
    priority = models.IntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['priority', '-created_at']

    def __str__(self):
        return f"{self.intent.name} | {self.match_type} | {self.pattern[:50]}"

class Response(models.Model):
    """
    A canned response associated with an Intent (or a Rule optionally).
    """
    intent = models.ForeignKey(Intent, on_delete=models.CASCADE, related_name='responses')
    text = models.TextField()
    # optional link to a rule (if response should be rule-specific)
    rule = models.ForeignKey(Rule, on_delete=models.SET_NULL, blank=True, null=True, related_name='responses')
    created_at = models.DateTimeField(auto_now_add=True)
    pronunciation = models.TextField(blank=True, default="")
    meaning = models.TextField(blank=True, default="") 

    def __str__(self):
        return self.text[:80]

class ChatLog(models.Model):
    user_text = models.TextField()
    bot_text = models.TextField(blank=True)
    matched_intent = models.CharField(max_length=150, blank=True)
    matched_rule = models.ForeignKey(Rule, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
