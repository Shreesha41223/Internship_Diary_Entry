from flask import Flask, render_template, request, send_file, jsonify
import fitz  # PyMuPDF
from datetime import datetime
from flask_cors import CORS  # To allow frontend requests
from io import BytesIO

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

PDF_TEMPLATE = "diary.pdf"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate-pdf", methods=["POST"])
def generate_pdf():
    try:
        data = request.json
        entries = data.get("entries", [])

        if not entries:
            return jsonify({"error": "No entries provided"}), 400

        doc_final = fitz.open()

        first_day = entries[0].get("day", "1")
        last_day = entries[-1].get("day", first_day)

        for entry in entries:
            doc = fitz.open(PDF_TEMPLATE)
            page = doc[0]

            day = entry.get("day")
            date = entry.get("date")
            industry = entry.get("industry")
            in_time = entry.get("inTime")
            out_time = entry.get("outTime")
            department = entry.get("department")
            software = entry.get("software")
            hod = entry.get("hod")
            main = entry.get("main")

            text_positions = [
                (130, 178, day), (440, 178, date), (300, 198, industry),
                (160, 218, in_time), (440, 218, out_time), (300, 233, department),
                (300, 247, software), (300, 260, hod)
            ]

            for x, y, text in text_positions:
                page.insert_text((x, y), text, fontsize=11, fontname="helv", color=(0, 0, 0))

            text_rect = fitz.Rect(80, 290, 80 + 460, 290 + 260)
            page.insert_textbox(text_rect, main, fontsize=11, fontname="helv", color=(0, 0, 0), align=0)

            doc_final.insert_pdf(doc)
            doc.close()

        # Create an in-memory byte stream for the PDF
        pdf_bytes = BytesIO()
        doc_final.save(pdf_bytes)
        pdf_bytes.seek(0)
        doc_final.close()

        if len(entries) == 1:
            final_pdf_name = f"Day_{first_day}_Diary.pdf"
        else:
            final_pdf_name = f"Day_{first_day}_to_{last_day}_Diary.pdf"

        return send_file(pdf_bytes, as_attachment=True, download_name=final_pdf_name, mimetype="application/pdf")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)