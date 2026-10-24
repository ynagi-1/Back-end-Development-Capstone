import requests
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from concert.forms import LoginForm, SignUpForm
from concert.models import Concert, ConcertAttending

def signup(request):
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("index")
    return render(request, "signup.html", {"form": form})

def index(request):
    return render(request, "index.html")

def remote_items(url, key):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    value = response.json()
    return value.get(key, []) if isinstance(value, dict) else value

def songs(request):
    try:
        items = remote_items(settings.SONGS_SERVICE_URL, "songs")
    except (requests.RequestException, ValueError):
        return render(request, "songs.html", {"songs": [], "service_error": "Songs are temporarily unavailable."}, status=503)
    return render(request, "songs.html", {"songs": items})

def photos(request):
    try:
        items = remote_items(settings.PICTURES_SERVICE_URL, "pictures")
    except (requests.RequestException, ValueError):
        return render(request, "photos.html", {"photos": [], "service_error": "Photos are temporarily unavailable."}, status=503)
    return render(request, "photos.html", {"photos": items})

def login_view(request):
    form = LoginForm(request=request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("index")
    return render(request, "login.html", {"form": form})

@require_POST
def logout_view(request):
    logout(request)
    return redirect("index")

@login_required(login_url="login")
def concerts(request):
    attendance = dict(ConcertAttending.objects.filter(user=request.user).values_list("concert_id", "attending"))
    rows = [{"concert": concert, "status": attendance.get(concert.id, "-")} for concert in Concert.objects.order_by("date", "id")]
    return render(request, "concerts.html", {"concerts": rows})

@login_required(login_url="login")
def concert_detail(request, id):
    concert = get_object_or_404(Concert, pk=id)
    response = concert.attendee.filter(user=request.user).first()
    status = response.attending if response else "-"
    return render(request, "concert_detail.html", {"concert_details": concert, "status": status, "attending_choices": ConcertAttending.AttendingChoices.choices})

@login_required(login_url="login")
@require_POST
def concert_attendee(request):
    concert_id = request.POST.get("concert_id", "")
    status = request.POST.get("attendee_choice")
    if not concert_id.isdigit() or status not in ConcertAttending.AttendingChoices.values:
        return HttpResponseBadRequest("Invalid concert or attendance choice")
    concert = get_object_or_404(Concert, pk=int(concert_id))
    ConcertAttending.objects.update_or_create(concert=concert, user=request.user, defaults={"attending": status})
    return redirect("concerts")
