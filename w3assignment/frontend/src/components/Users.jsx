import { useState, useEffect } from 'react'
import { getUsers, createUser, updateUser, deleteUser } from '../api'

function Users() {
    const [users, setUsers] = useState([])
    const [username, setUsername] = useState('')
    const [email, setEmail] = useState('')
    const [editingId, setEditingId] = useState(null)
    const [editUsername, setEditUsername] = useState('')
    const [editEmail, setEditEmail] = useState('')

    useEffect(() => {
        loadUsers()
    }, [])

    function loadUsers() {
        getUsers().then(res => setUsers(res.data))
    }

    function handleCreate() {
        if (!username || !email) return
        createUser({ username, email }).then(() => {
            setUsername('')
            setEmail('')
            loadUsers()
        })
    }

    function handleEdit(user) {
        setEditingId(user.id)
        setEditUsername(user.username)
        setEditEmail(user.email)
    }

    function handleUpdate() {
        updateUser(editingId, { username: editUsername, email: editEmail }).then(() => {
            setEditingId(null)
            loadUsers()
        })
    }

    function handleDelete(id) {
        deleteUser(id).then(() => loadUsers())
    }

    return (
        <div>
            <h2>Users</h2>
            <div className="form-row">
                <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={e => setUsername(e.target.value)}
                />
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                />
                <button onClick={handleCreate}>Add User</button>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Active</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {users.map(user => (
                        <tr key={user.id}>
                            {editingId === user.id ? (
                                <>
                                    <td>{user.id}</td>
                                    <td><input value={editUsername} onChange={e => setEditUsername(e.target.value)} /></td>
                                    <td><input value={editEmail} onChange={e => setEditEmail(e.target.value)} /></td>
                                    <td>{user.is_active ? 'Yes' : 'No'}</td>
                                    <td>
                                        <button onClick={handleUpdate}>Save</button>
                                        <button onClick={() => setEditingId(null)}>Cancel</button>
                                    </td>
                                </>
                            ) : (
                                <>
                                    <td>{user.id}</td>
                                    <td>{user.username}</td>
                                    <td>{user.email}</td>
                                    <td>{user.is_active ? 'Yes' : 'No'}</td>
                                    <td>
                                        <button onClick={() => handleEdit(user)}>Edit</button>
                                        <button onClick={() => handleDelete(user.id)}>Delete</button>
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

export default Users
