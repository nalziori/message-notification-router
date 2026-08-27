"""Build the standalone fixture context for eval/synthetic_cases.csv.

The 19 synthetic cases were written in August reusing REAL entity ids from the
challenge dataset (u_002, group_003, business_011, ...) so the router's context
lookups would resolve with no schema changes. That was the right call then; it
is exactly what stops the cases running now that the challenge dataset is not
redistributed.

This script writes the missing context tables -- users, groups, memberships,
businesses, relationships, message history and reactions, daily load -- for
only the entities those 19 cases reference. Everything here is invented. No
value is copied or derived from the challenge dataset.

Deliberately NOT written to make any particular expected label come out right.
Context engineered backwards from a known answer produces cases that are
unambiguous by construction, which is worthless as a test. These profiles are
written to be plausible and varied; the labels get assigned by a human reading
the assembled context afterwards (see label_sheet.py).

    python fixtures/build_fixtures.py
"""

import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent / "dataset"

# ---------------------------------------------------------------- users
# Four receivers (u_001/002/005/008) and five senders. Varied engagement:
# u_002 is an active replier, u_005 barely opens anything and reports a lot,
# u_008 opens but rarely replies.
USERS = [
    # user_id, dnd_window,    opened, replied, dismissed, reported
    ("u_001", "23:00-06:30",   38,  6, 11, 0),
    ("u_002", "22:30-07:00",   71, 24,  9, 1),
    ("u_005", "21:00-08:00",   12,  1, 33, 4),
    ("u_008", "00:00-06:00",   54,  4, 17, 0),
    ("u_007", "22:00-07:00",   29,  3, 21, 0),   # heavy forwarder (family group)
    ("u_013", "22:00-06:00",   40, 12,  6, 0),
    ("u_017", "23:30-07:30",   63, 31,  4, 0),   # u_002's close contact
    ("u_045", "21:30-07:00",   22,  9,  2, 0),   # school coordinator
    ("u_090", "", 3, 0, 1, 0),                    # brand new account, no pattern yet
]

# ---------------------------------------------------------------- groups
GROUPS = [
    ("group_001", "Family",              "family", 11, 2, "2023-04-02", 118),
    ("group_003", "Route B Parents",     "school",  34, 3, "2024-06-19",  47),
]

# group_id, user_id, role, joined_at, sent, read, replies, dismissed, muted
GROUP_MEMBERS = [
    ("group_001", "u_002", "member", "2023-04-02", 14, 96, 11, 12, 0),
    ("group_001", "u_007", "member", "2023-04-05", 61, 44,  3,  8, 0),
    ("group_001", "u_013", "admin",  "2023-04-02", 22, 88,  9,  2, 0),
    ("group_003", "u_002", "member", "2024-06-20",  6, 41,  4,  3, 0),
    ("group_003", "u_017", "member", "2024-06-22",  9, 33,  5,  6, 0),
    ("group_003", "u_045", "admin",  "2024-06-19", 28, 46, 12,  1, 0),
]

# ---------------------------------------------------------------- businesses
# business_001/011 are established and verified. business_041 is a young
# unverified account with reports. business_062 uses a lookalike domain that is
# far newer than the brand it claims -- the classic impersonation signature.
BUSINESSES = [
    # id, display, brand, category, verified, official_domain, sender_domain,
    # acct_age_days, sent_30d, reports_30d, sender_domain_age_days
    ("business_001", "ParcelPost",       "ParcelPost",  "ecommerce_delivery", 1,
     "parcelpost.example", "parcelpost.example", 1120, 980,  2, 1120),
    ("business_011", "Aster Clothing",   "Aster",       "retail_fashion",     1,
     "aster.example",      "aster.example",       742, 415,  1,  742),
    ("business_041", "Prize Central",    "",            "unknown",            0,
     "",                   "prizecentral-win.example", 26, 6100, 214, 26),
    ("business_062", "Meridian Bank",    "Meridian Bank", "banking",          0,
     "meridianbank.example", "meridian-bank-secure.example", 41, 3300, 187, 9),
]

# user_id, business_id, why_known, last_activity, allows_promo, opted_out_at,
# activity_180d, opened_30d, dismissed_30d, replied_30d, last_reply_at
USER_BUSINESS = [
    ("u_001", "business_001", "recent_parcel_delivery", "2026-07-29 14:02", 0, "", 7, 6, 1, 0, ""),
    ("u_008", "business_011", "repeat_customer",        "2026-07-26 19:41", 1, "", 14, 11, 2, 1, "2026-06-30 20:10"),
    ("u_002", "business_011", "single_purchase_last_year", "2026-02-14 11:20", 0,
     "2026-03-02 09:00", 2, 1, 5, 0, ""),
    # u_005 has no prior relationship with either sender below -- both are
    # first contact from accounts claiming to be something they aren't.
]

# ---------------------------------------------------------------- history
# Past messages the router can cite as evidence, with how the user reacted.
# Mixed on purpose: u_002 has both engaged-with and dismissed forwards from
# u_007, so "repetition" is not a one-way signal.
# msg_id, user, conv_type, group, business, sender, created_at, text, fwd
HISTORY = [
    ("fx_h_001", "u_002", "personal", "", "", "u_017", "2026-07-30 19:12",
     "Dinner moved to 8:30, does that still work?", 0),
    ("fx_h_002", "u_002", "personal", "", "", "u_017", "2026-07-28 08:40",
     "Left the keys with the neighbour, no rush picking them up.", 0),
    ("fx_h_003", "u_002", "personal", "", "", "u_017", "2026-07-21 22:05",
     "Can you call when you get a second? Bit of a situation here.", 0),
    ("fx_h_004", "u_002", "group", "group_001", "", "u_007", "2026-07-29 07:15",
     "Fwd: Ten foods that cleanse your liver overnight, share with loved ones.", 12),
    ("fx_h_005", "u_002", "group", "group_001", "", "u_007", "2026-07-24 06:58",
     "Fwd: Warning about a new phone scam going around, please forward.", 31),
    ("fx_h_006", "u_002", "group", "group_001", "", "u_007", "2026-07-18 07:02",
     "Fwd: Miracle cure they don't want you to know about!!", 44),
    ("fx_h_007", "u_002", "group", "group_001", "", "u_013", "2026-07-27 09:30",
     "Good morning all, wishing everyone a lovely week.", 0),
    ("fx_h_008", "u_002", "group", "group_001", "", "u_013", "2026-07-20 18:44",
     "Lunch at mine on Sunday, 1pm. Bring nothing, just come.", 0),
    ("fx_h_009", "u_002", "group", "group_003", "", "u_045", "2026-07-31 13:20",
     "Reminder: swimming kit needed tomorrow for Route B children.", 0),
    ("fx_h_010", "u_002", "group", "group_003", "", "u_045", "2026-07-25 16:05",
     "Bus will be 20 minutes late this afternoon due to roadworks.", 0),
    ("fx_h_011", "u_002", "group", "group_003", "", "u_017", "2026-07-22 12:33",
     "Anyone have a spare uniform jumper age 9? Happy to pay.", 0),
    ("fx_h_012", "u_002", "business", "", "business_011", "", "2026-07-15 10:00",
     "Mid-season sale starts today, up to 40% off everything.", 0),
    ("fx_h_013", "u_002", "business", "", "business_011", "", "2026-06-28 10:00",
     "Final hours! Sale ends midnight.", 0),
    ("fx_h_014", "u_008", "business", "", "business_011", "", "2026-07-26 19:40",
     "Your order has shipped, arriving Thursday.", 0),
    ("fx_h_015", "u_008", "business", "", "business_011", "", "2026-07-11 09:15",
     "New season pieces just landed, picked for you.", 0),
    ("fx_h_016", "u_001", "business", "", "business_001", "", "2026-07-29 14:00",
     "Out for delivery, arriving before 6pm today.", 0),
    ("fx_h_017", "u_001", "business", "", "business_001", "", "2026-07-14 11:31",
     "Your parcel is ready for collection at the locker.", 0),
    ("fx_h_018", "u_005", "business", "", "business_062", "", "2026-07-30 03:12",
     "Your account is at risk. Confirm your card PIN immediately to avoid closure.", 0),
    ("fx_h_019", "u_005", "business", "", "business_062", "", "2026-07-19 02:47",
     "Security notice: verify your identity now or lose access.", 0),
    ("fx_h_020", "u_005", "business", "", "business_041", "", "2026-07-26 21:30",
     "You are today's lucky winner! Claim within 1 hour.", 0),
    ("fx_h_021", "u_005", "personal", "", "", "u_013", "2026-07-23 17:10",
     "Are you free to talk this evening?", 0),
]

# user, message_id, opened, replied, reaction_min, dismissed, muted_after, reported
EVENTS = [
    ("u_002", "fx_h_001", 1, 1,   4, 0, 0, 0),
    ("u_002", "fx_h_002", 1, 1,  22, 0, 0, 0),
    ("u_002", "fx_h_003", 1, 1,   2, 0, 0, 0),
    ("u_002", "fx_h_004", 0, 0, "", 1, 0, 0),
    ("u_002", "fx_h_005", 1, 0,  38, 0, 0, 0),   # this one he actually read
    ("u_002", "fx_h_006", 0, 0, "", 1, 0, 0),
    ("u_002", "fx_h_007", 1, 0,  95, 0, 0, 0),
    ("u_002", "fx_h_008", 1, 1,  12, 0, 0, 0),
    ("u_002", "fx_h_009", 1, 1,   7, 0, 0, 0),
    ("u_002", "fx_h_010", 1, 0,  15, 0, 0, 0),
    ("u_002", "fx_h_011", 0, 0, "", 1, 0, 0),
    ("u_002", "fx_h_012", 0, 0, "", 1, 0, 0),
    ("u_002", "fx_h_013", 0, 0, "", 1, 1, 0),    # muted the thread after this
    ("u_008", "fx_h_014", 1, 0,   9, 0, 0, 0),
    ("u_008", "fx_h_015", 1, 1,  41, 0, 0, 0),
    ("u_001", "fx_h_016", 1, 0,   6, 0, 0, 0),
    ("u_001", "fx_h_017", 1, 0,  33, 0, 0, 0),
    ("u_005", "fx_h_018", 0, 0, "", 1, 1, 1),    # dismissed, muted AND reported
    ("u_005", "fx_h_019", 0, 0, "", 1, 0, 1),
    ("u_005", "fx_h_020", 0, 0, "", 1, 0, 1),
    ("u_005", "fx_h_021", 1, 1,  18, 0, 0, 0),
]

# The synthetic cases are dated 2026-08-01; give each receiver that day's load.
DAILY = [
    ("u_001", "2026-08-01",  9,  3),
    ("u_002", "2026-08-01", 31, 11),   # busy day -- raises the bar for notify
    ("u_005", "2026-08-01", 14, 12),
    ("u_008", "2026-08-01",  7,  2),
]

TABLES = {
    "users.csv": (
        ["user_id", "do_not_disturb_window", "messages_opened_30d",
         "messages_replied_30d", "notifications_dismissed_30d", "messages_reported_30d"],
        USERS),
    "groups.csv": (
        ["group_id", "group_name", "group_type", "member_count", "admin_count",
         "created_at", "messages_30d"],
        GROUPS),
    "group_members.csv": (
        ["group_id", "user_id", "role", "joined_at", "messages_sent_30d",
         "messages_read_30d", "replies_sent_30d", "notifications_dismissed_30d",
         "group_muted_by_user"],
        GROUP_MEMBERS),
    "business_accounts.csv": (
        ["business_id", "display_name", "brand_name", "category", "verified",
         "official_domain", "domain_used_by_sender", "account_age_days",
         "messages_sent_30d", "user_reports_30d", "domain_used_by_sender_age_days"],
        BUSINESSES),
    "user_business_history.csv": (
        ["user_id", "business_id", "why_user_knows_account", "last_activity_at",
         "allows_promotions", "promotions_opted_out_at", "activity_count_180d",
         "messages_opened_30d", "messages_dismissed_30d", "messages_replied_30d",
         "last_reply_at"],
        USER_BUSINESS),
    "message_history.csv": (
        ["message_id", "user_id", "conversation_type", "group_id", "business_id",
         "sender_user_id", "created_at", "message_text", "media_type", "media_id",
         "forwarded_count"],
        [(m, u, c, g, b, s, t, x, "", "", f) for m, u, c, g, b, s, t, x, f in HISTORY]),
    "message_events.csv": (
        ["user_id", "message_id", "message_opened", "message_replied",
         "reaction_time_minutes", "notification_dismissed", "muted_after_message",
         "message_reported"],
        EVENTS),
    "daily_notification_summary.csv": (
        ["user_id", "date", "notifications_sent", "notifications_dismissed"],
        DAILY),
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (header, rows) in TABLES.items():
        path = OUT / name
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerows(rows)
        print(f"  {name}: {len(rows)} rows")
    print(f"\nWrote {len(TABLES)} tables to {OUT}")


if __name__ == "__main__":
    main()
