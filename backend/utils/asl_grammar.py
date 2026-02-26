"""
ASL Grammar Rules Engine
Applies ASL grammar rules to word sequences for proper sign order
"""

import re


# ASL grammar markers
TIME_WORDS = [
    'tomorrow', 'yesterday', 'today', 'now', 'later', 'soon', 'early', 'late',
    'morning', 'afternoon', 'evening', 'night', 'day', 'week', 'month', 'year',
    'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
    'demain', 'hier', 'aujourd hui', 'maintenant', 'plus tard', 'bientôt',
    'matin', 'après midi', 'soir', 'nuit', 'jour', 'semaine', 'mois', 'année',
    'lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche',
    'غدا', 'أمس', 'اليوم', 'الآن', 'لاحقا', 'قريبا',
    'صباح', 'ظهر', 'مساء', 'ليل', 'يوم', 'أسبوع', 'شهر', 'سنة'
]

WH_WORDS = [
    'what', 'where', 'when', 'who', 'why', 'how', 'which',
    'quoi', 'où', 'quand', 'qui', 'pourquoi', 'comment', 'quel', 'quelle',
    'ماذا', 'أين', 'متى', 'من', 'لماذا', 'كيف', 'أي'
]

NEGATION_WORDS = [
    'not', 'no', 'never', 'nothing', 'nobody', 'none',
    'pas', 'non', 'jamais', 'rien', 'personne', 'aucun',
    'لا', 'ليس', 'أبدا', 'لا شيء', 'لا أحد'
]


def detect_sentence_type(text):
    """
    Detect sentence type for grammar application
    
    Args:
        text: Input text
        
    Returns:
        str: Sentence type ('wh_question', 'yes_no_question', 'command', 'negation', 'statement')
    """
    text_lower = text.lower().strip()
    words = text_lower.split()
    
    # WH-questions
    for wh_word in WH_WORDS:
        if text_lower.startswith(wh_word) or wh_word in words[:3]:
            return 'wh_question'
    
    # Yes/no questions (ends with ? or starts with auxiliary verbs)
    if text.endswith('?'):
        return 'yes_no_question'
    
    question_starts = ['do', 'does', 'did', 'is', 'are', 'was', 'were', 'can', 'could', 
                       'will', 'would', 'should', 'have', 'has', 'had',
                       'est ce que', 'avez vous', 'as tu', 'peux tu', 'pouvez vous',
                       'هل']
    if any(text_lower.startswith(q) for q in question_starts):
        return 'yes_no_question'
    
    # Commands (imperative)
    command_starts = ['please', 'go', 'come', 'stop', 'wait', 'help', 'give', 'take',
                      's il vous plaît', 'allez', 'venez', 'arrêtez', 'attendez',
                      'من فضلك', 'اذهب', 'تعال', 'توقف']
    if any(text_lower.startswith(c) for c in command_starts):
        return 'command'
    
    # Negations
    if any(neg in words for neg in NEGATION_WORDS):
        return 'negation'
    
    return 'statement'


def apply_asl_grammar(words, sentence_type='statement'):
    """
    Apply ASL grammar rules to word sequence
    
    ASL Grammar Rules:
    1. Time-First: Time expressions come first
    2. Topic-Comment: Topic established before comment
    3. Question Words: WH-words often at end
    4. Negation: Negation marker with headshake
    
    Args:
        words: List of words (already translated to ASL vocabulary)
        sentence_type: Type of sentence
        
    Returns:
        list: Reordered words following ASL grammar
    """
    if not words:
        return words
    
    # Convert to lowercase for comparison
    words_lower = [w.lower() for w in words]
    
    # Rule 1: Time-First
    time_markers = []
    other_words = []
    
    for i, word in enumerate(words):
        if words_lower[i] in [t.lower() for t in TIME_WORDS]:
            time_markers.append(word)
        else:
            other_words.append(word)
    
    # Start with time markers
    result = time_markers + other_words
    
    # Rule 2: WH-Question Reordering (move WH-word to end)
    if sentence_type == 'wh_question':
        wh_markers = []
        other_words = []
        
        for i, word in enumerate(result):
            word_lower = word.lower()
            if word_lower in [w.lower() for w in WH_WORDS]:
                wh_markers.append(word)
            else:
                other_words.append(word)
        
        # Move WH-word to end
        if wh_markers:
            result = other_words + wh_markers
    
    # Rule 3: Negation (keep NOT at end or with verb)
    if sentence_type == 'negation':
        not_words = []
        other_words = []
        
        for word in result:
            if word.upper() in ['NOT', 'NEVER', 'NOTHING', 'NO']:
                not_words.append(word)
            else:
                other_words.append(word)
        
        # Put negation after main content
        if not_words:
            result = other_words + not_words
    
    return result


def apply_topic_comment(words, topic_indices=None):
    """
    Apply topic-comment structure (advanced)
    
    In ASL, the topic is established first, then commented on.
    Example: "My brother is sick" → [BROTHER] [MY] [SICK]
    
    Args:
        words: List of words
        topic_indices: Indices of words that form the topic (if known)
        
    Returns:
        list: Reordered words
    """
    # This is a simplified version
    # Full implementation would require NLP to identify topic/comment
    
    if topic_indices:
        topic = [words[i] for i in topic_indices]
        comment = [words[i] for i in range(len(words)) if i not in topic_indices]
        return topic + comment
    
    return words


def add_non_manual_markers(asl_sequence, sentence_type):
    """
    Add non-manual markers (facial expressions, head movements)
    
    Args:
        asl_sequence: List of ASL signs
        sentence_type: Type of sentence
        
    Returns:
        dict: ASL sequence with non-manual markers
    """
    markers = {
        'signs': asl_sequence,
        'non_manual': []
    }
    
    if sentence_type == 'yes_no_question':
        markers['non_manual'].append({
            'type': 'eyebrows_raised',
            'duration': 'full_sentence'
        })
    
    elif sentence_type == 'wh_question':
        markers['non_manual'].append({
            'type': 'eyebrows_furrowed',
            'duration': 'full_sentence'
        })
    
    elif sentence_type == 'negation':
        markers['non_manual'].append({
            'type': 'headshake',
            'duration': 'with_negation_sign'
        })
    
    elif sentence_type == 'command':
        markers['non_manual'].append({
            'type': 'direct_gaze',
            'duration': 'full_sentence'
        })
    
    return markers


def optimize_sign_sequence(asl_sequence):
    """
    Optimize ASL sequence by removing redundant signs
    
    Args:
        asl_sequence: List of ASL signs
        
    Returns:
        list: Optimized sequence
    """
    if not asl_sequence:
        return asl_sequence
    
    # Remove consecutive duplicates
    optimized = [asl_sequence[0]]
    for sign in asl_sequence[1:]:
        if sign != optimized[-1]:
            optimized.append(sign)
    
    # Remove filler words that don't translate to ASL
    fillers = ['THE', 'A', 'AN', 'IS', 'ARE', 'AM', 'WAS', 'WERE']
    optimized = [sign for sign in optimized if sign.upper() not in fillers]
    
    return optimized


def get_grammar_explanation(sentence_type):
    """
    Get explanation of grammar rules applied
    
    Args:
        sentence_type: Type of sentence
        
    Returns:
        str: Explanation of grammar rules
    """
    explanations = {
        'wh_question': 'ASL Grammar: Question word moved to end, eyebrows furrowed',
        'yes_no_question': 'ASL Grammar: Eyebrows raised for yes/no question',
        'negation': 'ASL Grammar: Negation sign at end with headshake',
        'command': 'ASL Grammar: Direct imperative with direct gaze',
        'statement': 'ASL Grammar: Standard topic-comment structure',
        'time_first': 'ASL Grammar: Time expression moved to beginning'
    }
    
    return explanations.get(sentence_type, 'ASL Grammar: Standard structure')
