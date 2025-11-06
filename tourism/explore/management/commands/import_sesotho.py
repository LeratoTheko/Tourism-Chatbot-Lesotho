    # chatbot/management/commands/import_sesotho.py
import json
import re
from django.core.management.base import BaseCommand
from ...models import Intent, Rule, Response
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent / 'data (3).json'


class Command(BaseCommand):
    help = "Import Sesotho Q&A JSON into Intent/Rule/Response"

    def handle(self, *args, **options):
        if not DATA_PATH.exists():
            self.stdout.write(self.style.ERROR(f"Data file not found at {DATA_PATH}"))
            return

        data = json.loads(DATA_PATH.read_text(encoding='utf-8'))['data']
        created = 0
        for item in data:
            category = item.get('category') or item.get('intent') or 'Uncategorized'
            # get or create Intent
            intent, _ = Intent.objects.get_or_create(name=category)

            # Determine question text and answer text
            question = item.get('question') or item.get('user_query') or item.get('question_text') or None

            # Prepare response fields
            text = item.get('sesotho') or item.get('answer') or item.get('meaning') or item.get('text') or item.get('itinerary')
            pronunciation = item.get('pronunciation', '').strip()
            meaning = item.get('meaning', '').strip()

            # Create a rule: exact match if question exists, otherwise keyword
            if question:
                r = Rule.objects.create(intent=intent, match_type='exact', pattern=question.strip()[:200], priority=10)
                Response.objects.create(
                    intent=intent,
                    rule=r,
                    text=text or "",
                    pronunciation=pronunciation or "",
                    meaning=meaning or ""
                )
                created += 1
            else:
                # fallback: keyword rule based on category words
                kw = ','.join(list(set([w.lower() for w in re.findall(r"\w+", category)])))
                r = Rule.objects.create(intent=intent, match_type='keyword', pattern=kw, priority=50)
                Response.objects.create(
                    intent=intent,
                    text=text or "",
                    pronunciation=pronunciation or "",
                    meaning=meaning or ""
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Imported {created} items."))
