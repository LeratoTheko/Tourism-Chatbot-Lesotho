from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json

from .engine import get_response_for_text
from .models import ChatLog, Rule

# Create your views here.
def base(request):
    return render(request, 'explore/landing/base.html', {})


def feature(request):
    return render(request, 'explore/landing/features.html', {})



def about(request):
    return render(request, 'explore/landing/about.html', {})




# 🧩 1. ADD THIS FUNCTION (anywhere near the top of the file)
def format_trip_response(text):
    """
    Detects and prettifies trip itinerary lists if found in the response.
    """
    try:
        # Try to parse structured itinerary (list of dicts)
        if isinstance(text, str) and text.strip().startswith('['):
            # convert the Python-like string list into real Python object
            data = eval(text)
        elif isinstance(text, list):
            data = text
        else:
            return text

        # Build formatted string
        formatted = "🏞️ **4-Day Trip Itinerary: Maletsunyane Falls & Nature Exploration**\n\n"
        for d in data:
            formatted += f"**Day {d.get('day_number')} — {d.get('location')}**\n"
            for act in d.get('activities', []):
                formatted += f"- {act}\n"
            formatted += f"🚗 *Transport:* {d.get('transport')}\n"
            formatted += f"🍽️ *Meals:* {', '.join(d.get('meal_recommendations', []))}\n"
            formatted += f"📝 *Notes:* {d.get('notes')}\n\n"
        return formatted

    except Exception:
        # fallback to original unformatted text if parsing fails
        return text



# 💬 2. YOUR MAIN CHAT API ENDPOINT
@csrf_exempt
@require_POST
def chat_api(request):
    try:
        body_unicode = request.body.decode('utf-8')
        payload = json.loads(body_unicode)
        user_text = payload.get('message', '').strip()
        if not user_text:
            return JsonResponse({'error': 'Message is required'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Invalid JSON: {e}'}, status=400)

    # get AI/Rule-based response
    result = get_response_for_text(user_text)

    matched_rule = None
    if result.get('rule_id'):
        try:
            matched_rule = Rule.objects.get(id=result['rule_id'])
        except Rule.DoesNotExist:
            pass

    # 🧠 3. FORMAT THE RESPONSE TEXT HERE
    formatted_reply = format_trip_response(result.get('text', ''))

    # save chat log
    ChatLog.objects.create(
        user_text=user_text,
        bot_text=formatted_reply,
        matched_intent=result.get('intent') or '',
        matched_rule=matched_rule
    )

    # 🧾 4. RETURN JSON RESPONSE
    return JsonResponse({
        "status": "success",
        "user_message": user_text,
        "bot_reply": formatted_reply,
        "intent": result.get('intent'),
        "method": result.get('method')
    }, status=200)