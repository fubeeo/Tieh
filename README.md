# Tieh (Tiè!)

A simple web application to quickly transfer files from your phone to your PC using QR codes (or viceversa).

## Features

- Instant file sharing through local network
- QR code scanning for easy connection
- Image thumbnail previews
- Multiple file upload support

## Installation

```bash
git clone https://github.com/fubeeo/tieh.git
cd tieh
pip install .
```

## Usage

### Web Interface

1. Run the application:
```bash
tieh
```

2. Your default web browser will open automatically showing a QR code

3. On your phone:
   - Scan the QR code using your camera
   - Select files to upload
   - Click "Send"

### Direct File Sharing

Share a specific file directly:
```bash
tieh /path/to/file
```
This will:
1. Generate a QR code in the terminal
2. Create a temporary direct download link
3. When scanned, the QR code will download the file directly to the phone

## Requirements

- Python 3.7+
- Local network connection between phone and PC
- Web browser with camera access (for mobile device)
