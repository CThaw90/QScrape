## QScrape
A small Python utility tool to download all answers from a Quora profile to a text file

## Build QScrape from source
python -m pip install -r requirements.txt && python -m PyInstaller --onefile --console 'qscrape.py'
qscrape program will be located within the dist folder

## Usage
./qscrape https://www.quora.com/profile/<profilename>

