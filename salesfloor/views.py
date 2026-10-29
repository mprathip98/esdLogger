from calendar import weekday
from pathlib import Path
from xxlimited_35 import Null

from django.shortcuts import render, redirect
from django.contrib.messages import constants as messages
from .forms import testLogsForm, verificationForm
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
import io
from .models import testLogs, verification
from collections import OrderedDict
from datetime import datetime
from django.http import FileResponse
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image as ReportLabImage,
)



def home(request):
    if request.method == "POST":
        form = testLogsForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            form.save()
            messages.success(request, "Log Created Successfully!")
        else:
            print(form.errors)
            messages.error(request, "Log Not Created! Fill ALL Fields! Enter Valid Info!")
        return redirect("home")
    else:
        return render(request, "home.html")

def retrieve(request):
    last_week = timezone.now() - timedelta(days=7)
    recentData = testLogs.objects.filter(date__gte=last_week).order_by("date")
    filteredData = []
    data = testLogs.objects.all()
    initials = verification.objects.all()
    for record in recentData:
        record.verification_initials = (
            verification.objects
            .filter(date=record.date)
            .values_list("initials", flat=True)
            .first()
        )

    if request.method == "POST":
        startDate = request.POST.get("startDate")
        endDate = request.POST.get("endDate")
        filteredData = testLogs.objects.filter(date__range=(startDate, endDate))
        for records in filteredData:
            records.verification_initials = (
                verification.objects
                .filter(date=record.date)
                .values_list("initials", flat=True)
                .first()
            )


    return render(request, "retrieve.html", {'data': data, "recentData": recentData[::-1], "filteredData": filteredData, "initials": initials})

def retrieve_pdf(request):
    startDate = request.POST.get("startDate")
    endDate = request.POST.get("endDate")

    logs = testLogs.objects.none()

    if startDate and endDate:
        logs = (
            testLogs.objects
            .filter(date__range=(startDate, endDate))
            .order_by("date", "time")
        )

    # formatted dates for the PDF title
    formattedStartDate = (
        startDate.replace("-", "/") if startDate else "—"
    )

    formattedEndDate = (
        endDate.replace("-", "/") if endDate else "—"
    )

    titleText = (
        f"ESD Test Log For: "
        f"{formattedStartDate} to {formattedEndDate}"
    )

    styles = getSampleStyleSheet()

    titleStyle = ParagraphStyle(
        "PDFTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=16,
        spaceAfter=12,
    )

    dayHeaderStyle = ParagraphStyle(
        "DayHeader",
        parent=styles["Heading2"],
        fontSize=10,
        leading=12,
        spaceBefore=8,
        spaceAfter=4,
    )

    # Group records by date
    logsByDay = OrderedDict()

    for log in logs:
        logDate = log.date

        # Use this if date is a DateTimeField
        if isinstance(logDate, datetime):
            logDate = logDate.date()

        logsByDay.setdefault(logDate, []).append(log)

    # Create the PDF in memory
    buffer = io.BytesIO()
    titleText = f"Logs for {startDate} to {endDate}"
    doc = SimpleDocTemplate(
        buffer,
        titleText=titleText,
        pagesize=letter,


        topMargin=36,
        bottomMargin=36,
    )

    imagePath = Path(__file__).resolve().parent / "hyrelLogo.jpg"

    logo = ReportLabImage(
        str(imagePath),
        width=2 * inch,
        height=1 * inch,
    )

    story = [
        logo,
        Spacer(1, 0.15 * inch),
        Paragraph(titleText, titleStyle),
        Spacer(1, 0.15 * inch),
    ]

    recordNumber = 1

    # Create one section/table for each day
    for logDate, dayLogs in logsByDay.items():
        verifications = verification.objects.all()
        initials = verification.objects.filter(date=logDate).values_list("initials", flat=True)
        initial = list(initials)
        print(initial)
        if len(initial) > 0:

            initial = initial[0]
        else:
            initial = ""

        formattedDate = logDate.strftime("%m/%d/%Y")
        dayOfWeek = logDate.strftime("%A")

        # Day subheader
        dayHeader = Paragraph(
            f"{formattedDate}"
            f"<b> - </b> {dayOfWeek}"
            f"&nbsp;&nbsp;&nbsp;&nbsp;"
            f"<b>Verification:</b> {initial}",
            dayHeaderStyle,
        )

        story.append(dayHeader)

        # Date is removed because it is now in the subheader
        rows = [
            ["No.", "Name", "Time", "Station", "Result"]
        ]

        for obj in dayLogs:
            rows.append([
                str(recordNumber),
                str(obj.otherUser or obj.username or ""),
                str(obj.time or ""),
                str(obj.station or ""),
                str(obj.testResult or ""),
            ])

            recordNumber += 1

        table = Table(
            rows,
            colWidths=[
                0.6 * inch,   # No.
                1.6 * inch,   # Name
                1.0 * inch,   # Time
                2.2 * inch,   # Station
                1.3 * inch,   # Result
            ],
            repeatRows=1,
        )

        table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))

        story.append(table)
        story.append(Spacer(1, 0.15 * inch))

    # If no records were found, show a message instead of an empty PDF
    if not logsByDay:
        story.append(
            Paragraph(
                "No records found for the selected date range.",
                styles["Normal"],
            )
        )

    doc.build(story)

    buffer.seek(0)
    return FileResponse(
        buffer,
        as_attachment=False,
        filename=f"ESD_TEST_LOGS.pdf",
        content_type="application/pdf",
    )

def verify(request):
    logsText = ""
    requestDate = Null
    if request.method == "POST":
        logsText = ""
        if request.POST.get("action") == "checkLogs":
            logsText = ""
            requestDate = request.POST.get("date")

            logsByDay = testLogs.objects.filter(date=requestDate)
            logNo = len(logsByDay)

            logsText = f"Logs found: {logNo}"

        if request.POST.get("action") == "verifyLogs":
            form = verificationForm(request.POST)

            if form.is_valid():

                form.save()

                messages.success(request, "Verification Succeeded!")

            return redirect("verify")
        return render(request, "verify.html", {"logsText": logsText, "date": requestDate})


    else:
        return render(request, "verify.html", {"logsText": "", "date": Null})

#next step to make a git repo or git lab for deployment in render or vercel
#internal url - postgresql://esdapp_user:JN58xpE8snEEVSrjQtSQEkvuXNBOwMBD@dpg-dbgcuh7avr4c73dluv60-a/esdapp