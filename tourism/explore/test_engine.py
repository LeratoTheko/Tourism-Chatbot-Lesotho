# chatbot/tests/test_engine.py
from django.test import TestCase
from .engine import get_response_for_text
from .models import Intent, Rule, Response

class EngineTest(TestCase):
    def setUp(self):
        intent = Intent.objects.create(name="Testing")
        r = Rule.objects.create(intent=intent, match_type='exact', pattern='how do i say hello in sesotho', priority=1)
        Response.objects.create(intent=intent, rule=r, text='Lumela')

    def test_exact_match(self):
        res = get_response_for_text('How do I say hello in Sesotho')
        self.assertIn('Lumela', res['text'])
