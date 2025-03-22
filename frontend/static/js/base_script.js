import { socket } from './socket_script.js';
import { MusicPage } from './music_script.js';
import { MoviesPage } from './movies_script.js';
import { LogsPage } from './logs_script.js';
import { SettingsPage } from './settings_script.js';
import { SubscriptionsPage } from './subscriptions_script.js';
import { TasksPage } from './tasks_script.js';
import { UserPage } from './users_script.js';

class BasePage {
    constructor() {
        this.mainContent = document.querySelector('main');
        this.sidebarLinks = document.querySelectorAll('.sidebar-nav-item');
        this.pageInstances = {};

        this.setupSidebar();
    }

    setupSidebar() {
        const currentPage = window.location.pathname.split('/')[1] || 'music';

        this.sidebarLinks.forEach(link => {
            const page = link.getAttribute('data-page');
            link.classList.toggle('active', page === currentPage);

            link.addEventListener('click', (event) => this.handlePageChange(event, page));
        });

        this.loadPage(currentPage);
    }

    handlePageChange(event, page) {
        event.preventDefault();
        window.history.pushState({}, '', `/${page}`);

        this.sidebarLinks.forEach(link => link.classList.remove('active'));
        event.target.classList.add('active');

        this.loadPage(page);
    }

    async loadPage(page) {
        try {
            const response = await fetch(`/${page}`);
            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');

            this.mainContent.innerHTML = doc.querySelector('main').innerHTML;

            this.initPage(page);

        } catch (error) {
            console.error('Error loading page:', error);
            this.mainContent.innerHTML = '<p>Failed to load page. Please try again.</p>';
        }
    }

    initPage(page) {
        if (!this.pageInstances[page]) {
            if (page === 'music') {
                this.pageInstances.music = new MusicPage();
            } else if (page === 'movies') {
                this.pageInstances.movies = new MoviesPage();
            } else if (page === 'logs') {
                this.pageInstances.logs = new LogsPage();
            } else if (page === 'settings') {
                this.pageInstances.settings = new SettingsPage();
            } else if (page === 'subscriptions') {
                this.pageInstances.subscriptions = new SubscriptionsPage();
            } else if (page === 'tasks') {
                this.pageInstances.tasks = new TasksPage();
            } else if (page === 'users') {  
                this.pageInstances.users = new UserPage();
            }
        }

        if (this.pageInstances[page]) {
            console.log(page)
            this.pageInstances[page].init();
        }
    }
}

class Toaster {
    constructor() {
        socket.on("new_toast_msg", (data) => this.createToastMessage(data.title, data.message));
    }

    createToastMessage(header, message) {
        const toastContainer = document.querySelector('.toast-container');
        const toastTemplate = document.getElementById('toast-template').cloneNode(true);
        toastTemplate.classList.remove('d-none');

        toastTemplate.querySelector('.toast-header strong').textContent = header;
        toastTemplate.querySelector('.toast-body').textContent = message;
        toastTemplate.querySelector('.text-muted').textContent = new Date().toLocaleString();

        toastContainer.appendChild(toastTemplate);

        const toast = new bootstrap.Toast(toastTemplate);
        toast.show();

        toastTemplate.addEventListener('hidden.bs.toast', () => toastTemplate.remove());
    }
}

const toaster = new Toaster();

window.showToast = (header, message) => {
    toaster.createToastMessage(header, message);
};

document.addEventListener('DOMContentLoaded', () => new BasePage());
