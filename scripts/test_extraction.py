"""
Test ASL Pose Extraction
Quick test script to validate pose extraction on sample videos
"""

import sys
from pathlib import Path

# Test videos
TEST_VIDEOS = [
    'train/21/21_801.mp4',
    'train/hello/hello_1.mp4',
    'train/thanks/thanks_1.mp4',
    'train/yes/yes_1.mp4',
    'train/no/no_1.mp4'
]

def test_extraction():
    """Test pose extraction on sample videos"""
    print("🧪 Testing ASL Pose Extraction")
    print("=" * 60)
    
    # Check if MediaPipe is installed
    try:
        import mediapipe as mp
        import cv2
        print("✅ MediaPipe and OpenCV installed")
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("\nPlease install:")
        print("  conda install -c conda-forge mediapipe opencv")
        return False
    
    # Import extraction module
    sys.path.insert(0, str(Path(__file__).parent))
    from extract_pose_from_video import process_single_video
    
    # Test each video
    results = []
    for video_path in TEST_VIDEOS:
        if not Path(video_path).exists():
            print(f"\n⚠️  Skipping {video_path} (not found)")
            continue
        
        result = process_single_video(
            video_path,
            output_dir='backend/animations/test',
            sign_name=Path(video_path).parent.name
        )
        
        results.append(result)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    successful = [r for r in results if r and r['success']]
    failed = [r for r in results if r and not r['success']]
    
    print(f"✅ Successful: {len(successful)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    
    if successful:
        print("\n✅ Successful extractions:")
        for r in successful:
            anim = r['animation']
            print(f"  - {r['sign']}: {anim['duration']:.1f}s, {len(anim['keyframes'])} keyframes")
    
    if failed:
        print("\n❌ Failed extractions:")
        for r in failed:
            print(f"  - {r['sign']}: {r.get('error', 'Unknown error')}")
    
    return len(successful) > 0


if __name__ == '__main__':
    success = test_extraction()
    sys.exit(0 if success else 1)
