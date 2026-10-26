import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont
 
 
# 1. LADOWANIE MODELU
print("Ladowanie modelu YOLO...")
model = YOLO("yolov8n.pt")
 
 
# 2. POLSKIE NAZWY KLAS (zapis bez polskich znakow)
polskie_nazwy = {
    "person": "osoba",
    "bicycle": "rower",
    "car": "samochod",
    "motorcycle": "motocykl",
    "airplane": "samolot",
    "bus": "autobus",
    "train": "pociag",
    "truck": "ciezarowka",
    "boat": "lodz",
    "traffic light": "sygnalizacja",
    "fire hydrant": "hydrant",
    "stop sign": "znak stop",
    "parking meter": "parkomat",
    "bench": "lawka",
    "bird": "ptak",
    "cat": "kot",
    "dog": "pies",
    "horse": "kon",
    "sheep": "owca",
    "cow": "krowa",
    "elephant": "slon",
    "bear": "niedzwiedz",
    "zebra": "zebra",
    "giraffe": "zyrafa",
    "backpack": "plecak",
    "umbrella": "parasol",
    "handbag": "torebka",
    "tie": "krawat",
    "suitcase": "walizka",
    "frisbee": "frisbee",
    "skis": "narty",
    "snowboard": "snowboard",
    "sports ball": "pilka",
    "kite": "latawiec",
    "baseball bat": "kij baseballowy",
    "baseball glove": "rekawica",
    "skateboard": "deskorolka",
    "surfboard": "deska surfingowa",
    "tennis racket": "rakieta tenisowa",
    "bottle": "butelka",
    "wine glass": "kieliszek",
    "cup": "kubek",
    "fork": "widelec",
    "knife": "noz",
    "spoon": "lyzka",
    "bowl": "miska",
    "banana": "banan",
    "apple": "jablko",
    "sandwich": "kanapka",
    "orange": "pomarancza",
    "broccoli": "brokul",
    "carrot": "marchewka",
    "hot dog": "hot dog",
    "pizza": "pizza",
    "donut": "donut",
    "cake": "ciasto",
    "chair": "krzeslo",
    "couch": "sofa",
    "potted plant": "roslina",
    "bed": "lozko",
    "dining table": "stol",
    "toilet": "toaleta",
    "tv": "telewizor",
    "laptop": "laptop",
    "mouse": "mysz komputerowa",
    "remote": "pilot",
    "keyboard": "klawiatura",
    "cell phone": "telefon",
    "microwave": "mikrofalowka",
    "oven": "piekarnik",
    "toaster": "toster",
    "sink": "zlew",
    "refrigerator": "lodowka",
    "book": "ksiazka",
    "clock": "zegar",
    "vase": "wazon",
    "scissors": "nozyczki",
    "teddy bear": "mis pluszowy",
    "hair drier": "suszarka",
    "toothbrush": "szczoteczka"
}
 
 
# 3. CZCIONKA
try:
    sciezka_czcionki = r"C:\\Windows\\Fonts\\arial.ttf"
    czcionka = ImageFont.truetype(sciezka_czcionki, 30)
except OSError:
    czcionka = ImageFont.load_default()
 
 
# 4. URUCHOMIENIE KAMERY
kamera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
 
if not kamera.isOpened():
    print("Blad: nie mozna uruchomic kamery.")
    raise SystemExit
 
kamera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
kamera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
 
print("AI dziala! Nacisnij Q, aby zakonczyc.")
 
 
# 5. PETLA ROZPOZNAWANIA
while True:
    ok, klatka = kamera.read()
 
    if not ok:
        print("Nie udalo sie pobrac obrazu z kamery.")
        break
 
    wyniki = model.predict(
        klatka,
        conf=0.45,
        imgsz=640,
        verbose=False
    )
    wynik = wyniki[0]
 
    obraz_pil = Image.fromarray(
        cv2.cvtColor(klatka, cv2.COLOR_BGR2RGB)
    )
    rysuj = ImageDraw.Draw(obraz_pil)
 
    for box in wynik.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        klasa = int(box.cls[0])
        pewnosc = float(box.conf[0]) * 100
 
        nazwa_en = wynik.names[klasa]
        nazwa_pl = polskie_nazwy.get(nazwa_en, nazwa_en)
        etykieta = f"{nazwa_pl} {pewnosc:.0f}%"
 
        # Zielona ramka wokol wykrytego obiektu
        rysuj.rectangle(
            [x1, y1, x2, y2],
            outline=(0, 255, 80),
            width=4
        )
 
        # Wymiary etykiety
        lewo, gora, prawo, dol = rysuj.textbbox(
            (0, 0), etykieta, font=czcionka
        )
        szerokosc = prawo - lewo
        wysokosc = dol - gora
        padding = 8
 
        etykieta_y = y1 - wysokosc - 2 * padding
        if etykieta_y < 0:
            etykieta_y = y1 + 5
 
        # Ciemnozielone tlo
        rysuj.rectangle(
            [
                x1,
                etykieta_y,
                x1 + szerokosc + 2 * padding,
                etykieta_y + wysokosc + 2 * padding
            ],
            fill=(0, 90, 40)
        )
 
        # Bialy, duzy napis
        rysuj.text(
            (x1 + padding, etykieta_y + padding - gora),
            etykieta,
            font=czcionka,
            fill=(255, 255, 255),
            stroke_width=1,
            stroke_fill=(0, 0, 0)
        )
 
    obraz_ai = cv2.cvtColor(
        np.array(obraz_pil),
        cv2.COLOR_RGB2BGR
    )
 
    cv2.namedWindow("AI Vision - YOLO po polsku", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("AI Vision - YOLO po polsku", 1000, 750)
    cv2.imshow("AI Vision - YOLO po polsku", obraz_ai)
 
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
 
 
# 6. ZAMKNIECIE KAMERY
kamera.release()
cv2.destroyAllWindows()
print("Program zakonczony.")
