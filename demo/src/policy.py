SURE_ENOUGH = 0.8
LIKELY_NOTHING = 0.3
LIKELY_PROMISE = 0.5


def route(receipt, sure_enough=SURE_ENOUGH):
    intent = receipt['intent']
    unclear = intent['probabilities']['unclear']
    if intent['choice'] == 'unclear' or unclear >= LIKELY_NOTHING:
        return 'skip'
    if 'promises' not in receipt:
        return 'draft'
    if intent['confidence'] < sure_enough or receipt['promises'] >= LIKELY_PROMISE:
        return 'approve'
    return 'send'
