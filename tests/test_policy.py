from policy import route


def receipt(choice='pricing', confidence=0.9, unclear=0.0, **extra):
    probabilities = {'meeting': 0.0, 'pricing': 0.0, 'info': 0.0, 'unclear': unclear}
    intent = {'choice': choice, 'confidence': confidence, 'probabilities': probabilities}
    return {'intent': intent, **extra}


def test_unclear_choice_is_skipped():
    assert route(receipt('unclear', 0.95, unclear=0.95)) == 'skip'


def test_a_real_chance_of_nothing_to_answer_is_skipped():
    assert route(receipt('info', 0.41, unclear=0.43)) == 'skip'


def test_split_between_two_real_intents_gets_drafted():
    assert route(receipt('pricing', 0.49)) == 'draft'


def test_split_intent_goes_to_the_ae_after_drafting():
    assert route(receipt('pricing', 0.49, promises=0.1)) == 'approve'


def test_confident_clean_draft_is_sent():
    assert route(receipt(promises=0.1)) == 'send'


def test_draft_that_promises_something_needs_approval():
    assert route(receipt(promises=0.7)) == 'approve'


def test_stricter_threshold_moves_a_send_to_approval():
    assert route(receipt(confidence=0.85, promises=0.1), sure_enough=0.9) == 'approve'
