#!/usr/bin/env python3
"""Read note intervals with separate key-release and CC64-release endpoints.

Diagnostic only: sustain duration does not establish acoustic audibility.
CC64 convention: https://midi.org/midi-1-0-control-change-messages
"""
from bisect import bisect_right
from collections import defaultdict, deque
import struct


def read_intervals(data):
    if data[:4] != b'MThd' or len(data) < 14:
        raise ValueError('Invalid MIDI header')
    length, = struct.unpack_from('>I', data, 4)
    form, tracks, division = struct.unpack_from('>HHH', data, 8)
    if length < 6 or form not in (0, 1) or not division or division & 0x8000:
        raise ValueError('Unsupported MIDI format/timing')
    position = 8 + length
    events, tempos = [], [(0, -1, 500000)]
    last_tick = 0
    for track in range(tracks):
        if data[position:position + 4] != b'MTrk':
            raise ValueError('Missing MIDI track')
        size, = struct.unpack_from('>I', data, position + 4)
        position += 8
        end = position + size
        if end > len(data):
            raise ValueError('Truncated MIDI track')
        tick, running, order = 0, None, 0

        def variable():
            nonlocal position
            value = 0
            for _ in range(4):
                if position >= end:
                    raise ValueError('Truncated MIDI variable-length value')
                byte = data[position]
                position += 1
                value = (value << 7) | (byte & 127)
                if byte < 128:
                    return value
            raise ValueError('Invalid MIDI variable-length value')

        while position < end:
            tick += variable()
            if position >= end:
                raise ValueError('Truncated MIDI event')
            status = data[position]
            if status >= 128:
                position += 1
                if status < 240:
                    running = status
            elif running is None:
                raise ValueError('Missing running status')
            else:
                status = running
            order += 1
            sequence = (track, order)
            if status == 255:
                if position >= end:
                    raise ValueError('Truncated meta event')
                kind = data[position]
                position += 1
                count = variable()
                if position + count > end:
                    raise ValueError('Truncated meta payload')
                if kind == 81 and count == 3:
                    tempo = int.from_bytes(data[position:position + count], 'big')
                    if not tempo:
                        raise ValueError('Invalid MIDI tempo')
                    tempos.append((tick, sequence, tempo))
                position += count
            elif status in (240, 247):
                count = variable()
                position += count
                if position > end:
                    raise ValueError('Truncated sysex')
            else:
                kind = status & 240
                if kind not in (128, 144, 160, 176, 192, 208, 224):
                    raise ValueError('Unsupported MIDI event')
                count = 1 if kind in (192, 208) else 2
                if position + count > end:
                    raise ValueError('Truncated channel event')
                payload = data[position:position + count]
                if any(value >= 128 for value in payload):
                    raise ValueError('Invalid MIDI data byte')
                position += count
                events.append((tick, sequence, status & 15, kind, payload[0], payload[1] if count == 2 else 0))
        last_tick = max(last_tick, tick)
    # Merge tracks before applying channel-local pedal state.
    pressed, released = defaultdict(deque), defaultdict(list)
    pedal = [False] * 16
    notes = []
    for tick, sequence, channel, kind, first, second in sorted(events):
        if kind == 144 and second:
            note = dict(channel=channel, midi=first, start_tick=tick, key_end_tick=None, end_tick=None)
            pressed[channel, first].append(note)
            notes.append(note)
        elif kind == 128 or kind == 144 and not second:
            queue = pressed[channel, first]
            if queue:
                note = queue.popleft()
                note['key_end_tick'] = tick
                if pedal[channel]:
                    released[channel].append(note)
                else:
                    note['end_tick'] = tick
        elif kind == 176 and first == 64:
            down = second >= 64
            if pedal[channel] and not down:
                for note in released[channel]:
                    note['end_tick'] = tick
                released[channel].clear()
            pedal[channel] = down
    # An open pedal at EOF cannot imply infinite duration.
    for note in notes:
        if note['key_end_tick'] is None:
            note['key_end_tick'] = last_tick
        if note['end_tick'] is None:
            note['end_tick'] = last_tick
    # Stable ordering at identical ticks; default tempo precedes file events.
    tempos = sorted(tempos, key=lambda event: (event[0], (-1, -1) if event[1] == -1 else event[1]))
    ticks, seconds, rates = [0], [0.0], [500000]
    for tick, _, tempo in tempos:
        elapsed = seconds[-1] + (tick - ticks[-1]) * rates[-1] / division / 1000000
        ticks.append(tick)
        seconds.append(elapsed)
        rates.append(tempo)

    def time(tick):
        index = bisect_right(ticks, tick) - 1
        return seconds[index] + (tick - ticks[index]) * rates[index] / division / 1000000

    return [dict(midi=n['midi'], channel=n['channel'], start=time(n['start_tick']),
                 key_end=time(n['key_end_tick']), end=time(n['end_tick'])) for n in notes
            if n['key_end_tick'] > n['start_tick']]
