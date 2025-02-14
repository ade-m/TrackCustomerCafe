import cv2
import torch
import numpy as np
from ultralytics import YOLO
from collections import deque
import sys
import time

# Menambahkan path ke folder SORT
sys.path.append("sort")
from sort import Sort

# Load model YOLO
model = YOLO("yolo11n.pt")

# Buka video
video_path = "ObjectDetections/cafe3.mp4"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(f"Error: Tidak dapat membuka video {video_path}")
    exit()

# Inisialisasi tracker SORT
tracker = Sort(max_age=50, min_hits=5, iou_threshold=0.2)

# Dictionary untuk menyimpan waktu pelanggan dan ID warna
tracks = {}
colors = {}
time_tracking = {}
table_timers = {}

# Fungsi untuk merotasi titik-titik kotak meja
def rotate_box(center, width, height, angle):
    angle = np.radians(angle)
    cos_a, sin_a = np.cos(angle), np.sin(angle)

    dx, dy = width // 2, height // 2
    corners = np.array([
        [-dx, -dy],
        [dx, -dy],
        [dx, dy],
        [-dx, dy]
    ])

    rotated_corners = np.dot(corners, np.array([[cos_a, -sin_a], [sin_a, cos_a]]))
    rotated_corners += center
    return rotated_corners.astype(int)

# Definisi area meja dengan rotasi (tengah, lebar, tinggi, rotasi derajat)
tables = {
    "Meja 1": ((650, 700), 400, 150, -25),
    "Meja 2": ((1250, 450), 350, 150, -25),
    "Meja 3": ((1450, 300), 250, 120, -25),
    "Meja 4": ((1950, 450), 350, 150, -25),
    "Meja 5": ((1850, 650), 350, 150, -25),
    "Meja 6": ((1500, 1100), 600, 300, -25),
}

# Warna meja
table_colors = {
    "Meja 1": (255, 0, 0),  # Biru
    "Meja 2": (0, 255, 0),  # Hijau
    "Meja 3": (0, 0, 255),  # Merah
    "Meja 4": (0, 0, 255),  # Merah
    "Meja 5": (0, 0, 255),  # Merah
    "Meja 6": (0, 0, 255),  # Merah
}
# Fungsi untuk mengonversi detik ke format MM:SS
def format_time(seconds):
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02}:{secs:02}"
# Fungsi untuk mendapatkan warna unik
np.random.seed(42)
def get_color(obj_id):
    if obj_id not in colors:
        colors[obj_id] = tuple(map(int, np.random.randint(0, 255, size=3)))
    return colors[obj_id]

# Loop pemrosesan frame
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)
    detections = []

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0].item())
            if class_id == 0:  # Hanya deteksi orang
                bbox = list(map(int, box.xyxy[0]))
                conf = box.conf[0].item()
                if len(bbox) == 4:
                    detections.append(bbox + [conf])

    detections = np.array(detections) if len(detections) > 0 else np.empty((0, 5))
    tracked_objects = tracker.update(detections)

    current_time = time.time()

    # Gambar area meja yang diputar
    for table_name, (center, width, height, angle) in tables.items():
        color = table_colors[table_name]
        rotated_corners = rotate_box(center, width, height, angle)
        
        overlay = frame.copy()
        cv2.fillPoly(overlay, [rotated_corners], color)
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)

        # Tampilkan nama meja
        text_pos = tuple(rotated_corners[0])  # Posisi label meja
        cv2.putText(frame, table_name, text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 3, cv2.LINE_AA)

    # Periksa apakah pelanggan duduk di meja
    for obj in tracked_objects:
        x1, y1, x2, y2, obj_id = map(int, obj)
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        color = get_color(obj_id)

        # Simpan waktu pertama kali pelanggan terdeteksi
        if obj_id not in time_tracking:
            time_tracking[obj_id] = current_time

        elapsed_time = int(current_time - time_tracking[obj_id])
        elapsed_formatted = format_time(elapsed_time)
        # Gambar bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
        text = f"Cust. ID {obj_id} | {elapsed_formatted}s"
        cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 3, cv2.LINE_AA)

        # Cek apakah pelanggan berada dalam salah satu area meja
        for table_name, (center, width, height, angle) in tables.items():
            rotated_corners = rotate_box(center, width, height, angle)
            if cv2.pointPolygonTest(rotated_corners, (cx, cy), False) >= 0:
                if obj_id not in table_timers:
                    table_timers[obj_id] = {table_name: current_time}
                elif table_name not in table_timers[obj_id]:
                    table_timers[obj_id][table_name] = current_time
            elif obj_id in table_timers and table_name in table_timers[obj_id]:
                del table_timers[obj_id][table_name]

    # Hitung waktu pelanggan duduk di meja dan tampilkan
    for table_name, (center, width, height, angle) in tables.items():
        total_time = 0
        for obj_id in table_timers:
            if table_name in table_timers[obj_id]:
                total_time += int(current_time - table_timers[obj_id][table_name])
        total_formatted = format_time(total_time)
        text_pos = (center[0] - 50, center[1] + height // 2 + 30)
        cv2.putText(frame, f"{table_name}: {total_formatted}s", text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 3, cv2.LINE_AA)

    # Tampilkan hasil tracking
    cv2.imshow("Tracking Pelanggan & Meja", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
