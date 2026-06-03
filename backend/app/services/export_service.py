import csv
import io
import json

from app.models.response import SurveyResponse


def responses_to_csv(rows: list[SurveyResponse]) -> str:
    question_codes = sorted({code for row in rows for code in row.answers.keys()})
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["response_id", "respondent_key", "respondent_email", "country", "product", "service", "region", "score", "submitted_at", *question_codes])
    for row in rows:
        writer.writerow(
            [
                row.id,
                row.respondent_key,
                row.respondent_email or "",
                row.country or "",
                row.product or "",
                row.service or "",
                row.region or "",
                row.score if row.score is not None else "",
                row.submitted_at.isoformat(),
                *[row.answers.get(code, "") for code in question_codes],
            ]
        )
    return output.getvalue()


def responses_to_excel_xml(rows: list[SurveyResponse]) -> str:
    csv_text = responses_to_csv(rows)
    rows_xml = []
    for line in csv.reader(io.StringIO(csv_text)):
        cells = "".join(f"<Cell><Data ss:Type=\"String\">{str(value)}</Data></Cell>" for value in line)
        rows_xml.append(f"<Row>{cells}</Row>")
    return f"""<?xml version="1.0"?>
<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"
 xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">
 <Worksheet ss:Name="Responses"><Table>{''.join(rows_xml)}</Table></Worksheet>
</Workbook>"""


def responses_to_pdf_html(rows: list[SurveyResponse]) -> str:
    body = "\n".join(
        f"<tr><td>{row.id}</td><td>{row.respondent_key}</td><td>{row.submitted_at}</td><td><pre>{json.dumps(row.answers)}</pre></td></tr>"
        for row in rows
    )
    return f"<html><body><h1>Survey Responses</h1><table border='1'><tr><th>ID</th><th>Respondent</th><th>Submitted</th><th>Answers</th></tr>{body}</table></body></html>"
