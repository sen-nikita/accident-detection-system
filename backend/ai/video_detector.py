from ultralytics import YOLO

# Load YOLO model
model = YOLO("yolo11n.pt")

# Test traffic video
video_url = "https://youtu.be/LNwODJXcvt4"

print("\n" + "=" * 50)
print("🚗 AI TRAFFIC VIDEO DETECTION")
print("=" * 50)
print("Starting video analysis...")

# Run YOLO tracking
results = model.track(
    source=video_url,
    stream=True,
    show=True,
    persist=True
)

frame_count = 0

for result in results:
    frame_count += 1

    vehicle_count = 0

    if result.boxes is not None:
        for box in result.boxes:
            class_id = int(box.cls[0])
            object_name = model.names[class_id]

            if object_name in ["car", "truck", "bus", "motorcycle"]:
                vehicle_count += 1

    print(
        f"Frame {frame_count} | "
        f"Vehicles detected: {vehicle_count}"
    )

print("\n✅ Video processing completed!")