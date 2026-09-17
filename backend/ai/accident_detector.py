from ultralytics import YOLO
import cv2
import math
import os
import json
import re
from datetime import datetime


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

VIDEO_SOURCE = os.path.join(
    BASE_DIR,
    "videos",
    "v1.mov"
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "yolo11n.pt"
)

INCIDENT_FILE = os.path.join(
    BASE_DIR,
    "backend",
    "incidents.json"
)

EVIDENCE_FOLDER = os.path.join(
    BASE_DIR,
    "backend",
    "ai",
    "evidence"
)

os.makedirs(
    EVIDENCE_FOLDER,
    exist_ok=True
)


# ============================================================
# SETTINGS
# ============================================================

VEHICLE_CLASSES = {
    "car",
    "truck",
    "bus",
    "motorcycle"
}

CONFIDENCE = 0.25

MIN_IOU = 0.08

REQUIRED_COLLISION_FRAMES = 4

# OCR every N frames
OCR_INTERVAL = 8

# Minimum OCR confidence
OCR_CONFIDENCE = 0.25


CAMERA_LOCATION = "Main Road CCTV Camera"


# ============================================================
# EASY OCR
# ============================================================

print("\n" + "=" * 70)
print("🚗 AI ROAD ACCIDENT + NUMBER PLATE DETECTION")
print("=" * 70)

print("🔤 Loading EasyOCR...")

try:

    import easyocr

    ocr_reader = easyocr.Reader(
        ["en"],
        gpu=False
    )

    print("✅ EasyOCR loaded")

except Exception as error:

    print("❌ EasyOCR could not load")
    print(error)

    raise SystemExit


# ============================================================
# YOLO
# ============================================================

print("📦 Loading YOLO model...")

model = YOLO(
    MODEL_PATH
)

print("✅ YOLO model loaded")


# ============================================================
# NUMBER PLATE FUNCTIONS
# ============================================================

def clean_plate_text(text):

    if not text:
        return None

    # Uppercase
    text = text.upper()

    # Remove spaces and symbols
    text = re.sub(
        r"[^A-Z0-9]",
        "",
        text
    )

    # Plate should normally contain both
    # letters and numbers
    if not re.search(
        r"[A-Z]",
        text
    ):
        return None

    if not re.search(
        r"[0-9]",
        text
    ):
        return None

    # Reasonable plate length
    if len(text) < 5 or len(text) > 12:
        return None

    return text


def looks_like_indian_plate(text):

    if not text:
        return False

    # Common Indian registration pattern
    #
    # Example:
    # WB12AB1234
    # DL01CA1234
    # MH12DE1433
    #
    pattern = (
        r"^[A-Z]{2}"
        r"[0-9]{1,2}"
        r"[A-Z]{1,3}"
        r"[0-9]{1,4}$"
    )

    return bool(
        re.match(
            pattern,
            text
        )
    )


def read_number_plate(
    vehicle_crop
):

    if vehicle_crop is None:
        return None

    if vehicle_crop.size == 0:
        return None


    h, w = vehicle_crop.shape[:2]


    if h < 20 or w < 20:
        return None


    # --------------------------------------------------------
    # Number plate is generally around the lower/middle
    # section of a vehicle.
    # We create multiple candidate crops.
    # --------------------------------------------------------

    candidates = []


    # Lower 65%
    candidates.append(
        vehicle_crop[
            int(h * 0.35):h,
            :
        ]
    )


    # Lower 50%
    candidates.append(
        vehicle_crop[
            int(h * 0.50):h,
            :
        ]
    )


    # Full vehicle crop
    candidates.append(
        vehicle_crop
    )


    best_plate = None
    best_confidence = 0


    for candidate in candidates:

        if candidate.size == 0:
            continue


        # ----------------------------------------------------
        # Upscale
        # ----------------------------------------------------

        scale = 3

        enlarged = cv2.resize(
            candidate,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_CUBIC
        )


        # ----------------------------------------------------
        # Improve contrast
        # ----------------------------------------------------

        gray = cv2.cvtColor(
            enlarged,
            cv2.COLOR_BGR2GRAY
        )


        gray = cv2.GaussianBlur(
            gray,
            (3, 3),
            0
        )


        # ----------------------------------------------------
        # OCR
        # ----------------------------------------------------

        try:

            results = ocr_reader.readtext(
                enlarged,
                detail=1,
                paragraph=False,
                allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            )

        except Exception:

            continue


        for result in results:

            if len(result) < 3:
                continue


            text = result[1]

            confidence = float(
                result[2]
            )


            cleaned = clean_plate_text(
                text
            )


            if not cleaned:
                continue


            if confidence < OCR_CONFIDENCE:
                continue


            # Prefer Indian-looking registration numbers
            indian_format = looks_like_indian_plate(
                cleaned
            )


            score = confidence

            if indian_format:
                score += 0.25


            if score > best_confidence:

                best_confidence = score

                best_plate = cleaned


    return best_plate


# ============================================================
# GENERAL FUNCTIONS
# ============================================================

def center_of(box):

    x1, y1, x2, y2 = box

    return (
        int((x1 + x2) / 2),
        int((y1 + y2) / 2)
    )


def distance(
    point1,
    point2
):

    return math.sqrt(
        (point1[0] - point2[0]) ** 2
        +
        (point1[1] - point2[1]) ** 2
    )


def iou(
    box1,
    box2
):

    x1 = max(
        box1[0],
        box2[0]
    )

    y1 = max(
        box1[1],
        box2[1]
    )

    x2 = min(
        box1[2],
        box2[2]
    )

    y2 = min(
        box1[3],
        box2[3]
    )


    width = max(
        0,
        x2 - x1
    )

    height = max(
        0,
        y2 - y1
    )


    intersection = (
        width * height
    )


    area1 = (
        max(
            0,
            box1[2] - box1[0]
        )
        *
        max(
            0,
            box1[3] - box1[1]
        )
    )


    area2 = (
        max(
            0,
            box2[2] - box2[0]
        )
        *
        max(
            0,
            box2[3] - box2[1]
        )
    )


    union = (
        area1
        +
        area2
        -
        intersection
    )


    if union <= 0:
        return 0


    return intersection / union


# ============================================================
# INCIDENT FILE
# ============================================================

def load_incidents():

    try:

        if not os.path.exists(
            INCIDENT_FILE
        ):

            return []


        with open(
            INCIDENT_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(
                file
            )


        if isinstance(
            data,
            list
        ):

            return data


        if isinstance(
            data,
            dict
        ):

            return data.get(
                "incidents",
                []
            )


    except Exception as error:

        print(
            "⚠️ Incident read error:",
            error
        )


    return []


# ============================================================
# SAVE INCIDENT
# ============================================================

def save_incident(
    vehicle1,
    vehicle2,
    plate1,
    plate2,
    dist,
    overlap,
    image_path
):

    incidents = load_incidents()


    incident_id = (
        len(incidents) + 1
    )


    incident = {

        "id":
            incident_id,

        "vehicle_1":
            int(vehicle1),

        "vehicle_2":
            int(vehicle2),

        "plate_1":
            plate1
            if plate1
            else "NOT DETECTED",

        "plate_2":
            plate2
            if plate2
            else "NOT DETECTED",

        "distance":
            round(
                float(dist),
                2
            ),

        "iou":
            round(
                float(overlap),
                3
            ),

        "time":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "location":
            CAMERA_LOCATION,

        "evidence":
            os.path.relpath(
                image_path,
                BASE_DIR
            ),

        "status":
            "ACCIDENT CONFIRMED"

    }


    incidents.append(
        incident
    )


    with open(
        INCIDENT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            incidents,
            file,
            indent=4
        )


    print("\n")
    print("=" * 70)
    print("🚨🚨🚨 ACCIDENT CONFIRMED 🚨🚨🚨")
    print("=" * 70)

    print(
        f"🚗 Vehicle 1 ID : {vehicle1}"
    )

    print(
        f"🔢 Plate 1      : {plate1 or 'NOT DETECTED'}"
    )

    print(
        f"🚗 Vehicle 2 ID : {vehicle2}"
    )

    print(
        f"🔢 Plate 2      : {plate2 or 'NOT DETECTED'}"
    )

    print(
        f"📏 Distance     : {dist:.2f}px"
    )

    print(
        f"📦 IoU          : {overlap:.3f}"
    )

    print(
        f"📍 Location     : {CAMERA_LOCATION}"
    )

    print(
        f"🕐 Time         : {incident['time']}"
    )

    print(
        f"📸 Evidence     : {image_path}"
    )

    print(
        "🚓 EMERGENCY ALERT GENERATED"
    )

    print(
        "💾 INCIDENT SAVED TO DASHBOARD"
    )

    print("=" * 70)


# ============================================================
# OPEN VIDEO
# ============================================================

print(
    f"🎥 Video: {VIDEO_SOURCE}"
)


cap = cv2.VideoCapture(
    VIDEO_SOURCE
)


if not cap.isOpened():

    print(
        "❌ Cannot open v1.mov"
    )

    print(
        f"Expected: {VIDEO_SOURCE}"
    )

    raise SystemExit


fps = cap.get(
    cv2.CAP_PROP_FPS
)

if fps <= 0:
    fps = 30


width = int(
    cap.get(
        cv2.CAP_PROP_FRAME_WIDTH
    )
)

height = int(
    cap.get(
        cv2.CAP_PROP_FRAME_HEIGHT
    )

)


total_frames = int(
    cap.get(
        cv2.CAP_PROP_FRAME_COUNT
    )
)


print(
    f"📐 Resolution: {width} x {height}"
)

print(
    f"🎞️ FPS: {fps:.2f}"
)

print(
    f"🎞️ Frames: {total_frames}"
)

print(
    "▶️ Starting AI analysis..."
)

print("=" * 70)


# ============================================================
# TRACKING
# ============================================================

previous_centers = {}

collision_frames = {}

confirmed_pairs = set()


# Plate cache:
# track ID -> plate
plate_cache = {}

# Last frame OCR was attempted
plate_last_attempt = {}


# ============================================================
# MAIN LOOP
# ============================================================

frame_number = 0


while True:

    success, frame = cap.read()


    if not success:

        print(
            "\n✅ Video analysis completed."
        )

        break


    frame_number += 1


    # ========================================================
    # YOLO TRACKING
    # ========================================================

    results = model.track(
        frame,
        persist=True,
        conf=CONFIDENCE,
        verbose=False
    )


    current_vehicles = {}


    # ========================================================
    # DETECT VEHICLES
    # ========================================================

    for result in results:

        if result.boxes is None:
            continue


        if result.boxes.id is None:
            continue


        boxes = (
            result.boxes.xyxy
            .cpu()
            .numpy()
        )


        ids = (
            result.boxes.id
            .cpu()
            .numpy()
            .astype(int)
        )


        classes = (
            result.boxes.cls
            .cpu()
            .numpy()
            .astype(int)
        )


        confidences = (
            result.boxes.conf
            .cpu()
            .numpy()
        )


        for box, track_id, class_id, conf in zip(
            boxes,
            ids,
            classes,
            confidences
        ):

            name = model.names[
                int(class_id)
            ]


            if name not in VEHICLE_CLASSES:
                continue


            x1, y1, x2, y2 = map(
                int,
                box
            )


            # Keep inside image
            x1 = max(
                0,
                x1
            )

            y1 = max(
                0,
                y1
            )

            x2 = min(
                width,
                x2
            )

            y2 = min(
                height,
                y2
            )


            center = center_of(
                (
                    x1,
                    y1,
                    x2,
                    y2
                )
            )


            # =================================================
            # NUMBER PLATE OCR
            # =================================================

            plate = plate_cache.get(
                int(track_id)
            )


            should_read_plate = (
                frame_number
                -
                plate_last_attempt.get(
                    int(track_id),
                    -999
                )
                >= OCR_INTERVAL
            )


            if should_read_plate:

                plate_last_attempt[
                    int(track_id)
                ] = frame_number


                vehicle_crop = frame[
                    y1:y2,
                    x1:x2
                ]


                detected_plate = read_number_plate(
                    vehicle_crop
                )


                if detected_plate:

                    plate_cache[
                        int(track_id)
                    ] = detected_plate

                    plate = detected_plate


                    print(
                        f"🔢 Plate detected | "
                        f"Vehicle ID {track_id}: "
                        f"{detected_plate}"
                    )


            current_vehicles[
                int(track_id)
            ] = {

                "box":
                    (
                        x1,
                        y1,
                        x2,
                        y2
                    ),

                "center":
                    center,

                "name":
                    name,

                "plate":
                    plate,

                "confidence":
                    float(conf)

            }


            # =================================================
            # DRAW VEHICLE BOX
            # =================================================

            cv2.rectangle(
                frame,

                (
                    x1,
                    y1
                ),

                (
                    x2,
                    y2
                ),

                (0, 255, 0),

                2
            )


            # =================================================
            # VEHICLE LABEL
            # =================================================

            label = (
                f"{name.upper()} "
                f"ID:{track_id}"
            )


            if plate:

                label += (
                    f" | {plate}"
                )


            else:

                label += (
                    " | Plate: Detecting..."
                )


            cv2.rectangle(
                frame,

                (
                    x1,
                    max(
                        0,
                        y1 - 28
                    )
                ),

                (
                    min(
                        width,
                        x1 + 330
                    ),

                    y1
                ),

                (0, 180, 0),

                -1
            )


            cv2.putText(
                frame,

                label,

                (
                    x1 + 4,
                    max(
                        19,
                        y1 - 8
                    )
                ),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.48,

                (255, 255, 255),

                1,

                cv2.LINE_AA
            )


            # =================================================
            # CENTER
            # =================================================

            cv2.circle(
                frame,
                center,
                4,
                (0, 255, 255),
                -1
            )


    # ========================================================
    # COLLISION CHECK
    # ========================================================

    ids_list = list(
        current_vehicles.keys()
    )


    for i in range(
        len(ids_list)
    ):

        for j in range(
            i + 1,
            len(ids_list)
        ):

            id1 = ids_list[i]

            id2 = ids_list[j]


            v1 = current_vehicles[
                id1
            ]

            v2 = current_vehicles[
                id2
            ]


            box1 = v1["box"]

            box2 = v2["box"]


            center1 = v1[
                "center"
            ]

            center2 = v2[
                "center"
            ]


            pair = tuple(
                sorted(
                    [
                        id1,
                        id2
                    ]
                )
            )


            dist = distance(
                center1,
                center2
            )


            overlap = iou(
                box1,
                box2
            )


            # =================================================
            # ACTUAL OVERLAP REQUIRED
            # =================================================

            collision_condition = (
                overlap >= MIN_IOU
            )


            if collision_condition:

                collision_frames[pair] = (
                    collision_frames.get(
                        pair,
                        0
                    ) + 1
                )


                cv2.line(
                    frame,

                    center1,
                    center2,

                    (0, 0, 255),

                    3
                )


            else:

                collision_frames[pair] = 0


            # =================================================
            # ACCIDENT CONFIRMED
            # =================================================

            if (
                collision_frames.get(
                    pair,
                    0
                )
                >= REQUIRED_COLLISION_FRAMES
            ):

                if pair not in confirmed_pairs:

                    confirmed_pairs.add(
                        pair
                    )


                    # -----------------------------------------
                    # PLATES
                    # -----------------------------------------

                    plate1 = v1.get(
                        "plate"
                    )

                    plate2 = v2.get(
                        "plate"
                    )


                    # -----------------------------------------
                    # EVIDENCE
                    # -----------------------------------------

                    timestamp = datetime.now().strftime(
                        "%Y%m%d_%H%M%S_%f"
                    )


                    evidence_path = os.path.join(
                        EVIDENCE_FOLDER,

                        f"accident_{timestamp}.jpg"
                    )


                    cv2.putText(
                        frame,

                        "ACCIDENT CONFIRMED",

                        (
                            30,
                            50
                        ),

                        cv2.FONT_HERSHEY_SIMPLEX,

                        1.0,

                        (0, 0, 255),

                        3
                    )


                    cv2.putText(
                        frame,

                        "EMERGENCY ALERT",

                        (
                            30,
                            90
                        ),

                        cv2.FONT_HERSHEY_SIMPLEX,

                        0.8,

                        (0, 0, 255),

                        2
                    )


                    # Show plates in evidence
                    cv2.putText(
                        frame,

                        f"PLATE 1: {plate1 or 'NOT DETECTED'}",

                        (
                            30,
                            125
                        ),

                        cv2.FONT_HERSHEY_SIMPLEX,

                        0.65,

                        (0, 255, 255),

                        2
                    )


                    cv2.putText(
                        frame,

                        f"PLATE 2: {plate2 or 'NOT DETECTED'}",

                        (
                            30,
                            155
                        ),

                        cv2.FONT_HERSHEY_SIMPLEX,

                        0.65,

                        (0, 255, 255),

                        2
                    )


                    cv2.imwrite(
                        evidence_path,
                        frame
                    )


                    # -----------------------------------------
                    # SAVE INCIDENT
                    # -----------------------------------------

                    save_incident(
                        id1,
                        id2,
                        plate1,
                        plate2,
                        dist,
                        overlap,
                        evidence_path
                    )


    # ========================================================
    # PREVIOUS CENTERS
    # ========================================================

    previous_centers = {

        vehicle_id:
            vehicle["center"]

        for vehicle_id, vehicle
        in current_vehicles.items()

    }


    # ========================================================
    # STATUS
    # ========================================================

    cv2.putText(
        frame,

        "AI ACCIDENT + NUMBER PLATE DETECTION",

        (
            20,
            height - 45
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.65,

        (0, 255, 0),

        2
    )


    cv2.putText(
        frame,

        f"Frame: {frame_number}/{total_frames}",

        (
            20,
            height - 15
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.5,

        (255, 255, 255),

        1
    )


    # ========================================================
    # SHOW
    # ========================================================

    cv2.imshow(
        "AI Accident + Number Plate Detection",
        frame
    )


    key = cv2.waitKey(
        1
    ) & 0xFF


    if key == ord("q"):

        print(
            "\n🛑 Detection stopped."
        )

        break


# ============================================================
# CLEANUP
# ============================================================

cap.release()

cv2.destroyAllWindows()


print("\n" + "=" * 70)
print("✅ AI DETECTION FINISHED")
print("=" * 70)