"""
Batch Process ASL Training Videos
Processes all videos in the train directory and generates animation data
"""

import os
import sys
from pathlib import Path
import json
from extract_pose_from_video import ASLPoseExtractor, process_single_video

def batch_process_signs(train_dir='train', output_dir='backend/animations/keyframes', 
                        limit=None, categories=None):
    """
    Batch process all ASL sign videos
    
    Args:
        train_dir: Directory containing sign folders
        output_dir: Output directory for animation JSON files
        limit: Maximum number of signs to process (None = all)
        categories: List of specific sign names to process (None = all)
    """
    train_path = Path(train_dir)
    output_path = Path(output_dir)
    
    if not train_path.exists():
        print(f"❌ Training directory not found: {train_dir}")
        return
    
    # Get all sign folders
    sign_folders = sorted([d for d in train_path.iterdir() if d.is_dir()])
    
    # Filter by categories if specified
    if categories:
        sign_folders = [d for d in sign_folders if d.name in categories]
    
    # Limit if specified
    if limit:
        sign_folders = sign_folders[:limit]
    
    total = len(sign_folders)
    print(f"\n🎬 Batch Processing {total} ASL Signs")
    print(f"📂 Input: {train_dir}")
    print(f"📁 Output: {output_dir}")
    print("=" * 60)
    
    results = {
        'success': [],
        'failed': [],
        'no_videos': []
    }
    
    for idx, sign_folder in enumerate(sign_folders, 1):
        sign_name = sign_folder.name
        
        # Find video files
        videos = list(sign_folder.glob('*.mp4'))
        
        if not videos:
            print(f"\n[{idx}/{total}] ⚠️  {sign_name}: No videos found")
            results['no_videos'].append(sign_name)
            continue
        
        # Use first video as reference
        video_path = videos[0]
        
        print(f"\n[{idx}/{total}] Processing: {sign_name}")
        print(f"  📹 Video: {video_path.name} ({len(videos)} total)")
        
        # Process video
        result = process_single_video(video_path, output_dir, sign_name)
        
        if result and result['success']:
            results['success'].append({
                'sign': sign_name,
                'video': video_path.name,
                'duration': result['animation']['duration'],
                'keyframes': len(result['animation']['keyframes'])
            })
            print(f"  ✅ Success ({result['animation']['duration']:.1f}s, "
                  f"{len(result['animation']['keyframes'])} keyframes)")
        else:
            results['failed'].append({
                'sign': sign_name,
                'error': result.get('error', 'Unknown error') if result else 'Processing failed'
            })
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 BATCH PROCESSING SUMMARY")
    print("=" * 60)
    print(f"✅ Successful: {len(results['success'])}")
    print(f"❌ Failed: {len(results['failed'])}")
    print(f"⚠️  No videos: {len(results['no_videos'])}")
    print(f"📊 Total: {total}")
    
    if results['failed']:
        print("\n❌ Failed signs:")
        for item in results['failed'][:10]:  # Show first 10
            print(f"  - {item['sign']}: {item['error']}")
        if len(results['failed']) > 10:
            print(f"  ... and {len(results['failed']) - 10} more")
    
    # Save results
    results_file = output_path / 'batch_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Results saved to: {results_file}")
    
    # Generate combined JavaScript file
    if results['success']:
        generate_combined_js(results['success'], output_path)
    
    return results


def generate_combined_js(successful_signs, output_dir):
    """Generate a single JavaScript file with all animations"""
    output_dir = Path(output_dir)
    js_file = output_dir.parent / 'asl_animations.js'
    
    print(f"\n📝 Generating combined JavaScript file...")
    
    animations_code = []
    
    for item in successful_signs:
        sign_name = item['sign']
        json_file = output_dir / f"{sign_name}.json"
        
        if json_file.exists():
            with open(json_file, 'r') as f:
                animation_data = json.load(f)
            
            keyframes_json = json.dumps(animation_data['keyframes'], indent=12)
            
            js_code = f"""    '{sign_name.upper()}': {{
        duration: {animation_data['duration']},
        keyframes: {keyframes_json}
    }}"""
            
            animations_code.append(js_code)
    
    # Create complete JavaScript file
    full_js = f"""/**
 * ASL Animation Data - Auto-generated
 * Contains {len(animations_code)} ASL sign animations
 * Generated from training videos using MediaPipe pose extraction
 */

const ASL_ANIMATIONS = {{
{',\n'.join(animations_code)}
}};

// Export for use in avatar_3d.js
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = ASL_ANIMATIONS;
}}
"""
    
    with open(js_file, 'w') as f:
        f.write(full_js)
    
    print(f"  ✅ Generated: {js_file}")
    print(f"  📊 Contains {len(animations_code)} animations")
    
    return js_file


# Priority categories for phased processing
PRIORITY_CATEGORIES = {
    'phase1_numbers': [
        '21', '22', '23', '24', '25', '26', '27', '28', '29', '30',
        'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine',
        'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen',
        'sixteen', 'seventeen', 'eighteen', 'nineteen', 'twenty'
    ],
    'phase1_greetings': [
        'hello', 'hi', 'goodbye', 'thanks', 'please', 'sorry', 'welcome',
        'good_morning', 'good_afternoon', 'good_night', 'how_are_you',
        'nice_to_meet_you', 'see_you_later', 'bye'
    ],
    'phase1_actions': [
        'eat', 'drink', 'sleep', 'walk', 'run', 'sit', 'stand', 'help',
        'stop', 'go', 'come', 'give', 'take', 'want', 'need', 'like',
        'love', 'know', 'understand', 'think', 'learn', 'teach'
    ],
    'phase1_emotions': [
        'happy', 'sad', 'angry', 'excited', 'tired', 'sick', 'hurt',
        'afraid', 'nervous', 'confused', 'surprised'
    ]
}


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Batch process ASL training videos')
    parser.add_argument('--train-dir', default='train', help='Training directory')
    parser.add_argument('--output-dir', default='backend/animations/keyframes',
                       help='Output directory')
    parser.add_argument('--limit', type=int, help='Limit number of signs to process')
    parser.add_argument('--phase', choices=['1', '2', '3', 'all'], default='all',
                       help='Processing phase (1=priority, 2=extended, 3=remaining, all=everything)')
    parser.add_argument('--category', help='Specific category (e.g., phase1_numbers)')
    
    args = parser.parse_args()
    
    # Determine which signs to process
    categories = None
    if args.phase == '1':
        # Combine all phase 1 categories
        categories = []
        for cat_signs in PRIORITY_CATEGORIES.values():
            categories.extend(cat_signs)
        print(f"📋 Phase 1: Processing {len(categories)} priority signs")
    elif args.category and args.category in PRIORITY_CATEGORIES:
        categories = PRIORITY_CATEGORIES[args.category]
        print(f"📋 Category '{args.category}': Processing {len(categories)} signs")
    
    # Run batch processing
    results = batch_process_signs(
        train_dir=args.train_dir,
        output_dir=args.output_dir,
        limit=args.limit,
        categories=categories
    )
    
    # Exit code based on results
    if results and len(results['success']) > 0:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
