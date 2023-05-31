const hamburger = document.querySelector('.hamburger');
const mobileMenu = document.querySelector('.mobile-menu');
if (hamburger) {
    hamburger.addEventListener('click', function() {
        this.classList.toggle('is-active');
        mobileMenu.classList.toggle('is-open');
    });
}

const acct = document.querySelector('.acct-btn');
const acctMenu = document.querySelector('.account-menu');
if (acct) {
    const acctIcon = acct.querySelector('.material-icons');
    acct.addEventListener('click', () => {
        acctIcon.innerText = acctIcon.innerText === 'pets' ? 'close' : 'pets';
        acctMenu.classList.toggle('is-open');
    });
}

const login = document.querySelector('.login-btn');
const loginMenu = document.querySelector('.login-menu');
if (login) {
    const loginIcon = login.querySelector('.material-icons');
    login.addEventListener('click', () => {
        loginIcon.innerText = loginIcon.innerText === 'pets' ? 'close' : 'pets';
        loginMenu.classList.toggle('is-open');
    });
}

function submitChange() {
    const dropdown = document.getElementsByName("doctor")[0];
    const selectedOption = dropdown.value;
    document.getElementById("selectedOption").value = selectedOption;
    document.getElementById("update").submit();
}

function activeNav(navItem) {
    const nav = document.getElementById(navItem);
    nav.classList.add("is-active");
}