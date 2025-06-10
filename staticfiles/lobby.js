document.addEventListener('DOMContentLoaded', () => {
    const playerListElement = document.getElementById('player-list');
    const startGameButton = document.getElementById('start-game');
    const exitRoomButton = document.getElementById('exit-room');

    let isOwner = false;

    async function fetchRoomStatus() {
        try {
            const response = await fetch(`/api/room/${ROOM_CODE}/status/`);
            if (!response.ok) {
            	if (response.status === 404) {
        	    throw new Error('Page not found (404)');
        	}
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
            
            if (error.message.includes('404')) {
        	window.location.href = '/';
    	    }
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
            if(isOwner)
            {
            	document.getElementById('hostmsg').innerHTML = "";
            }
        } else {
            startGameButton.disabled = true;
            if(isOwner)
            {
            	document.getElementById('hostmsg').innerHTML = "You need at least three players to start playing. <br>Waiting for other players to join...";
            }
        }
    }
    if (exitRoomButton) {
    exitRoomButton.addEventListener('click', async () => {
        try {
            const response = await fetch(`/exit/${ROOM_CODE}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            });
            if (!response.ok) {
            	if (response.status === 404) {
        	    throw new Error('Page not found (404)');
        	}
                alert('Failed to start game.');
            }
        } catch (error) {
            console.error('Start error:', error);
        }
        window.location.href = '/';
    });
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
            	if (response.status === 404) {
        	    throw new Error('Page not found (404)');
        	}
                alert('Failed to start game.');
            }
        } catch (error) {
            console.error('Start error:', error);
            
            if (error.message.includes('404')) {
        	window.location.href = '/';
    	    }
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
