# Renti Domain Context

AI Companion Chatbot and digital intervention system to support young adults and dual-users in Indonesia to quit smoking and vaping.

## Cessation Psychology

**Readiness Stage**:
The user's psychological state of preparedness to quit smoking/vaping based on the MAPR framework and Transtheoretical Model (`precontemplation`, `contemplation`, `action`, `maintenance`, `relapse`).
_Avoid_: User status, progress level, addiction phase

**Urge Surfing**:
A CBT and mindfulness technique where the user observes craving sensations like ocean waves without acting on the urge until it subsides.
_Avoid_: Craving resistance, distraction tactic

**Motivational Interviewing**:
A client-centered counseling approach using OARS and reflective listening to elicit intrinsic motivation and change talk for users in contemplation.
_Avoid_: Persuasion, advice-giving

**Social Refusal Script**:
A contextual rejection script that helps the user politely and assertively refuse cigarette or vape offers in Indonesian social settings like warkop and tongkrongan.
_Avoid_: Rejection template, canned response

## Safety & Governance

**Safety Policy Action**:
The discrete safety governance outcome decided by the policy engine for an incoming message (`ALLOW`, `SAFE_REDIRECT`, `CLARIFY`, `BLOCK_AND_SIGNPOST`).
_Avoid_: Moderation result, filter flag

**Signposting**:
Immediate direct referral to official Indonesian emergency numbers (119 Ext 8 for mental health crises or 119 for medical emergencies) without therapeutic improvisation.
_Avoid_: Hotline recommendation, crisis chat

**Zone Route**:
The operational domain partition for an incoming user turn (`zone_1_craving`, `zone_1_contemplation`, `zone_2_emotional`, `zone_3_out_of_scope`, `refusal_script`, `crisis`).
_Avoid_: Intent category, topic bucket

## Memory & Context

**Rolling Summary**:
An incremental narrative rollup of past conversation turns maintained in persistent storage to provide longitudinal continuity without vector embeddings.
_Avoid_: Conversation memory vector, chat history dump

**Context Tags**:
Structured key-value metadata extracted from conversations describing current triggers, emotional states, and physical locations.
_Avoid_: User tags, session attributes

## Companion Behavior

**Tone**:
The conversational register (`casual`, `standard`, `formal`) that Renti detects from the user's message and mirrors in its replies to keep the interaction natural.
_Avoid_: Writing style, personality, vibe
