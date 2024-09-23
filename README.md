# SnippingPanda
A small tool to create a screenshot of your screens, create a areal screenshot by defining the desired area and read QRCodes. 

Multiple screen setups are also supported now. You can decide which screen you want to take a screenshot of. You can also take a screenshot of all screens.

## QRCodes
- Select the QR code you want to read by marking it with a rectangle
- If a QR code is detected, it is shown on the UI
- The QR code can be opened by double clicking
- The content of the QR code is also displayed underneath
- To copy the content to the clipboard just simply click on it

## Build
`PyInstaller` was used to build the project on windows. To run it on another platform, it may need to be built for it. 

1. Open terminal, navigate in root directory, create and activate a virtual environment
> python -m venv venv

On Linux:
> source ./venv/bin/activate

On Windows:
> . ./venv/Scripts/activate

2. Install pyinstaller using pip
> pip install pyinstaller

3. Execute build command
> pyinstaller --clean -y -n "SnippingPanda" --add-data="static\no_qr_code.png;files" --onefile --icon="static\icon.ico" --noconsole .\main.py

### Upcoming
- [ ] QR code Creator
- [ ] Multiple QR code Reader
- [X] Multiple Monitor support
- [ ] Give user feedback with toasts (e.g., if the content of the QR code is copied by clicking on the text)
