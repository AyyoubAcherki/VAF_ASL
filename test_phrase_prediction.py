"""
Test ASL Phrase Prediction
Validates phrase-level ASL prediction with grammar rules
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

# Import directly from backend.utils
try:
    from backend.utils.predict_video import predict_text_to_asl
    from backend.utils.asl_grammar import detect_sentence_type, apply_asl_grammar
    from backend.utils.asl_phrases import get_phrase_count, get_all_phrases, get_phrase_match
    print("✅ Successfully imported ASL modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Test phrases
TEST_PHRASES = [
    # French
    ("Comment allez-vous?", "HOW_ARE_YOU or YOU + HOW"),
    ("Merci beaucoup", "THANK_YOU"),
    ("Je ne comprends pas", "UNDERSTAND + NOT"),
    ("À demain", "TOMORROW + SEE + YOU"),
    ("Où sont les toilettes?", "BATHROOM + WHERE"),
    
    # English
    ("How are you?", "HOW_ARE_YOU or YOU + HOW"),
    ("Thank you very much", "THANK_YOU"),
    ("I don't understand", "UNDERSTAND + NOT"),
    ("See you tomorrow", "TOMORROW + SEE + YOU"),
    ("Where is the bathroom?", "BATHROOM + WHERE"),
    
    # Arabic
    ("كيف حالك", "HOW_ARE_YOU or YOU + HOW"),
    ("شكرا جزيلا", "THANK_YOU"),
    ("لا أفهم", "UNDERSTAND + NOT"),
    
    # Constructed phrases (not in database)
    ("Je vais à l'école demain", "TOMORROW + SCHOOL + I + GO"),
    ("I am happy today", "TODAY + I + HAPPY"),
]

def test_phrase_prediction():
    """Test phrase prediction with various inputs"""
    print("🧪 Testing ASL Phrase Prediction")
    print("=" * 70)
    
    success_count = 0
    total_count = len(TEST_PHRASES)
    
    for i, (text, expected) in enumerate(TEST_PHRASES, 1):
        print(f"\n[{i}/{total_count}] Testing: \"{text}\"")
        print(f"  Expected: {expected}")
        
        try:
            result = predict_text_to_asl(text, apply_grammar=True)
            
            if result:
                asl_seq = ' + '.join(result['asl_sequence'])
                print(f"  ✅ Result: {asl_seq}")
                print(f"  Type: {result['type']}")
                print(f"  Grammar: {result.get('grammar_type', 'none')}")
                print(f"  Confidence: {result.get('confidence', 0):.1%}")
                
                if result.get('non_manual'):
                    print(f"  Non-manual: {result['non_manual']}")
                
                success_count += 1
            else:
                print(f"  ❌ No result returned")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Successful: {success_count}/{total_count}")
    print(f"❌ Failed: {total_count - success_count}/{total_count}")
    
    if success_count == total_count:
        print("\n🎉 All tests passed!")
        return True
    else:
        print(f"\n⚠️  {total_count - success_count} tests failed")
        return False


def test_grammar_rules():
    """Test specific grammar rules"""
    print("\n\n🔧 Testing Grammar Rules")
    print("=" * 70)
    
    # Test sentence type detection
    tests = [
        ("Comment allez-vous?", "wh_question"),
        ("Avez-vous faim?", "yes_no_question"),
        ("Je ne sais pas", "negation"),
        ("Allez à l'école", "command"),
        ("Je suis heureux", "statement"),
    ]
    
    for text, expected_type in tests:
        detected = detect_sentence_type(text)
        status = "✅" if detected == expected_type else "❌"
        print(f"{status} \"{text}\" → {detected} (expected: {expected_type})")
    
    # Test grammar application
    print("\n🔄 Testing Grammar Application:")
    
    # Time-first rule
    words = ['I', 'GO', 'SCHOOL', 'TOMORROW']
    result = apply_asl_grammar(words, 'statement')
    print(f"  Time-first: {' '.join(words)} → {' '.join(result)}")
    
    # WH-question reordering
    words = ['WHERE', 'YOU', 'GO']
    result = apply_asl_grammar(words, 'wh_question')
    print(f"  WH-question: {' '.join(words)} → {' '.join(result)}")
    
    # Negation
    words = ['I', 'KNOW', 'NOT']
    result = apply_asl_grammar(words, 'negation')
    print(f"  Negation: {' '.join(words)} → {' '.join(result)}")


def test_phrase_database():
    """Test phrase database"""
    print("\n\n📚 Testing Phrase Database")
    print("=" * 70)
    
    total = get_phrase_count()
    print(f"Total phrases in database: {total}")
    
    # Test some matches
    test_texts = [
        "comment allez vous",
        "merci beaucoup",
        "je ne comprends pas",
        "how are you",
        "thank you",
    ]
    
    print("\nTesting phrase matching:")
    for text in test_texts:
        key, data = get_phrase_match(text)
        if data:
            print(f"  ✅ \"{text}\" → {' + '.join(data['asl_sequence'])}")
        else:
            print(f"  ❌ \"{text}\" → No match")


if __name__ == '__main__':
    print("🚀 ASL Phrase Prediction Test Suite\n")
    
    # Run all tests
    phrase_success = test_phrase_prediction()
    test_grammar_rules()
    test_phrase_database()
    
    # Exit code
    sys.exit(0 if phrase_success else 1)
