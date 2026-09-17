from ultralytics import YOLO

# Load YOLO model
model = YOLO("yolo11n.pt")

print("\n" + "=" * 40)
print("🚗 AI VEHICLE DETECTION SYSTEM")
print("=" * 40)

# Run detection
results = model("https://ultralytics.com/images/bus.jpg")

# Display detected objects
for result in results:

    if result.boxes is None:
        print("No objects detected.")
        continue

    for box in result.boxes:

        class_id = int(box.cls[0])
        confidence = float(box.conf[0])

        object_name = model.names[class_id]

        print(
            f"Object: {object_name} | "
            f"Confidence: {confidence:.2%}"
        )

print("=" * 40)
print("✅ Detection completed!")