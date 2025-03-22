import { socket } from './socket_script.js';

export class UserPage {
    constructor() {
        this.editUserModal = new bootstrap.Modal(document.getElementById('editUserModal'));
        this.newUserModal = new bootstrap.Modal(document.getElementById('newUserModal'));
        this.init();
    }

    init() {
        if (!this.eventListenersSet) {
            this.setupEventListeners();
            this.setupSocketListeners();
            this.fetchUsers();
            this.eventListenersSet = true;
        }
    }

    setupEventListeners() {
        document.addEventListener("click", (event) => {
            if (event.target.classList.contains("edit-btn")) {
                const userId = event.target.closest("li").dataset.userId;
                this.editUser(userId);
            } else if (event.target.classList.contains("delete-btn")) {
                const userId = event.target.closest("li").dataset.userId;
                this.deleteUser(userId);
            }
        });

        document.getElementById("editUserForm").addEventListener("submit", (event) => {
            event.preventDefault();
            const userId = document.getElementById("userId").value;
            const username = document.getElementById("username").value;
            const password = document.getElementById("password").value;
            const role = document.getElementById("role").value;

            socket.emit("save_user", { id: userId, name: username, password, role });
            this.editUserModal.hide();
        });

        document.getElementById("newUserForm").addEventListener("submit", (event) => {
            event.preventDefault();

            const name = document.getElementById("newUsername").value;
            const password = document.getElementById("newPassword").value;
            const role = document.getElementById("newRole").value;

            console.log(`Creating user: ${name}`);

            socket.emit("create_user", { name, password, role });
            this.newUserModal.hide();
        });
    }

    editUser(userId) {
        const userElement = document.querySelector(`[data-user-id="${userId}"]`);
        if (!userElement) return;

        const username = userElement.querySelector(".user-name").textContent.trim();

        document.getElementById("userId").value = userId;
        document.getElementById("username").value = username;
        document.getElementById("password").value = "";
        document.getElementById("role").value = userElement.dataset.role;

        this.editUserModal.show();
    }

    deleteUser(userId) {
        if (confirm("Are you sure?")) {
            socket.emit("delete_user", { id: userId });
        }
    }

    setupSocketListeners() {
        // When a user is created, updated, or deleted, re-fetch the users list
        socket.on("user_created", () => {
            this.fetchUsers();
        });

        socket.on("user_updated", () => {
            this.fetchUsers();
        });

        socket.on("user_deleted", () => {
            this.fetchUsers();
        });

        // When the page is first loaded, fetch the users list
        socket.on("users_list", (data) => {
            this.renderUsers(data.users);
        });
    }

    fetchUsers() {
        // Emit a request to the server to fetch the latest list of users
        socket.emit("get_users");
    }

    renderUsers(users) {
        const adminList = document.getElementById('admin-list');
        const userList = document.getElementById('user-list');

        // Clear current lists
        adminList.innerHTML = '';
        userList.innerHTML = '';

        // Rebuild the user list without breaking the layout
        users.forEach(user => {
            const userElement = this.createUserElement(user);
            
            if (user.role === 'admin') {
                adminList.appendChild(userElement);
            } else {
                userList.appendChild(userElement);
            }
        });
    }

    createUserElement(user) {
        const userElement = document.createElement('li');
        userElement.classList.add('list-group-item', 'd-flex', 'justify-content-between', 'align-items-center');
        userElement.dataset.userId = user.id;
        userElement.dataset.role = user.role;

        userElement.innerHTML = `
            <span class="user-name">${user.name}</span>
            <div>
                <button class="btn btn-sm btn-warning edit-btn">Edit</button>
                <button class="btn btn-sm btn-danger delete-btn">Delete</button>
            </div>
        `;
        
        return userElement;
    }
}
