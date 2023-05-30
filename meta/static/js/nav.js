function openMenu() {
    let hamburgerMenuContainer = document.querySelector("#hamburger-menu-container")
    hamburgerMenuContainer.classList.add('show-hamburger-menu')
    isMenuOpened = true
}

function closeMenu() {
    let hamburgerMenuContainer = document.querySelector("#hamburger-menu-container")
    hamburgerMenuContainer.classList.remove('show-hamburger-menu')
}

document.addEventListener('click', (event)=>{
    const hamburgerMenuContainer = document.querySelector('#hamburger-menu-container')
    const hamburgerButton = document.querySelector('#hamburger-button')

    if (!hamburgerMenuContainer.contains(event.target) && 
        !hamburgerButton.contains(event.target) &&
        isMenuOpened) {
            closeMenu()
    }
})

window.addEventListener('resize', ()=>{
    if (window.innerWidth > 590) {
        closeMenu()
        /* let hamburgerMenuContainer = document.querySelector('hamburger-menu-container') */
    }
})


let isMenuOpened = false