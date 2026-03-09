import { useState } from 'react'
import Users from './components/Users'
import Projects from './components/Projects'
import Tasks from './components/Tasks'

function App() {
    const [tab, setTab] = useState('users')

    return (
        <div className="app">
            <h1>Project Manager</h1>
            <div className="tabs">
                <button className={tab === 'users' ? 'active' : ''} onClick={() => setTab('users')}>Users</button>
                <button className={tab === 'projects' ? 'active' : ''} onClick={() => setTab('projects')}>Projects</button>
                <button className={tab === 'tasks' ? 'active' : ''} onClick={() => setTab('tasks')}>Tasks</button>
            </div>
            <div className="content">
                {tab === 'users' && <Users />}
                {tab === 'projects' && <Projects />}
                {tab === 'tasks' && <Tasks />}
            </div>
        </div>
    )
}

export default App
