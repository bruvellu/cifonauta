(() => {
    function openMenu() {
        nav.setAttribute('data-state', 'open')
    }
    
    function closeMenu() {
        nav.setAttribute('data-state', 'close')
    }
    
    const hamburger = document.querySelector('[data-hamburger]')
    const nav = document.querySelector('[data-navigation]')
    const closeNav = nav.querySelector('[data-close-navigation]')

    hamburger.addEventListener('click', openMenu)
    closeNav.addEventListener('click', closeMenu)

    document.addEventListener('click', (event)=>{
        console.log(nav.dataset.state)
        if (!nav.contains(event.target) && 
            !hamburger.contains(event.target) &&
            nav.dataset.state == 'open') {
                closeMenu()
        }
    })
    
    window.addEventListener('resize', ()=>{
        if (window.innerWidth > 1024) {
            closeMenu()
        }
    })
    
})()