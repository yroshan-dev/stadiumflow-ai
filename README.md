# StadiumFlow AI

StadiumFlow AI is a GenAI-enabled smart stadium assistant built for the Smart Stadiums & Tournament Experience challenge.

The solution supports fans, volunteers, organizers, and venue staff during large tournaments such as the FIFA World Cup 2026. It helps improve stadium navigation, crowd management, accessibility support, multilingual-style assistance, and real-time operational decision support.

## Chosen Vertical

Smart Stadiums & Tournament Experience.

## Problem Statement

Large stadium events create operational pressure for fans and venue teams. Fans may struggle with navigation, exits, transport, accessibility needs, food zones, queues, and emergency support. Venue staff and volunteers also need fast, clear, and context-aware instructions during crowded situations.

A normal information page is not enough because stadium conditions can change quickly. StadiumFlow AI acts as a decision-support assistant that converts user context and live operational inputs into clear guidance.

## Approach and Logic

The project uses a lightweight decision engine to analyze stadium context.

The system considers:

- User type
- Current location
- Fan need
- Crowd level
- Wait time
- Incident count
- Zone risk
- Accessibility needs
- Volunteer role

Based on these inputs, the system generates:

- Fan guidance
- Crowd-risk labels
- Ranked stadium zones
- Volunteer briefings
- Accessibility-aware movement advice

The app uses transparent rule-based logic to simulate GenAI-style assistance without requiring external APIs or secret keys.

## How the Solution Works

The app contains four assistant modes:

### 1. Fan Assistant

Fans enter their location and need. The assistant generates short, clear guidance for navigation, transport, medical support, food zones, or exits.

### 2. Crowd Intelligence Dashboard

Venue staff enter crowd levels, wait times, and incidents for stadium zones. The system calculates a risk score and ranks zones by operational priority.

### 3. Volunteer Briefing Generator

Organizers can generate short volunteer instructions based on zone, issue type, and risk level.

### 4. Accessibility Support

The assistant creates simple guidance for wheelchair users, elderly visitors, low-vision visitors, families, and lost visitors.

## Assumptions Made

- Crowd level is entered on a 1 to 5 scale.
- Wait time is estimated by venue staff.
- Incident count refers to currently reported local issues.
- The app is a prototype and does not connect to live stadium sensors.
- The system does not collect or store personal data.

## Evaluation Alignment

### Code Quality

The project separates UI code from decision logic. `app.py` handles the Streamlit interface, while `stadium_engine.py` contains the scoring and recommendation logic.

### Security

The app does not use API keys, passwords, databases, or private user data. It can run locally without secrets.

### Efficiency

The app is lightweight and uses simple Python logic. It has minimal dependencies and stays well under the 10 MB repository limit.

### Testing

The core functions are tested using Pytest in `tests/test_stadium_engine.py`.

### Accessibility

The app includes accessibility-specific guidance for wheelchair access, elderly support, low-vision support, hearing support, families, and lost visitors.

## Tech Stack

- Python
- Streamlit
- Pandas
- Pytest
