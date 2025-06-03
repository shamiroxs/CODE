document.addEventListener('DOMContentLoaded', () => {
    const ROOM_CODE = window.ROOM_CODE;
    const playerHand = document.getElementById('player-hand');
    const tableCards = document.getElementById('table-cards');
    const timerDisplay = document.getElementById('timer');
    const swapButton = document.getElementById('swapButton');
    const turnIndicator = document.querySelector('div strong');
    const winMessage = document.querySelector('.alert-success');

    let selectedHandCard = null;
    let selectedTableCard = null;
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
                checkSwapReady();
            });
        });

        tableCards.querySelectorAll('.selectable-card').forEach(card => {
            card.addEventListener('click', () => {
                if (!isPlayerTurn || hasWon) return;

                tableCards.querySelectorAll('.selectable-card').forEach(c => c.classList.remove('border-success'));
                card.classList.add('border', 'border-success');
                selectedTableCard = card.dataset.card;
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
                    hand_card: selectedHandCard,
                    table_card: selectedTableCard
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
                swapButton.disabled = true;
                alert("⏱ Time's up! Turn ended.");
               
            }
        }, 1000);
    }

    function stopTimer() {
        clearInterval(timerInterval);
        timerDisplay.textContent = '-';
    }

    async function fetchGameState() {
        try {
            const response = await fetch(`/api/room/${ROOM_CODE}/status/`);
            if (!response.ok) throw new Error('Failed to fetch game state');

            const data = await response.json();
            
            const currentPlayer = data.players.find(player => player.username === data.current_user);

            updateTableCards(data.table_cards);                       
            updateTurn(currentPlayer.username);
	    updatePlayerHand(currentPlayer.hand);
	    updateWinStatus(currentPlayer.has_won);

            isPlayerTurn = data.your_turn;
            if (isPlayerTurn && !data.players.has_won) {
                swapButton.disabled = !(selectedHandCard && selectedTableCard);
                startTimer(10);
            } else {
                swapButton.disabled = true;
                stopTimer();
            }

        } catch (error) {
            console.error('Error updating game state:', error);
        }
    }

    function updateTurn(username) {
        turnIndicator.textContent = username;
    }

    function updateTableCards(cards) {
        tableCards.innerHTML = '';
        cards.forEach(card => {
            const div = document.createElement('div');
            div.className = 'card m-2 text-center p-3 selectable-card';
            div.dataset.card = card;
            div.textContent = card;
            tableCards.appendChild(div);
        });
        setupCardSelection();
    }

    function updatePlayerHand(cards) {
        playerHand.innerHTML = '';
        cards.forEach(card => {
            const div = document.createElement('div');
            div.className = 'card m-2 text-center p-3 selectable-card';
            div.dataset.card = card;
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
            swapButton.disabled = true;
            stopTimer();
        }
    }

    fetchGameState();
    setInterval(fetchGameState, 11000); 
});
