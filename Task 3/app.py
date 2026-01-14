from flask import Flask, render_template, request, send_file, redirect, url_for
from crypto_utils import encrypt_file, decrypt_file
import os
from io import BytesIO

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"txt", "pdf", "docx", "png", "jpg", "jpeg"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    if request.method == "POST":
        file = request.files.get("file")
        password = request.form.get("password")

        if not file or not password:
            message = "File and password required"
        elif not allowed_file(file.filename):
            message = "Invalid file type"
        else:
            data = file.read()
            if len(data) > MAX_FILE_SIZE:
                message = "File too large (Max 5MB)"
            else:
                encrypted_data = encrypt_file(data, password)
                with open(os.path.join(UPLOAD_FOLDER, file.filename), "wb") as f:
                    f.write(encrypted_data)
                message = "File uploaded and encrypted successfully"

    files = os.listdir(UPLOAD_FOLDER)
    return render_template("index.html", files=files, message=message)

@app.route("/download/<filename>", methods=["POST"])
def download(filename):
    password = request.form.get("password")
    if not password:
        return "Password required"

    try:
        with open(os.path.join(UPLOAD_FOLDER, filename), "rb") as f:
            decrypted = decrypt_file(f.read(), password)

        return send_file(
            BytesIO(decrypted),
            download_name=filename,
            as_attachment=True
        )
    except Exception:
        return "Wrong password or corrupted file"

@app.route("/delete/<filename>")
def delete(filename):
    os.remove(os.path.join(UPLOAD_FOLDER, filename))
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
