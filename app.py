import os
import sqlite3
from flask import Flask, render_template, request
from extractor.reader import read_document
from extractor.classifier import classify_document
from extractor.fields import extract_fields

# Detect if running on Vercel
IS_VERCEL = os.environ.get("VERCEL") is not None

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

if IS_VERCEL:
    # Vercel: use /tmp (only writable directory)
    UPLOAD_FOLDER = "/tmp/uploads"
    DB_DIR = "/tmp/instance"
    DB_PATH = os.path.join(DB_DIR, "doc_ai.db")
else:
    # Local dev: original paths
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    DB_DIR = os.path.join(BASE_DIR, "instance")
    DB_PATH = os.path.join(DB_DIR, "doc_ai.db")

# Create necessary folders
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}


# ---------- DB helpers ----------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_type TEXT NOT NULL,
            name TEXT,
            dl_number TEXT,
            dob TEXT,
            borrower_name TEXT,
            customer_no TEXT,
            expire_date TEXT,
            employee_name TEXT,
            employer_name TEXT,
            net_pay TEXT,
            ein TEXT,
            year TEXT,
            passport_number TEXT,
            country TEXT,
            raw_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.commit()
    conn.close()


def save_to_db(doc_type, fields, raw_text):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO documents (
            doc_type, name, dl_number, dob,
            borrower_name, customer_no, expire_date,
            employee_name, employer_name, net_pay,
            ein, year, passport_number, country, raw_text
        )
        VALUES (
            :doc_type, :name, :dl_number, :dob,
            :borrower_name, :customer_no, :expire_date,
            :employee_name, :employer_name, :net_pay,
            :ein, :year, :passport_number, :country, :raw_text
        )
        """,
        {
            "doc_type": doc_type,
            "name": fields.get("name"),
            "dl_number": fields.get("dl_number"),
            "dob": fields.get("dob"),
            "borrower_name": fields.get("borrower_name"),
            "customer_no": fields.get("customer_no"),
            "expire_date": fields.get("expire_date"),
            "employee_name": fields.get("employee_name"),
            "employer_name": fields.get("employer_name"),
            "net_pay": fields.get("net_pay"),
            "ein": fields.get("ein"),
            "year": fields.get("year"),
            "passport_number": fields.get("passport_number"),
            "country": fields.get("country"),
            "raw_text": raw_text,
        },
    )
    conn.commit()
    conn.close()


# ---------- Ensure DB is initialized (Flask 3.x safe) ----------
db_initialized = False


@app.before_request
def setup_db():
    global db_initialized
    if not db_initialized:
        init_db()
        db_initialized = True


# ---------- Routes ----------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("document")
        if not file or file.filename == "":
            return render_template(
                "index.html",
                error="Please select a file.",
                doc_type=None,
                fields=None,
                text=None,
            )

        # check extension
        _, ext = os.path.splitext(file.filename)
        ext = ext.lower()
        if ext not in ALLOWED_EXTENSIONS:
            return render_template(
                "index.html",
                error=f"Unsupported file type: {ext}. Please upload a PDF or image.",
                doc_type=None,
                fields=None,
                text=None,
            )

        # save uploaded file
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(save_path)

        # 1. extract text
        try:
            text = read_document(save_path)
            # ---- debug output in terminal ----
            print("======== RAW TEXT SAMPLE ========")
            print("Length:", len(text), "characters")
            print(text[:1000])
            print("=================================")
        except Exception as e:
            return render_template(
                "index.html",
                error=f"Error reading document: {e}",
                doc_type=None,
                fields=None,
                text=None,
            )

        # handle empty text (likely scanned image PDF)
        if not text.strip():
            return render_template(
                "index.html",
                error="No readable text found in PDF (maybe a scanned image).",
                doc_type="Others",
                fields=None,
                text=text,
            )

        # 2. classify type
        doc_type = classify_document(text)

        # 3. extract fields
        fields = extract_fields(doc_type, text)

        # 4. save to DB
        try:
            save_to_db(doc_type, fields, text)
        except Exception as e:
            return render_template(
                "index.html",
                error=f"Error saving to database: {e}",
                doc_type=doc_type,
                fields=fields,
                text=text,
            )

        return render_template(
            "index.html",
            error=None,
            doc_type=doc_type,
            fields=fields,
            text=text,
        )

    # GET
    return render_template(
        "index.html",
        error=None,
        doc_type=None,
        fields=None,
        text=None,
    )


@app.route("/records")
def records():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM documents ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return render_template("records.html", rows=rows)


if __name__ == "__main__":
    # Local dev server
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
