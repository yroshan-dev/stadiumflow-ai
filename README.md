# StadiumFlow AI

StadiumFlow AI is a GenAI-powered football match assistant for ticketed fans.

Instead of showing every fan the same generic stadium map, the app uses a fan's ticket number to personalise match-day guidance. After login, the system loads the fan's match, gate, zone, stand, block, row, seat, and preferred language. It then shows nearby toilets, food stalls, water points, medical rooms, steward desks, and emergency exits relevant to that fan's ticket zone.

## Chosen Vertical

Football match fan support.

This version focuses only on ticketed football match fans. It does not try to serve volunteers, stadium administrators, vendors, police, or general event operations. The narrower scope keeps the product easier to test, easier to understand, and more useful for one clear user group.

## Problem

Large football stadiums usually give fans generic maps and broad instructions. During match day, that is not enough.

A fan in the East Stand does not need the whole stadium map. They need fast answers to questions such as:

- Where is my seat?
- Which gate should I use?
- Where is the nearest toilet?
- Where can I get water?
- Where is the nearest first aid room?
- Which exit should I use after the match?

StadiumFlow AI solves this by using the fan's ticket as the starting point for personalised guidance.

## Solution

The app follows a simple ticket-aware flow:

```text
Ticket number
→ Ticket profile
→ Fan zone
→ Zone-specific facilities
→ MyZone AI guidance
