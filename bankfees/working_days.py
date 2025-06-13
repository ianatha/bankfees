#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import argparse

# --- Ορισμός επίσημων αργιών για το 2025 ---
HOLIDAYS_2025 = {
    datetime.date(2025, 1, 1):  "Πρωτοχρονιά",
    datetime.date(2025, 1, 6):  "Άγια Θεοφάνεια",
    datetime.date(2025, 3, 3):  "Καθαρά Δευτέρα",
    datetime.date(2025, 3, 25): "Επανάσταση του 1821",
    datetime.date(2025, 4, 18): "Μεγάλη Παρασκευή",
    datetime.date(2025, 4, 20): "Πάσχα",
    datetime.date(2025, 4, 21): "Δευτέρα του Πάσχα",
    datetime.date(2025, 5, 1):  "Εργατική Πρωτομαγιά",
    datetime.date(2025, 6, 8):  "Πεντηκοστή",
    datetime.date(2025, 6, 9):  "Αγίου Πνεύματος",
    datetime.date(2025, 8, 15): "Κοίμηση Θεοτόκου",
    datetime.date(2025, 10,28): "Επέτειος του Όχι",
    datetime.date(2025, 11,17): "Πολυτεχνείο",
    datetime.date(2025, 12,25): "Χριστούγεννα",
    datetime.date(2025, 12,26): "Σύναξη Θεοτόκου",
}

def daterange(start_date, end_date):
    """Γεννήτρια που δίνει όλες τις ημερομηνίες από start έως end (inclusive)."""
    for n in range((end_date - start_date).days + 1):
        yield start_date + datetime.timedelta(days=n)

def main():
    # 1. Παράμετροι γραμμής εντολών
    parser = argparse.ArgumentParser(
        description="Υπολογισμός εργάσιμων ημερών μεταξύ δύο ημερομηνιών (Ελλάδα 2025)"
    )
    parser.add_argument("start_date",
                        help="Ημερομηνία έναρξης σε μορφή YYYY-MM-DD")
    parser.add_argument("end_date",
                        help="Ημερομηνία λήξης σε μορφή YYYY-MM-DD")
    args = parser.parse_args()

    # 2. Μετατροπή σε datetime.date
    start = datetime.datetime.strptime(args.start_date, "%Y-%m-%d").date()
    end   = datetime.datetime.strptime(args.end_date,   "%Y-%m-%d").date()

    # 3. Λίστα όλων των ημερών
    all_dates = list(daterange(start, end))
    total_days = len(all_dates)

    # 4. Βρίσκουμε Σαββατοκύριακα
    weekend_dates = [d for d in all_dates if d.weekday() >= 5]

    # 5. Βρίσκουμε αργίες που πέφτουν Δευτ.–Παρασκευή
    holiday_dates = [
        d for d in all_dates
        if d in HOLIDAYS_2025 and d.weekday() < 5
    ]

    # 6. Υπολογισμός εργάσιμων
    working_days = total_days - len(weekend_dates) - len(holiday_dates)

    # --- Έξοδος ---
    print(f"Σύνολο ημερολογιακών ημερών: {total_days}\n")

    print(f"Αφαιρούμε Σαββατοκύριακα ({len(weekend_dates)} ημέρες):")
    for d in weekend_dates:
        day_name = "Σάββατο" if d.weekday() == 5 else "Κυριακή"
        print(f"  - {d} ({day_name})")
    print()

    print(f"Αφαιρούμε επίσημες αργίες ({len(holiday_dates)} ημέρες):")
    for d in holiday_dates:
        print(f"  - {d}: {HOLIDAYS_2025[d]}")
    print()

    print(f"Συνολικές εργάσιμες ημέρες: {working_days}")

if __name__ == "__main__":
    main()