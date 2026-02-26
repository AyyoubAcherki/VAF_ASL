
import sys
import os
sys.path.insert(0, os.getcwd())

from backend.utils.predict_video import predict_text_to_asl

def debug_prediction(text):
    print(f"\n🔍 Testing: {text}")
    try:
        res = predict_text_to_asl(text)
        print(f"  Type: {res.get('type')}")
        print(f"  Signs: {' '.join(res.get('asl_sequence', []))}")
        print(f"  Grammar: {res.get('grammar_type')}")
        if 'matched_pattern' in res:
            print(f"  Pattern: {res['matched_pattern']}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

if __name__ == '__main__':
    debug_prediction('Je ne sais pas')
    debug_prediction('Comment allez-vous?')
    debug_prediction('Où vas-tu?')
    debug_prediction('Thank you')
