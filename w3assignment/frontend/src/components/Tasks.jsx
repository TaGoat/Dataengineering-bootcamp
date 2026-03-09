import { useState, useEffect } from 'react'
import { getTasks, createTask, updateTask, deleteTask } from '../api'
import { getUsers } from '../api'
import { getProjects } from '../api'

function Tasks() {
    const [tasks, setTasks] = useState([])
    const [users, setUsers] = useState([])
    const [projects, setProjects] = useState([])
    const [title, setTitle] = useState('')
    const [description, setDescription] = useState('')
    const [status, setStatus] = useState('pending')
    const [projectId, setProjectId] = useState('')
    const [assignedTo, setAssignedTo] = useState('')
    const [editingId, setEditingId] = useState(null)
    const [editTitle, setEditTitle] = useState('')
    const [editDescription, setEditDescription] = useState('')
    const [editStatus, setEditStatus] = useState('')

    useEffect(() => {
        loadTasks()
        getUsers().then(res => setUsers(res.data))
        getProjects().then(res => setProjects(res.data))
    }, [])

    function loadTasks() {
        getTasks().then(res => setTasks(res.data))
    }

    function handleCreate() {
        if (!title || !projectId) return
        const data = {
            title,
            description,
            status,
            project_id: parseInt(projectId),
            assigned_to: assignedTo ? parseInt(assignedTo) : null
        }
        createTask(data).then(() => {
            setTitle('')
            setDescription('')
            setStatus('pending')
            setProjectId('')
            setAssignedTo('')
            loadTasks()
        })
    }

    function handleEdit(task) {
        setEditingId(task.id)
        setEditTitle(task.title)
        setEditDescription(task.description || '')
        setEditStatus(task.status)
    }

    function handleUpdate() {
        updateTask(editingId, {
            title: editTitle,
            description: editDescription,
            status: editStatus
        }).then(() => {
            setEditingId(null)
            loadTasks()
        })
    }

    function handleDelete(id) {
        deleteTask(id).then(() => loadTasks())
    }

    function getUserName(id) {
        const user = users.find(u => u.id === id)
        return user ? user.username : '-'
    }

    function getProjectName(id) {
        const project = projects.find(p => p.id === id)
        return project ? project.title : id
    }

    return (
        <div>
            <h2>Tasks</h2>
            <div className="form-row">
                <input
                    type="text"
                    placeholder="Task Title"
                    value={title}
                    onChange={e => setTitle(e.target.value)}
                />
                <input
                    type="text"
                    placeholder="Description"
                    value={description}
                    onChange={e => setDescription(e.target.value)}
                />
                <select value={status} onChange={e => setStatus(e.target.value)}>
                    <option value="pending">Pending</option>
                    <option value="in_progress">In Progress</option>
                    <option value="done">Done</option>
                </select>
                <select value={projectId} onChange={e => setProjectId(e.target.value)}>
                    <option value="">Select Project</option>
                    {projects.map(p => (
                        <option key={p.id} value={p.id}>{p.title}</option>
                    ))}
                </select>
                <select value={assignedTo} onChange={e => setAssignedTo(e.target.value)}>
                    <option value="">Assign To</option>
                    {users.map(u => (
                        <option key={u.id} value={u.id}>{u.username}</option>
                    ))}
                </select>
                <button onClick={handleCreate}>Add Task</button>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Title</th>
                        <th>Description</th>
                        <th>Status</th>
                        <th>Project</th>
                        <th>Assigned To</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {tasks.map(task => (
                        <tr key={task.id}>
                            {editingId === task.id ? (
                                <>
                                    <td>{task.id}</td>
                                    <td><input value={editTitle} onChange={e => setEditTitle(e.target.value)} /></td>
                                    <td><input value={editDescription} onChange={e => setEditDescription(e.target.value)} /></td>
                                    <td>
                                        <select value={editStatus} onChange={e => setEditStatus(e.target.value)}>
                                            <option value="pending">Pending</option>
                                            <option value="in_progress">In Progress</option>
                                            <option value="done">Done</option>
                                        </select>
                                    </td>
                                    <td>{getProjectName(task.project_id)}</td>
                                    <td>{getUserName(task.assigned_to)}</td>
                                    <td>
                                        <button onClick={handleUpdate}>Save</button>
                                        <button onClick={() => setEditingId(null)}>Cancel</button>
                                    </td>
                                </>
                            ) : (
                                <>
                                    <td>{task.id}</td>
                                    <td>{task.title}</td>
                                    <td>{task.description}</td>
                                    <td><span className={`status ${task.status}`}>{task.status}</span></td>
                                    <td>{getProjectName(task.project_id)}</td>
                                    <td>{getUserName(task.assigned_to)}</td>
                                    <td>
                                        <button onClick={() => handleEdit(task)}>Edit</button>
                                        <button onClick={() => handleDelete(task.id)}>Delete</button>
                                    </td>
                                </>
                            )}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}

export default Tasks
