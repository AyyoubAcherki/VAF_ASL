"""
ASL Pose Extraction from Training Videos
Extracts hand and body pose data from ASL training videos using MediaPipe
and converts them to avatar-compatible keyframe animations.
"""

import cv2
import mediapipe as mp
import mediapipe.solutions.holistic as mp_holistic
import json
import numpy as np
from pathlib import Path
import argparse
import sys

class ASLPoseExtractor:
    def __init__(self):
        self.mp_holistic = mp_holistic.Holistic
        self.holistic = self.mp_holistic(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            model_complexity=1
        )
        
    def extract_keyframes(self, video_path, sample_rate=5):
        """
        Extract pose keyframes from video
        
        Args:
            video_path: Path to video file
            sample_rate: Extract every Nth frame (default: 5)
            
        Returns:
            dict: Animation data with keyframes
        """
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        
        keyframes = []
        frame_idx = 0
        
        print(f"  Processing {frame_count} frames at {fps:.1f} fps...")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Sample frames at specified rate
            if frame_idx % sample_rate == 0:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.holistic.process(rgb_frame)
                
                keyframe = {
                    'time': frame_idx / fps if fps > 0 else 0,
                    'frame': frame_idx
                }
                
                # Extract right hand landmarks (primary hand for ASL)
                if results.right_hand_landmarks:
                    landmarks = results.right_hand_landmarks.landmark
                    keyframe['rightHand'] = {
                        'wrist': [landmarks[0].x, landmarks[0].y, landmarks[0].z],
                        'thumb_tip': [landmarks[4].x, landmarks[4].y, landmarks[4].z],
                        'index_tip': [landmarks[8].x, landmarks[8].y, landmarks[8].z],
                        'middle_tip': [landmarks[12].x, landmarks[12].y, landmarks[12].z],
                        'ring_tip': [landmarks[16].x, landmarks[16].y, landmarks[16].z],
                        'pinky_tip': [landmarks[20].x, landmarks[20].y, landmarks[20].z],
                        # Finger base joints for curl calculation
                        'thumb_base': [landmarks[2].x, landmarks[2].y, landmarks[2].z],
                        'index_base': [landmarks[5].x, landmarks[5].y, landmarks[5].z],
                        'middle_base': [landmarks[9].x, landmarks[9].y, landmarks[9].z],
                        'ring_base': [landmarks[13].x, landmarks[13].y, landmarks[13].z],
                        'pinky_base': [landmarks[17].x, landmarks[17].y, landmarks[17].z]
                    }
                
                # Extract left hand landmarks (for two-handed signs)
                if results.left_hand_landmarks:
                    landmarks = results.left_hand_landmarks.landmark
                    keyframe['leftHand'] = {
                        'wrist': [landmarks[0].x, landmarks[0].y, landmarks[0].z],
                        'thumb_tip': [landmarks[4].x, landmarks[4].y, landmarks[4].z],
                        'index_tip': [landmarks[8].x, landmarks[8].y, landmarks[8].z],
                        'middle_tip': [landmarks[12].x, landmarks[12].y, landmarks[12].z],
                        'ring_tip': [landmarks[16].x, landmarks[16].y, landmarks[16].z],
                        'pinky_tip': [landmarks[20].x, landmarks[20].y, landmarks[20].z]
                    }
                
                # Extract pose landmarks (shoulders, elbows for arm position)
                if results.pose_landmarks:
                    pose = results.pose_landmarks.landmark
                    keyframe['pose'] = {
                        'right_shoulder': [pose[12].x, pose[12].y, pose[12].z],
                        'right_elbow': [pose[14].x, pose[14].y, pose[14].z],
                        'left_shoulder': [pose[11].x, pose[11].y, pose[11].z],
                        'left_elbow': [pose[13].x, pose[13].y, pose[13].z]
                    }
                
                keyframes.append(keyframe)
            
            frame_idx += 1
        
        cap.release()
        
        print(f"  Extracted {len(keyframes)} keyframes")
        
        return {
            'duration': duration,
            'fps': fps,
            'total_frames': frame_count,
            'keyframes': keyframes
        }
    
    def calculate_finger_curl(self, hand_data):
        """
        Calculate finger curl values (0 = extended, 1 = closed)
        Based on distance between fingertip and base
        """
        if not hand_data:
            return {}
        
        fingers = {}
        finger_names = ['thumb', 'index', 'middle', 'ring', 'pinky']
        
        for finger in finger_names:
            tip = np.array(hand_data.get(f'{finger}_tip', [0, 0, 0]))
            base = np.array(hand_data.get(f'{finger}_base', [0, 0, 0]))
            wrist = np.array(hand_data.get('wrist', [0, 0, 0]))
            
            # Calculate distances
            tip_to_wrist = np.linalg.norm(tip - wrist)
            base_to_wrist = np.linalg.norm(base - wrist)
            
            # Curl ratio (closer to wrist = more curled)
            if base_to_wrist > 0:
                curl = 1.0 - (tip_to_wrist / base_to_wrist)
                curl = max(0.0, min(1.0, curl))  # Clamp to [0, 1]
            else:
                curl = 0.0
            
            fingers[finger] = round(curl, 2)
        
        return fingers
    
    def convert_to_avatar_format(self, pose_data, sign_name):
        """
        Convert MediaPipe pose data to avatar keyframe format
        
        Args:
            pose_data: Raw pose data from extract_keyframes
            sign_name: Name of the ASL sign
            
        Returns:
            dict: Avatar-compatible animation data
        """
        avatar_keyframes = []
        
        for kf in pose_data['keyframes']:
            avatar_kf = {
                'time': round(kf['time'], 3)
            }
            
            # Convert right hand position
            if 'rightHand' in kf:
                wrist = kf['rightHand']['wrist']
                
                # Map MediaPipe coordinates (0-1) to avatar space
                # MediaPipe: x=0 (left) to 1 (right), y=0 (top) to 1 (bottom)
                # Avatar: x=-0.5 to 0.5, y=0.8 to 1.8, z=0 to 0.5
                avatar_kf['rightHand'] = {
                    'pos': {
                        'x': round((wrist[0] - 0.5) * 0.8, 3),  # Center and scale
                        'y': round(1.8 - wrist[1] * 0.8, 3),    # Flip Y and scale to chest-head range
                        'z': round(wrist[2] * 0.5, 3)           # Depth
                    }
                }
                
                # Calculate finger curls
                fingers = self.calculate_finger_curl(kf['rightHand'])
                if fingers:
                    avatar_kf['fingers'] = {'right': fingers}
            
            # Convert arm rotation (if pose data available)
            if 'pose' in kf:
                shoulder = np.array(kf['pose']['right_shoulder'])
                elbow = np.array(kf['pose']['right_elbow'])
                
                # Calculate arm angle
                arm_vector = elbow - shoulder
                z_rot = np.arctan2(arm_vector[1], arm_vector[0])
                
                avatar_kf['rightArm'] = {
                    'rot': {
                        'z': round(z_rot, 3)
                    }
                }
            
            avatar_keyframes.append(avatar_kf)
        
        return {
            'name': sign_name.lower(),
            'duration': round(pose_data['duration'], 2),
            'keyframes': avatar_keyframes
        }
    
    def save_animation(self, animation_data, output_path):
        """Save animation data to JSON file"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(animation_data, f, indent=2)
        
        print(f"  ✓ Saved to {output_path}")
    
    def generate_javascript(self, animation_data, sign_name):
        """Generate JavaScript code for avatar_3d.js"""
        keyframes_json = json.dumps(animation_data['keyframes'], indent=16)
        
        js_code = f"""        '{sign_name.upper()}': {{
            duration: {animation_data['duration']},
            keyframes: {keyframes_json}
        }}"""
        
        return js_code


def process_single_video(video_path, output_dir, sign_name=None):
    """Process a single video file"""
    video_path = Path(video_path)
    
    if not video_path.exists():
        print(f"❌ Video not found: {video_path}")
        return None
    
    if sign_name is None:
        sign_name = video_path.parent.name
    
    print(f"\n📹 Processing: {sign_name}")
    print(f"  Video: {video_path.name}")
    
    try:
        extractor = ASLPoseExtractor()
        
        # Extract pose data
        pose_data = extractor.extract_keyframes(video_path)
        
        # Convert to avatar format
        animation_data = extractor.convert_to_avatar_format(pose_data, sign_name)
        
        # Save JSON
        output_path = Path(output_dir) / f"{sign_name}.json"
        extractor.save_animation(animation_data, output_path)
        
        # Generate JavaScript
        js_code = extractor.generate_javascript(animation_data, sign_name)
        
        return {
            'sign': sign_name,
            'animation': animation_data,
            'js_code': js_code,
            'success': True
        }
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'sign': sign_name,
            'success': False,
            'error': str(e)
        }


def main():
    parser = argparse.ArgumentParser(description='Extract ASL poses from training videos')
    parser.add_argument('video', help='Path to video file or directory')
    parser.add_argument('--output', '-o', default='backend/animations/keyframes',
                       help='Output directory for JSON files')
    parser.add_argument('--sign', '-s', help='Sign name (default: parent folder name)')
    
    args = parser.parse_args()
    
    result = process_single_video(args.video, args.output, args.sign)
    
    if result and result['success']:
        print(f"\n✅ Successfully processed: {result['sign']}")
        print(f"\nJavaScript code (add to avatar_3d.js):")
        print(result['js_code'])
    else:
        print(f"\n❌ Failed to process video")
        sys.exit(1)


if __name__ == '__main__':
    main()
