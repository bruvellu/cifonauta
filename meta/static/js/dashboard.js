(() => {
    function openMenu() {
        document.body.append(overlay)

        nav.setAttribute('data-state', 'open')
        closeNav.focus()
    }
    
    function closeMenu() {
        overlay.remove()

        nav.setAttribute('data-state', 'close')
        hamburger.focus()
    }

    function trapFocus(event) {
        const firstFocusable = focusableElements[0]
        const lastFocusable = focusableElements[focusableElements.length - 1]

        if (event.key === 'Tab') {
            if (event.shiftKey && document.activeElement === firstFocusable) {
                event.preventDefault()
                lastFocusable.focus()
            } else if (!event.shiftKey && document.activeElement === lastFocusable) {
                event.preventDefault()
                firstFocusable.focus()
            }
        }
    }
    
    const hamburger = document.querySelector('[data-hamburger]')
    const nav = document.querySelector('[data-navigation]')
    const closeNav = nav.querySelector('[data-close-navigation]')

    const overlay = document.createElement('div')
    overlay.classList.add('overlay')

    const focusableElements = [...nav.querySelectorAll(
        'a, button, input, textarea, select, details, [tabindex]:not([tabindex="-1"])')
    ].filter(elem => {
        if(!elem.hasAttribute('disabled') && !elem.hasAttribute('hidden') && elem.type != 'hidden') return elem
    })

    hamburger.addEventListener('click', openMenu)
    closeNav.addEventListener('click', closeMenu)
    nav.addEventListener('keydown', trapFocus)
    overlay.addEventListener('click', closeMenu)
    
    window.addEventListener('resize', ()=>{
        if (window.innerWidth > 1024) {
            closeMenu()
        }
    })
    
})()