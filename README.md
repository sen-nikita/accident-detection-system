# AI Road Accident Detection & Emergency Alert System

> **Project Status:** Working Prototype | Actively Under Development

An AI-powered road safety system that uses Computer Vision and YOLO-based object detection to monitor road traffic, detect potential vehicle collisions, capture accident evidence, and generate emergency alerts through a web-based monitoring dashboard.

---

## 📌 Project Overview

Road accidents require quick detection and response. This project explores how Artificial Intelligence and Computer Vision can assist in automated road safety monitoring.

The current prototype analyzes road traffic video, detects and tracks vehicles, identifies potential collisions, captures evidence, records incidents, and updates a web-based monitoring dashboard.

The system is being continuously improved with features such as improved accident detection, number plate recognition, and real-time CCTV/RTSP stream support.

---

## 🚧 Project Status

This project is currently a **working prototype** and is under active development.

### Implemented

- YOLO-based vehicle detection
- Vehicle tracking
- Potential collision detection
- Consecutive-frame collision confirmation
- Accident evidence capture
- Incident recording
- Web-based monitoring dashboard
- Emergency alert interface
- Experimental number plate OCR
- Accident monitoring map interface

### Currently Improving

- Accident detection accuracy
- Number plate recognition
- Real-time alert synchronization
- CCTV/RTSP stream support

> The project is being developed incrementally, with additional features and improvements planned.

---

## ✨ Key Features

### 🤖 AI-Based Vehicle Detection

The system uses YOLO-based computer vision to detect vehicles from road traffic footage.

Vehicles such as the following can be detected:

- Cars
- Trucks
- Buses
- Motorcycles

### 🎯 Vehicle Tracking

Detected vehicles are assigned tracking IDs, allowing the system to follow individual vehicles across multiple video frames.

### 💥 Potential Accident Detection

The prototype analyzes the relationship between detected vehicles to identify potential collisions.

The current detection logic considers:

- Distance between vehicles
- Bounding-box overlap
- IoU (Intersection over Union)
- Consecutive-frame confirmation

Using multiple conditions helps reduce false alerts caused by vehicles simply passing close to each other.

### 📸 Accident Evidence Capture

When a potential collision is confirmed, the system captures an evidence image and records the incident information.

### 🚨 Emergency Alert

When an incident is confirmed, the dashboard can:

1. Record the incident
2. Capture evidence
3. Update the incident list
4. Display an emergency alert
5. Update the monitoring dashboard

> **Note:** Emergency notification is currently a prototype/simulation and is not directly connected to real police, ambulance, or emergency-service APIs.

### 📊 Monitoring Dashboard

The web dashboard provides:

- AI detection status
- CCTV/video feed
- Accident count
- Alert count
- Recent incidents
- Incident information
- Accident monitoring map
- Emergency notifications

### 🔢 Number Plate Recognition

The project includes an experimental number plate recognition component using **EasyOCR**.

The feature is intended to assist in identifying vehicles involved in detected incidents.

Recognition accuracy depends on factors such as:

- Video quality
- Camera angle
- Lighting
- Vehicle distance
- Plate visibility
- Image resolution

If a number plate cannot be reliably read, the system does not generate an assumed plate number.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | AI processing and backend development |
| Flask | Web application backend |
| YOLO | Vehicle detection and tracking |
| OpenCV | Video processing |
| EasyOCR | Experimental number plate recognition |
| HTML | Dashboard structure |
| CSS | Dashboard styling |
| JavaScript | Frontend interaction |
| Leaflet.js | Interactive map |
| JSON | Incident data storage |
| Git & GitHub | Version control |

---

## 🧠 System Workflow

```text
Road Video / CCTV Feed
        ↓
YOLO Vehicle Detection
        ↓
Vehicle Tracking
        ↓
Vehicle Position Analysis
        ↓
Collision Detection
        ↓
Consecutive-Frame Confirmation
        ↓
Incident Confirmation
        ↓
Evidence Capture
        ↓
Incident Recording
        ↓
Dashboard Update
        ↓
Emergency Alert
---

## 🔮 Future Enhancements

- Real-time CCTV/RTSP stream integration
- Improved accident detection accuracy
- Dedicated accident detection model
- Accident severity classification
- Advanced number plate recognition (ANPR)
- GPS-based accident location tracking
- Real-time SMS/mobile emergency notifications
- Police and ambulance API integration
- Multi-camera monitoring
- Speed and traffic violation detection
- Accident analytics and heatmaps
- Mobile application
- Cloud deployment
- Edge AI support

