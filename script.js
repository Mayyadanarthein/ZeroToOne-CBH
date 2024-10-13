document.addEventListener('DOMContentLoaded', function() {
    const joinRoom = document.getElementById('joinRoom');
    const makeRoom = document.getElementById('makeRoom');
    const enterRoom = document.getElementById('enterRoom');
    const roomWindow = document.getElementById('roomWindow');
    const roomTitle = document.getElementById('roomTitle');
    const roomDetails = document.getElementById('roomDetails');
    const closeRoom = document.getElementById('closeRoom');

    function showRoom(title, details) {
        roomTitle.textContent = title;
        roomDetails.innerHTML = details;
        roomWindow.style.display = 'flex';
    }

    joinRoom.addEventListener('click', function() {
        showRoom('Join a Random Room', 'You are joining a random room...');
    });

    makeRoom.addEventListener('click', function() {
        showRoom('Make a Room', 'Create your own room here...');
    });

    enterRoom.addEventListener('click', function() {
        showRoom('Enter a Room Code', '<input type="text" placeholder="Enter room code">');
    });

    closeRoom.addEventListener('click', function() {
        roomWindow.style.display = 'none';
    });
});
