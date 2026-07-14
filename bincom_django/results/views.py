from datetime import datetime

from django.db import transaction
from django.db.models import Sum, Exists, OuterRef
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages

from .models import State, Lga, Ward, PollingUnit, Party, AnnouncedPuResult


# --------------------------------------------------------------------------
# Q1: Result for a single polling unit, chosen via chained State -> LGA ->
# Ward -> Polling Unit select boxes (AJAX-populated, no full page reload).
# --------------------------------------------------------------------------
def pu_result(request):
    states = State.objects.all().filter(state_name="Delta").order_by("state_name")
    pu_id = request.GET.get("polling_unit")
    results = None
    polling_unit = None
    ward = None
    lga = None

    if pu_id:
        polling_unit = PollingUnit.objects.filter(pk=pu_id).first()
        if polling_unit:
            ward = Ward.objects.filter(pk=polling_unit.uniquewardid).first()
            lga = Lga.objects.filter(lga_id=polling_unit.lga_id).first()
            results = AnnouncedPuResult.objects.filter(
                polling_unit_uniqueid=str(polling_unit.uniqueid)
            ).order_by("-party_score")

    return render(
        request,
        "results/pu_result.html",
        {
            "states": states,
            "polling_unit": polling_unit,
            "ward": ward,
            "lga": lga,
            "results": results,
        },
    )


def ajax_lgas(request):
    state_id = request.GET.get("state_id")

    lgas = (
        Lga.objects.filter(state_id=state_id)
        .annotate(
            has_polling_units=Exists(
                PollingUnit.objects.filter(
                    lga_id=OuterRef("lga_id")
                )
            )
        )
        .filter(has_polling_units=True)
        .order_by("lga_name")
    )

    data = list(lgas.values("uniqueid", "lga_name"))
    return JsonResponse(data, safe=False)


def ajax_wards(request):
    lga_uniqueid = request.GET.get("lga_uniqueid")
    lga = Lga.objects.filter(pk=lga_uniqueid).first()

    data = []
    if lga:
        wards = (
            Ward.objects.filter(lga_id=lga.lga_id)
            .annotate(
                has_polling_units=Exists(
                    PollingUnit.objects.filter(
                        uniquewardid=OuterRef("uniqueid")
                    )
                )
            )
            .filter(has_polling_units=True)
            .order_by("ward_name")
        )

        data = list(wards.values("uniqueid", "ward_name"))

    return JsonResponse(data, safe=False)

def ajax_polling_units(request):
    """ward_uniqueid is Ward.uniqueid; polling_unit.uniquewardid references it directly."""
    ward_uniqueid = request.GET.get("ward_uniqueid")
    data = list(
        PollingUnit.objects.filter(uniquewardid=ward_uniqueid)
        .order_by("polling_unit_name")
        .values("uniqueid", "polling_unit_name", "polling_unit_number")
    )
    return JsonResponse(data, safe=False)


# --------------------------------------------------------------------------
# Q2: Summed total result of ALL polling units under a chosen LGA.
# Deliberately built from announced_pu_results (NOT announced_lga_results),
# so it works as an independent cross-check of the officially announced
# LGA figures.
# --------------------------------------------------------------------------
def lga_result(request):
    lgas = Lga.objects.all().order_by("lga_name")
    lga_uniqueid = request.GET.get("lga")
    totals = None
    selected_lga = None

    if lga_uniqueid:
        selected_lga = Lga.objects.filter(pk=lga_uniqueid).first()
        if selected_lga:
            pu_uniqueids = list(
                PollingUnit.objects.filter(lga_id=selected_lga.lga_id).values_list(
                    "uniqueid", flat=True
                )
            )
            # announced_pu_results.polling_unit_uniqueid is stored as a string
            pu_uniqueid_strs = [str(u) for u in pu_uniqueids]

            totals = (
                AnnouncedPuResult.objects.filter(
                    polling_unit_uniqueid__in=pu_uniqueid_strs
                )
                .values("party_abbreviation")
                .annotate(total_score=Sum("party_score"))
                .order_by("-total_score")
            )

    return render(
        request,
        "results/lga_result.html",
        {"lgas": lgas, "selected_lga": selected_lga, "totals": totals},
    )


# --------------------------------------------------------------------------
# Q3: Store results for ALL parties for a NEW polling unit.
# Party list comes from the real `party` lookup table (PDP, DPP, ACN, PPA,
# CDC, JP, ANPP, LABOUR, CPP).
# --------------------------------------------------------------------------
def add_pu_result(request):
    states = State.objects.all().order_by("state_name")
    parties = Party.objects.all().order_by("partyid")

    if request.method == "POST":
        ward_uniqueid = request.POST.get("ward")
        pu_number = request.POST.get("pu_number", "").strip()
        pu_name = request.POST.get("pu_name", "").strip()

        ward = Ward.objects.filter(pk=ward_uniqueid).first()

        if not ward:
            messages.error(request, "Please select a valid ward.")
        else:
            with transaction.atomic():
                pu = PollingUnit.objects.create(
                    polling_unit_id=0,  # legacy per-LGA numbering, not used by lookups here
                    ward_id=ward.ward_id,
                    lga_id=ward.lga_id,
                    uniquewardid=ward.uniqueid,
                    polling_unit_number=pu_number,
                    polling_unit_name=pu_name or None,
                    entered_by_user="django_app",
                    date_entered=datetime.now(),
                    user_ip_address=request.META.get("REMOTE_ADDR", ""),
                )
                for party in parties:
                    score = request.POST.get(f"score_{party.partyid}", "0") or "0"
                    AnnouncedPuResult.objects.create(
                        polling_unit_uniqueid=str(pu.uniqueid),
                        party_abbreviation=party.partyid[:4].upper(),  # ensure max length 4
                        party_score=int(score),
                        entered_by_user="django_app",
                        date_entered=datetime.now(),
                        user_ip_address=request.META.get("REMOTE_ADDR", ""),
                    )
            messages.success(
                request,
                f"Polling unit created (uniqueid={pu.uniqueid}) with results for {parties.count()} parties.",
            )
            return redirect("add_pu_result")

    return render(
        request,
        "results/add_pu_result.html",
        {"states": states, "parties": parties},
    )
