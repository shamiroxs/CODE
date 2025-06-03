document.addEventListener('DOMContentLoaded', () => {
    const playerListElement = document.getElementById('player-list');
    const startGameButton = document.getElementById('start-game');

    let isOwner = false;

    async function fetchRoomStatus() {
        try {
            const response = await fetch(`/api/room/${ROOM_CODE}/status/`);
            if (!response.ok) {
                throw new Error('Failed to fetch room status.');
            }
            const data = await response.json();
            updatePlayerList(data.players);
            checkStartCondition(data);
            if (data.room_status === "playing") {
                window.location.href = `/game/${ROOM_CODE}/`;
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }

    function updatePlayerList(players) {
        playerListElement.innerHTML = '';
        players.forEach((player, index) => {
            const li = document.createElement('li');
            li.className = 'list-group-item';
            li.textContent = player.username + (index === 0 ? ' (Owner)' : '');
            playerListElement.appendChild(li);
        });
    }

    function checkStartCondition(data) {
        const players = data.players;
        const currentUser = data.current_user;

        isOwner = players.length > 0 && players[0].username === currentUser;

        if (players.length >= 3 && isOwner) {
            startGameButton.disabled = false;
            document.getElementById('hostmsg').innerHTML = "";
        } else {
            startGameButton.disabled = true;
            if(isOwner)
            {
            	document.getElementById('hostmsg').innerHTML = "You need at least three players to start playing. <br>Waiting for other players to join...";
            }
        }
    }

    startGameButton.addEventListener('click', async () => {
        try {
            const response = await fetch(`/api/room/${ROOM_CODE}/start/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            });
            if (response.ok) {
                window.location.href = `/game/${ROOM_CODE}/`;
            } else {
                alert('Failed to start game.');
            }
        } catch (error) {
            console.error('Start error:', error);
        }
    });

    function getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue;
    }

    fetchRoomStatus();
    setInterval(fetchRoomStatus, 3000);
});
