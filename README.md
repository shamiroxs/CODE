# CODE: A Real-Time Web-Based Multiplayer Card Game

## Overview

**CODE** is a real-time multiplayer card game designed entirely for the web. Players join a virtual room and race to collect cards spelling out **C-O-D-E** through turn-based card swapping. It is built using Django, JavaScript, and responsive design techniques, the game supports real-time play with room-based coordination, turn handling, and game state persistence.

The inspiration for this project came from a traditional game called **Kozhithala**, which is popular in my hometown. Players write Malayalam letters on paper chits and compete to collect a specific word. I reimagined that analog game for a digital, globally accessible experience using English letters and a theme relevant to computer science students. The result is a modern, lightweight game that honors its roots while embracing new tech.

This project was not only about building a game, it was about solving a real-world social barrier I faced. During my college years, gaming with friends required downloading various apps, connecting to shared hotspots, and figuring out which game group to join. This hassle often prevented me from joining in. **CODE** is my answer: a shared digital space, instantly accessible, where everyone can play together anytime, anywhere.

---

## Snapshots

![Alt text](images/1.png)
![Alt text](images/2.png)
![Alt text](images/3.png)

<a href="https://youtu.be/lF_DLCy6PEA" target="_blank">
  <img src="https://img.shields.io/badge/Watch%20on-YouTube-red?logo=youtube&style=for-the-badge" alt="Watch on YouTube"/>
</a>

---

## Distinctiveness and Complexity
### Distinctiveness:

This project is an interactive, real-time multiplayer game featuring custom mechanics and a fully engineered game loop. I designed and implemented the turn-based logic, player specific hand visibility, game start coordination, win detection, and asynchronous status polling. Inspired by my cultural background, I translated the concept into a web-based format.

### Complexity:

This project simulates a full multiplayer game system using only Django and JavaScript. It manages complex game state (hands, turns, win conditions), synchronizes players via polling without WebSockets, and enforces host-based authority. The dynamic frontend allows real-time interactions like card swapping and timed turns, with instant win detection, all without page reloads.

---

## File Overview

### Core Django Files:

* `views.py`: Handles routes for joining/creating rooms, starting the game, swapping cards, and status polling.
* `models.py`: Defines `Room`, and `Player` models.
* `urls.py`: Maps all routes including game APIs and frontend pages.
* `game_logic.py`: Encapsulates reusable functions like `start_game`, `deal_cards`, `swap_card`, and `check_win`.
* `utils.py`: Contains `generate_room_code()` and `shuffle_deck()` utility functions.

### Templates:

* `layout.html`: Base layout with navigation and scripts used across all pages.
* `home.html`: Homepage with login/register buttons and game intro.
* `create.html`: Room creation interface for hosts.
* `join.html`: Lobby page where players wait for the game to start.
* `game.html`: Main game UI showing cards, timer, and player actions.

### Static Files:

* `styles.css`: Mobile-friendly card grid layout, hover animations, and responsive UI.
* `lobby.js`: Polls server for game start status and auto-redirects players to game screen.
* `game.js`: Handles card swapping, timer countdowns, win detection, and turn interactivity.

### Other:

* `README.md`: You’re reading it.
* `requirements.txt`: Lists required packages.

---

## How to Run the Application

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/code-game.git
   cd code-game
   ```

2. **Create virtual environment and install dependencies**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Apply migrations and start the server**:

   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

4. **Access in your browser**:
   Open `http://127.0.0.1:8000/` and:

   * Login or register
   * Create or join a room
   * Wait for others
   * Start the game
   * Swap cards and race to spell **C-O-D-E**!

---

## Additional Notes

* The app is built without WebSockets. If you’d like to enhance real-time performance, consider using **Django Channels**.
* Guest player support (for anonymous users) can be extended further by assigning random names.
* Victory condition is defined as having a hand that contains exactly one of each: `'C', 'O', 'D', 'E'`.

---

I built this project not just to complete an assignment, but to solve a real problem I encountered in college: **barriers to inclusive, spontaneous gaming**. With CODE, there's no excuse to not jump in and have fun with friends, whether you're in the same room or miles apart.
