document.addEventListener("DOMContentLoaded", () => {
    startGame();
    const drawButton = document.getElementById('draw-button');
    const playButton = document.getElementById('play-button');
    const playInput = document.getElementById('play-input');

    drawButton.addEventListener('click', () => {
        fetch('/draw')
            .then(response => response.json())
            .then(data => {
                console.log(data);
                displayPlayerHand(data.player_hand);
                updateDiscardPile(data.top_discard);
                displayComputerHand(data.computer_hand);
                displayMessage(data);
            })
            .catch(error => {
                console.error('Error:', error);
        });
    });

    playButton.addEventListener('click', () => {

        if (playInput.value === '') {
            const messageElement = document.getElementById('chat');
            messageElement.innerHTML += `<p class='error'>Please play a card!</p>`;
            return;
        }

        const cardParts = playInput.value.split(' of ');  // Assuming format "Rank of Suit"
        const card = { rank: cardParts[0], suit: cardParts[1] };
        
        fetch('/play', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({card: card}),
        })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                displayPlayerHand(data.player_hand);
                updateDiscardPile(data.top_discard);
                displayComputerHand(data.computer_hand);
                displayMessage(data);
            })
            .catch(error => {
                console.error('Error:', error);
        });
    });
    

    // Functions to update UI based on server responses
    // e.g., function updateHand(cards) { ... }
});

// AJAX functions to communicate with the Flask server
function startGame() {
    try {
        fetch('/start')
            .then(response => response.json())
            .then(data => {
                displayPlayerHand(data.player_hand);
                updateDiscardPile(data.top_discard);
                displayComputerHand(data.computer_hand);
                // Other UI updates as necessary
            });
    } catch (error) {
        console.log(error);
    }
}

function displayPlayerHand(cards) {
    if (!cards) {
        console.error('Invalid or undefined card data');
        return;
    }
    const handElement = document.getElementById('player-hand');
    handElement.innerHTML = ''; // Wyczyść rękę gracza (nwm czy potrzebne do wywalenia jak cos xpp)
    cards.forEach(card => {
        handElement.innerHTML += `<div class="card">${card.rank} of ${card.suit}</div>`; // Wyswietl karty gracza
    });
}

function updateDiscardPile(card) {
    if (!card) {
        console.error('Invalid or undefined card data');
        return;
    }
    const discardPileElement = document.getElementById('discard-pile');
    discardPileElement.innerHTML = `<div class="card">${card.rank} of ${card.suit}</div>`; // Wyswietl ostatnia karte na stosie
}

function displayComputerHand(cards) {
    if (!cards) {
        console.error('Invalid or undefined card data');
        return;
    }
    const handleElement = document.getElementById('computer-hand');
    handleElement.innerHTML = ''; // Wyczyść rękę komputera (nwm czy potrzebne do wywalenia jak cos xpp)
    //cards.forEach(card => { //for future debbuging
    //    handleElement.innerHTML += `<div class="card">${card.rank} of ${card.suit}</div>`; // Wyswietl karty gracza
    //}); // Wyswietl liczbę kart w ręce komputera
    handleElement.innerHTML += `<div class="card">${cards.length}</div>`; // Wyswietl liczbę kart w ręce komputera
}

function displayMessage(message) {
    if (!message) {
        console.error('Invalid or undefined message');
        return;
    }
    const messageElement = document.getElementById('chat');
    messageElement.innerHTML += `<p>${message.message}<br>${message.computer_turn.message}</p>`; // Wyswietl wiadomosc
}