from datetime import date

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from identity.request import AuthenticatedRequest

_WEEKDAYS = (
    "월요일",
    "화요일",
    "수요일",
    "목요일",
    "금요일",
    "토요일",
    "일요일",
)


def kicker_for(day: date) -> str:
    return f"{_WEEKDAYS[day.weekday()]}, {day.month}월 {day.day}일"


@login_required
@require_http_methods(["GET"])
def home_desk_view(request: AuthenticatedRequest) -> HttpResponse:
    return render(
        request,
        "highlights/home.html",
        {"desk_kwargs": {"kicker": kicker_for(date.today())}},
    )
