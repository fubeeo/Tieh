import io
import os
import socket
import webbrowser
from appdirs import user_data_dir

import PIL
import qrcode
from flask import (
    Flask,
    redirect,
    render_template,
    request,
    send_file,
    send_from_directory,
    url_for,
)
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
from threading import Timer

APP_NAME = "Tieh"
APP_AUTHOR = "Fubeeo"
APP_DATA_DIR = user_data_dir(APP_NAME, APP_AUTHOR)
UPLOAD_FOLDER = os.path.join(APP_DATA_DIR, "uploads")
THUMBNAIL_FOLDER = os.path.join(APP_DATA_DIR, "thumbnails")

app = Flask(__name__)
socketio = SocketIO(app)


@app.route("/")
def index():
    hostname = socket.getfqdn()
    local_ip = socket.gethostbyname_ex(hostname)[2][1]
    port = 5000
    qr_data = f"http://{local_ip}:{port}/send_page"

    return render_template("index.html", url=qr_data, files=os.listdir(UPLOAD_FOLDER))


@app.route("/qrcode", methods=["GET"])
def generate_qrcode():
    # Get data from query parameters
    qr_data = request.args.get("data", "")
    if not qr_data:
        return "No data provided", 400

    # Generate QR code
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=7,
        border=0,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    # Create image
    img = qr.make_image(fill_color="black", back_color="white")

    # Save to bytes buffer instead of file
    img_buffer = io.BytesIO()
    img.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    return send_file(img_buffer, mimetype="image/png", as_attachment=False)


@app.route("/send_page")
def send_page():
    return render_template("send.html")


@app.route("/send", methods=["POST"])
def send():
    if not request.files:
        return "No files uploaded", 400

    uploaded_files = request.files.getlist("files[]")

    for file in uploaded_files:
        if not file or not file.filename:
            continue

        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        # Prevent path traversal
        if not os.path.abspath(file_path).startswith(os.path.abspath(UPLOAD_FOLDER)):
            return "Invalid file path", 400

        try:
            file.save(file_path)

            if file.mimetype.startswith("image"):
                thumbnail = PIL.Image.open(file_path)
                thumbnail.thumbnail((128, 128))
                thumbnail.save(os.path.join(THUMBNAIL_FOLDER, filename))

        except Exception as e:
            return f"Error saving file: {str(e)}", 500

    socketio.emit("file_uploaded", namespace="/")
    return redirect(url_for("received"))


@app.route("/received")
def received():
    return render_template("received.html", files=os.listdir(UPLOAD_FOLDER))


@app.route("/uploads/<filename>")
def get_file(filename):
    return send_from_directory(os.path.abspath(UPLOAD_FOLDER), filename)


@app.route("/thumbnails/<filename>")
def get_thumbnail(filename):
    return send_from_directory(os.path.abspath(THUMBNAIL_FOLDER), filename)


@app.route("/clear", methods=["POST"])
def clear():
    for folder in [UPLOAD_FOLDER, THUMBNAIL_FOLDER]:
        for file in os.listdir(folder):
            os.remove(os.path.join(folder, file))
    socketio.emit("file_uploaded", namespace="/")
    return "", 200


def open_browser():
    webbrowser.open("http://localhost:5000")


def main():
    # Create app data directories
    os.makedirs(APP_DATA_DIR, exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(THUMBNAIL_FOLDER, exist_ok=True)

    Timer(1, open_browser).start()
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)


if __name__ == "__main__":
    main()
