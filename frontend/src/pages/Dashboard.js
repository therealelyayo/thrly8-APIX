import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Dashboard() {
  const [templates, setTemplates] = useState([]);
  const [recipients, setRecipients] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [smtp, setSmtp] = useState({ host: '', port: '', username: '', password: '' });
  const [newTemplate, setNewTemplate] = useState({ name: '', content: '' });
  const [newRecipient, setNewRecipient] = useState('');
  const [newSubject, setNewSubject] = useState('');
  const [sendMethod, setSendMethod] = useState('API');
  const [smtpMode, setSmtpMode] = useState('localhost');
  const [sendSpeed, setSendSpeed] = useState(1);
  const [message, setMessage] = useState('');

  const token = localStorage.getItem('access_token');
  const axiosInstance = axios.create({
    baseURL: 'http://localhost:8000',
    headers: { Authorization: `Bearer ${token}` }
  });

  useEffect(() => {
    fetchData();
    fetchSmtp();
  }, []);

  const fetchData = async () => {
    try {
      const [tplRes, recRes, subRes] = await Promise.all([
        axiosInstance.get('/templates'),
        axiosInstance.get('/recipients'),
        axiosInstance.get('/subjects')
      ]);
      setTemplates(tplRes.data);
      setRecipients(recRes.data);
      setSubjects(subRes.data);
    } catch (error) {
      console.error(error);
    }
  };

  const fetchSmtp = async () => {
    try {
      const res = await axiosInstance.get('/smtp_credentials');
      setSmtp(res.data);
    } catch {
      setSmtp({ host: '', port: '', username: '', password: '' });
    }
  };

  const addTemplate = async () => {
    if (!newTemplate.name || !newTemplate.content) return;
    try {
      await axiosInstance.post('/templates', newTemplate);
      setNewTemplate({ name: '', content: '' });
      fetchData();
    } catch (error) {
      console.error(error);
    }
  };

  const addRecipient = async () => {
    if (!newRecipient) return;
    try {
      await axiosInstance.post('/recipients', { email: newRecipient });
      setNewRecipient('');
      fetchData();
    } catch (error) {
      console.error(error);
    }
  };

  const addSubject = async () => {
    if (!newSubject) return;
    try {
      await axiosInstance.post('/subjects', { text: newSubject });
      setNewSubject('');
      fetchData();
    } catch (error) {
      console.error(error);
    }
  };

  const saveSmtp = async () => {
    try {
      await axiosInstance.post('/smtp_credentials', smtp);
      setMessage('SMTP credentials saved.');
    } catch (error) {
      console.error(error);
      setMessage('Failed to save SMTP credentials.');
    }
  };

  const sendEmails = async () => {
    if (templates.length === 0) {
      setMessage('Please add at least one email template.');
      return;
    }
    try {
      const templateId = templates[0].id; // For simplicity, use first template
      const res = await axiosInstance.post('/send_emails', null, {
        params: {
          template_id: templateId,
          send_method: sendMethod,
          smtp_mode: smtpMode,
          send_speed: sendSpeed
        }
      });
      setMessage('Emails sent. Check console for details.');
      console.log(res.data.results);
    } catch (error) {
      console.error(error);
      setMessage('Failed to send emails.');
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    window.location.reload();
  };

  return (
    <div style={{ maxWidth: 800, margin: 'auto', padding: 20 }}>
      <h2>Dashboard</h2>
      <button onClick={logout}>Logout</button>

      <section>
        <h3>Email Templates</h3>
        <input
          type="text"
          placeholder="Template Name"
          value={newTemplate.name}
          onChange={e => setNewTemplate({ ...newTemplate, name: e.target.value })}
        />
        <textarea
          placeholder="Template Content (HTML)"
          value={newTemplate.content}
          onChange={e => setNewTemplate({ ...newTemplate, content: e.target.value })}
          rows={6}
          style={{ width: '100%' }}
        />
        <button onClick={addTemplate}>Add Template</button>
        <ul>
          {templates.map(t => (
            <li key={t.id}>{t.name}</li>
          ))}
        </ul>
      </section>

      <section>
        <h3>Recipients</h3>
        <input
          type="email"
          placeholder="Recipient Email"
          value={newRecipient}
          onChange={e => setNewRecipient(e.target.value)}
        />
        <button onClick={addRecipient}>Add Recipient</button>
        <ul>
          {recipients.map(r => (
            <li key={r.id}>{r.email}</li>
          ))}
        </ul>
      </section>

      <section>
        <h3>Subjects</h3>
        <input
          type="text"
          placeholder="Subject Text"
          value={newSubject}
          onChange={e => setNewSubject(e.target.value)}
        />
        <button onClick={addSubject}>Add Subject</button>
        <ul>
          {subjects.map(s => (
            <li key={s.id}>{s.text}</li>
          ))}
        </ul>
      </section>

      <section>
        <h3>SMTP Credentials</h3>
        <input
          type="text"
          placeholder="Host"
          value={smtp.host}
          onChange={e => setSmtp({ ...smtp, host: e.target.value })}
        />
        <input
          type="number"
          placeholder="Port"
          value={smtp.port}
          onChange={e => setSmtp({ ...smtp, port: e.target.value })}
        />
        <input
          type="text"
          placeholder="Username"
          value={smtp.username}
          onChange={e => setSmtp({ ...smtp, username: e.target.value })}
        />
        <input
          type="password"
          placeholder="Password"
          value={smtp.password}
          onChange={e => setSmtp({ ...smtp, password: e.target.value })}
        />
        <button onClick={saveSmtp}>Save SMTP Credentials</button>
      </section>

      <section>
        <h3>Send Emails</h3>
        <label>
          Send Method:
          <select value={sendMethod} onChange={e => setSendMethod(e.target.value)}>
            <option value="API">API</option>
            <option value="SMTP">SMTP</option>
          </select>
        </label>
        {sendMethod === "SMTP" && (
          <label>
            SMTP Mode:
            <select value={smtpMode} onChange={e => setSmtpMode(e.target.value)}>
              <option value="localhost">Localhost</option>
              <option value="smtp">SMTP Server</option>
            </select>
          </label>
        )}
        <label>
          Send Speed (emails per second):
          <input
            type="number"
            min="0.1"
            step="0.1"
            value={sendSpeed}
            onChange={e => setSendSpeed(parseFloat(e.target.value))}
          />
        </label>
        <button onClick={sendEmails}>Send Emails</button>
      </section>

      {message && <p>{message}</p>}
    </div>
  );
}

export default Dashboard;
