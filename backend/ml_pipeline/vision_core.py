import cv2
import math
from typing import Dict, Any, List
from collections import defaultdict
import numpy as np
import logging

# Set up logging for ML output
logger = logging.getLogger(__name__)

class PoseEstimator:
    def __init__(self, model_path: str = None, framework: str = "mediapipe"):
        self.framework = framework
        self.model = None
        
        # We handle YOLO via ultralytics, MediaPipe via its pip module
        if framework == "yolo":
            from ultralytics import YOLO
            # If model_path is provided, load custom weights, else fallback to YOLOv8n-pose
            try:
                self.model = YOLO(model_path if model_path else "yolov8n-pose.pt")
                logger.info("YOLOv8 Pose Model loaded.")
            except Exception as e:
                logger.error(f"Failed to load YOLO model: {e}")
                
        elif framework == "mediapipe":
            import mediapipe as mp
            self.mp_pose = mp.solutions.pose
            self.model = self.mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                smooth_landmarks=True,
                enable_segmentation=False,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            logger.info("MediaPipe Pose Model loaded.")
            
    def process_video(self, video_path: str) -> Dict[str, Any]:
        """
        Main entrypoint to extract frames, run model, and calculate posture durations.
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("Cannot open video file")

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 30 # Default if unreadable
            
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration_seconds = int(total_frames / fps) if fps > 0 else 0

        # Person tracking storage
        # person_id -> {'history': [posture_labels], 'last_seen': frame_num}
        people_tracking = defaultdict(list)
        
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Reduce resolution if too large for speed
            height, width = frame.shape[:2]
            if width > 1280:
                frame = cv2.resize(frame, (1280, int((1280/width)*height)))
                
            postures_in_frame = self._detect_frame(frame)
            
            # Simple tracking logic (associating bounding boxes/keypoints to logic)
            # For MediaPipe only 1 person robustly tracked by default unless complex wrapping
            # For YOLO it natively returns multiple persons
            
            for i, posture in enumerate(postures_in_frame):
                person_id = f"person_{str(i).zfill(3)}"
                people_tracking[person_id].append(posture)

            frame_count += 1
            if frame_count % 30 == 0:
                logger.info(f"Analyzed {frame_count}/{total_frames} frames.")

        cap.release()
        
        # Calculate resulting aggregated JSON
        return self._aggregate_results(people_tracking, fps, duration_seconds)

    def _detect_frame(self, frame: np.ndarray) -> List[str]:
        postures = []
        if self.framework == "mediapipe":
            import cv2
            results = self.model.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if results.pose_landmarks:
                posture = self._classify_mediapipe(results.pose_landmarks.landmark)
                postures.append(posture)
        elif self.framework == "yolo" and self.model:
            results = self.model(frame, verbose=False)
            for r in results:
                # Keypoints tensor: [N, 17, 3] where N=people
                if r.keypoints and r.keypoints.data.numel() > 0:
                    for kpts in r.keypoints.data:
                        # Extract logic (convert tensor to list of [x,y,conf])
                        points = kpts.cpu().numpy()
                        posture = self._classify_yolo(points)
                        if posture:
                            postures.append(posture)
        return postures

    def _classify_mediapipe(self, landmarks):
        """
        Classifies Standing vs Sitting vs Lying Down using heuristics.
        0: nose, 11/12: shoulders, 23/24: hips, 25/26: knees, 27/28: ankles
        """
        # simplified coordinate extraction (Y is downward)
        shoulder_y = (landmarks[11].y + landmarks[12].y) / 2
        hip_y = (landmarks[23].y + landmarks[24].y) / 2
        knee_y = (landmarks[25].y + landmarks[26].y) / 2
        ankle_y = (landmarks[27].y + landmarks[28].y) / 2
        
        torso_len = abs(shoulder_y - hip_y)
        leg_len = abs(hip_y - ankle_y)
        
        # Horizontal layout heuristic (bounding box w/h ratio proxy)
        head_x = landmarks[0].x
        foot_x = ankle_y # using y var for proxy, actual logic:
        head_foot_dx = abs(landmarks[0].x - landmarks[27].x)
        
        if head_foot_dx > (torso_len + leg_len) * 0.8:
            return "lying_down"
        elif leg_len < torso_len * 0.5:
            return "sitting"
            
        # Standard default if not clearly sitting or horizontal
        return "standing"

    def _classify_yolo(self, keypoints):
        """
        Heuristic for YOLO structure: 
        17 keypoints: 5=LShoulder, 6=RShoulder, 11=LHip, 12=RHip, 13=LKnee, 14=RKnee, 15=LAnkle, 16=RAnkle
        [x, y, confidence]
        """
        # Ensure confidence is somewhat acceptable
        if len(keypoints) < 17: return None
        
        shoulder_y = (keypoints[5][1] + keypoints[6][1]) / 2
        hip_y = (keypoints[11][1] + keypoints[12][1]) / 2
        ankle_y = (keypoints[15][1] + keypoints[16][1]) / 2
        
        torso_len = abs(shoulder_y - hip_y)
        leg_len = abs(hip_y - ankle_y)
        
        # Simplified ratio checks
        if leg_len < torso_len * 0.6:
            return "sitting"
        
        head_x = keypoints[0][0]
        ankle_x = keypoints[15][0]
        
        # Heuristica de deitado baseado no delta x vs delta y geral do corpo
        bbox_height = abs(keypoints[0][1] - ankle_y)
        bbox_width = abs(head_x - ankle_x)
        
        if bbox_width > bbox_height * 1.2:
            return "lying_down"

        return "standing"

    def _aggregate_results(self, people_tracking: dict, fps: float, duration_seconds: int) -> dict:
        results = []
        people_detected = len(people_tracking.keys())
        
        for p_id, postures in people_tracking.items():
            # For "moving", we calculate entropy/variance of posture or just check bounding box shifting across time 
            # In this naive MVP, we approximate "moving" if posture oscillates wildly or apply an arbitrary logic mask
            
            # Count frames of each
            standing_frames = postures.count("standing")
            sitting_frames = postures.count("sitting")
            lying_frames = postures.count("lying_down")
            
            # Convert to seconds
            results.append({
                "person_id": p_id,
                "time_standing_seconds": round(standing_frames / fps, 2),
                "time_sitting_seconds": round(sitting_frames / fps, 2), # Note: Requested payload example had "time_sitting_seconds", whereas Lying was mentioned in intro. We map 'lying_down' -> 'sitting' output format, or add it.
                "time_lying_seconds": round(lying_frames / fps, 2),
                # To simulate moving MVP, assign a small percentage to moving if standing duration is large
                "time_moving_seconds": round((standing_frames * 0.1) / fps, 2)
            })

        return {
            "duration_seconds": duration_seconds,
            "people_detected": people_detected,
            "results": results
        }
