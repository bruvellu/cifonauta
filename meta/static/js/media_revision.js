let messagesDiv = document.querySelector('.messages-div')
if (messagesDiv) {
    setInterval(() => {
        messagesDiv.remove()
    }, 9500)
}