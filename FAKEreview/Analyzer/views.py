import os
import pickle

from django.conf import settings
from django.db.models import Count
from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Review, Profile
from .serializers import ReviewSerializer, ReviewInputSerializer

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.db.models import Avg

#  Load ML models 
BASE_DIR = settings.BASE_DIR

model = pickle.load(
    open(os.path.join(BASE_DIR, 'ml_models', 'esambler_review.pkl'), 'rb')
)
senti_model = pickle.load(
    open(os.path.join(BASE_DIR, 'ml_models', 'senti.pkl'), 'rb')
)
senti_tfidf = pickle.load(
    open(os.path.join(BASE_DIR, 'ml_models', 'tfidf.pkl'), 'rb')
)


def home(request):
    return render(request, 'Home.html')


def register_views(request):
    if request.method == 'POST':
        username  = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        image     = request.FILES.get('image')

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})
        if password1 != password2:
            return render(request, 'register.html', {'error': 'Passwords do not match'})

        user = User.objects.create_user(username=username, password=password1)
        if image:
            user.profile.image = image
            user.profile.save()

        return redirect('login')

    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user     = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('check_review')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})

    return render(request, 'login.html')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def predict_reviews(request):
    serializer = ReviewInputSerializer(data=request.data)

    if serializer.is_valid():
        text = str(serializer.validated_data['text'])

        try:
            model_pred = model.predict([text])[0]

            confidance = None
            if hasattr(model, 'predict_proba'):
                proba      = model.predict_proba([text])[0]
                confidance = float(max(proba))

            result = 'FAKE' if model_pred == 'CG' else 'GENUINE'

            review = Review.objects.create(
                user=request.user,
                text=text,
                prediction=result,
                confidance=confidance,
            )

            return Response({
                'id':         review.id,
                'text':       text,
                'prediction': result,
                'confidance': confidance,
            })

        except Exception as e:
            return Response({'error': str(e)}, status=500)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@login_required
def how_it_work(request):
    return render(request, 'know.html')


@login_required
def check_review(request):
    return render(request, 'index.html')


@login_required
def dashboard(request):
    reviews = Review.objects.filter(user=request.user).order_by('-id')

    total    = reviews.count()
    fake     = reviews.filter(prediction='FAKE').count()
    genuine  = reviews.filter(prediction='GENUINE').count()
    positive = reviews.filter(sentiments='positive').count()
    negative = reviews.filter(sentiments='negative').count()

    avg_conf_raw   = reviews.aggregate(avg=Avg('confidance'))['avg'] or 0
    avg_confidence = round(avg_conf_raw * 100, 2)

    # ── Build a clean list for the per-review table ──────────────────────────
    # Normalise field names so the template can use consistent keys
    review_list = []
    for r in reviews:
        conf_pct = round((r.confidance or 0) * 100, 1)
        review_list.append({
            'text':       r.text,
            'label':      r.prediction.capitalize(),   # "Fake" / "Genuine"
            'sentiment':  (r.sentiments or 'unknown').capitalize(),
            'confidence': conf_pct,
            'conf_class': 'high' if conf_pct >= 80 else ('medium' if conf_pct >= 50 else 'low'),
        })

    context = {
        'total':          total,
        'fake':           fake,
        'genuine':        genuine,
        'positive':       positive,
        'negative':       negative,
        'avg_confidence': avg_confidence,
        'reviews':        review_list,       # ← NEW: passed to template
    }

    return render(request, 'dashboard.html', context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def predict_sentimets(request):
    text      = request.data.get('text')
    review_id = request.data.get('review_id')

    if not text:
        return Response({'error': 'Text is required'}, status=400)
    if not review_id:
        return Response({'error': 'Review ID required'}, status=400)

    vector       = senti_tfidf.transform([text])
    predict_senti = senti_model.predict(vector)[0]
    result       = 'negative' if predict_senti == 0 else 'positive'

    try:
        review           = Review.objects.get(id=review_id, user=request.user)
        review.sentiments = result
        review.save()
    except Review.DoesNotExist:
        return Response({'error': 'Review not found or not allowed'}, status=404)

    return Response({'text': text, 'sentiments': result})


def logout_view(request):
    logout(request)
    return redirect('home')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_reviews(request):
    reviews    = Review.objects.filter(user=request.user).order_by('created_at')
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)

@login_required
def bulk_check_page(request):
    """Renders the bulk review check page."""
    return render(request, 'bulk_check.html')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_predict_reviews(request):
    """
    Accepts a list of review texts, runs fake-detection on all of them,
    and optionally runs sentiment analysis too.

    Reviews can now span MULTIPLE LINES each. The frontend should send
    reviews separated by a BLANK LINE (i.e. "\n\n") instead of a single
    newline, so a single review can safely contain its own line breaks.

    Expected JSON body (preferred — frontend sends a pre-split list):
    {
        "reviews":        ["review text 1\nstill review 1", "review text 2", ...],
        "with_sentiment": true   // optional, default false
    }

    Also accepts a raw blob if you'd rather split server-side:
    {
        "text":           "review one line a\nreview one line b\n\nreview two...",
        "with_sentiment": true
    }

    Returns:
    {
        "results": [
            {
                "text":       "...",
                "prediction": "FAKE" | "GENUINE",
                "confidence": 0.91,        // float 0-1
                "sentiment":  "positive" | "negative" | null
            },
            ...
        ],
        "summary": {
            "total":    N,
            "fake":     N,
            "genuine":  N,
            "positive": N,
            "negative": N
        }
    }
    """
    with_sentiment = bool(request.data.get('with_sentiment', False))

    # ── Build the list of review texts ──────────────────────────────────────
    # Two supported input shapes:
    #   1. "reviews": [...]   → list already split (each item may contain \n)
    #   2. "text": "..."      → one big blob, split here on BLANK lines
    reviews_input = request.data.get('reviews', None)
    raw_text      = request.data.get('text', None)

    if isinstance(reviews_input, list) and len(reviews_input) > 0:
        # Each list item is one review — may itself contain multiple lines.
        texts = [str(t).strip() for t in reviews_input if str(t).strip()]

    elif isinstance(raw_text, str) and raw_text.strip():
        
        normalised = raw_text.replace('\r\n', '\n').replace('\r', '\n')
        chunks     = re.split(r'\n\s*\n+', normalised)
        texts      = [c.strip() for c in chunks if c.strip()]

    else:
        return Response(
            {'error': 'Provide either a non-empty "reviews" list or a "text" blob.'},
            status=400
        )

    if not texts:
        return Response({'error': 'No reviews found after parsing input.'}, status=400)

    MAX_BULK = 500   
    if len(texts) > MAX_BULK:
        return Response(
            {'error': f'Maximum {MAX_BULK} reviews per request.'},
            status=400
        )

    # ── Run fake-detection on all texts at once ───────────────────────────────
    try:
        predictions = model.predict(texts)               # batch predict
        probas      = None
        if hasattr(model, 'predict_proba'):
            probas = model.predict_proba(texts)           # shape (N, 2)
    except Exception as e:
        return Response({'error': f'Model error: {str(e)}'}, status=500)

    
    sentiments = [None] * len(texts)
    if with_sentiment:
        try:
            vectors     = senti_tfidf.transform(texts)
            senti_preds = senti_model.predict(vectors)
            sentiments  = ['negative' if p == 0 else 'positive' for p in senti_preds]
        except Exception:
            # Sentiment failure is non-fatal — return nulls
            sentiments = [None] * len(texts)

    # ── Build results list + save to DB ──────────────────────────────────────
    results        = []
    review_objects = []

    for i, text in enumerate(texts):
        raw_pred   = predictions[i]
        prediction = 'FAKE' if raw_pred == 'CG' else 'GENUINE'
        confidence = float(max(probas[i])) if probas is not None else None
        sentiment  = sentiments[i]

        try:
            review = Review(
                user=request.user,
                text=text,
                prediction=prediction,
                confidance=confidence,
                sentiments=sentiment,
            )
            review_objects.append(review)
        except Exception:
            pass   # DB save failure should not break the response

        results.append({
            'text':       text,
            'prediction': prediction,
            'confidence': confidence,
            'sentiment':  sentiment,
        })

    # Bulk-create all DB rows in one query
    try:
        Review.objects.bulk_create(review_objects)
    except Exception:
        pass   # Non-fatal if bulk_create fails

    # ── Summary ───────────────────────────────────────────────────────────────
    total    = len(results)
    fake     = sum(1 for r in results if r['prediction'] == 'FAKE')
    genuine  = total - fake
    positive = sum(1 for r in results if r['sentiment'] == 'positive')
    negative = sum(1 for r in results if r['sentiment'] == 'negative')

    return Response({
        'results': results,
        'summary': {
            'total':    total,
            'fake':     fake,
            'genuine':  genuine,
            'positive': positive,
            'negative': negative,
        }
    })