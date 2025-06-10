document.addEventListener('DOMContentLoaded', () => {
    const ROOM_CODE = window.ROOM_CODE;
    const playerHand = document.getElementById('player-hand');
    const tableCards = document.getElementById('table-cards');
    const timerDisplay = document.getElementById('timer');
    const swapButton = document.getElementById('swapButton');
    const turnIndicator = document.getElementById('turn-id');
    const winMessage = document.querySelector('.alert-success');

    let selectedHandCard = null;
    let selectedTableCard = null;
    
    let selectedHandIndex = null;
    let selectedTableIndex = null;
    
    let timer = 10;
    let timerInterval = null;
    let isPlayerTurn = false;
    let hasWon = false;

    function getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue;
    }

    function setupCardSelection() {

        playerHand.querySelectorAll('.selectable-card').forEach(card => {
            card.addEventListener('click', () => {
                if (!isPlayerTurn || hasWon) return;

                playerHand.querySelectorAll('.selectable-card').forEach(c => c.classList.remove('border-primary'));
                card.classList.add('border', 'border-primary');
                selectedHandCard = card.dataset.card;
                selectedHandIndex = parseInt(card.dataset.index);
                checkSwapReady();
            });
        });

        tableCards.querySelectorAll('.selectable-card').forEach(card => {
            card.addEventListener('click', () => {
                if (!isPlayerTurn || hasWon) return;

                tableCards.querySelectorAll('.selectable-card').forEach(c => c.classList.remove('border-success'));
                card.classList.add('border', 'border-success');
                selectedTableCard = card.dataset.card;
                selectedTableIndex = parseInt(card.dataset.index);
                checkSwapReady();
            });
        });
    }

    function checkSwapReady() {
        swapButton.disabled = !(selectedHandCard && selectedTableCard && isPlayerTurn && !hasWon);
    }

    swapButton.addEventListener('click', async () => {
        if (!selectedHandCard || !selectedTableCard) return;

        swapButton.disabled = true;  

        try {
            const response = await fetch(`/api/room/${ROOM_CODE}/swap/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    hand_index: selectedHandIndex,
    		    table_index: selectedTableIndex
                })
            });
            
            if (!response.ok) {
                const data = await response.json();
                alert(`Swap failed: ${data.error || 'Unknown error'}`);
                swapButton.disabled = false;
                return;
            }

            selectedHandCard = null;
            selectedTableCard = null;
            swapButton.disabled = true;

            await fetchGameState();

        } catch (error) {
            alert('Error sending swap request.');
            console.error(error);
            swapButton.disabled = false;
        }
    });

    function startTimer(seconds) {
        timer = seconds;
        timerDisplay.textContent = timer;
        clearInterval(timerInterval);
        timerInterval = setInterval(() => {
            timer--;
            timerDisplay.textContent = timer;
            if (timer <= 0) {
                clearInterval(timerInterval);
                timerDisplay.textContent = 'Time UP!';
                
                fetch(`/api/room/${ROOM_CODE}/timeout/`, {
        		method: 'POST',
        		headers: {
            		'X-CSRFToken': getCSRFToken(),
    		    	},
    		})
    		.then(response => {
        		if (!response.ok) {
            		console.error("Failed to notify server about timeout.");
        		}
        		return response.json();
    		})
    		.then(data => {
	        	console.log('Turn ended due to timeout:', data);
        		fetchGameState(); 
    		})
		.catch(error => {
	        console.error("Error in timeout request:", error);
	    	});
               
            }
        }, 1000);
    }

    function stopTimer() {
        clearInterval(timerInterval);
        
        setTimeout(() => {
            	timerDisplay.textContent = '-';
            }, 1000);
    }
    
    async function fetchGameState() {
        try {
            const response = await fetch(`/api/room/${ROOM_CODE}/status/`);
            if (!response.ok) {
        	if (response.status === 404) {
        	    throw new Error('Page not found (404)');
        	}
        	throw new Error(`Failed to fetch game state: ${response.status}`);
   	    }
            const data = await response.json();
            
            if (data.redirect) {
            	window.location.href = data.redirect_url;
            	console.log(data.redirect_url);
            	return;
            }
            
            const currentPlayer = data.players.find(player => player.username === data.current_user);
            let currentTurnPlayer = data.players.find(player => player.is_turn === true);

            updateTableCards(data.table_cards); 
            //updateTurn(currentTurnPlayer.username);
	    updatePlayerHand(currentPlayer.hand);
	    updateWinStatus(currentPlayer.has_won);
	    
	    if (currentTurnPlayer) {
		updateTurn(currentTurnPlayer.username);
	    } else {
    		console.warn("No current turn player found in data.players.");
    		
    		setTimeout(() => {
                window.location.href = `/join/${ROOM_CODE}/`;
                fetch(`/api/endgame/${ROOM_CODE}/`, {
        	    method: 'GET',
        	})
        	.then(response => {
        	    if (!response.ok) {
                	throw new Error("Failed to reset game");
            	    }
        	})
        	.catch(error => {
        	    console.error('Reset error:', error);
        	});
            }, 3000);
	    }
	    
	    if (data.winner_username && data.winner_username !== data.current_user) {
    		showWinnerMessage(data.winner_username);
	    }


            isPlayerTurn = data.your_turn;
            if (isPlayerTurn && !data.players.has_won) {
                swapButton.disabled = !(selectedHandCard && selectedTableCard);
                startTimer(6);
            } else {
                swapButton.disabled = true;
                stopTimer();
            }

        } catch (error) {
            console.error('Error updating game state:', error);
            
            if (error.message.includes('404')) {
        	window.location.href = '/';
    	    }
        }
    }

    function updateTurn(username) {
        turnIndicator.innerHTML = '<strong>Turn:</strong> ' + username;
    }


    function updateTableCards(cards) {
        tableCards.innerHTML = '';
        cards.forEach((card, index) => {
            const div = document.createElement('div');
            div.className = 'card m-2 text-center p-3 selectable-card';
            div.dataset.card = card;
            div.dataset.index = index;
            div.textContent = card;
            tableCards.appendChild(div);
        });
        setupCardSelection();
    }

    function updatePlayerHand(cards) {
        playerHand.innerHTML = '';
        cards.forEach((card, index) => {
            const div = document.createElement('div');
            div.className = 'card m-2 text-center p-3 selectable-card';
            div.dataset.card = card;
            div.dataset.index = index;
            div.textContent = card;
            playerHand.appendChild(div);
        });
        setupCardSelection();
    }

    function updateWinStatus(hasWonFlag) {
        hasWon = hasWonFlag;
        if (hasWon) {
            if (!winMessage) {
            
                const alertDiv = document.createElement('div');
                alertDiv.className = 'alert alert-success text-center fs-4';
                alertDiv.textContent = '🎉 Congratulations! You won the game!';
                playerHand.parentNode.insertBefore(alertDiv, playerHand);
            }
            //add fetch for winning
            swapButton.disabled = true;
            stopTimer();
            
            setTimeout(() => {
            	window.location.href = `/join/${ROOM_CODE}/`;
            	
            }, 3000);
        }
    }
    
    function showWinnerMessage(username) {
        if (!document.querySelector('.alert-info')) {
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-info text-center fs-4';
            alertDiv.textContent = `🏆 ${username} has won the game!`;
            playerHand.parentNode.insertBefore(alertDiv, playerHand);
        
            stopTimer();
            swapButton.disabled = true;

            // Redirect after short delay
            setTimeout(() => {
                window.location.href = `/join/${ROOM_CODE}/`;
                fetch(`/api/endgame/${ROOM_CODE}/`, {
        	    method: 'GET',
        	})
        	.then(response => {
        	    if (!response.ok) {
                	throw new Error("Failed to reset game");
            	    }
        	})
        	.catch(error => {
        	    console.error('Reset error:', error);
        	});
            }, 3000);
    }
}


    fetchGameState();
    setInterval(fetchGameState, 6500); 
});
