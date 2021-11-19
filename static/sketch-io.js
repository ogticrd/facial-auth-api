const socket = io()

socket.on('result', (data) => {
    console.log('Result: ')
    console.log(data)
})

socket.emit('verify', {cedula: '11111111111', id:'fklmndfpoklnkgmnglkd', source: 'data:video/webm;base64,fefjkneflnejfknolfvnrklvnlvkcjnlkvndklvjnlkfjkldjfekfnkwelfnwkfwefwejm;kfmwekfwem;fwekwenfk;lwenf;wekfnwekfnwe;kbn;lfmneljmwelfjme;lfnwe;knwekvnwlfjkwnklwndjwekbdwjhcvwbhjbcwejhvbkebvjkbvfkjvbfjkvbfdjkvbefjkvbefjkvbefjvbeflvbefvklbjlfvbelfvbefjldknfoadknfjdlkfgnsdljkg'}, sendConfirmation)
function sendConfirmation(){
    console.log('Sent to verify')
}