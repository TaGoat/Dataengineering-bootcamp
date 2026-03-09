import { useState, useEffect } from 'react'
import { getProjects, createProject, updateProject, deleteProject } from '../api'
import { getUsers } from '../api'

function Projects() {
    const [projects, setProjects] = useState([])
    const [users, setUsers] = useState([])
    const [title, setTitle] = useState('')
    const [description, setDescription] = useState('')
    const [ownerId, setOwnerId] = useState('')
    const [editingId, setEditingId] = useState(null)
    const [editTitle, setEditTitle] = useState('')
    const [editDescription, setEditDescription] = useState('')

    useEffect(() => {
        loadProjects()
        getUsers().then(res => setUsers(res.data))
    }, [])

    function loadProjects() {
        getProjects().then(res => setProjects(res.data))
    }

    function handleCreate() {
        if (!title || !ownerId) return
        createProject({ title, description, owner_id: parseInt(ownerId) }).then(() => {
            setTitle('')
            setDescription('')
            setOwnerId('')
            loadProjects()
        })
    }

    function handleEdit(project) {
        setEditingId(project.id)
        setEditTitle(project.title)
        setEditDescription(project.description || '')
    }

    function handleUpdate() {
        updateProject(editingId, { title: editTitle, description: editDescription }).then(() => {
            setEditingId(null)
            loadProjects()
        })
    }

    function handleDelete(id) {
        deleteProject(id).then(() => loadProjects())
    }

    function getUserName(id) {
        const user = users.find(u => u.id === id)
        return user ? user.username : id
    }

    return (
        <div>
            <h2>Projects</h2>
            <div className="form-row">
                <input
                    type="text"
                    placeholder="Project Title"
                    value={title}
                    onChange={e => setTitle(e.target.value)}
                />
                <input
                    type="text"
                    placeholder="Description"
                    value={description}
                    onChange={e => setDescription(e.target.value)}
                />
                <select value={ownerId} onChange={e => setOwnerId(e.target.value)}>
                    <option value="">Select Owner</option>
                    {users.map(user => (
                        <option key={user.id} value={user.id}>{user.username}</option>
                    ))}
                </select>
                <button onClick={handleCreate}>Add Project</button>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Title</th>
                        <th>Description</th>
                        <th>Owner</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {projects.map(project => (
                        <tr key={project.id}>
                            {editingId === project.id ? (
                                <>
                                    <td>{project.id}</td>
                                    <td><input value={editTitle} onChange={e => setEditTitle(e.target.value)} /></td>
                                    <td><input value={editDescription} onChange={e => setEditDescription(e.target.value)} /></td>
                                    <td>{getUserName(project.owner_id)}</td>
                                    <td>
                                        <button onClick={handleUpdate}>Save</button>
                                        <button onClick={() => setEditingId(null)}>Cancel</button>
                                    </td>
                                </>
                            ) : (
                                <>
                                    <td>{project.id}</td>
                                    <td>{project.title}</td>
                                    <td>{project.description}</td>
                                    <td>{getUserName(project.owner_id)}</td>
                                    <td>
                                        <button onClick={() => handleEdit(project)}>Edit</button>
                                        <button onClick={() => handleDelete(project.id)}>Delete</button>
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

export default Projects
