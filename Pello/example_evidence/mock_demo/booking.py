"""Correct demo appointment engine, NOT a production Google Calendar integration."""
from threading import RLock

class ClinicBooking:
    def __init__(self):
        self._lock = RLock()
        self._by_request = {}
        self._by_slot = {}

    def reserve(self, slot, customer_id, request_id, confirmed):
        if not all(isinstance(x, str) and x.strip() for x in (slot, customer_id, request_id)):
            raise ValueError("Missing booking field")
        with self._lock:
            if request_id in self._by_request:
                previous = self._by_request[request_id]
                if previous["slot"] != slot or previous["customer_id"] != customer_id:
                    raise ValueError("Request key collision")
                return previous.copy()
            if not confirmed:
                raise ValueError("Booking requires confirmation")
            if slot in self._by_slot:
                raise ValueError("Slot already reserved")
            booking = {"slot": slot, "customer_id": customer_id, "request_id": request_id}
            self._by_request[request_id] = booking
            self._by_slot[slot] = request_id
            return booking.copy()

    def cancel(self, request_id):
        with self._lock:
            booking = self._by_request.pop(request_id, None)
            if booking is None:
                return False
            self._by_slot.pop(booking["slot"], None)
            return True

    def slots(self, candidates):
        with self._lock:
            return [slot for slot in candidates if slot not in self._by_slot]
