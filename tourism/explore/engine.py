import re
import random
from difflib import SequenceMatcher
from .models import Rule, Response, Intent

def _normalize(text: str) -> str:
    return (text or "").strip().lower()

def fuzzy_ratio(a, b):
    return int(SequenceMatcher(None, a, b).ratio() * 100)

def find_rule_for_text(user_text: str, fuzzy_threshold: int = 70):
    u = _normalize(user_text)

    # 1) exact rules (case-insensitive)
    exact_rules = Rule.objects.filter(match_type='exact')
    for r in exact_rules:
        if _normalize(r.pattern) == u:
            return r, 'exact'

    # 2) regex rules
    regex_rules = Rule.objects.filter(match_type='regex')
    for r in regex_rules:
        try:
            if re.search(r.pattern, user_text, flags=re.IGNORECASE):
                return r, 'regex'
        except re.error:
            continue

    # 3) keyword rules - pattern is comma-separated keywords
    keyword_rules = Rule.objects.filter(match_type='keyword')
    for r in keyword_rules:
        keywords = [k.strip() for k in r.pattern.split(',') if k.strip()]
        # require at least one keyword match
        if any(kw in u for kw in keywords):
            return r, 'keyword'

    # 4) fuzzy match against exact patterns (helpful for typos)
    best = (None, 0)  # (rule, score)
    for r in exact_rules:
        score = fuzzy_ratio(_normalize(r.pattern), u)
        if score > best[1]:
            best = (r, score)
    if best[0] and best[1] >= fuzzy_threshold:
        return best[0], 'fuzzy'

    # 5) fallback: try to pick an intent by matching category words in user's text (weak)
    intents = Intent.objects.all()
    for intent in intents:
        key_words = [w.lower() for w in re.findall(r"\w+", intent.name)]
        if any(k in u for k in key_words):
            # return the top response for that intent
            possible_rules = intent.rules.all().order_by('priority')
            if possible_rules.exists():
                return possible_rules.first(), 'intent_keyword'

    return None, None



def get_response_for_text(user_text: str):
    rule, method = find_rule_for_text(user_text)
    if rule:
        # Prefer rule-specific responses first
        responses = Response.objects.filter(rule=rule)
        if not responses.exists():
            responses = Response.objects.filter(intent=rule.intent)

        if responses.exists():
            resp = random.choice(list(responses))

            # Base reply
            reply_text = resp.text or ""

            # Add pronunciation and meaning each on its own line
            extra_parts = []
            if getattr(resp, "pronunciation", None):
                extra_parts.append(f"🔊 Pronunciation: {resp.pronunciation}")
            if getattr(resp, "meaning", None) and resp.meaning.strip() != "":
                extra_parts.append(f"💡 Meaning: {resp.meaning}")

            # Join extra parts with double newlines for readability
            if extra_parts:
                reply_text += "\n\n" + "\n".join(extra_parts)

            return {
                'text': reply_text.strip(),
                'intent': rule.intent.name,
                'rule_id': rule.id,
                'method': method
            }

    # Default fallback reply
    return {
        'text': (
            "Ke kopa tšoarelo, ha ke utloisise.\n"
            "Ka kōpo hlakisa potso kapa re kopa 'help' "
            "(I’m sorry, I don't understand. Please rephrase or ask 'help')."
        ),
        'intent': None,
        'rule_id': None,
        'method': 'fallback'
    }



def format_itinerary_html(itinerary):
    """
    Convert a list of day dicts into appealing, readable HTML for the chatbot.
    """
    if not isinstance(itinerary, list):
        return f"<p>{itinerary}</p>"

    html = """
    <div style="font-family: 'Poppins', sans-serif; color: #f1f1f1; line-height: 1.6;">
      <div style="border-left: 4px solid #23bec8; padding-left: 10px; margin-bottom: 10px;">
        <h5 style="color:#23bec8; font-weight:700; margin:0;">🗓️ 4-Day Adventure Plan</h5>
        <p style="margin:2px 0 8px; font-size:0.9rem; color:#aaa;">
          Here’s your detailed itinerary — enjoy Lesotho’s breathtaking beauty!
        </p>
      </div>
    """

    for day in itinerary:
        html += f"""
        <div style="background:#111; border-radius:12px; padding:12px 14px; margin-bottom:12px; border:1px solid #1e1e1e;">
          <h6 style="color:#23bec8; font-weight:600; margin-bottom:4px;">
            Day {day.get('day_number', '')}: {day.get('location', '')}
          </h6>
          <ul style="padding-left:18px; margin:4px 0 8px;">
        """

        for act in day.get('activities', []):
            html += f"<li style='margin-bottom:4px;'>{act}</li>"

        html += "</ul>"

        if day.get('transport'):
            html += f"<p style='margin:0;'><strong>🚗 Transport:</strong> {day['transport']}</p>"
        if day.get('meal_recommendations'):
            html += f"<p style='margin:0;'><strong>🍽️ Meals:</strong> {', '.join(day['meal_recommendations'])}</p>"
        if day.get('notes'):
            html += f"<p style='margin:4px 0 0; color:#bbb; font-size:0.9rem;'><em>💡 {day['notes']}</em></p>"

        html += "</div>"

    html += "</div>"
    return html.strip()
