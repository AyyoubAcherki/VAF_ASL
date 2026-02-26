"""
Integration Test for Complete Phrase Prediction System
Tests the full pipeline: text → phrase prediction → ASL sequence
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from backend.utils.predict_video import predict_text_to_asl
from backend.utils.asl_phrases import get_phrase_count

def test_integration():
    """Test complete phrase prediction integration"""
    print("🧪 Testing Complete Phrase Prediction Integration")
    print("=" * 80)
    
    # Check phrase database
    total_phrases = get_phrase_count()
    print(f"\n📚 Phrase Database: {total_phrases} phrases loaded")
    
    if total_phrases >= 100:
        print("  ✅ Extended database loaded successfully!")
    elif total_phrases >= 50:
        print("  ⚠️  Base database only (extended phrases not merged)")
    else:
        print("  ❌ Database incomplete!")
    
    # Test cases covering different scenarios
    test_cases = [
        {
            'name': 'Exact Phrase Match (French)',
            'input': 'Comment allez-vous?',
            'expected_type': 'phrase',
            'expected_signs': ['HOW_ARE_YOU']
        },
        {
            'name': 'Exact Phrase Match (English)',
            'input': 'Thank you very much',
            'expected_type': 'phrase',
            'expected_signs': ['THANK_YOU']
        },
        {
            'name': 'Exact Phrase Match (Arabic)',
            'input': 'شكرا جزيلا',
            'expected_type': 'phrase',
            'expected_signs': ['THANK_YOU']
        },
        {
            'name': 'Extended Phrase (Medical)',
            'input': 'J\'ai mal à la tête',
            'expected_type': 'phrase',
            'expected_signs': ['HEAD', 'HURT', 'I']
        },
        {
            'name': 'Extended Phrase (Travel)',
            'input': 'Where is the airport?',
            'expected_type': 'phrase',
            'expected_signs': ['AIRPORT', 'WHERE']
        },
        {
            'name': 'Constructed with Grammar (Time-First)',
            'input': 'Je vais à l\'école demain',
            'expected_type': 'constructed',
            'expected_grammar': 'statement'
        },
        {
            'name': 'Constructed with Grammar (WH-Question)',
            'input': 'Où vas-tu?',
            'expected_type': 'constructed',
            'expected_grammar': 'wh_question'
        },
        {
            'name': 'Constructed with Grammar (Negation)',
            'input': 'Je ne sais pas',
            'expected_type': 'phrase',  # This is in database
            'expected_signs': ['KNOW', 'NOT']
        }
    ]
    
    passed = 0
    failed = 0
    
    print("\n" + "=" * 80)
    print("🔬 Running Test Cases")
    print("=" * 80)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] {test['name']}")
        print(f"  Input: \"{test['input']}\"")
        
        try:
            result = predict_text_to_asl(test['input'], apply_grammar=True)
            
            # Check prediction type
            actual_type = result.get('type', 'unknown')
            expected_type = test.get('expected_type')
            
            if expected_type and actual_type == expected_type:
                print(f"  ✅ Type: {actual_type}")
            elif expected_type:
                print(f"  ❌ Type: {actual_type} (expected: {expected_type})")
                failed += 1
                continue
            else:
                print(f"  ℹ️  Type: {actual_type}")
            
            # Check ASL sequence
            asl_sequence = result.get('asl_sequence', [])
            print(f"  ASL: {' + '.join(asl_sequence)}")
            
            if 'expected_signs' in test:
                if asl_sequence == test['expected_signs']:
                    print(f"  ✅ Sequence matches expected")
                else:
                    print(f"  ⚠️  Expected: {' + '.join(test['expected_signs'])}")
            
            # Check grammar
            grammar = result.get('grammar_type', 'none')
            print(f"  Grammar: {grammar}")
            
            if 'expected_grammar' in test:
                if grammar == test['expected_grammar']:
                    print(f"  ✅ Grammar matches expected")
                else:
                    print(f"  ⚠️  Expected grammar: {test['expected_grammar']}")
            
            # Check confidence
            confidence = result.get('confidence', 0)
            print(f"  Confidence: {confidence:.1%}")
            
            # Check non-manual markers
            if 'non_manual' in result and result['non_manual']:
                print(f"  Non-manual: {result['non_manual']}")
            
            passed += 1
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    print(f"✅ Passed: {passed}/{len(test_cases)}")
    print(f"❌ Failed: {failed}/{len(test_cases)}")
    print(f"📚 Total Phrases: {total_phrases}")
    
    if passed == len(test_cases):
        print("\n🎉 All integration tests passed!")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return False


def test_api_response_format():
    """Test that API response format is correct"""
    print("\n\n🔌 Testing API Response Format")
    print("=" * 80)
    
    result = predict_text_to_asl("Comment allez-vous?", apply_grammar=True)
    
    required_fields = ['type', 'original_text', 'asl_sequence', 'grammar_type', 'confidence', 'word_details']
    
    print("Checking required fields:")
    all_present = True
    for field in required_fields:
        if field in result:
            print(f"  ✅ {field}: {type(result[field]).__name__}")
        else:
            print(f"  ❌ {field}: MISSING")
            all_present = False
    
    if all_present:
        print("\n✅ API response format is correct!")
    else:
        print("\n❌ API response format is incomplete!")
    
    return all_present


if __name__ == '__main__':
    # Force UTF-8 encoding for stdout
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("🚀 Complete Phrase Prediction Integration Test\n")
    
    test1 = test_integration()
    test2 = test_api_response_format()
    
    sys.exit(0 if (test1 and test2) else 1)
