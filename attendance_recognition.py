import face_recognition
import cv2
import os
import numpy as np

def load_known_faces(dataset_path="extracted_faces"):
    known_face_encodings = []
    known_face_names = []

    for person_name in os.listdir(dataset_path):
        person_folder = os.path.join(dataset_path, person_name)
        if not os.path.isdir(person_folder):
            continue

        for image_file in os.listdir(person_folder):
            image_path = os.path.join(person_folder, image_file)
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)

            if encodings:
                known_face_encodings.append(encodings[0])
                known_face_names.append(person_name)
                print(f"✅ Loaded: {person_name} - {image_file}")
            else:
                print(f"⚠️ No face found in {image_file}")

    return known_face_encodings, known_face_names
def process_video_and_mark_attendance(video_path, dataset_path="extracted_faces", skip_frames=5):
    known_encodings, known_names = load_known_faces(dataset_path)
    attendance = {name: "Absent" for name in known_names}
    cap = cv2.VideoCapture(video_path)
    frame_count = 0

    unknown_faces_dir = "static/unknown_faces"
    os.makedirs(unknown_faces_dir, exist_ok=True)
    unknown_index = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % skip_frames != 0:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
            name = "Unknown"
            if known_encodings:
                face_distances = face_recognition.face_distance(known_encodings, encoding)
                best_match_index = np.argmin(face_distances)
                if face_distances[best_match_index] < 0.4:
                    name = known_names[best_match_index]

            if name != "Unknown":
                attendance[name] = "Present"
            else:
                # Save frame for user input
                face_img = frame[top:bottom, left:right]
                img_path = os.path.join(unknown_faces_dir, f"unknown_{unknown_index}.jpg")
                cv2.imwrite(img_path, face_img)
                unknown_index += 1

    cap.release()
    return attendance
