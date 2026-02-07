# Stores live transcript in memory during call
live_calls = {}


def add_line(call_id: str, speaker: str, text: str):
    if call_id not in live_calls:
        live_calls[call_id] = []

    live_calls[call_id].append(f"{speaker}: {text}")


def get_transcript(call_id: str):
    return "\n".join(live_calls.get(call_id, []))


def clear_call(call_id: str):
    if call_id in live_calls:
        del live_calls[call_id]
