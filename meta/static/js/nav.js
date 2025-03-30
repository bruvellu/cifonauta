(() => {
    function openMenu() {
        document.body.append(overlay)

        hamburgerMenu.setAttribute('data-state', 'open')
        closeNav.focus()
    }

    function closeMenu() {
        overlay.remove()

        hamburgerMenu.setAttribute('data-state', 'close')
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
    const hamburgerMenu = document.querySelector('[data-hamburger-menu]')
    const closeNav = hamburgerMenu.querySelector('[data-hamburger-menu-close]')

    const overlay = document.createElement('div')
    overlay.classList.add('overlay')

    const focusableElements = [...hamburgerMenu.querySelectorAll(
        'a, button, input, textarea, select, details, [tabindex]:not([tabindex="-1"])')
    ].filter(elem => {
        if(!elem.hasAttribute('disabled') && !elem.hasAttribute('hidden') && elem.type != 'hidden') return elem
    })

    hamburger.addEventListener('click', openMenu)
    closeNav.addEventListener('click', closeMenu)
    hamburgerMenu.addEventListener('keydown', trapFocus)
    overlay.addEventListener('click', closeMenu)

    window.addEventListener('resize', ()=>{
        if (window.innerWidth > 590) {
            closeMenu()
        }
    })
})()