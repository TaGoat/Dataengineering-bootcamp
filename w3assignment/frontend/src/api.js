import axios from 'axios'

const api = axios.create({
    baseURL: 'http://127.0.0.1:8000'
})

export function getUsers() {
    return api.get('/users/')
}

export function createUser(data) {
    return api.post('/users/', data)
}

export function updateUser(id, data) {
    return api.put(`/users/${id}`, data)
}

export function deleteUser(id) {
    return api.delete(`/users/${id}`)
}

export function getProjects() {
    return api.get('/projects/')
}

export function createProject(data) {
    return api.post('/projects/', data)
}

export function updateProject(id, data) {
    return api.put(`/projects/${id}`, data)
}

export function deleteProject(id) {
    return api.delete(`/projects/${id}`)
}

export function getTasks() {
    return api.get('/tasks/')
}

export function createTask(data) {
    return api.post('/tasks/', data)
}

export function updateTask(id, data) {
    return api.put(`/tasks/${id}`, data)
}

export function deleteTask(id) {
    return api.delete(`/tasks/${id}`)
}
