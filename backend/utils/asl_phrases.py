"""
ASL Phrase Database
Contains common phrases and their ASL sign sequences with grammar rules
"""

# Common ASL phrase patterns with multi-language support
ASL_PHRASES = {
    # ===== GREETINGS =====
    'how_are_you': {
        'patterns': [
            'comment allez vous',
            'comment vas tu',
            'comment ça va',
            'how are you',
            'how do you do',
            'كيف حالك',
            'كيف الحال'
        ],
        'asl_sequence': ['HOW_ARE_YOU'],
        'alternative': ['YOU', 'HOW'],
        'grammar': 'question',
        'confidence': 1.0
    },
    
    'nice_to_meet_you': {
        'patterns': [
            'enchanté',
            'ravi de vous rencontrer',
            'nice to meet you',
            'pleased to meet you',
            'تشرفنا',
            'سعيد بلقائك'
        ],
        'asl_sequence': ['NICE', 'MEET', 'YOU'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    'good_morning': {
        'patterns': [
            'bonjour',
            'bon matin',
            'good morning',
            'صباح الخير'
        ],
        'asl_sequence': ['GOOD_MORNING'],
        'grammar': 'greeting',
        'confidence': 1.0
    },
    
    'good_night': {
        'patterns': [
            'bonne nuit',
            'good night',
            'مساء الخير',
            'تصبح على خير'
        ],
        'asl_sequence': ['GOOD_NIGHT'],
        'grammar': 'greeting',
        'confidence': 1.0
    },
    
    # ===== QUESTIONS =====
    'what_is_your_name': {
        'patterns': [
            'comment vous appelez vous',
            'comment tu t appelles',
            'quel est votre nom',
            'what is your name',
            'what\'s your name',
            'ما اسمك'
        ],
        'asl_sequence': ['YOUR', 'NAME', 'WHAT'],  # Question word last in ASL
        'grammar': 'wh_question',
        'confidence': 1.0
    },
    
    'where_are_you_from': {
        'patterns': [
            'd où venez vous',
            'd où viens tu',
            'where are you from',
            'من أين أنت'
        ],
        'asl_sequence': ['YOU', 'FROM', 'WHERE'],
        'grammar': 'wh_question',
        'confidence': 1.0
    },
    
    'how_old_are_you': {
        'patterns': [
            'quel âge avez vous',
            'quel âge as tu',
            'how old are you',
            'كم عمرك'
        ],
        'asl_sequence': ['YOUR', 'AGE', 'HOW_MANY'],
        'grammar': 'wh_question',
        'confidence': 1.0
    },
    
    'what_time_is_it': {
        'patterns': [
            'quelle heure est il',
            'what time is it',
            'كم الساعة'
        ],
        'asl_sequence': ['TIME', 'NOW', 'WHAT'],
        'grammar': 'wh_question',
        'confidence': 1.0
    },
    
    # ===== POLITE EXPRESSIONS =====
    'thank_you_very_much': {
        'patterns': [
            'merci beaucoup',
            'thank you very much',
            'thanks a lot',
            'شكرا جزيلا'
        ],
        'asl_sequence': ['THANK_YOU'],
        'alternative': ['THANKS', 'VERY_MUCH'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    'you_are_welcome': {
        'patterns': [
            'de rien',
            'je vous en prie',
            'you are welcome',
            'you\'re welcome',
            'العفو'
        ],
        'asl_sequence': ['WELCOME'],
        'alternative': ['YOU', 'WELCOME'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    'excuse_me': {
        'patterns': [
            'excusez moi',
            'excuse moi',
            'pardon',
            'excuse me',
            'عفوا',
            'المعذرة'
        ],
        'asl_sequence': ['EXCUSE_ME'],
        'grammar': 'polite',
        'confidence': 1.0
    },
    
    'i_am_sorry': {
        'patterns': [
            'je suis désolé',
            'désolé',
            'i am sorry',
            'i\'m sorry',
            'sorry',
            'آسف',
            'أنا آسف'
        ],
        'asl_sequence': ['SORRY'],
        'alternative': ['I', 'SORRY'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    # ===== BASIC NEEDS =====
    'i_need_help': {
        'patterns': [
            'j ai besoin d aide',
            'aidez moi',
            'i need help',
            'help me',
            'أحتاج مساعدة',
            'ساعدني'
        ],
        'asl_sequence': ['HELP', 'NEED', 'I'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    'i_dont_understand': {
        'patterns': [
            'je ne comprends pas',
            'i don\'t understand',
            'i do not understand',
            'لا أفهم'
        ],
        'asl_sequence': ['UNDERSTAND', 'NOT'],
        'grammar': 'negation',
        'non_manual': 'headshake',
        'confidence': 1.0
    },
    
    'can_you_repeat': {
        'patterns': [
            'pouvez vous répéter',
            'peux tu répéter',
            'can you repeat',
            'please repeat',
            'هل يمكنك الإعادة'
        ],
        'asl_sequence': ['REPEAT', 'PLEASE'],
        'alternative': ['YOU', 'REPEAT', 'CAN'],
        'grammar': 'question',
        'confidence': 1.0
    },
    
    'i_dont_know': {
        'patterns': [
            'je ne sais pas',
            'i don\'t know',
            'i do not know',
            'لا أعرف'
        ],
        'asl_sequence': ['KNOW', 'NOT'],
        'grammar': 'negation',
        'non_manual': 'headshake',
        'confidence': 1.0
    },
    
    # ===== TIME EXPRESSIONS =====
    'see_you_tomorrow': {
        'patterns': [
            'à demain',
            'see you tomorrow',
            'أراك غدا'
        ],
        'asl_sequence': ['TOMORROW', 'SEE', 'YOU'],  # Time first in ASL
        'grammar': 'time_first',
        'confidence': 1.0
    },
    
    'see_you_later': {
        'patterns': [
            'à plus tard',
            'à tout à l heure',
            'see you later',
            'أراك لاحقا'
        ],
        'asl_sequence': ['LATER', 'SEE', 'YOU'],
        'grammar': 'time_first',
        'confidence': 1.0
    },
    
    'what_time': {
        'patterns': [
            'à quelle heure',
            'what time',
            'في أي وقت'
        ],
        'asl_sequence': ['TIME', 'WHAT'],
        'grammar': 'wh_question',
        'confidence': 1.0
    },
    
    # ===== FEELINGS =====
    'i_am_happy': {
        'patterns': [
            'je suis heureux',
            'je suis heureuse',
            'i am happy',
            'i\'m happy',
            'أنا سعيد'
        ],
        'asl_sequence': ['I', 'HAPPY'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    'i_am_tired': {
        'patterns': [
            'je suis fatigué',
            'je suis fatiguée',
            'i am tired',
            'i\'m tired',
            'أنا متعب'
        ],
        'asl_sequence': ['I', 'TIRED'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    'i_am_hungry': {
        'patterns': [
            'j ai faim',
            'i am hungry',
            'i\'m hungry',
            'أنا جائع'
        ],
        'asl_sequence': ['I', 'HUNGRY'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    'i_am_sick': {
        'patterns': [
            'je suis malade',
            'i am sick',
            'i\'m sick',
            'أنا مريض'
        ],
        'asl_sequence': ['I', 'SICK'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    # ===== DIRECTIONS =====
    'where_is_the_bathroom': {
        'patterns': [
            'où sont les toilettes',
            'où est la salle de bain',
            'where is the bathroom',
            'where is the restroom',
            'أين الحمام'
        ],
        'asl_sequence': ['BATHROOM', 'WHERE'],
        'grammar': 'wh_question',
        'confidence': 1.0
    },
    
    'turn_left': {
        'patterns': [
            'tournez à gauche',
            'turn left',
            'انعطف يسارا'
        ],
        'asl_sequence': ['LEFT', 'TURN'],
        'grammar': 'command',
        'confidence': 1.0
    },
    
    'turn_right': {
        'patterns': [
            'tournez à droite',
            'turn right',
            'انعطف يمينا'
        ],
        'asl_sequence': ['RIGHT', 'TURN'],
        'grammar': 'command',
        'confidence': 1.0
    },
    
    # ===== SHOPPING =====
    'how_much': {
        'patterns': [
            'combien',
            'combien ça coûte',
            'how much',
            'how much does it cost',
            'كم الثمن',
            'بكم'
        ],
        'asl_sequence': ['COST', 'HOW_MUCH'],
        'grammar': 'wh_question',
        'confidence': 1.0
    },
    
    'i_want_this': {
        'patterns': [
            'je veux ça',
            'je veux ceci',
            'i want this',
            'أريد هذا'
        ],
        'asl_sequence': ['THIS', 'WANT', 'I'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    'do_you_have': {
        'patterns': [
            'avez vous',
            'as tu',
            'do you have',
            'هل لديك'
        ],
        'asl_sequence': ['YOU', 'HAVE', 'QUESTION'],
        'grammar': 'yes_no_question',
        'confidence': 1.0
    },
    
    # ===== COMMON RESPONSES =====
    'yes_please': {
        'patterns': [
            'oui s il vous plaît',
            'oui merci',
            'yes please',
            'نعم من فضلك'
        ],
        'asl_sequence': ['YES', 'PLEASE'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    'no_thank_you': {
        'patterns': [
            'non merci',
            'no thank you',
            'no thanks',
            'لا شكرا'
        ],
        'asl_sequence': ['NO', 'THANK_YOU'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    'maybe': {
        'patterns': [
            'peut être',
            'peut-être',
            'maybe',
            'perhaps',
            'ربما'
        ],
        'asl_sequence': ['MAYBE'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    # ===== INTRODUCTIONS =====
    'my_name_is': {
        'patterns': [
            'je m appelle',
            'mon nom est',
            'my name is',
            'اسمي'
        ],
        'asl_sequence': ['MY', 'NAME'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    'i_am_from': {
        'patterns': [
            'je viens de',
            'je suis de',
            'i am from',
            'i\'m from',
            'أنا من'
        ],
        'asl_sequence': ['I', 'FROM'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    # ===== EMERGENCY =====
    'call_the_police': {
        'patterns': [
            'appelez la police',
            'call the police',
            'اتصل بالشرطة'
        ],
        'asl_sequence': ['POLICE', 'CALL'],
        'grammar': 'command',
        'confidence': 1.0
    },
    
    'i_need_a_doctor': {
        'patterns': [
            'j ai besoin d un médecin',
            'i need a doctor',
            'أحتاج طبيب'
        ],
        'asl_sequence': ['DOCTOR', 'NEED', 'I'],
        'grammar': 'statement',
        'confidence': 1.0
    }
}


def get_phrase_match(text):
    """
    Find matching phrase pattern in database
    
    Args:
        text: Input text (normalized)
        
    Returns:
        tuple: (phrase_key, phrase_data) or (None, None)
    """
    import re
    
    # Normalize text
    text_normalized = text.lower().strip()
    text_normalized = re.sub(r'[^\w\s]', '', text_normalized)
    text_normalized = re.sub(r'\s+', ' ', text_normalized)
    
    # Check for exact matches
    for phrase_key, phrase_data in ASL_PHRASES.items():
        for pattern in phrase_data['patterns']:
            pattern_normalized = re.sub(r'[^\w\s]', '', pattern.lower())
            pattern_normalized = re.sub(r'\s+', ' ', pattern_normalized)
            
            if pattern_normalized == text_normalized:
                return (phrase_key, phrase_data)
            
            # Check if pattern is contained in text
            if pattern_normalized in text_normalized:
                return (phrase_key, phrase_data)
    
    return (None, None)


def get_all_phrases():
    """Get list of all phrase keys"""
    return list(ASL_PHRASES.keys())


def get_phrase_count():
    """Get total number of phrases in database"""
    return len(ASL_PHRASES)


# Merge extended phrases on module load
try:
    from .asl_phrases_extended import EXTENDED_ASL_PHRASES
    ASL_PHRASES.update(EXTENDED_ASL_PHRASES)
    print(f"✅ Loaded {len(ASL_PHRASES)} total ASL phrases (50 base + {len(EXTENDED_ASL_PHRASES)} extended)")
except ImportError:
    print(f"ℹ️  Using {len(ASL_PHRASES)} base ASL phrases")
