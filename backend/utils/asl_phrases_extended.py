"""
Extended ASL Phrase Database - Additional 50 Phrases
Adds work, school, medical, travel, and social conversation phrases
"""

# Extended phrases to add to ASL_PHRASES dictionary
EXTENDED_ASL_PHRASES = {
    # ===== WORK & SCHOOL =====
    'what_is_your_job': {
        'patterns': [
            'quel est votre travail',
            'que faites vous comme travail',
            'what is your job',
            'what do you do',
            'ما هو عملك'
        ],
        'asl_sequence': ['YOUR', 'WORK', 'WHAT'],
        'grammar': 'wh_question',
        'confidence': 1.0
    },
    
    'i_am_a_student': {
        'patterns': [
            'je suis étudiant',
            'je suis étudiante',
            'i am a student',
            'i\'m a student',
            'أنا طالب'
        ],
        'asl_sequence': ['I', 'STUDENT'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    'i_work_at': {
        'patterns': [
            'je travaille à',
            'je travaille chez',
            'i work at',
            'أعمل في'
        ],
        'asl_sequence': ['I', 'WORK'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    'i_am_learning': {
        'patterns': [
            'j apprends',
            'je suis en train d apprendre',
            'i am learning',
            'i\'m learning',
            'أتعلم'
        ],
        'asl_sequence': ['I', 'LEARN'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    # ===== MEDICAL =====
    'i_have_a_headache': {
        'patterns': [
            'j ai mal à la tête',
            'i have a headache',
            'عندي صداع'
        ],
        'asl_sequence': ['HEAD', 'HURT', 'I'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    'i_feel_dizzy': {
        'patterns': [
            'j ai des vertiges',
            'je me sens étourdi',
            'i feel dizzy',
            'أشعر بالدوار'
        ],
        'asl_sequence': ['I', 'DIZZY'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    'i_need_medicine': {
        'patterns': [
            'j ai besoin de médicaments',
            'i need medicine',
            'أحتاج دواء'
        ],
        'asl_sequence': ['MEDICINE', 'NEED', 'I'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    'where_is_the_hospital': {
        'patterns': [
            'où est l hôpital',
            'where is the hospital',
            'أين المستشفى'
        ],
        'asl_sequence': ['HOSPITAL', 'WHERE'],
        'grammar': 'wh_question',
        'confidence': 1.0
    },
    
    # ===== TRAVEL =====
    'where_is_the_airport': {
        'patterns': [
            'où est l aéroport',
            'where is the airport',
            'أين المطار'
        ],
        'asl_sequence': ['AIRPORT', 'WHERE'],
        'grammar': 'wh_question',
        'confidence': 1.0
    },
    
    'i_am_lost': {
        'patterns': [
            'je suis perdu',
            'je suis perdue',
            'i am lost',
            'i\'m lost',
            'أنا ضائع'
        ],
        'asl_sequence': ['I', 'LOST'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    'how_do_i_get_to': {
        'patterns': [
            'comment aller à',
            'comment je vais à',
            'how do i get to',
            'كيف أصل إلى'
        ],
        'asl_sequence': ['HOW', 'GO'],
        'grammar': 'wh_question',
        'confidence': 1.0
    },
    
    'i_need_a_taxi': {
        'patterns': [
            'j ai besoin d un taxi',
            'i need a taxi',
            'أحتاج تاكسي'
        ],
        'asl_sequence': ['TAXI', 'NEED', 'I'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    # ===== FOOD & DINING =====
    'i_am_thirsty': {
        'patterns': [
            'j ai soif',
            'i am thirsty',
            'i\'m thirsty',
            'أنا عطشان'
        ],
        'asl_sequence': ['I', 'THIRSTY'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    'i_am_vegetarian': {
        'patterns': [
            'je suis végétarien',
            'je suis végétarienne',
            'i am vegetarian',
            'i\'m vegetarian',
            'أنا نباتي'
        ],
        'asl_sequence': ['I', 'VEGETARIAN'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    'the_bill_please': {
        'patterns': [
            'l addition s il vous plaît',
            'l addition svp',
            'the bill please',
            'check please',
            'الحساب من فضلك'
        ],
        'asl_sequence': ['BILL', 'PLEASE'],
        'grammar': 'polite',
        'confidence': 1.0
    },
    
    'this_is_delicious': {
        'patterns': [
            'c est délicieux',
            'this is delicious',
            'هذا لذيذ'
        ],
        'asl_sequence': ['THIS', 'DELICIOUS'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    # ===== SOCIAL =====
    'how_was_your_day': {
        'patterns': [
            'comment s est passée ta journée',
            'comment était ta journée',
            'how was your day',
            'كيف كان يومك'
        ],
        'asl_sequence': ['YOUR', 'DAY', 'HOW'],
        'grammar': 'wh_question',
        'confidence': 1.0
    },
    
    'i_miss_you': {
        'patterns': [
            'tu me manques',
            'vous me manquez',
            'i miss you',
            'أفتقدك'
        ],
        'asl_sequence': ['I', 'MISS', 'YOU'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    'congratulations': {
        'patterns': [
            'félicitations',
            'congratulations',
            'congrats',
            'مبروك'
        ],
        'asl_sequence': ['CONGRATULATIONS'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    'happy_birthday': {
        'patterns': [
            'joyeux anniversaire',
            'bon anniversaire',
            'happy birthday',
            'عيد ميلاد سعيد'
        ],
        'asl_sequence': ['HAPPY', 'BIRTHDAY'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    'good_luck': {
        'patterns': [
            'bonne chance',
            'good luck',
            'حظ سعيد'
        ],
        'asl_sequence': ['GOOD', 'LUCK'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    # ===== WEATHER =====
    'how_is_the_weather': {
        'patterns': [
            'quel temps fait il',
            'comment est le temps',
            'how is the weather',
            'what\'s the weather like',
            'كيف الطقس'
        ],
        'asl_sequence': ['WEATHER', 'HOW'],
        'grammar': 'wh_question',
        'confidence': 1.0
    },
    
    'it_is_hot': {
        'patterns': [
            'il fait chaud',
            'it is hot',
            'it\'s hot',
            'الجو حار'
        ],
        'asl_sequence': ['HOT'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    'it_is_cold': {
        'patterns': [
            'il fait froid',
            'it is cold',
            'it\'s cold',
            'الجو بارد'
        ],
        'asl_sequence': ['COLD'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    'it_is_raining': {
        'patterns': [
            'il pleut',
            'it is raining',
            'it\'s raining',
            'تمطر'
        ],
        'asl_sequence': ['RAIN'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    # ===== NUMBERS & COUNTING =====
    'how_many': {
        'patterns': [
            'combien',
            'how many',
            'كم عدد'
        ],
        'asl_sequence': ['HOW_MANY'],
        'grammar': 'wh_question',
        'confidence': 1.0
    },
    
    'too_expensive': {
        'patterns': [
            'trop cher',
            'c est trop cher',
            'too expensive',
            'غالي جدا'
        ],
        'asl_sequence': ['EXPENSIVE', 'TOO_MUCH'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    # ===== ABILITIES =====
    'i_can': {
        'patterns': [
            'je peux',
            'i can',
            'أستطيع'
        ],
        'asl_sequence': ['I', 'CAN'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    'i_cannot': {
        'patterns': [
            'je ne peux pas',
            'i cannot',
            'i can\'t',
            'لا أستطيع'
        ],
        'asl_sequence': ['CAN\'T', 'I'],
        'grammar': 'negation',
        'non_manual': 'headshake',
        'confidence': 1.0
    },
    
    # ===== PREFERENCES =====
    'i_like': {
        'patterns': [
            'j aime',
            'i like',
            'أحب'
        ],
        'asl_sequence': ['I', 'LIKE'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    'i_dont_like': {
        'patterns': [
            'je n aime pas',
            'i don\'t like',
            'i do not like',
            'لا أحب'
        ],
        'asl_sequence': ['LIKE', 'NOT', 'I'],
        'grammar': 'negation',
        'non_manual': 'headshake',
        'confidence': 1.0
    },
    
    'i_love': {
        'patterns': [
            'j adore',
            'i love',
            'أعشق'
        ],
        'asl_sequence': ['I', 'LOVE'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    # ===== AGREEMENT =====
    'i_agree': {
        'patterns': [
            'je suis d accord',
            'd accord',
            'i agree',
            'أوافق'
        ],
        'asl_sequence': ['I', 'AGREE'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    'i_disagree': {
        'patterns': [
            'je ne suis pas d accord',
            'i disagree',
            'لا أوافق'
        ],
        'asl_sequence': ['DISAGREE', 'I'],
        'grammar': 'negation',
        'confidence': 1.0
    },
    
    # ===== REQUESTS =====
    'can_you_help_me': {
        'patterns': [
            'pouvez vous m aider',
            'peux tu m aider',
            'can you help me',
            'هل يمكنك مساعدتي'
        ],
        'asl_sequence': ['YOU', 'HELP', 'ME', 'CAN'],
        'grammar': 'yes_no_question',
        'confidence': 1.0
    },
    
    'please_wait': {
        'patterns': [
            'attendez s il vous plaît',
            'attends',
            'please wait',
            'wait please',
            'انتظر من فضلك'
        ],
        'asl_sequence': ['WAIT', 'PLEASE'],
        'grammar': 'command',
        'confidence': 1.0
    },
    
    'come_here': {
        'patterns': [
            'venez ici',
            'viens ici',
            'come here',
            'تعال هنا'
        ],
        'asl_sequence': ['COME', 'HERE'],
        'grammar': 'command',
        'confidence': 1.0
    },
    
    'go_away': {
        'patterns': [
            'allez vous en',
            'va t en',
            'go away',
            'اذهب بعيدا'
        ],
        'asl_sequence': ['GO', 'AWAY'],
        'grammar': 'command',
        'confidence': 1.0
    },
    
    # ===== COMMON EXPRESSIONS =====
    'of_course': {
        'patterns': [
            'bien sûr',
            'of course',
            'بالطبع'
        ],
        'asl_sequence': ['OF_COURSE'],
        'alternative': ['YES', 'SURE'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    'no_problem': {
        'patterns': [
            'pas de problème',
            'no problem',
            'لا مشكلة'
        ],
        'asl_sequence': ['NO', 'PROBLEM'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    'i_think_so': {
        'patterns': [
            'je pense que oui',
            'je crois que oui',
            'i think so',
            'أعتقد ذلك'
        ],
        'asl_sequence': ['I', 'THINK', 'YES'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    'i_dont_think_so': {
        'patterns': [
            'je ne pense pas',
            'je ne crois pas',
            'i don\'t think so',
            'لا أعتقد ذلك'
        ],
        'asl_sequence': ['THINK', 'NOT', 'I'],
        'grammar': 'negation',
        'non_manual': 'headshake',
        'confidence': 1.0
    },
    
    # ===== FAMILY (Extended) =====
    'this_is_my_family': {
        'patterns': [
            'c est ma famille',
            'voici ma famille',
            'this is my family',
            'هذه عائلتي'
        ],
        'asl_sequence': ['MY', 'FAMILY', 'THIS'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    'i_have_children': {
        'patterns': [
            'j ai des enfants',
            'i have children',
            'لدي أطفال'
        ],
        'asl_sequence': ['I', 'HAVE', 'CHILDREN'],
        'grammar': 'statement',
        'confidence': 1.0
    },
    
    # ===== TECHNOLOGY =====
    'do_you_have_wifi': {
        'patterns': [
            'avez vous le wifi',
            'as tu le wifi',
            'do you have wifi',
            'هل لديك واي فاي'
        ],
        'asl_sequence': ['YOU', 'HAVE', 'WIFI'],
        'grammar': 'yes_no_question',
        'confidence': 1.0
    },
    
    'what_is_the_password': {
        'patterns': [
            'quel est le mot de passe',
            'what is the password',
            'what\'s the password',
            'ما هي كلمة السر'
        ],
        'asl_sequence': ['PASSWORD', 'WHAT'],
        'grammar': 'wh_question',
        'confidence': 1.0
    },
    
    # ===== EMERGENCY (Extended) =====
    'help_me': {
        'patterns': [
            'aidez moi',
            'aide moi',
            'help me',
            'ساعدني'
        ],
        'asl_sequence': ['HELP', 'ME'],
        'grammar': 'command',
        'confidence': 1.0
    },
    
    'call_an_ambulance': {
        'patterns': [
            'appelez une ambulance',
            'call an ambulance',
            'اتصل بالإسعاف'
        ],
        'asl_sequence': ['AMBULANCE', 'CALL'],
        'grammar': 'command',
        'confidence': 1.0
    }
}


# Function to merge extended phrases into main database
def add_extended_phrases():
    """Add extended phrases to the main ASL_PHRASES dictionary"""
    from backend.utils.asl_phrases import ASL_PHRASES
    ASL_PHRASES.update(EXTENDED_ASL_PHRASES)
    return len(ASL_PHRASES)
