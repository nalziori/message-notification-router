# 합성 케이스 19건 — 라벨링 시트

각 케이스는 **라우터가 실제로 모델에게 보내는 컨텍스트 그대로**입니다.
아래 `action:` / `message_type:` 옆 빈칸을 채우세요.

- action: `notify | digest | mute`
- message_type: `personal, urgent, event, payment, business_update, promotion, greeting, forward, spam, scam, unknown`

판단이 갈리면 `note:`에 왜 애매한지 한 줄 남겨 주세요 — 그 자체가 유용한 신호입니다.
8월 라벨은 일부러 숨겼습니다(앵커링 방지). 채운 뒤 `compare_labels.py`로 대조합니다.

---

## 1. `synth_msg_01`

```
Incoming message_id: synth_msg_01
conversation_type: personal | created_at: 2026-08-01 12:00 | forwarded_count: 0
sender_user_id: u_017 | group_id: (n/a) | business_id: (n/a)
message_text: "Hey, are we still on for dinner tonight around 8? No rush, just checking."

Receiving user profile: user_id=u_002, do_not_disturb_window=22:30-07:00, messages_opened_30d=71, messages_replied_30d=24, notifications_dismissed_30d=9, messages_reported_30d=1
Group + this user's membership: (none)
Business sender + this user's relationship with it: (none)
This user's notification load today: user_id=u_002, date=2026-08-01, notifications_sent=31, notifications_dismissed=11

Relevant past messages from this user (only cite ids from this list):
  [fx_h_001] 2026-07-30 19:12 sender=u_017 group=(n/a) business=(n/a) text="Dinner moved to 8:30, does that still work?" | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_002] 2026-07-28 08:40 sender=u_017 group=(n/a) business=(n/a) text="Left the keys with the neighbour, no rush picking them up." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_011] 2026-07-22 12:33 sender=u_017 group=group_003 business=(n/a) text="Anyone have a spare uniform jumper age 9? Happy to pay." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_003] 2026-07-21 22:05 sender=u_017 group=(n/a) business=(n/a) text="Can you call when you get a second? Bit of a situation here." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_009] 2026-07-31 13:20 sender=u_045 group=group_003 business=(n/a) text="Reminder: swimming kit needed tomorrow for Route B children." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_004] 2026-07-29 07:15 sender=u_007 group=group_001 business=(n/a) text="Fwd: Ten foods that cleanse your liver overnight, share with loved ones." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_007] 2026-07-27 09:30 sender=u_013 group=group_001 business=(n/a) text="Good morning all, wishing everyone a lovely week." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_010] 2026-07-25 16:05 sender=u_045 group=group_003 business=(n/a) text="Bus will be 20 minutes late this afternoon due to roadworks." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_005] 2026-07-24 06:58 sender=u_007 group=group_001 business=(n/a) text="Fwd: Warning about a new phone scam going around, please forward." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_008] 2026-07-20 18:44 sender=u_013 group=group_001 business=(n/a) text="Lunch at mine on Sunday, 1pm. Bring nothing, just come." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_006] 2026-07-18 07:02 sender=u_007 group=group_001 business=(n/a) text="Fwd: Miracle cure they don't want you to know about!!" | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_012] 2026-07-15 10:00 sender=(n/a) group=(n/a) business=business_011 text="Mid-season sale starts today, up to 40% off everything." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
```

```yaml
message_id:   synth_msg_01
action:       notify
message_type: personal
note:         
```

---

## 2. `synth_msg_02`

```
Incoming message_id: synth_msg_02
conversation_type: personal | created_at: 2026-08-01 12:00 | forwarded_count: 0
sender_user_id: u_017 | group_id: (n/a) | business_id: (n/a)
message_text: "Emergency -- I'm locked out and the landlord isn't picking up. Can you call me back right now?"

Receiving user profile: user_id=u_002, do_not_disturb_window=22:30-07:00, messages_opened_30d=71, messages_replied_30d=24, notifications_dismissed_30d=9, messages_reported_30d=1
Group + this user's membership: (none)
Business sender + this user's relationship with it: (none)
This user's notification load today: user_id=u_002, date=2026-08-01, notifications_sent=31, notifications_dismissed=11

Relevant past messages from this user (only cite ids from this list):
  [fx_h_001] 2026-07-30 19:12 sender=u_017 group=(n/a) business=(n/a) text="Dinner moved to 8:30, does that still work?" | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_002] 2026-07-28 08:40 sender=u_017 group=(n/a) business=(n/a) text="Left the keys with the neighbour, no rush picking them up." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_011] 2026-07-22 12:33 sender=u_017 group=group_003 business=(n/a) text="Anyone have a spare uniform jumper age 9? Happy to pay." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_003] 2026-07-21 22:05 sender=u_017 group=(n/a) business=(n/a) text="Can you call when you get a second? Bit of a situation here." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_009] 2026-07-31 13:20 sender=u_045 group=group_003 business=(n/a) text="Reminder: swimming kit needed tomorrow for Route B children." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_004] 2026-07-29 07:15 sender=u_007 group=group_001 business=(n/a) text="Fwd: Ten foods that cleanse your liver overnight, share with loved ones." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_007] 2026-07-27 09:30 sender=u_013 group=group_001 business=(n/a) text="Good morning all, wishing everyone a lovely week." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_010] 2026-07-25 16:05 sender=u_045 group=group_003 business=(n/a) text="Bus will be 20 minutes late this afternoon due to roadworks." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_005] 2026-07-24 06:58 sender=u_007 group=group_001 business=(n/a) text="Fwd: Warning about a new phone scam going around, please forward." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_008] 2026-07-20 18:44 sender=u_013 group=group_001 business=(n/a) text="Lunch at mine on Sunday, 1pm. Bring nothing, just come." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_006] 2026-07-18 07:02 sender=u_007 group=group_001 business=(n/a) text="Fwd: Miracle cure they don't want you to know about!!" | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_012] 2026-07-15 10:00 sender=(n/a) group=(n/a) business=business_011 text="Mid-season sale starts today, up to 40% off everything." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
```

```yaml
message_id:   synth_msg_02
action:       notify
message_type: urgent
note:         
```

---

## 3. `synth_msg_03`

```
Incoming message_id: synth_msg_03
conversation_type: group | created_at: 2026-08-01 12:00 | forwarded_count: 0
sender_user_id: u_045 | group_id: group_003 | business_id: (n/a)
message_text: "Route B parents: pickup moved to 3:45 today because of the assembly, please plan accordingly."

Receiving user profile: user_id=u_002, do_not_disturb_window=22:30-07:00, messages_opened_30d=71, messages_replied_30d=24, notifications_dismissed_30d=9, messages_reported_30d=1
Group + this user's membership: group_id=group_003, group_name=Route B Parents, group_type=school, member_count=34, admin_count=3, created_at=2024-06-19, messages_30d=47, user_id=u_002, role=member, joined_at=2024-06-20, messages_sent_30d=6, messages_read_30d=41, replies_sent_30d=4, notifications_dismissed_30d=3, group_muted_by_user=0
Business sender + this user's relationship with it: (none)
This user's notification load today: user_id=u_002, date=2026-08-01, notifications_sent=31, notifications_dismissed=11

Relevant past messages from this user (only cite ids from this list):
  [fx_h_009] 2026-07-31 13:20 sender=u_045 group=group_003 business=(n/a) text="Reminder: swimming kit needed tomorrow for Route B children." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_010] 2026-07-25 16:05 sender=u_045 group=group_003 business=(n/a) text="Bus will be 20 minutes late this afternoon due to roadworks." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_011] 2026-07-22 12:33 sender=u_017 group=group_003 business=(n/a) text="Anyone have a spare uniform jumper age 9? Happy to pay." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_001] 2026-07-30 19:12 sender=u_017 group=(n/a) business=(n/a) text="Dinner moved to 8:30, does that still work?" | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_004] 2026-07-29 07:15 sender=u_007 group=group_001 business=(n/a) text="Fwd: Ten foods that cleanse your liver overnight, share with loved ones." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_002] 2026-07-28 08:40 sender=u_017 group=(n/a) business=(n/a) text="Left the keys with the neighbour, no rush picking them up." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_007] 2026-07-27 09:30 sender=u_013 group=group_001 business=(n/a) text="Good morning all, wishing everyone a lovely week." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_005] 2026-07-24 06:58 sender=u_007 group=group_001 business=(n/a) text="Fwd: Warning about a new phone scam going around, please forward." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_003] 2026-07-21 22:05 sender=u_017 group=(n/a) business=(n/a) text="Can you call when you get a second? Bit of a situation here." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_008] 2026-07-20 18:44 sender=u_013 group=group_001 business=(n/a) text="Lunch at mine on Sunday, 1pm. Bring nothing, just come." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_006] 2026-07-18 07:02 sender=u_007 group=group_001 business=(n/a) text="Fwd: Miracle cure they don't want you to know about!!" | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_012] 2026-07-15 10:00 sender=(n/a) group=(n/a) business=business_011 text="Mid-season sale starts today, up to 40% off everything." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
```

```yaml
message_id:   synth_msg_03
action:       digest
message_type: unknown
note:         This message seems like parent's group chatting room. It is just a notification for parents to change plan to pick up their kids according to changed plan. I think it's not personal, not urgent. And group chat notifications are usually classified as digest. But it can be notify in this message.
```

---

## 4. `synth_msg_04`

```
Incoming message_id: synth_msg_04
conversation_type: group | created_at: 2026-08-01 12:00 | forwarded_count: 0
sender_user_id: u_017 | group_id: group_003 | business_id: (n/a)
message_text: "Selling a barely-used badminton racket, good condition. Pickup near the school gate this Friday if anyone wants it."

Receiving user profile: user_id=u_002, do_not_disturb_window=22:30-07:00, messages_opened_30d=71, messages_replied_30d=24, notifications_dismissed_30d=9, messages_reported_30d=1
Group + this user's membership: group_id=group_003, group_name=Route B Parents, group_type=school, member_count=34, admin_count=3, created_at=2024-06-19, messages_30d=47, user_id=u_002, role=member, joined_at=2024-06-20, messages_sent_30d=6, messages_read_30d=41, replies_sent_30d=4, notifications_dismissed_30d=3, group_muted_by_user=0
Business sender + this user's relationship with it: (none)
This user's notification load today: user_id=u_002, date=2026-08-01, notifications_sent=31, notifications_dismissed=11

Relevant past messages from this user (only cite ids from this list):
  [fx_h_011] 2026-07-22 12:33 sender=u_017 group=group_003 business=(n/a) text="Anyone have a spare uniform jumper age 9? Happy to pay." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_001] 2026-07-30 19:12 sender=u_017 group=(n/a) business=(n/a) text="Dinner moved to 8:30, does that still work?" | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_002] 2026-07-28 08:40 sender=u_017 group=(n/a) business=(n/a) text="Left the keys with the neighbour, no rush picking them up." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_003] 2026-07-21 22:05 sender=u_017 group=(n/a) business=(n/a) text="Can you call when you get a second? Bit of a situation here." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_009] 2026-07-31 13:20 sender=u_045 group=group_003 business=(n/a) text="Reminder: swimming kit needed tomorrow for Route B children." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_010] 2026-07-25 16:05 sender=u_045 group=group_003 business=(n/a) text="Bus will be 20 minutes late this afternoon due to roadworks." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_004] 2026-07-29 07:15 sender=u_007 group=group_001 business=(n/a) text="Fwd: Ten foods that cleanse your liver overnight, share with loved ones." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_007] 2026-07-27 09:30 sender=u_013 group=group_001 business=(n/a) text="Good morning all, wishing everyone a lovely week." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_005] 2026-07-24 06:58 sender=u_007 group=group_001 business=(n/a) text="Fwd: Warning about a new phone scam going around, please forward." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_008] 2026-07-20 18:44 sender=u_013 group=group_001 business=(n/a) text="Lunch at mine on Sunday, 1pm. Bring nothing, just come." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_006] 2026-07-18 07:02 sender=u_007 group=group_001 business=(n/a) text="Fwd: Miracle cure they don't want you to know about!!" | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_012] 2026-07-15 10:00 sender=(n/a) group=(n/a) business=business_011 text="Mid-season sale starts today, up to 40% off everything." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
```

```yaml
message_id:   synth_msg_04
action:       digest
message_type: personal
note:         It seems like personal sales message, but not scam or spam. This chat room is school parents chat room so not scam or spam. Not a notification, personal sales message. 
```

---

## 5. `synth_msg_05`

```
Incoming message_id: synth_msg_05
conversation_type: group | created_at: 2026-08-01 12:00 | forwarded_count: 0
sender_user_id: u_013 | group_id: group_001 | business_id: (n/a)
message_text: "Good morning family! Hope everyone has a peaceful and blessed day today."

Receiving user profile: user_id=u_002, do_not_disturb_window=22:30-07:00, messages_opened_30d=71, messages_replied_30d=24, notifications_dismissed_30d=9, messages_reported_30d=1
Group + this user's membership: group_id=group_001, group_name=Family, group_type=family, member_count=11, admin_count=2, created_at=2023-04-02, messages_30d=118, user_id=u_002, role=member, joined_at=2023-04-02, messages_sent_30d=14, messages_read_30d=96, replies_sent_30d=11, notifications_dismissed_30d=12, group_muted_by_user=0
Business sender + this user's relationship with it: (none)
This user's notification load today: user_id=u_002, date=2026-08-01, notifications_sent=31, notifications_dismissed=11

Relevant past messages from this user (only cite ids from this list):
  [fx_h_007] 2026-07-27 09:30 sender=u_013 group=group_001 business=(n/a) text="Good morning all, wishing everyone a lovely week." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_008] 2026-07-20 18:44 sender=u_013 group=group_001 business=(n/a) text="Lunch at mine on Sunday, 1pm. Bring nothing, just come." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_004] 2026-07-29 07:15 sender=u_007 group=group_001 business=(n/a) text="Fwd: Ten foods that cleanse your liver overnight, share with loved ones." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_005] 2026-07-24 06:58 sender=u_007 group=group_001 business=(n/a) text="Fwd: Warning about a new phone scam going around, please forward." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_006] 2026-07-18 07:02 sender=u_007 group=group_001 business=(n/a) text="Fwd: Miracle cure they don't want you to know about!!" | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_009] 2026-07-31 13:20 sender=u_045 group=group_003 business=(n/a) text="Reminder: swimming kit needed tomorrow for Route B children." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_001] 2026-07-30 19:12 sender=u_017 group=(n/a) business=(n/a) text="Dinner moved to 8:30, does that still work?" | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_002] 2026-07-28 08:40 sender=u_017 group=(n/a) business=(n/a) text="Left the keys with the neighbour, no rush picking them up." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_010] 2026-07-25 16:05 sender=u_045 group=group_003 business=(n/a) text="Bus will be 20 minutes late this afternoon due to roadworks." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_011] 2026-07-22 12:33 sender=u_017 group=group_003 business=(n/a) text="Anyone have a spare uniform jumper age 9? Happy to pay." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_003] 2026-07-21 22:05 sender=u_017 group=(n/a) business=(n/a) text="Can you call when you get a second? Bit of a situation here." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_012] 2026-07-15 10:00 sender=(n/a) group=(n/a) business=business_011 text="Mid-season sale starts today, up to 40% off everything." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
```

```yaml
message_id:   synth_msg_05
action:       digest
message_type: greeting
note:         
```

---

## 6. `synth_msg_06`

```
Incoming message_id: synth_msg_06
conversation_type: group | created_at: 2026-08-01 12:00 | forwarded_count: 9
sender_user_id: u_007 | group_id: group_001 | business_id: (n/a)
message_text: "Fwd: Doctors say drinking warm turmeric water every morning boosts immunity, please share with family."

Receiving user profile: user_id=u_002, do_not_disturb_window=22:30-07:00, messages_opened_30d=71, messages_replied_30d=24, notifications_dismissed_30d=9, messages_reported_30d=1
Group + this user's membership: group_id=group_001, group_name=Family, group_type=family, member_count=11, admin_count=2, created_at=2023-04-02, messages_30d=118, user_id=u_002, role=member, joined_at=2023-04-02, messages_sent_30d=14, messages_read_30d=96, replies_sent_30d=11, notifications_dismissed_30d=12, group_muted_by_user=0
Business sender + this user's relationship with it: (none)
This user's notification load today: user_id=u_002, date=2026-08-01, notifications_sent=31, notifications_dismissed=11

Relevant past messages from this user (only cite ids from this list):
  [fx_h_004] 2026-07-29 07:15 sender=u_007 group=group_001 business=(n/a) text="Fwd: Ten foods that cleanse your liver overnight, share with loved ones." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_005] 2026-07-24 06:58 sender=u_007 group=group_001 business=(n/a) text="Fwd: Warning about a new phone scam going around, please forward." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_006] 2026-07-18 07:02 sender=u_007 group=group_001 business=(n/a) text="Fwd: Miracle cure they don't want you to know about!!" | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_007] 2026-07-27 09:30 sender=u_013 group=group_001 business=(n/a) text="Good morning all, wishing everyone a lovely week." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_008] 2026-07-20 18:44 sender=u_013 group=group_001 business=(n/a) text="Lunch at mine on Sunday, 1pm. Bring nothing, just come." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_009] 2026-07-31 13:20 sender=u_045 group=group_003 business=(n/a) text="Reminder: swimming kit needed tomorrow for Route B children." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_001] 2026-07-30 19:12 sender=u_017 group=(n/a) business=(n/a) text="Dinner moved to 8:30, does that still work?" | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_002] 2026-07-28 08:40 sender=u_017 group=(n/a) business=(n/a) text="Left the keys with the neighbour, no rush picking them up." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_010] 2026-07-25 16:05 sender=u_045 group=group_003 business=(n/a) text="Bus will be 20 minutes late this afternoon due to roadworks." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_011] 2026-07-22 12:33 sender=u_017 group=group_003 business=(n/a) text="Anyone have a spare uniform jumper age 9? Happy to pay." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_003] 2026-07-21 22:05 sender=u_017 group=(n/a) business=(n/a) text="Can you call when you get a second? Bit of a situation here." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_012] 2026-07-15 10:00 sender=(n/a) group=(n/a) business=business_011 text="Mid-season sale starts today, up to 40% off everything." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
```

```yaml
message_id:   synth_msg_06
action:       digest
message_type: forward
note:         
```

---

## 7. `synth_msg_08`

```
Incoming message_id: synth_msg_08
conversation_type: business | created_at: 2026-08-01 12:00 | forwarded_count: 0
sender_user_id: (n/a) | group_id: (n/a) | business_id: business_011
message_text: "Hi! A new arrival just dropped in your size based on your last order. Check it out in the app."

Receiving user profile: user_id=u_008, do_not_disturb_window=00:00-06:00, messages_opened_30d=54, messages_replied_30d=4, notifications_dismissed_30d=17, messages_reported_30d=0
Group + this user's membership: (none)
Business sender + this user's relationship with it: business_id=business_011, display_name=Aster Clothing, brand_name=Aster, category=retail_fashion, verified=1, official_domain=aster.example, domain_used_by_sender=aster.example, account_age_days=742, messages_sent_30d=415, user_reports_30d=1, domain_used_by_sender_age_days=742, user_id=u_008, why_user_knows_account=repeat_customer, last_activity_at=2026-07-26 19:41, allows_promotions=1, activity_count_180d=14, messages_opened_30d=11, messages_dismissed_30d=2, messages_replied_30d=1, last_reply_at=2026-06-30 20:10
This user's notification load today: user_id=u_008, date=2026-08-01, notifications_sent=7, notifications_dismissed=2

Relevant past messages from this user (only cite ids from this list):
  [fx_h_014] 2026-07-26 19:40 sender=(n/a) group=(n/a) business=business_011 text="Your order has shipped, arriving Thursday." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_015] 2026-07-11 09:15 sender=(n/a) group=(n/a) business=business_011 text="New season pieces just landed, picked for you." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
```

```yaml
message_id:   synth_msg_08
action:       digest
message_type: business_update
note:         
```

---

## 8. `synth_msg_09`

```
Incoming message_id: synth_msg_09
conversation_type: business | created_at: 2026-08-01 12:00 | forwarded_count: 0
sender_user_id: (n/a) | group_id: (n/a) | business_id: business_062
message_text: "URGENT: Your bank account will be suspended in 2 hours. Reply with your debit card number and OTP to verify and avoid suspension."

Receiving user profile: user_id=u_005, do_not_disturb_window=21:00-08:00, messages_opened_30d=12, messages_replied_30d=1, notifications_dismissed_30d=33, messages_reported_30d=4
Group + this user's membership: (none)
Business sender + this user's relationship with it: business_id=business_062, display_name=Meridian Bank, brand_name=Meridian Bank, category=banking, verified=0, official_domain=meridianbank.example, domain_used_by_sender=meridian-bank-secure.example, account_age_days=41, messages_sent_30d=3300, user_reports_30d=187, domain_used_by_sender_age_days=9
This user's notification load today: user_id=u_005, date=2026-08-01, notifications_sent=14, notifications_dismissed=12

Relevant past messages from this user (only cite ids from this list):
  [fx_h_018] 2026-07-30 03:12 sender=(n/a) group=(n/a) business=business_062 text="Your account is at risk. Confirm your card PIN immediately to avoid closure." | reaction: opened=0 replied=0 dismissed=1 muted_after=1 reported=1
  [fx_h_019] 2026-07-19 02:47 sender=(n/a) group=(n/a) business=business_062 text="Security notice: verify your identity now or lose access." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=1
  [fx_h_020] 2026-07-26 21:30 sender=(n/a) group=(n/a) business=business_041 text="You are today's lucky winner! Claim within 1 hour." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=1
  [fx_h_021] 2026-07-23 17:10 sender=u_013 group=(n/a) business=(n/a) text="Are you free to talk this evening?" | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
```

```yaml
message_id:   synth_msg_09
action:       mute
message_type: scam
note:         
```

---

## 9. `synth_msg_10`

```
Incoming message_id: synth_msg_10
conversation_type: business | created_at: 2026-08-01 12:00 | forwarded_count: 0
sender_user_id: (n/a) | group_id: (n/a) | business_id: business_041
message_text: "CONGRATULATIONS you have been selected!! Claim your free prize now by clicking the link and entering your details!!!"

Receiving user profile: user_id=u_005, do_not_disturb_window=21:00-08:00, messages_opened_30d=12, messages_replied_30d=1, notifications_dismissed_30d=33, messages_reported_30d=4
Group + this user's membership: (none)
Business sender + this user's relationship with it: business_id=business_041, display_name=Prize Central, category=unknown, verified=0, domain_used_by_sender=prizecentral-win.example, account_age_days=26, messages_sent_30d=6100, user_reports_30d=214, domain_used_by_sender_age_days=26
This user's notification load today: user_id=u_005, date=2026-08-01, notifications_sent=14, notifications_dismissed=12

Relevant past messages from this user (only cite ids from this list):
  [fx_h_020] 2026-07-26 21:30 sender=(n/a) group=(n/a) business=business_041 text="You are today's lucky winner! Claim within 1 hour." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=1
  [fx_h_018] 2026-07-30 03:12 sender=(n/a) group=(n/a) business=business_062 text="Your account is at risk. Confirm your card PIN immediately to avoid closure." | reaction: opened=0 replied=0 dismissed=1 muted_after=1 reported=1
  [fx_h_021] 2026-07-23 17:10 sender=u_013 group=(n/a) business=(n/a) text="Are you free to talk this evening?" | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_019] 2026-07-19 02:47 sender=(n/a) group=(n/a) business=business_062 text="Security notice: verify your identity now or lose access." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=1
```

```yaml
message_id:   synth_msg_10
action:       mute
message_type: scam
note:         Bulk blast (6100 msgs/30d) so spam is arguable, but it asks for personal details behind a prize lure on a 26-day-old domain -- fraud intent tips it to scam.
```

---

## 10. `synth_msg_11`

```
Incoming message_id: synth_msg_11
conversation_type: personal | created_at: 2026-08-01 12:00 | forwarded_count: 0
sender_user_id: u_090 | group_id: (n/a) | business_id: (n/a)
message_text: "hi, saw your post about tutoring, do you still have slots open"

Receiving user profile: user_id=u_002, do_not_disturb_window=22:30-07:00, messages_opened_30d=71, messages_replied_30d=24, notifications_dismissed_30d=9, messages_reported_30d=1
Group + this user's membership: (none)
Business sender + this user's relationship with it: (none)
This user's notification load today: user_id=u_002, date=2026-08-01, notifications_sent=31, notifications_dismissed=11

Relevant past messages from this user (only cite ids from this list):
  [fx_h_009] 2026-07-31 13:20 sender=u_045 group=group_003 business=(n/a) text="Reminder: swimming kit needed tomorrow for Route B children." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_001] 2026-07-30 19:12 sender=u_017 group=(n/a) business=(n/a) text="Dinner moved to 8:30, does that still work?" | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_004] 2026-07-29 07:15 sender=u_007 group=group_001 business=(n/a) text="Fwd: Ten foods that cleanse your liver overnight, share with loved ones." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_002] 2026-07-28 08:40 sender=u_017 group=(n/a) business=(n/a) text="Left the keys with the neighbour, no rush picking them up." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_007] 2026-07-27 09:30 sender=u_013 group=group_001 business=(n/a) text="Good morning all, wishing everyone a lovely week." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_010] 2026-07-25 16:05 sender=u_045 group=group_003 business=(n/a) text="Bus will be 20 minutes late this afternoon due to roadworks." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_005] 2026-07-24 06:58 sender=u_007 group=group_001 business=(n/a) text="Fwd: Warning about a new phone scam going around, please forward." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_011] 2026-07-22 12:33 sender=u_017 group=group_003 business=(n/a) text="Anyone have a spare uniform jumper age 9? Happy to pay." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_003] 2026-07-21 22:05 sender=u_017 group=(n/a) business=(n/a) text="Can you call when you get a second? Bit of a situation here." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_008] 2026-07-20 18:44 sender=u_013 group=group_001 business=(n/a) text="Lunch at mine on Sunday, 1pm. Bring nothing, just come." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_006] 2026-07-18 07:02 sender=u_007 group=group_001 business=(n/a) text="Fwd: Miracle cure they don't want you to know about!!" | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_012] 2026-07-15 10:00 sender=(n/a) group=(n/a) business=business_011 text="Mid-season sale starts today, up to 40% off everything." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
```

```yaml
message_id:   synth_msg_11
action:       digest
message_type: unknown
note:         Reads like a genuine reply to the user's own tutoring post (would be personal), but u_090 has no group, no business tie and zero history here, so unknown is the safer call.
```

---

## 11. `synth_msg_12`

```
Incoming message_id: synth_msg_12
conversation_type: group | created_at: 2026-08-01 12:00 | forwarded_count: 0
sender_user_id: u_045 | group_id: group_003 | business_id: (n/a)
message_text: "@u_002 quick one -- can you send the signed consent form before 5pm today? Office closes early."

Receiving user profile: user_id=u_002, do_not_disturb_window=22:30-07:00, messages_opened_30d=71, messages_replied_30d=24, notifications_dismissed_30d=9, messages_reported_30d=1
Group + this user's membership: group_id=group_003, group_name=Route B Parents, group_type=school, member_count=34, admin_count=3, created_at=2024-06-19, messages_30d=47, user_id=u_002, role=member, joined_at=2024-06-20, messages_sent_30d=6, messages_read_30d=41, replies_sent_30d=4, notifications_dismissed_30d=3, group_muted_by_user=0
Business sender + this user's relationship with it: (none)
This user's notification load today: user_id=u_002, date=2026-08-01, notifications_sent=31, notifications_dismissed=11

Relevant past messages from this user (only cite ids from this list):
  [fx_h_009] 2026-07-31 13:20 sender=u_045 group=group_003 business=(n/a) text="Reminder: swimming kit needed tomorrow for Route B children." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_010] 2026-07-25 16:05 sender=u_045 group=group_003 business=(n/a) text="Bus will be 20 minutes late this afternoon due to roadworks." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_011] 2026-07-22 12:33 sender=u_017 group=group_003 business=(n/a) text="Anyone have a spare uniform jumper age 9? Happy to pay." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_001] 2026-07-30 19:12 sender=u_017 group=(n/a) business=(n/a) text="Dinner moved to 8:30, does that still work?" | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_004] 2026-07-29 07:15 sender=u_007 group=group_001 business=(n/a) text="Fwd: Ten foods that cleanse your liver overnight, share with loved ones." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_002] 2026-07-28 08:40 sender=u_017 group=(n/a) business=(n/a) text="Left the keys with the neighbour, no rush picking them up." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_007] 2026-07-27 09:30 sender=u_013 group=group_001 business=(n/a) text="Good morning all, wishing everyone a lovely week." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_005] 2026-07-24 06:58 sender=u_007 group=group_001 business=(n/a) text="Fwd: Warning about a new phone scam going around, please forward." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_003] 2026-07-21 22:05 sender=u_017 group=(n/a) business=(n/a) text="Can you call when you get a second? Bit of a situation here." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_008] 2026-07-20 18:44 sender=u_013 group=group_001 business=(n/a) text="Lunch at mine on Sunday, 1pm. Bring nothing, just come." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_006] 2026-07-18 07:02 sender=u_007 group=group_001 business=(n/a) text="Fwd: Miracle cure they don't want you to know about!!" | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_012] 2026-07-15 10:00 sender=(n/a) group=(n/a) business=business_011 text="Mid-season sale starts today, up to 40% off everything." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
```

```yaml
message_id:   synth_msg_12
action:       notify
message_type: urgent
note:         
```

---

## 12. `synth_msg_13`

```
Incoming message_id: synth_msg_13
conversation_type: business | created_at: 2026-08-01 12:00 | forwarded_count: 0
sender_user_id: (n/a) | group_id: (n/a) | business_id: business_001
message_text: "Your order has been delivered. Thanks for shopping with us!"

Receiving user profile: user_id=u_001, do_not_disturb_window=23:00-06:30, messages_opened_30d=38, messages_replied_30d=6, notifications_dismissed_30d=11, messages_reported_30d=0
Group + this user's membership: (none)
Business sender + this user's relationship with it: business_id=business_001, display_name=ParcelPost, brand_name=ParcelPost, category=ecommerce_delivery, verified=1, official_domain=parcelpost.example, domain_used_by_sender=parcelpost.example, account_age_days=1120, messages_sent_30d=980, user_reports_30d=2, domain_used_by_sender_age_days=1120, user_id=u_001, why_user_knows_account=recent_parcel_delivery, last_activity_at=2026-07-29 14:02, allows_promotions=0, activity_count_180d=7, messages_opened_30d=6, messages_dismissed_30d=1, messages_replied_30d=0
This user's notification load today: user_id=u_001, date=2026-08-01, notifications_sent=9, notifications_dismissed=3

Relevant past messages from this user (only cite ids from this list):
  [fx_h_016] 2026-07-29 14:00 sender=(n/a) group=(n/a) business=business_001 text="Out for delivery, arriving before 6pm today." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_017] 2026-07-14 11:31 sender=(n/a) group=(n/a) business=business_001 text="Your parcel is ready for collection at the locker." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
```

```yaml
message_id:   synth_msg_13
action:       digest
message_type: business_update
note:         
```

---

## 13. `synth_msg_14`

```
Incoming message_id: synth_msg_14
conversation_type: group | created_at: 2026-08-01 12:00 | forwarded_count: 47
sender_user_id: u_007 | group_id: group_001 | business_id: (n/a)
message_text: "Fwd: Fwd: Fwd: this message has been forwarded many times, click here to win a free iPhone, forward to 10 people to activate"

Receiving user profile: user_id=u_002, do_not_disturb_window=22:30-07:00, messages_opened_30d=71, messages_replied_30d=24, notifications_dismissed_30d=9, messages_reported_30d=1
Group + this user's membership: group_id=group_001, group_name=Family, group_type=family, member_count=11, admin_count=2, created_at=2023-04-02, messages_30d=118, user_id=u_002, role=member, joined_at=2023-04-02, messages_sent_30d=14, messages_read_30d=96, replies_sent_30d=11, notifications_dismissed_30d=12, group_muted_by_user=0
Business sender + this user's relationship with it: (none)
This user's notification load today: user_id=u_002, date=2026-08-01, notifications_sent=31, notifications_dismissed=11

Relevant past messages from this user (only cite ids from this list):
  [fx_h_004] 2026-07-29 07:15 sender=u_007 group=group_001 business=(n/a) text="Fwd: Ten foods that cleanse your liver overnight, share with loved ones." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_005] 2026-07-24 06:58 sender=u_007 group=group_001 business=(n/a) text="Fwd: Warning about a new phone scam going around, please forward." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_006] 2026-07-18 07:02 sender=u_007 group=group_001 business=(n/a) text="Fwd: Miracle cure they don't want you to know about!!" | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_007] 2026-07-27 09:30 sender=u_013 group=group_001 business=(n/a) text="Good morning all, wishing everyone a lovely week." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_008] 2026-07-20 18:44 sender=u_013 group=group_001 business=(n/a) text="Lunch at mine on Sunday, 1pm. Bring nothing, just come." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_009] 2026-07-31 13:20 sender=u_045 group=group_003 business=(n/a) text="Reminder: swimming kit needed tomorrow for Route B children." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_001] 2026-07-30 19:12 sender=u_017 group=(n/a) business=(n/a) text="Dinner moved to 8:30, does that still work?" | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_002] 2026-07-28 08:40 sender=u_017 group=(n/a) business=(n/a) text="Left the keys with the neighbour, no rush picking them up." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_010] 2026-07-25 16:05 sender=u_045 group=group_003 business=(n/a) text="Bus will be 20 minutes late this afternoon due to roadworks." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_011] 2026-07-22 12:33 sender=u_017 group=group_003 business=(n/a) text="Anyone have a spare uniform jumper age 9? Happy to pay." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_003] 2026-07-21 22:05 sender=u_017 group=(n/a) business=(n/a) text="Can you call when you get a second? Bit of a situation here." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_012] 2026-07-15 10:00 sender=(n/a) group=(n/a) business=business_011 text="Mid-season sale starts today, up to 40% off everything." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
```

```yaml
message_id:   synth_msg_14
action:       mute
message_type: spam
note:         forwarded_count=47 through the family group, but it is chain-letter prize bait, not the informational forwards u_007 usually sends -- spam rather than forward; scam is arguable since it dangles a free iPhone behind a link.
```

---

## 14. `synth_msg_15`

**첨부 image**: [poster] A promotional sale advertisement with plain beige background and brown text announcing a discount offer.
  - OCR: MEGA SALE / Flat 60% OFF / Ends tonight! / Use code SAVE60

```
Incoming message_id: synth_msg_15
conversation_type: business | created_at: 2026-08-01 12:00 | forwarded_count: 0
sender_user_id: (n/a) | group_id: (n/a) | business_id: business_011
message_text: "(empty -- see media below)"

Receiving user profile: user_id=u_002, do_not_disturb_window=22:30-07:00, messages_opened_30d=71, messages_replied_30d=24, notifications_dismissed_30d=9, messages_reported_30d=1
Group + this user's membership: (none)
Business sender + this user's relationship with it: business_id=business_011, display_name=Aster Clothing, brand_name=Aster, category=retail_fashion, verified=1, official_domain=aster.example, domain_used_by_sender=aster.example, account_age_days=742, messages_sent_30d=415, user_reports_30d=1, domain_used_by_sender_age_days=742, user_id=u_002, why_user_knows_account=single_purchase_last_year, last_activity_at=2026-02-14 11:20, allows_promotions=0, promotions_opted_out_at=2026-03-02 09:00, activity_count_180d=2, messages_opened_30d=1, messages_dismissed_30d=5, messages_replied_30d=0
This user's notification load today: user_id=u_002, date=2026-08-01, notifications_sent=31, notifications_dismissed=11
Attached image analysis: description="A promotional sale advertisement with plain beige background and brown text announcing a discount offer." ocr_text="MEGA SALE
Flat 60% OFF
Ends tonight!
Use code SAVE60" doc_type=poster objects=['promotional text', 'discount code SAVE60']

Relevant past messages from this user (only cite ids from this list):
  [fx_h_012] 2026-07-15 10:00 sender=(n/a) group=(n/a) business=business_011 text="Mid-season sale starts today, up to 40% off everything." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_013] 2026-06-28 10:00 sender=(n/a) group=(n/a) business=business_011 text="Final hours! Sale ends midnight." | reaction: opened=0 replied=0 dismissed=1 muted_after=1 reported=0
  [fx_h_009] 2026-07-31 13:20 sender=u_045 group=group_003 business=(n/a) text="Reminder: swimming kit needed tomorrow for Route B children." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_001] 2026-07-30 19:12 sender=u_017 group=(n/a) business=(n/a) text="Dinner moved to 8:30, does that still work?" | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_004] 2026-07-29 07:15 sender=u_007 group=group_001 business=(n/a) text="Fwd: Ten foods that cleanse your liver overnight, share with loved ones." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_002] 2026-07-28 08:40 sender=u_017 group=(n/a) business=(n/a) text="Left the keys with the neighbour, no rush picking them up." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_007] 2026-07-27 09:30 sender=u_013 group=group_001 business=(n/a) text="Good morning all, wishing everyone a lovely week." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_010] 2026-07-25 16:05 sender=u_045 group=group_003 business=(n/a) text="Bus will be 20 minutes late this afternoon due to roadworks." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_005] 2026-07-24 06:58 sender=u_007 group=group_001 business=(n/a) text="Fwd: Warning about a new phone scam going around, please forward." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_011] 2026-07-22 12:33 sender=u_017 group=group_003 business=(n/a) text="Anyone have a spare uniform jumper age 9? Happy to pay." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_003] 2026-07-21 22:05 sender=u_017 group=(n/a) business=(n/a) text="Can you call when you get a second? Bit of a situation here." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_008] 2026-07-20 18:44 sender=u_013 group=group_001 business=(n/a) text="Lunch at mine on Sunday, 1pm. Bring nothing, just come." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
```

```yaml
message_id:   synth_msg_15
action:       mute
message_type: promotion
note:         
```

---

## 15. `synth_msg_16`

**첨부 image**: [other] A text-based security alert message on a beige background claiming an unusual login was detected and urging OTP verification to avoid account lock. This resembles a phishing-style social engineering message, presented as image content rather than an instruction to act on.
  - OCR: SECURITY ALERT / Unusual login detected / Verify your OTP now / or account will be locked

```
Incoming message_id: synth_msg_16
conversation_type: business | created_at: 2026-08-01 12:00 | forwarded_count: 0
sender_user_id: (n/a) | group_id: (n/a) | business_id: business_062
message_text: "(empty -- see media below)"

Receiving user profile: user_id=u_005, do_not_disturb_window=21:00-08:00, messages_opened_30d=12, messages_replied_30d=1, notifications_dismissed_30d=33, messages_reported_30d=4
Group + this user's membership: (none)
Business sender + this user's relationship with it: business_id=business_062, display_name=Meridian Bank, brand_name=Meridian Bank, category=banking, verified=0, official_domain=meridianbank.example, domain_used_by_sender=meridian-bank-secure.example, account_age_days=41, messages_sent_30d=3300, user_reports_30d=187, domain_used_by_sender_age_days=9
This user's notification load today: user_id=u_005, date=2026-08-01, notifications_sent=14, notifications_dismissed=12
Attached image analysis: description="A text-based security alert message on a beige background claiming an unusual login was detected and urging OTP verification to avoid account lock. This resembles a phishing-style social engineering message, presented as image content rather than an instruction to act on." ocr_text="SECURITY ALERT
Unusual login detected
Verify your OTP now
or account will be locked" doc_type=other objects=['text alert', 'warning message']

Relevant past messages from this user (only cite ids from this list):
  [fx_h_018] 2026-07-30 03:12 sender=(n/a) group=(n/a) business=business_062 text="Your account is at risk. Confirm your card PIN immediately to avoid closure." | reaction: opened=0 replied=0 dismissed=1 muted_after=1 reported=1
  [fx_h_019] 2026-07-19 02:47 sender=(n/a) group=(n/a) business=business_062 text="Security notice: verify your identity now or lose access." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=1
  [fx_h_020] 2026-07-26 21:30 sender=(n/a) group=(n/a) business=business_041 text="You are today's lucky winner! Claim within 1 hour." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=1
  [fx_h_021] 2026-07-23 17:10 sender=u_013 group=(n/a) business=(n/a) text="Are you free to talk this evening?" | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
```

```yaml
message_id:   synth_msg_16
action:       mute
message_type: scam
note:         
```

---

## 16. `synth_msg_17`

**첨부 image**: [other] A simple text note announcing a family dinner event with time and location details on a light beige background.
  - OCR: Family Dinner / Sunday 7pm /  / at grandma's place

```
Incoming message_id: synth_msg_17
conversation_type: group | created_at: 2026-08-01 12:00 | forwarded_count: 0
sender_user_id: u_013 | group_id: group_001 | business_id: (n/a)
message_text: "(empty -- see media below)"

Receiving user profile: user_id=u_002, do_not_disturb_window=22:30-07:00, messages_opened_30d=71, messages_replied_30d=24, notifications_dismissed_30d=9, messages_reported_30d=1
Group + this user's membership: group_id=group_001, group_name=Family, group_type=family, member_count=11, admin_count=2, created_at=2023-04-02, messages_30d=118, user_id=u_002, role=member, joined_at=2023-04-02, messages_sent_30d=14, messages_read_30d=96, replies_sent_30d=11, notifications_dismissed_30d=12, group_muted_by_user=0
Business sender + this user's relationship with it: (none)
This user's notification load today: user_id=u_002, date=2026-08-01, notifications_sent=31, notifications_dismissed=11
Attached image analysis: description="A simple text note announcing a family dinner event with time and location details on a light beige background." ocr_text="Family Dinner
Sunday 7pm

at grandma's place" doc_type=other objects=[]

Relevant past messages from this user (only cite ids from this list):
  [fx_h_007] 2026-07-27 09:30 sender=u_013 group=group_001 business=(n/a) text="Good morning all, wishing everyone a lovely week." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_008] 2026-07-20 18:44 sender=u_013 group=group_001 business=(n/a) text="Lunch at mine on Sunday, 1pm. Bring nothing, just come." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_004] 2026-07-29 07:15 sender=u_007 group=group_001 business=(n/a) text="Fwd: Ten foods that cleanse your liver overnight, share with loved ones." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_005] 2026-07-24 06:58 sender=u_007 group=group_001 business=(n/a) text="Fwd: Warning about a new phone scam going around, please forward." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_006] 2026-07-18 07:02 sender=u_007 group=group_001 business=(n/a) text="Fwd: Miracle cure they don't want you to know about!!" | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_009] 2026-07-31 13:20 sender=u_045 group=group_003 business=(n/a) text="Reminder: swimming kit needed tomorrow for Route B children." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_001] 2026-07-30 19:12 sender=u_017 group=(n/a) business=(n/a) text="Dinner moved to 8:30, does that still work?" | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_002] 2026-07-28 08:40 sender=u_017 group=(n/a) business=(n/a) text="Left the keys with the neighbour, no rush picking them up." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_010] 2026-07-25 16:05 sender=u_045 group=group_003 business=(n/a) text="Bus will be 20 minutes late this afternoon due to roadworks." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_011] 2026-07-22 12:33 sender=u_017 group=group_003 business=(n/a) text="Anyone have a spare uniform jumper age 9? Happy to pay." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_003] 2026-07-21 22:05 sender=u_017 group=(n/a) business=(n/a) text="Can you call when you get a second? Bit of a situation here." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_012] 2026-07-15 10:00 sender=(n/a) group=(n/a) business=business_011 text="Mid-season sale starts today, up to 40% off everything." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
```

```yaml
message_id:   synth_msg_17
action:       digest
message_type: event
note:         Sunday dinner is days away so digest, but u_013's last invite (fx_h_008) was opened and replied to, so notify is defensible for a high-engagement family sender.
```

---

## 17. `synth_msg_18`

**첨부 voice**: 음성 전사: "Hey it's me. Just checking in. Nothing urgent. Call me whenever you get a chance."

```
Incoming message_id: synth_msg_18
conversation_type: personal | created_at: 2026-08-01 12:00 | forwarded_count: 0
sender_user_id: u_017 | group_id: (n/a) | business_id: (n/a)
message_text: "(empty -- see media below)"

Receiving user profile: user_id=u_002, do_not_disturb_window=22:30-07:00, messages_opened_30d=71, messages_replied_30d=24, notifications_dismissed_30d=9, messages_reported_30d=1
Group + this user's membership: (none)
Business sender + this user's relationship with it: (none)
This user's notification load today: user_id=u_002, date=2026-08-01, notifications_sent=31, notifications_dismissed=11
Attached voice note transcript: "Hey it's me. Just checking in. Nothing urgent. Call me whenever you get a chance."

Relevant past messages from this user (only cite ids from this list):
  [fx_h_001] 2026-07-30 19:12 sender=u_017 group=(n/a) business=(n/a) text="Dinner moved to 8:30, does that still work?" | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_002] 2026-07-28 08:40 sender=u_017 group=(n/a) business=(n/a) text="Left the keys with the neighbour, no rush picking them up." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_011] 2026-07-22 12:33 sender=u_017 group=group_003 business=(n/a) text="Anyone have a spare uniform jumper age 9? Happy to pay." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_003] 2026-07-21 22:05 sender=u_017 group=(n/a) business=(n/a) text="Can you call when you get a second? Bit of a situation here." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_009] 2026-07-31 13:20 sender=u_045 group=group_003 business=(n/a) text="Reminder: swimming kit needed tomorrow for Route B children." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_004] 2026-07-29 07:15 sender=u_007 group=group_001 business=(n/a) text="Fwd: Ten foods that cleanse your liver overnight, share with loved ones." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_007] 2026-07-27 09:30 sender=u_013 group=group_001 business=(n/a) text="Good morning all, wishing everyone a lovely week." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_010] 2026-07-25 16:05 sender=u_045 group=group_003 business=(n/a) text="Bus will be 20 minutes late this afternoon due to roadworks." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_005] 2026-07-24 06:58 sender=u_007 group=group_001 business=(n/a) text="Fwd: Warning about a new phone scam going around, please forward." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_008] 2026-07-20 18:44 sender=u_013 group=group_001 business=(n/a) text="Lunch at mine on Sunday, 1pm. Bring nothing, just come." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_006] 2026-07-18 07:02 sender=u_007 group=group_001 business=(n/a) text="Fwd: Miracle cure they don't want you to know about!!" | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_012] 2026-07-15 10:00 sender=(n/a) group=(n/a) business=business_011 text="Mid-season sale starts today, up to 40% off everything." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
```

```yaml
message_id:   synth_msg_18
action:       digest
message_type: personal
note:         The transcript says "nothing urgent, call whenever" and today's load is already 31 sent / 11 dismissed, so digest -- but u_017 is opened+replied 3/3 in history, so notify is arguable.
```

---

## 18. `synth_msg_19`

**첨부 voice**: 음성 전사: "Please call me back right away. Something came up and I really need your help in the next few minutes."

```
Incoming message_id: synth_msg_19
conversation_type: personal | created_at: 2026-08-01 12:00 | forwarded_count: 0
sender_user_id: u_017 | group_id: (n/a) | business_id: (n/a)
message_text: "(empty -- see media below)"

Receiving user profile: user_id=u_002, do_not_disturb_window=22:30-07:00, messages_opened_30d=71, messages_replied_30d=24, notifications_dismissed_30d=9, messages_reported_30d=1
Group + this user's membership: (none)
Business sender + this user's relationship with it: (none)
This user's notification load today: user_id=u_002, date=2026-08-01, notifications_sent=31, notifications_dismissed=11
Attached voice note transcript: "Please call me back right away. Something came up and I really need your help in the next few minutes."

Relevant past messages from this user (only cite ids from this list):
  [fx_h_001] 2026-07-30 19:12 sender=u_017 group=(n/a) business=(n/a) text="Dinner moved to 8:30, does that still work?" | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_002] 2026-07-28 08:40 sender=u_017 group=(n/a) business=(n/a) text="Left the keys with the neighbour, no rush picking them up." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_011] 2026-07-22 12:33 sender=u_017 group=group_003 business=(n/a) text="Anyone have a spare uniform jumper age 9? Happy to pay." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_003] 2026-07-21 22:05 sender=u_017 group=(n/a) business=(n/a) text="Can you call when you get a second? Bit of a situation here." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_009] 2026-07-31 13:20 sender=u_045 group=group_003 business=(n/a) text="Reminder: swimming kit needed tomorrow for Route B children." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_004] 2026-07-29 07:15 sender=u_007 group=group_001 business=(n/a) text="Fwd: Ten foods that cleanse your liver overnight, share with loved ones." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_007] 2026-07-27 09:30 sender=u_013 group=group_001 business=(n/a) text="Good morning all, wishing everyone a lovely week." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_010] 2026-07-25 16:05 sender=u_045 group=group_003 business=(n/a) text="Bus will be 20 minutes late this afternoon due to roadworks." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_005] 2026-07-24 06:58 sender=u_007 group=group_001 business=(n/a) text="Fwd: Warning about a new phone scam going around, please forward." | reaction: opened=1 replied=0 dismissed=0 muted_after=0 reported=0
  [fx_h_008] 2026-07-20 18:44 sender=u_013 group=group_001 business=(n/a) text="Lunch at mine on Sunday, 1pm. Bring nothing, just come." | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
  [fx_h_006] 2026-07-18 07:02 sender=u_007 group=group_001 business=(n/a) text="Fwd: Miracle cure they don't want you to know about!!" | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
  [fx_h_012] 2026-07-15 10:00 sender=(n/a) group=(n/a) business=business_011 text="Mid-season sale starts today, up to 40% off everything." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=0
```

```yaml
message_id:   synth_msg_19
action:       notify
message_type: urgent
note:         
```

---

## 19. `synth_msg_20`

**첨부 voice**: 음성 전사: "This is your bank calling. Your account has suspicious activity. Please say your one-time password now to secure your account."

```
Incoming message_id: synth_msg_20
conversation_type: business | created_at: 2026-08-01 12:00 | forwarded_count: 0
sender_user_id: (n/a) | group_id: (n/a) | business_id: business_062
message_text: "(empty -- see media below)"

Receiving user profile: user_id=u_005, do_not_disturb_window=21:00-08:00, messages_opened_30d=12, messages_replied_30d=1, notifications_dismissed_30d=33, messages_reported_30d=4
Group + this user's membership: (none)
Business sender + this user's relationship with it: business_id=business_062, display_name=Meridian Bank, brand_name=Meridian Bank, category=banking, verified=0, official_domain=meridianbank.example, domain_used_by_sender=meridian-bank-secure.example, account_age_days=41, messages_sent_30d=3300, user_reports_30d=187, domain_used_by_sender_age_days=9
This user's notification load today: user_id=u_005, date=2026-08-01, notifications_sent=14, notifications_dismissed=12
Attached voice note transcript: "This is your bank calling. Your account has suspicious activity. Please say your one-time password now to secure your account."

Relevant past messages from this user (only cite ids from this list):
  [fx_h_018] 2026-07-30 03:12 sender=(n/a) group=(n/a) business=business_062 text="Your account is at risk. Confirm your card PIN immediately to avoid closure." | reaction: opened=0 replied=0 dismissed=1 muted_after=1 reported=1
  [fx_h_019] 2026-07-19 02:47 sender=(n/a) group=(n/a) business=business_062 text="Security notice: verify your identity now or lose access." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=1
  [fx_h_020] 2026-07-26 21:30 sender=(n/a) group=(n/a) business=business_041 text="You are today's lucky winner! Claim within 1 hour." | reaction: opened=0 replied=0 dismissed=1 muted_after=0 reported=1
  [fx_h_021] 2026-07-23 17:10 sender=u_013 group=(n/a) business=(n/a) text="Are you free to talk this evening?" | reaction: opened=1 replied=1 dismissed=0 muted_after=0 reported=0
```

```yaml
message_id:   synth_msg_20
action:       mute
message_type: scam
note:         
```

---
